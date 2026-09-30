"""CHI14: CHI13 routing with dated marginal crop economics."""

from collections import Counter, defaultdict
from copy import deepcopy

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

from src.agents.chi13 import *  # Reuse CHI13's tested routing/execution primitives.


STATES = {}


def _configuration(configuration=None):
    config = configuration or {}
    return {
        "turnsPerDay": config.get("turnsPerDay", 24),
        "episodeSteps": config.get("episodeSteps", 720),
        "maxMarketOrdersPerTurn": config.get("maxMarketOrdersPerTurn", 10),
        "townShopSellInterval": config.get("townShopSellInterval", 4),
        "townCenterSellInterval": config.get("townCenterSellInterval", 24),
        "farmHandCostMult": config.get("farmHandCostMult", 1),
    }


def _market_params(obs, configuration=None):
    params = obs["market"].get("params")
    if params:
        return params
    overrides = (configuration or {}).get("marketParams")
    return engine._resolve_market_params(overrides)


def market_projection_valid(obs, configuration=None):
    """The observed quote must agree with the exact local pricing function."""
    params = _market_params(obs, configuration)
    return all(
        engine.market_price(item, obs["market"]["inventory"][item], params)
        == obs["market"]["prices"][item]
        for item in engine.PRODUCTS
    )


def project_market(obs, sales=(), buys=(), configuration=None):
    """Project dated transactions with the engine's unit pricing and town order."""
    config = _configuration(configuration)
    params = _market_params(obs, configuration)
    if not market_projection_valid(obs, configuration):
        return {"valid": False, "reason": "observed market price mismatch"}

    start = obs.get("step", obs["day"] * config["turnsPerDay"] + obs["hour"])
    final = config["episodeSteps"] - 2
    inventory = Counter(obs["market"]["inventory"])
    revenue = Counter()
    expense = Counter()
    quotes = defaultdict(list)
    events = defaultdict(list)
    for sale in sales:
        events[sale["tick"]].append((0 if sale.get("owner") == "opponent" else 1,
                                     "SELL", sale))
    for buy in buys:
        events[buy["tick"]].append((2, "BUY_PRODUCT", buy))

    trajectory = {}
    shops = list(obs.get("town", {}).get("unlocked_shops", []))
    for tick in range(start, final + 1):
        for _, op, event in sorted(events.get(tick, ()), key=lambda value: value[0]):
            item = event["item"]
            owner = event.get("owner", "self")
            for _ in range(max(0, int(event["quantity"]))):
                if op == "SELL":
                    price = engine.market_price(item, inventory[item], params)
                    revenue[owner] += price
                    quotes[tick, item].append(price)
                    if price > engine.PRICE_FLOOR:
                        inventory[item] += 1
                else:
                    price = engine.market_price(item, inventory[item] - 1, params)
                    expense[owner] += price
                    inventory[item] -= 1

        if tick % config["townShopSellInterval"] == 0:
            for shop in shops:  # Duplicates are distinct shop instances.
                products = engine.SHOPS[shop]
                for item in products:
                    inventory[item] -= 2 if len(products) == 1 else 1
        if tick % config["townCenterSellInterval"] == 0:
            for item in engine.TOWN_CENTER_PRODUCTS:
                inventory[item] -= 1
        trajectory[tick] = dict(inventory)

    return {"valid": True, "revenue": revenue, "expense": expense,
            "quotes": dict(quotes), "inventory": dict(inventory),
            "trajectory": trajectory}


def _sell_tick(obs, position, harvest_day, configuration=None):
    """Earliest WATER/HARVEST/return/DROP/SELL sequence on a harvest day."""
    # ponytail: one-worker earliest route; use the daily route simulator here if
    # paired replays show shed/slot contention changing the selected crop.
    config = _configuration(configuration)
    hour = 2 + distance(position, nearest_shed(obs, position)) + 1
    tick = harvest_day * config["turnsPerDay"] + hour
    return tick if tick <= config["episodeSteps"] - 2 else None


def _plant_production(tile, current_day):
    """Remaining dated yields under daily water, without invented fertilizer."""
    crop = tile["crop"]
    data = engine.CROPS[crop]
    planted = tile["planted_day"]
    age = current_day - planted
    events = []
    if data["ongoing"]:
        held = max(0, tile.get("yield_units", 0))
        if held and age >= data["first_yield_day"]:
            events.append((current_day, held))
        for index in range(data["max_yield"]):
            day = planted + data["first_yield_day"] + index * data["interval"]
            if day > current_day:
                events.append((day, 1))
        return events

    harvest_day = max(current_day, planted + data["first_yield_day"])
    if age > data["max_yield_day"] and tile.get("yield_units", 0) <= 0:
        return []
    amount = max(0, tile.get("yield_units", 1))
    start = max(current_day, planted + data["first_yield_day"])
    end = min(harvest_day, planted + data["max_yield_day"])
    for day in range(start, end + 1):
        if day == current_day and tile.get("watered_today"):
            continue
        amount = min(data["max_yield"], amount + 1)
    return [(harvest_day, amount)] if amount else []


