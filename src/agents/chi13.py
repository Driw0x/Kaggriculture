"""CHI13: targeted CHI12 evolution with global routing and planned land use."""

from collections import Counter
from copy import deepcopy
from math import ceil

from src.agents import chi12 as _base
from src.agents.chi12 import *  # Reuse CHI12's tested engine-facing primitives.


STATES = {}
LAND_ORDER = ("NE", "SW", "SE")
LAND_COSTS = (1000, 2000, 4000)


def quadrant_positions(quadrant):
    x0 = 0 if quadrant in ("NW", "SW") else 5
    y0 = 0 if quadrant in ("NW", "NE") else 5
    return [(x, y) for y in range(y0, y0 + 5) for x in range(x0, x0 + 5)]


def next_land(obs):
    count = len(farm(obs).get("unlocked_quadrants", ["NW"])) - 1
    if count >= len(LAND_ORDER):
        return None
    return LAND_ORDER[count], LAND_COSTS[count]


def projected_land(obs, quadrant):
    result = deepcopy(obs)
    own = result["farms"][result["player"]]
    own["unlocked_quadrants"] = [*own.get("unlocked_quadrants", ["NW"]), quadrant]
    for x, y in quadrant_positions(quadrant):
        if own["tiles"][y][x] == "LOCKED":
            own["tiles"][y][x] = None
    return result


def _crop_profit(obs, crop, final_day):
    if obs["day"] + FIRST_YIELD[crop] > final_day:
        return 0
    expected_yield = MAX_YIELD[crop]
    return expected_yield * obs["market"]["prices"].get(crop, 0) - SEED_COST[crop]


def committed_market_cost(obs, plan, configuration=None):
    """Conservative cash already committed by accepted routes."""
    total = 0
    hire_index = farm(obs)["hires_today"]
    for hour in sorted((plan or {}).get("market", {})):
        for order in plan["market"][hour]:
            op = order[0]
            if op == "BUY_SEED":
                total += SEED_COST[order[1]] * order[2]
            elif op == "BUY_ANIMAL":
                total += ANIMAL_COST[order[1]] * order[2]
            elif op == "BUY_PRODUCT":
                total += obs["market"]["prices"].get(order[1], 0) * order[2]
            elif op == "HIRE":
                total += hire_cost(hire_index, configuration)
                hire_index += 1
    return total


def plan_land_expansion(obs, plan=None, configuration=None):
    """Return a concrete, affordable and routable use plan for the next quadrant."""
    land = next_land(obs)
    _, final_day, last = limits(obs, configuration)
    if land is None or obs["hour"] >= last or obs["day"] >= final_day:
        return None
    quadrant, land_cost = land
    crop, unit_profit = max(
        ((crop, _crop_profit(obs, crop, final_day)) for crop in SEED_COST),
        key=lambda pair: (pair[1], -FIRST_YIELD[pair[0]], pair[0]),
    )
    if unit_profit <= 0:
        return None

    # Installation must fit beside today's accepted work. New hands start at T+1.
    baseline = sum(route["cost"] for route in (plan or {}).get("routes", {}).values())
    workers = len(positions(obs))
    candidates = sorted(quadrant_positions(quadrant),
                        key=lambda pos: (distance(pos, nearest_shed(obs, pos)), pos[1], pos[0]))
    available_cash = farm(obs)["money"] - committed_market_cost(obs, plan, configuration)
    best = None
    for count in range(1, len(candidates) + 1):
        work = baseline + count * 4  # PLANT, WATER and compact travel allowance.
        required_workers = ceil(work / max(1, last - obs["hour"] + 1))
        extra_workers = max(0, required_workers - workers)
        hire_total = sum(hire_cost(farm(obs)["hires_today"] + i, configuration)
                         for i in range(extra_workers))
        cost = land_cost + count * SEED_COST[crop] + hire_total
        profit = count * unit_profit - land_cost - hire_total
        if profit <= 0 or available_cash < cost:
            continue
        best = dict(quadrant=quadrant, cost=land_cost, crop=crop,
                    layout={pos: crop for pos in candidates[:count]},
                    extra_workers=extra_workers, expected_profit=profit)
    return best


