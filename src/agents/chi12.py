"""CHI12: CHI3 production with the daily planner in docs/chi/detail_corrige.

Routes include explicit loads, deadlines and the return to the shed. Only
invalid routes are rebuilt between daily plans. CHI3 is read-only.
"""

from collections import Counter
from copy import deepcopy

from src.agents.chi3 import (
    ANIMAL_STATE, CROP_PRODUCTION, CROP_STATE, coordinates_to_path, distance,
)


CRITIQUE, PRODUCTION, RENDEMENT, PREPARATION, SECONDAIRE = range(5)
SEED_COST = dict(WHEAT=10, CARROT=20, TOMATO=50, STRAWBERRY=100, MELON=80)
ANIMAL_COST = dict(GOOSE=300, COW=400, SHEEP=500)
FIRST_YIELD = dict(WHEAT=2, CARROT=2, TOMATO=8, STRAWBERRY=10, MELON=10)
MAX_YIELD = dict(WHEAT=6, CARROT=4, TOMATO=4, STRAWBERRY=4, MELON=6)
BONUS_WINDOW = dict(WHEAT=(2, 4), CARROT=(2, 3), MELON=(6, 12))
ANIMAL_PRODUCT = dict(GOOSE="EGG", COW="MILK", SHEEP="WOOL")
ANIMAL_TIMING = dict(GOOSE=(4, 1, 4), COW=(8, 2, 6), SHEEP=(6, 3, 6))
PRODUCTS = (*SEED_COST, "EGG", "MILK", "WOOL", "FERTILIZER")
MOVES = dict(NORTH=(0, -1), SOUTH=(0, 1), EAST=(1, 0), WEST=(-1, 0))
STATES = {}


def farm(obs):
    return obs["farms"][obs["player"]]


def limits(obs, configuration=None):
    config = configuration or {}
    turns = config.get("turnsPerDay", 24)
    final_step = config.get("episodeSteps", 720) - 2
    day_end = min(turns - 1, final_step - obs["day"] * turns)
    return turns, final_step // turns, day_end


def shed_tiles(obs):
    half = len(farm(obs)["tiles"]) // 2
    return [(half - 1, half - 1), (half, half - 1),
            (half - 1, half), (half, half)]


def nearest_shed(obs, pos):
    return min(shed_tiles(obs), key=lambda target: distance(pos, target))


def positions(obs):
    return [tuple(farm(obs)["farmer"]), *map(tuple, farm(obs)["hands"])]


def path_between(start, target):
    return coordinates_to_path(start, [(None, target)])