def _new_plant_events(crop, planted_day):
    data = engine.CROPS[crop]
    if data["ongoing"]:
        return [(planted_day + data["first_yield_day"] + index * data["interval"], 1)
                for index in range(data["max_yield"])]
    harvest_day = planted_day + data["first_yield_day"]
    bonus_days = sum(data["first_yield_day"] <= age <= data["max_yield_day"]
                     for age in range(data["first_yield_day"] + 1))
    return [(harvest_day, min(data["max_yield"], 1 + bonus_days))]


def production_lots(obs, layout=None, configuration=None, include_opponent=False,
                    install_day=None):
    """Build distinct, sellable dated lots from visible and accepted plants."""
    config = _configuration(configuration)
    final = config["episodeSteps"] - 2
    install_day = obs["day"] if install_day is None else install_day
    lots = []
    seen = set()

    def add(owner, position, crop, events, source):
        for harvest_day, quantity in events:
            tick = _sell_tick(obs, position, harvest_day, configuration)
            if tick is not None and tick <= final and quantity > 0:
                lots.append(dict(owner=owner, position=position, item=crop,
                                 quantity=quantity, harvest_day=harvest_day,
                                 tick=tick, source=source))

    own = farm(obs)
    for y, row in enumerate(own["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                seen.add((x, y))
                add("self", (x, y), tile["crop"], _plant_production(tile, obs["day"]),
                    ("existing", obs["player"], x, y, tile["planted_day"]))

    for position, crop in (layout or {}).items():
        if crop not in SEED_COST or position in seen:
            continue
        add("self", position, crop, _new_plant_events(crop, install_day),
            ("planned", position, install_day))

    if include_opponent:
        for player, other in enumerate(obs["farms"]):
            if player == obs["player"]:
                continue
            for y, row in enumerate(other["tiles"]):
                for x, tile in enumerate(row):
                    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                        add("opponent", (x, y), tile["crop"],
                            _plant_production(tile, obs["day"]),
                            ("visible_opponent", player, x, y, tile["planted_day"]))
    return lots


def _layout_from_plan(obs, plan):
    layout = {}
    for y, row in enumerate(farm(obs)["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and (tile.get("crop") or tile.get("animal")):
                layout[x, y] = tile.get("crop") or tile["animal"]
    for route in (plan or {}).get("routes", {}).values():
        for task in route.get("tasks", []):
            for action in task.get("actions", []):
                if action[0] in ("PLANT", "PLACE"):
                    layout[task["position"]] = action[1]
    return layout


def _hire_total(obs, plan, configuration=None):
    index = farm(obs)["hires_today"]
    total = 0
    for hour in sorted((plan or {}).get("market", {})):
        for order in plan["market"][hour]:
            if order[0] == "HIRE":
                total += hire_cost(index, configuration)
                index += 1
    return total


def evaluate_layout(obs, layout, route_plan=None, configuration=None, land_cost=0):
    """Return central/prudent final coins; unsold output contributes zero."""
    own_central = production_lots(obs, layout, configuration)
    own_prudent = production_lots(obs, layout, configuration, include_opponent=True)
    # Current shed products are part of both references and can affect later prices.
    now = obs.get("step", obs["day"] * _configuration(configuration)["turnsPerDay"] + obs["hour"])
    stock_sales = [dict(owner="self", item=item, quantity=quantity, tick=now)
                   for item, quantity in obs["private"]["shed"].items()
                   if item in engine.PRODUCTS and quantity > 0]
    central = project_market(obs, [*stock_sales, *own_central], configuration=configuration)
    prudent = project_market(obs, [*stock_sales, *own_prudent], configuration=configuration)
    if not central["valid"] or not prudent["valid"]:
        return {"feasible": False, "reason": central.get("reason") or prudent.get("reason")}

    planned = sum(SEED_COST[crop] for position, crop in layout.items()
                  if crop in SEED_COST and not (
                      isinstance(farm(obs)["tiles"][position[1]][position[0]], dict)
                      and farm(obs)["tiles"][position[1]][position[0]].get("crop") == crop))
    hires = _hire_total(obs, route_plan, configuration)
    fixed = planned + hires + land_cost
    money = farm(obs)["money"]
    return {"feasible": True,
            "coins_final": money + central["revenue"]["self"] - fixed,
            "coins_final_prudent": money + prudent["revenue"]["self"] - fixed,
            "revenue": central["revenue"]["self"],
            "revenue_prudent": prudent["revenue"]["self"],
            "seed_cost": planned, "hire_cost": hires, "land_cost": land_cost,
            "lots": own_central, "projection": central,
            "prudent_projection": prudent}


def marginal_crop_contribution(obs, layout, crop, position, route_plan=None,
                               candidate_plan=None, configuration=None):
    """Compare complete reference/candidate portfolios under identical assumptions."""
    reference = evaluate_layout(obs, layout, route_plan, configuration)
    candidate_layout = dict(layout)
    candidate_layout[position] = crop
    candidate = evaluate_layout(obs, candidate_layout, candidate_plan, configuration)
    if not reference.get("feasible") or not candidate.get("feasible"):
        return {"feasible": False}
    return {"feasible": True, "layout": candidate_layout, "evaluation": candidate,
            "contribution": candidate["coins_final"] - reference["coins_final"],
            "contribution_prudent": (candidate["coins_final_prudent"]
                                      - reference["coins_final_prudent"])}


def plan_land_expansion(obs, plan=None, configuration=None):
    """Select each new tile by its recomputed marginal projected contribution."""
    land = next_land(obs)
    _, final_day, last = limits(obs, configuration)
    if land is None or obs["hour"] >= last or obs["day"] >= final_day:
        return None
    if not market_projection_valid(obs, configuration):
        return None
    quadrant, land_cost = land
    virtual = projected_land(obs, quadrant)
    baseline_layout = _layout_from_plan(obs, plan)
    baseline_plan = plan or build_plan(obs, baseline_layout, configuration)
    reference = evaluate_layout(obs, baseline_layout, baseline_plan, configuration)
    if not reference.get("feasible"):
        return None

    accepted = dict(baseline_layout)
    new_layout = {}
    best_prefix = None
    # ponytail: test the earliest feasible install date; add event-derived dates
    # only if paired replays show delayed installation changing the best prefix.
    candidates = sorted(quadrant_positions(quadrant),
                        key=lambda pos: (distance(pos, nearest_shed(virtual, pos)), pos[1], pos[0]))
    current_plan = baseline_plan
    for position in candidates:
        choices = []
        for crop in sorted(SEED_COST):
            if not _new_plant_events(crop, obs["day"]):
                continue
            result = marginal_crop_contribution(
                virtual, accepted, crop, position, current_plan, current_plan, configuration)
            if result.get("feasible") and result["contribution_prudent"] > 0:
                choices.append((result["contribution_prudent"], result["contribution"],
                                crop, result))
        if not choices:
            continue
        selected = None
        for _, _, crop, result in sorted(choices, reverse=True):
            trial_plan = build_plan(virtual, result["layout"], configuration)
            assigned = {task["position"] for route in trial_plan["routes"].values()
                        for task in route["tasks"]}
            if position not in assigned:
                continue
            result = marginal_crop_contribution(
                virtual, accepted, crop, position, current_plan, trial_plan, configuration)
            if result.get("feasible") and result["contribution_prudent"] > 0:
                selected = crop, result, trial_plan
                break
        if selected is None:
            continue
        crop, result, current_plan = selected
        accepted[position] = crop
        new_layout[position] = crop

        with_land = evaluate_layout(virtual, accepted, current_plan, configuration, land_cost)
        gain = with_land["coins_final"] - reference["coins_final"]
        prudent_gain = with_land["coins_final_prudent"] - reference["coins_final_prudent"]
        incremental_seed = with_land["seed_cost"] - reference["seed_cost"]
        incremental_hire = with_land["hire_cost"] - reference["hire_cost"]
        cash_needed = land_cost + incremental_seed + max(0, incremental_hire)
        if prudent_gain > 0 and farm(obs)["money"] - committed_market_cost(
                obs, plan, configuration) >= cash_needed:
            candidate = dict(quadrant=quadrant, cost=land_cost,
                             crop=crop, layout=dict(new_layout),
                             extra_workers=max(0, sum(order == ["HIRE"]
                                 for orders in current_plan["market"].values() for order in orders)
                                 - sum(order == ["HIRE"] for orders in baseline_plan["market"].values()
                                       for order in orders)),
                             expected_profit=gain, prudent_profit=prudent_gain)
            if best_prefix is None or (prudent_gain, gain, len(new_layout)) > (
                    best_prefix[0], best_prefix[1], len(best_prefix[2]["layout"])):
                best_prefix = prudent_gain, gain, candidate
    return best_prefix[2] if best_prefix else None


def agent(obs, configuration=None):
    """CHI13 execution loop with CHI14 marginal land planning."""
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
            if candidate and len(state["plan"]["market"].get(hour, [])) < config.get(
                    "maxMarketOrdersPerTurn", 10):
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