def future_shed(obs, routes, market, until=None):
    """Central shed projection: stock + planned returns/buys - pickups/sales."""
    stock = Counter(obs["private"]["shed"])
    until = limits(obs)[2] if until is None else until
    events = []
    for route in routes.values():
        for step in route.get("steps", []):
            if obs["hour"] <= step["hour"] <= until:
                events.append((step["hour"], 0, step["action"], route.get("cargo", {})))
    for hour, orders in market.items():
        if obs["hour"] <= hour <= until:
            events.extend((hour, 1, order, {}) for order in orders)
    for _, _, action, cargo in sorted(events, key=lambda event: event[:2]):
        if action[0] == "PICKUP":
            stock[action[1]] -= action[2]
        elif action[0] == "DROP":
            stock.update(cargo)
        elif action[0] == "SELL":
            stock[action[1]] -= min(stock[action[1]], action[2])
        elif action[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
            stock[action[1]] += action[2]
    return +stock


def consolidate_market_orders(market, start, last, limit=10):
    """One final owner for aggregation, deduplication and per-tick limits."""
    result = {}
    carry = []
    for hour in range(start, last + 1):
        orders = merge_orders(carry + market.get(hour, []), 1000)
        result[hour], carry = orders[:limit], orders[limit:]
    return {hour: orders for hour, orders in result.items() if orders}


def _route_candidate(obs, tasks, worker, start, available, inventory, ready,
                     routes, market, configuration):
    best = None
    for index in range(len(tasks)):
        ordered = tasks[:index] + [tasks[-1]] + tasks[index:-1]
        route = compile_route(obs, ordered, start, available, inventory, ready, configuration)
        if route is not None:
            route = protect_storage(obs, route, routes, market, configuration)
        if route is not None and (best is None or route["cost"] < best["cost"]):
            best = route
    return best


def build_plan(obs, layout, configuration=None, kept=None):
    """Assign every group across existing workers before considering a HIRE."""
    config = configuration or {}
    kept = dict(kept or {})
    reserved = {step["task"] for route in kept.values() for step in route["steps"]
                if step["hour"] >= obs["hour"] and step["task"] is not None}
    remaining = [task for task in generate_tasks(obs, layout, config)
                 if task["position"] not in reserved]
    kept_tasks = [dict(actions=[step["action"] for step in route["steps"]
                                if step["hour"] >= obs["hour"]]) for route in kept.values()]
    market, ready = plan_logistics(obs, kept_tasks + remaining, config)
    routes = kept
    starts = positions(obs)
    inventories = obs["private"]["inventories"]
    initial_workers = len(starts)
    max_workers = config.get("maxWorkers", float("inf"))
    _, _, last = limits(obs, config)
    cap = config.get("maxMarketOrdersPerTurn", 10)

    route_tasks = {worker: [] for worker in range(initial_workers) if worker not in kept}
    while remaining:
        task = remaining[0]
        choices = []
        for worker, assigned in route_tasks.items():
            candidate = _route_candidate(obs, assigned + [task], worker, starts[worker],
                                         obs["hour"], inventories[worker], ready,
                                         routes, market, config)
            if candidate is not None:
                old_cost = routes.get(worker, {}).get("cost", 0)
                choices.append((candidate["cost"] - old_cost, candidate["cost"], worker, candidate))
        if choices:
            _, _, worker, route = min(choices)
            route_tasks[worker] = route["tasks"]
            routes[worker] = route
            remaining.remove(task)
            continue
        reduced = essential_bundle(task)
        if reduced is not None and task["priority"] <= PRODUCTION:
            remaining[0] = reduced
            continue
        break

    money = farm(obs)["money"]
    worker = initial_workers
    while (remaining and remaining[0]["priority"] <= PRODUCTION
           and worker < max_workers):
        cost = hire_cost(farm(obs)["hires_today"] + worker - initial_workers, config)
        if money < cost:
            break
        hire_hour = next((hour for hour in range(obs["hour"], last)
                          if len(market.get(hour, [])) < cap), None)
        if hire_hour is None:
            break
        occupants = Counter(position_at(routes.get(i, {}), pos, hire_hour)
                            for i, pos in enumerate(starts))
        start = min(shed_tiles(obs), key=lambda pos: (occupants[pos], shed_tiles(obs).index(pos)))
        assigned = []
        route = None
        for task in list(remaining):
            candidate = compile_route(obs, assigned + [task], start, hire_hour + 1,
                                      {}, ready, config)
            if candidate is not None:
                candidate = protect_storage(obs, candidate, routes, market, config)
            if candidate is not None:
                assigned, route = candidate["tasks"], candidate
                remaining.remove(task)
        if route is None:
            break
        route["hire_hour"] = hire_hour
        routes[worker] = route
        market.setdefault(hire_hour, []).append(["HIRE"])
        starts.append(start)
        money -= cost
        worker += 1

    for worker, inventory in enumerate(inventories):
        if worker not in routes and any(inventory.values()):
            route = compile_route(obs, [], starts[worker], obs["hour"], inventory,
                                  configuration=config)
            if route:
                routes[worker] = route

    pickups, seed_need = Counter(), Counter()
    for route in routes.values():
        for step in route["steps"]:
            if step["hour"] < obs["hour"]:
                continue
            if step["action"][0] == "PICKUP":
                pickups[step["action"][1]] += step["action"][2]
            elif step["action"][0] == "PLANT":
                seed_need[step["action"][1]] += 1
    for orders in market.values():
        for order in orders:
            if order[0] in ("BUY_PRODUCT", "BUY_ANIMAL"):
                order[2] = max(0, pickups[order[1]] - obs["private"]["shed"].get(order[1], 0))
            elif order[0] == "BUY_SEED":
                order[2] = max(0, seed_need[order[1]] - obs["private"]["seeds"].get(order[1], 0))
    market = consolidate_market_orders(market, obs["hour"], last, cap)
    return dict(routes=routes, market=market, unassigned=remaining)


def agent(obs, configuration=None):
    """CHI12 execution loop with CHI13 state, routing and land confirmation."""
    config = configuration or {}
    hour, day = obs["hour"], obs["day"]
    turns, _, last = limits(obs, config)
    tick = day * turns + hour
    player = obs["player"]
    state = STATES.get(player)
    if state is None or tick <= state["tick"]:
        state = dict(day=-1, tick=-1, layout=choose_placements(obs), replans=0,
                     daily_plans=0, blocked_actions=0, storage_waits=0,
                     quadrants=tuple(farm(obs).get("unlocked_quadrants", ["NW"])))
        STATES[player] = state
    quadrants = tuple(farm(obs).get("unlocked_quadrants", ["NW"]))
    land_changed = quadrants != state["quadrants"]
    land_failed = (not land_changed and "land_plan" in state and
                   state.get("land_sent_tick", tick) < tick)
    if land_failed:
        state.pop("land_plan", None)
        state.pop("land_sent_tick", None)
    if land_changed:
        pending = state.pop("land_plan", None)
        if pending and pending["quadrant"] in quadrants:
            state["layout"].update(pending["layout"])
        state["quadrants"] = quadrants
    new_day = day != state["day"]
    if new_day:
        state["plan"] = build_plan(obs, state["layout"], config)
        if "land_plan" not in state:
            candidate = plan_land_expansion(obs, state["plan"], config)
            if candidate and len(state["plan"]["market"].get(hour, [])) < config.get("maxMarketOrdersPerTurn", 10):
                state["land_plan"] = candidate
                state["plan"]["market"].setdefault(hour, []).append(["BUY_LAND"])
        state["day"] = day
        state["daily_plans"] += 1
    plan = state["plan"]
    steps = current_steps(plan, hour)
    stock, seeds = Counter(obs["private"]["shed"]), Counter(obs["private"]["seeds"])
    invalid = {worker for worker, step in sorted(steps.items())
               if not action_valid(obs, worker, step, stock, seeds)}
    invalid.update(changed_routes(obs, plan))
    invalid.update(worker for worker, route in plan["routes"].items()
                   if worker >= len(positions(obs)) and route["available"] <= hour)
    if not new_day:
        failed = {(slot, item) for slot, item, amount in state.get("expected_buys", [])
                  if obs["private"][slot].get(item, 0) < amount}
        for worker, route in plan["routes"].items():
            if any(step["hour"] >= hour and ((step["action"][0] == "PICKUP" and
                    ("shed", step["action"][1]) in failed) or
                    (step["action"][0] == "PLANT" and ("seeds", step["action"][1]) in failed))
                   for step in route["steps"]):
                invalid.add(worker)
    shops = tuple(obs.get("town", {}).get("unlocked_shops", []))
    prices = obs["market"]["prices"]
    economic_change = not new_day and (land_changed or land_failed or
        shops != state.get("shops", shops) or any(
            abs(price - state.get("prices", prices).get(item, price)) > max(10, price * .3)
            for item, price in prices.items()))
    if invalid or economic_change:
        kept = {worker: route for worker, route in plan["routes"].items()
                if worker not in invalid and worker < len(positions(obs)) and route["finish"] > hour}
        plan = state["plan"] = build_plan(obs, state["layout"], config, kept)
        state["replans"] += 1
        steps = current_steps(plan, hour)
    if new_day or invalid or economic_change:
        state["shops"], state["prices"] = shops, dict(prices)

    stock, seeds = Counter(obs["private"]["shed"]), Counter(obs["private"]["seeds"])
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
    orders = merge_orders([order for order in plan["market"].get(hour, [])
                           if order[0] != "SELL"], 1000)
    market = merge_orders(sell_orders(view, reserve, incoming) + orders,
                          config.get("maxMarketOrdersPerTurn", 10))
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
        elif order[0] == "BUY_LAND":
            state["land_sent_tick"] = tick
    state["expected_buys"] = [(slot, item, (seeds if slot == "seeds" else expected_stock)[item])
                              for slot, item in bought]
    state["tick"] = tick
    return dict(farmer=actions[0], hands=actions[1:], market=market)