def choose_placements(obs):
    """Retain existing production; put CHI3's most visited objects nearest shed."""
    desired = Counter(data["crop"] for data in CROP_STATE.values())
    desired.update(data["animal"] for data in ANIMAL_STATE.values())
    layout, candidates = {}, []
    for y, row in enumerate(farm(obs)["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and (tile.get("crop") or tile.get("animal")):
                item = tile.get("crop") or tile["animal"]
                layout[x, y] = item
                desired[item] -= 1
            elif tile != "LOCKED":
                candidates.append((x, y))
    order = [*ANIMAL_COST, "TOMATO", "STRAWBERRY", "MELON", "CARROT", "WHEAT"]
    for item in order:
        for _ in range(max(0, desired[item])):
            if not candidates:
                break  # CHI3's 25 objects fit NW: no speculative land expansion.
            similar = [pos for pos, placed in layout.items() if placed == item]
            visits = 4 if item in ANIMAL_COST else 2 if item in ("TOMATO", "STRAWBERRY") else 1

            def cost(pos):
                tile = farm(obs)["tiles"][pos[1]][pos[0]]
                compatible = (isinstance(tile, dict) and
                              tile.get("kind") == ("COOP" if item == "GOOSE" else "PASTURE"))
                return (visits * distance(pos, nearest_shed(obs, pos))
                        + .1 * min((distance(pos, other) for other in similar), default=0)
                        + (0 if tile is None or compatible else 1), pos)

            pos = min(candidates, key=cost)
            candidates.remove(pos)
            layout[pos] = item
    return layout


def harvestable(tile, day):
    if not isinstance(tile, dict) or tile.get("yield_units", 0) <= 0:
        return False
    return (tile.get("animal") in ANIMAL_COST or
            (tile.get("kind") == "PLANT" and
             day - tile["planted_day"] >= FIRST_YIELD[tile["crop"]]))


def fertilize_profitable(obs, tile, final_day):
    crop, day = tile["crop"], obs["day"]
    age = day - tile["planted_day"]
    if tile.get("fertilized_until_day", -1) >= day or tile.get("watered_today"):
        return False
    # Ongoing production at the next refresh uses TODAY's water/fertilizer.
    if crop in BONUS_WINDOW:
        first, _ = BONUS_WINDOW[crop]
        if age != first:
            return False
        extra = {"WHEAT": 2, "CARROT": 1, "MELON": 0}[crop]
    else:
        events = CROP_PRODUCTION[crop]["harvest_ages"]
        extra = sum(age < event <= age + 3 and
                    tile["planted_day"] + event <= final_day for event in events)
        if age + 1 not in events:
            return False
    prices = obs["market"]["prices"]
    return extra * prices.get(crop, 0) > prices.get("FERTILIZER", 100)


def generate_tasks(obs, layout, configuration=None):
    """One ordered, atomic bundle per tile, with per-action priority/deadline."""
    turns, final_day, last = limits(obs, configuration)
    day = obs["day"]
    final = day == final_day
    tasks = []
    prices = obs["market"]["prices"]
    for y, row in enumerate(farm(obs)["tiles"]):
        for x, raw_tile in enumerate(row):
            pos = (x, y)
            tile = raw_tile if isinstance(raw_tile, dict) else {}
            kind = tile.get("kind")
            desired = layout.get(pos)
            actions, priorities, deadlines = [], [], []

            def add(action, priority, deadline=last):
                actions.append(action)
                priorities.append(priority)
                deadlines.append(deadline)

            if kind == "PLANT":
                crop = tile["crop"]
                age = day - tile["planted_day"]
                ongoing = CROP_PRODUCTION[crop]["type"] == "ONGOING"
                ages = CROP_PRODUCTION[crop]["harvest_ages"]
                decay = tile.get("max_lifespan_step", -1)
                risk = decay >= 0 and decay <= (day + 1) * turns
                harvest = harvestable(tile, day) and (final or risk or age >= ages[0])
                finished = (harvest and not ongoing) or (ongoing and age >= ages[-1])
                if not final and fertilize_profitable(obs, tile, final_day):
                    add(["FERTILIZE"], RENDEMENT)
                if not tile.get("watered_today") and (not final or harvest):
                    bonus = crop in BONUS_WINDOW and BONUS_WINDOW[crop][0] <= age <= BONUS_WINDOW[crop][1]
                    if (not final and not finished) or bonus:
                        add(["WATER"], CRITIQUE if tile.get("consecutive_unwatered", 0) else RENDEMENT)
                if harvest:
                    deadline = last
                    if decay >= 0 and decay < (day + 1) * turns:
                        deadline = max(obs["hour"], decay - day * turns)
                    add(["HARVEST"], CRITIQUE if risk or final else PRODUCTION, deadline)
                if not finished or (finished and not harvest and tile.get("yield_units", 0)):
                    desired = None
            elif tile.get("animal") in ANIMAL_COST:
                animal = tile["animal"]
                first, interval, cap = ANIMAL_TIMING[animal]
                age = day - tile["placed_day"]
                next_yield = age + 1 >= first and (age + 1 - first) % interval == 0
                if not final and not tile.get("fed_today"):
                    add(["FEED"], CRITIQUE if tile.get("consecutive_unfed", 0) else PRODUCTION)
                if tile.get("yield_units", 0):
                    saturation = next_yield and tile["yield_units"] + 1 + tile.get("pending_care_bonus", 0) >= cap
                    add(["HARVEST"], CRITIQUE if saturation or final else PRODUCTION)
                if not final and not tile.get("cared_today"):
                    add(["CARE"], RENDEMENT)
                if tile.get("fertilizer_available"):
                    add(["COLLECT_FERTILIZER"], SECONDAIRE)
                desired = None
            if desired in SEED_COST and day + FIRST_YIELD[desired] <= final_day:
                if raw_tile is not None and not (kind == "PLANT" and ["HARVEST"] in actions and
                                                CROP_PRODUCTION[tile["crop"]]["type"] == "ONE_TIME"):
                    add(["DIG"], PREPARATION)
                add(["PLANT", desired], PRODUCTION)
                add(["WATER"], PRODUCTION)
            elif desired in ANIMAL_COST and day + ANIMAL_TIMING[desired][0] <= final_day:
                structure = "COOP" if desired == "GOOSE" else "PASTURE"
                if kind != structure:
                    if raw_tile is not None:
                        add(["DIG"], PREPARATION)
                    add(["BUILD_" + structure], PRODUCTION)
                add(["PLACE", desired], PRODUCTION)
                add(["FEED"], PRODUCTION)
                add(["CARE"], RENDEMENT)
            if actions:
                product = tile.get("crop") or ANIMAL_PRODUCT.get(tile.get("animal"), desired)
                value = prices.get(product, 0) * max(1, tile.get("yield_units", 0))
                tasks.append(dict(position=pos, actions=actions, priorities=priorities,
                                  deadlines=deadlines, priority=min(priorities),
                                  deadline=min(deadlines), value=value))
    return sorted(tasks, key=lambda task: (task["deadline"], task["priority"], -task["value"]))


def requirements(tasks):
    items, seeds = Counter(), Counter()
    for task in tasks:
        for action in task["actions"]:
            if action[0] == "FEED":
                items["WHEAT"] += 1
            elif action[0] == "FERTILIZE":
                items["FERTILIZER"] += 1
            elif action[0] == "PLACE":
                items[action[1]] += 1
            elif action[0] == "PLANT":
                seeds[action[1]] += 1
    return items, seeds


def simulate_tile_action(tile, action, day, inventory, turns=24):
    """Small inventory/yield forecast, checked against the engine in tests."""
    tile = deepcopy(tile)
    op = action[0]
    if op in ("DIG", "BUILD_COOP", "BUILD_PASTURE", "PLANT", "PLACE"):
        if op == "DIG":
            return None
        if op.startswith("BUILD_"):
            return {"kind": op[6:]}
        item = action[1]
        if op == "PLANT":
            ongoing = CROP_PRODUCTION[item]["type"] == "ONGOING"
            return dict(kind="PLANT", crop=item, planted_day=day, watered_today=False,
                        consecutive_unwatered=1, yield_units=0 if ongoing else 1,
                        max_lifespan_step=-1 if ongoing else (day + BONUS_WINDOW[item][1] + 1) * turns,
                        fertilized_until_day=-1)
        inventory[item] -= 1
        return dict(kind="COOP" if item == "GOOSE" else "PASTURE", animal=item,
                    placed_day=day, fed_today=False, consecutive_unfed=0, cared_today=False,
                    yield_units=0, fertilizer_available=False, pending_care_bonus=0)
    if op == "FERTILIZE":
        inventory["FERTILIZER"] -= 1
        tile["fertilized_until_day"] = max(tile.get("fertilized_until_day", -1), day + 2)
    elif op == "WATER":
        crop = tile["crop"]
        age = day - tile["planted_day"]
        if not tile.get("watered_today") and crop in BONUS_WINDOW:
            start, end = BONUS_WINDOW[crop]
            if start <= age <= end:
                bonus = 2 if tile.get("fertilized_until_day", -1) >= day else 1
                tile["yield_units"] = min(MAX_YIELD[crop], tile["yield_units"] + bonus)
        tile["watered_today"] = True
    elif op == "HARVEST":
        item = tile.get("crop") or ANIMAL_PRODUCT[tile["animal"]]
        inventory[item] += tile["yield_units"]
        tile["yield_units"] = 0
        if item in BONUS_WINDOW:
            return None
    elif op == "FEED":
        inventory["WHEAT"] -= 1
        tile["fed_today"] = True
    elif op == "CARE":
        tile["cared_today"] = True
    elif op == "COLLECT_FERTILIZER":
        inventory["FERTILIZER"] += 1
        tile["fertilizer_available"] = False
    return tile


def compile_route(obs, tasks, start, available, inventory=None, ready=None, configuration=None):
    """Return None if any action or final DROP misses its real playable tick."""
    turns, _, last = limits(obs, configuration)
    needs, seed_need = requirements(tasks)
    inventory = Counter(inventory or {})
    pickups = Counter({item: max(0, amount - inventory[item]) for item, amount in needs.items()})
    ready = ready or {}
    pos, tick, steps = tuple(start), available, []

    def emit(action, tile=None, task=None):
        nonlocal pos, tick
        steps.append(dict(hour=tick, position=pos, action=action,
                          tile=deepcopy(tile), task=task))
        if action[0] in MOVES:
            dx, dy = MOVES[action[0]]
            pos = pos[0] + dx, pos[1] + dy
        tick += 1

    def travel(target):
        for action in path_between(pos, target):
            emit(action)

    if any(pickups.values()):
        travel(nearest_shed(obs, pos))
    for item, amount in pickups.items():
        if amount:
            while tick < ready.get(("item", item), available):
                emit(["PASS"])
            emit(["PICKUP", item, amount])
            inventory[item] += amount
    seed_ready = max((ready.get(("seed", item), available) for item in seed_need), default=available)
    while tick < seed_ready:
        emit(["PASS"])
    for task in tasks:
        travel(task["position"])
        tile = deepcopy(farm(obs)["tiles"][pos[1]][pos[0]])
        for action, deadline in zip(task["actions"], task["deadlines"]):
            if tick > deadline:
                return None
            emit(action, tile, task["position"])
            tile = simulate_tile_action(tile, action, obs["day"], inventory, turns)
    cargo = +inventory
    if cargo:
        travel(nearest_shed(obs, pos))
        emit(["DROP"])
    if tick > last + 1:
        return None
    return dict(tasks=list(tasks), steps=steps, start=tuple(start), available=available,
                pickups=+pickups, seeds=seed_need, cargo=cargo, finish=tick,
                cost=tick - available)


def merge_orders(orders, limit=10):
    merged, indices = [], {}
    for order in orders:
        if len(order) == 3:
            key = tuple(order[:2])
            if key in indices:
                merged[indices[key]][2] += order[2]
                continue
            if order[2] <= 0:
                continue
            indices[key] = len(merged)
        merged.append(list(order))
    return merged[:limit]


def sell_orders(obs, reserve=None, incoming=None):
    reserve = reserve or {}
    stock = Counter(obs["private"]["shed"]) + Counter(incoming or {})
    # CHI3 has no sale policy. Sell surplus immediately, reserving route inputs.
    return [["SELL", item, amount - reserve.get(item, 0)]
            for item, amount in stock.items()
            if item in PRODUCTS and amount > reserve.get(item, 0)]


def plan_logistics(obs, tasks, configuration=None):
    cap = (configuration or {}).get("maxMarketOrdersPerTurn", 10)
    items, seed_need = requirements(tasks)
    stock = obs["private"]["shed"]
    sales = sell_orders(obs, items)
    buys = [["BUY_PRODUCT" if item in PRODUCTS else "BUY_ANIMAL", item, n - stock.get(item, 0)]
            for item, n in items.items() if n > stock.get(item, 0)]
    buys += [["BUY_SEED", item, n - obs["private"]["seeds"].get(item, 0)]
             for item, n in seed_need.items() if n > obs["private"]["seeds"].get(item, 0)]
    orders = merge_orders(sales + buys, 1000)
    market, ready = {}, {}
    for index, order in enumerate(orders):
        hour = obs["hour"] + index // cap
        market.setdefault(hour, []).append(order)
        if order[0].startswith("BUY_"):
            ready["seed" if order[0] == "BUY_SEED" else "item", order[1]] = hour + 1
    return market, ready


def position_at(route, current, hour):
    pos = tuple(current)
    for step in route.get("steps", []):
        if step["hour"] > hour:
            break
        pos = step["position"]
        if step["action"][0] in MOVES:
            dx, dy = MOVES[step["action"][0]]
            pos = pos[0] + dx, pos[1] + dy
    return pos


def hire_cost(count, configuration=None):
    a, b = 1, 1
    for _ in range(count):
        a, b = b, a + b
    return a * (configuration or {}).get("farmHandCostMult", 1)


def protect_storage(obs, route, other_routes, market, configuration=None):
    """Reserve each future DROP before sales; redistribute if returns won't fit.

Surplus is sold every tick. A return may wait for those sales, but its HARVEST
is unchanged. Rejecting an insertion leaves that bundle for another route.
"""
    config = configuration or {}
    capacity = config.get("shedCapacity", 100)
    _, _, last = limits(obs, config)
    while True:
        routes = [*other_routes.values(), route]
        events = {}
        reserve = Counter()
        for current in routes:
            for step in current["steps"]:
                if step["hour"] < obs["hour"]:
                    continue
                action = step["action"]
                if action[0] == "PICKUP":
                    reserve[action[1]] += action[2]
                if action[0] in ("PICKUP", "DROP"):
                    events.setdefault(step["hour"], []).append((action, current["cargo"]))
        stock = Counter(obs["private"]["shed"])
        overflow = False
        for hour in range(obs["hour"], last + 1):
            for action, cargo in events.get(hour, []):
                if action[0] == "PICKUP":
                    stock[action[1]] -= action[2]
                    reserve[action[1]] -= action[2]
                else:
                    stock.update(cargo)
                    overflow |= sum(stock.values()) > capacity
            if overflow:
                break
            for item in PRODUCTS:
                stock[item] = min(stock[item], reserve[item])
            for order in market.get(hour, []):
                if order[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
                    stock[order[1]] += order[2]
        if not overflow:
            return route
        if not route["steps"] or route["steps"][-1]["action"] != ["DROP"] or route["finish"] > last:
            return None
        route["steps"][-1]["hour"] += 1
        route["finish"] += 1
        route["cost"] += 1


def essential_bundle(task):
    """Keep dependencies and loss prevention when optional care will not fit."""
    indices = [i for i, (action, priority) in enumerate(zip(task["actions"], task["priorities"]))
               if priority <= PRODUCTION or action[0] in ("DIG", "BUILD_COOP", "BUILD_PASTURE")]
    if not indices or len(indices) == len(task["actions"]):
        return None
    result = dict(task)
    for field in ("actions", "priorities", "deadlines"):
        result[field] = [task[field][i] for i in indices]
    return result


def build_plan(obs, layout, configuration=None, kept=None):
    """Greedy insertion with capacity/HIRE and paths from each actual spawn."""
    config = configuration or {}
    kept = dict(kept or {})
    reserved = {step["task"] for route in kept.values() for step in route["steps"]
                if step["hour"] >= obs["hour"] and step["task"] is not None}
    tasks = [task for task in generate_tasks(obs, layout, config) if task["position"] not in reserved]
    kept_tasks = [dict(actions=[step["action"] for step in route["steps"]
                                if step["hour"] >= obs["hour"]]) for route in kept.values()]
    market, ready = plan_logistics(obs, kept_tasks + tasks, config)
    routes = kept
    remaining = list(tasks)
    pos = positions(obs)
    initial_workers = len(pos)
    inventories = obs["private"]["inventories"]
    _, _, last = limits(obs, config)
    cap = config.get("maxMarketOrdersPerTurn", 10)
    money = farm(obs)["money"]
    # Conservative budget: sales are worth at least $1/unit; buys have a price
    # margin. Actual failures are reconciled from the next observation.
    for orders in market.values():
        for op, item, amount in orders:
            if op == "SELL":
                money += amount
            else:
                price = (SEED_COST[item] if op == "BUY_SEED" else ANIMAL_COST[item]
                         if op == "BUY_ANIMAL" else obs["market"]["prices"][item] * 1.1 + 1)
                money -= price * amount
    worker = 0
    while remaining:
        if worker in kept:
            worker += 1
            continue
        hire_hour = None
        if worker < initial_workers:
            start, available = pos[worker], obs["hour"]
            inventory = inventories[worker]
        else:
            cost = hire_cost(farm(obs)["hires_today"] + worker - initial_workers, config)
            if money < cost:
                break
            hire_hour = obs["hour"]
            while len(market.get(hire_hour, [])) >= cap:
                hire_hour += 1
            if hire_hour >= last:
                break
            occupants = Counter(position_at(routes.get(i, {}), p, hire_hour) for i, p in enumerate(pos))
            start = min(shed_tiles(obs), key=lambda p: occupants[p])
            available, inventory = hire_hour + 1, {}
        route_tasks, route = [], None
        # ponytail: greedy insertion on <=25 CHI3 tiles; add local swaps only
        # when measured workloads need better packing, not a generic VRP solver.
        while remaining:
            current = route_tasks[-1]["position"] if route_tasks else start
            ordered = sorted(remaining, key=lambda task: (
                task["deadline"], task["priority"], distance(current, task["position"]), -task["value"]))
            found = False
            for task in ordered:
                candidate = compile_route(obs, route_tasks + [task], start, available,
                                          inventory, ready, config)
                selected = task
                if candidate is None and not route_tasks:
                    selected = essential_bundle(task)
                    if selected:
                        candidate = compile_route(obs, [selected], start, available, inventory, ready, config)
                if candidate is not None:
                    candidate = protect_storage(obs, candidate, routes, market, config)
                if candidate is not None:
                    route_tasks.append(selected)
                    remaining.remove(task)
                    route = candidate
                    found = True
                    break
            if not found:
                break
        if route is None:
            if worker >= initial_workers:
                break
        else:
            routes[worker] = route
            if hire_hour is not None:
                market.setdefault(hire_hour, []).append(["HIRE"])
                route["hire_hour"] = hire_hour
                pos.append(start)
                money -= cost
        worker += 1
    # Return already carried products even when no new task can be assigned.
    for worker, inventory in enumerate(inventories):
        if worker not in routes and any(inventory.values()):
            route = compile_route(obs, [], pos[worker], obs["hour"], inventory, configuration=config)
            if route:
                routes[worker] = route
    # Credit the actual worker inventories; buy only assigned route inputs.
    pickups, seed_need = Counter(), Counter()
    for route in routes.values():
        for step in route["steps"]:
            if step["hour"] < obs["hour"]:
                continue
            action = step["action"]
            if action[0] == "PICKUP":
                pickups[action[1]] += action[2]
            elif action[0] == "PLANT":
                seed_need[action[1]] += 1
    for hour, orders in market.items():
        for order in orders:
            if order[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
                order[2] = max(0, pickups[order[1]] - obs["private"]["shed"].get(order[1], 0))
            elif order[0] == "BUY_SEED":
                order[2] = max(0, seed_need[order[1]] - obs["private"]["seeds"].get(order[1], 0))
        market[hour] = merge_orders(orders, cap)
    return dict(routes=routes, market=market, unassigned=remaining)


def action_valid(obs, worker, step, stock, seeds):
    pos = positions(obs)
    if worker >= len(pos) or pos[worker] != step["position"]:
        return False
    action = step["action"]
    op = action[0]
    inventory = obs["private"]["inventories"][worker]
    tile = farm(obs)["tiles"][pos[worker][1]][pos[worker][0]]
    if op in MOVES or op == "PASS":
        return True
    if op == "PICKUP":
        if pos[worker] not in shed_tiles(obs) or stock.get(action[1], 0) < action[2]:
            return False
        stock[action[1]] -= action[2]
        return True
    if op == "DROP":
        return pos[worker] in shed_tiles(obs)
    if op == "PLANT":
        if tile is not None or seeds.get(action[1], 0) < 1:
            return False
        seeds[action[1]] -= 1
        return True
    if op.startswith("BUILD_"):
        return tile is None
    if not isinstance(tile, dict):
        return False
    expected = step.get("tile")
    if isinstance(expected, dict) and any(tile.get(key) != expected.get(key)
                                         for key in ("kind", "crop", "animal", "planted_day", "placed_day")):
        return False
    if op == "DIG":
        return "animal" not in tile
    if op == "PLACE":
        return ("animal" not in tile and tile.get("kind") == ("COOP" if action[1] == "GOOSE" else "PASTURE")
                and inventory.get(action[1], 0) >= 1)
    if op == "HARVEST":
        return harvestable(tile, obs["day"])
    if op == "WATER":
        return tile.get("kind") == "PLANT" and not tile.get("watered_today")
    if op == "FERTILIZE":
        return tile.get("kind") == "PLANT" and inventory.get("FERTILIZER", 0) >= 1
    if tile.get("animal") not in ANIMAL_COST:
        return False
    if op == "FEED":
        return not tile.get("fed_today") and inventory.get("WHEAT", 0) >= 1
    if op == "CARE":
        return not tile.get("cared_today")
    return op == "COLLECT_FERTILIZER" and tile.get("fertilizer_available", False)


def current_steps(plan, hour):
    return {worker: step for worker, route in plan["routes"].items()
            for step in route["steps"] if step["hour"] == hour}


def changed_routes(obs, plan):
    """Detect unexpected weeds/production before workers travel to those tiles."""
    changed = set()
    for worker, route in plan["routes"].items():
        checked = set()
        for step in route["steps"]:
            pos = step["task"]
            if step["hour"] < obs["hour"] or pos is None or pos in checked:
                continue
            checked.add(pos)
            actual = farm(obs)["tiles"][pos[1]][pos[0]]
            expected = step["tile"]
            if isinstance(actual, dict) and isinstance(expected, dict):
                fields = ("kind", "crop", "animal", "planted_day", "placed_day", "yield_units")
                mismatch = any(actual.get(key) != expected.get(key) for key in fields)
            else:
                mismatch = actual != expected
            if mismatch:
                changed.add(worker)
                break
    return changed


def protected_inputs(plan, hour):
    reserve = Counter()
    for route in plan["routes"].values():
        for step in route["steps"]:
            if step["hour"] >= hour and step["action"][0] == "PICKUP":
                reserve[step["action"][1]] += step["action"][2]
    return reserve


def agent(obs, configuration=None):
    config = configuration or {}
    hour, day = obs["hour"], obs["day"]
    turns, _, last = limits(obs, config)
    tick = day * turns + hour
    player = obs["player"]
    state = STATES.get(player)
    if state is None or tick <= state["tick"]:
        state = dict(day=-1, tick=-1, layout=choose_placements(obs), replans=0,
                     daily_plans=0, blocked_actions=0, storage_waits=0)
        STATES[player] = state
    new_day = day != state["day"]
    if new_day:
        state["plan"] = build_plan(obs, state["layout"], config)
        state["day"] = day
        state["daily_plans"] += 1
    plan = state["plan"]
    steps = current_steps(plan, hour)
    stock = Counter(obs["private"]["shed"])
    seeds = Counter(obs["private"]["seeds"])
    invalid = {worker for worker, step in sorted(steps.items())
               if not action_valid(obs, worker, step, stock, seeds)}
    invalid.update(changed_routes(obs, plan))
    invalid.update(worker for worker, route in plan["routes"].items()
                   if worker >= len(positions(obs)) and route["available"] <= hour)
    if not new_day:
        failed_buys = {(slot, item) for slot, item, amount in state.get("expected_buys", [])
                       if obs["private"][slot].get(item, 0) < amount}
        for worker, route in plan["routes"].items():
            if any(step["hour"] >= hour and (
                (step["action"][0] == "PICKUP" and ("shed", step["action"][1]) in failed_buys) or
                (step["action"][0] == "PLANT" and ("seeds", step["action"][1]) in failed_buys))
                   for step in route["steps"]):
                invalid.add(worker)
    shops = tuple(obs.get("town", {}).get("unlocked_shops", []))
    prices = obs["market"]["prices"]
    economic_change = not new_day and (
        shops != state.get("shops", shops) or
        any(abs(price - state.get("prices", prices).get(item, price)) > max(10, price * .3)
            for item, price in prices.items()))
    if invalid or economic_change:
        kept = {worker: route for worker, route in plan["routes"].items()
                if worker not in invalid and worker < len(positions(obs)) and route["finish"] > hour}
        plan = build_plan(obs, state["layout"], config, kept)
        state["plan"] = plan
        state["replans"] += 1
        steps = current_steps(plan, hour)
    if new_day or invalid or economic_change:
        state["shops"], state["prices"] = shops, dict(prices)
    stock = Counter(obs["private"]["shed"])
    seeds = Counter(obs["private"]["seeds"])
    actions = [["PASS"] for _ in positions(obs)]
    incoming = Counter()
    capacity = config.get("shedCapacity", 100)
    for worker, step in sorted(steps.items()):
        if not action_valid(obs, worker, step, stock, seeds):
            state["blocked_actions"] += 1
            continue
        action = step["action"]
        if action[0] == "DROP":
            cargo = Counter(obs["private"]["inventories"][worker])
            if sum(stock.values()) + sum(incoming.values()) + sum(cargo.values()) > capacity:
                # SELL follows unit actions. Preserve cargo and shift only this
                # return; the harvest is never postponed to make shed space.
                for future in plan["routes"][worker]["steps"]:
                    if future["hour"] >= hour:
                        future["hour"] += 1
                plan["routes"][worker]["finish"] += 1
                state["storage_waits"] += 1
                continue
            incoming.update(cargo)
        actions[worker] = action
    reserve = protected_inputs(plan, hour)
    for action in actions:
        if action[0] == "PICKUP":
            reserve[action[1]] -= action[2]
    view = dict(obs, private=dict(obs["private"], shed=stock))
    sales = sell_orders(view, reserve, incoming)
    orders = merge_orders([order for order in plan["market"].get(hour, []) if order[0] != "SELL"], 1000)
    market = merge_orders(sales + orders, config.get("maxMarketOrdersPerTurn", 10))
    sent = Counter(tuple(order) for order in market if order[0] != "SELL")
    for order in orders:
        key = tuple(order)
        if sent[key]:
            sent[key] -= 1
        elif hour < last:
            plan["market"].setdefault(hour + 1, []).append(order)
    expected_stock = Counter(stock) + incoming
    bought = set()
    for order in market:
        if order[0] == "SELL":
            expected_stock[order[1]] -= min(order[2], expected_stock[order[1]])
        elif order[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
            expected_stock[order[1]] += order[2]
            bought.add(("shed", order[1]))
        elif order[0] == "BUY_SEED":
            seeds[order[1]] += order[2]
            bought.add(("seeds", order[1]))
    state["expected_buys"] = [(slot, item, (seeds if slot == "seeds" else expected_stock)[item])
                              for slot, item in bought]
    state["tick"] = tick
    return dict(farmer=actions[0], hands=actions[1:], market=market)
