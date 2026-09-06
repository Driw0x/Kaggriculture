CROP_STATE = {
    (0, 0): {"crop": "WHEAT", "planted": False, "harvest": False},
    (1, 0): {"crop": "WHEAT", "planted": False, "harvest": False},
    (2, 0): {"crop": "WHEAT", "planted": False, "harvest": False},
    (3, 0): {"crop": "WHEAT", "planted": False, "harvest": False},
    (4, 0): {"crop": "STRAWBERRY", "planted": False, "harvest": False},
    (0, 1): {"crop": "WHEAT", "planted": False, "harvest": False},
    (1, 1): {"crop": "WHEAT", "planted": False, "harvest": False},
    (2, 1): {"crop": "WHEAT", "planted": False, "harvest": False},
    (3, 1): {"crop": "MELON", "planted": False, "harvest": False},
    (4, 1): {"crop": "CARROT", "planted": False, "harvest": False},
    (0, 2): {"crop": "WHEAT", "planted": False, "harvest": False},
    (1, 2): {"crop": "WHEAT", "planted": False, "harvest": False},
    (2, 2): {"crop": "TOMATO", "planted": False, "harvest": False},
    (3, 2): {"crop": "CARROT", "planted": False, "harvest": False},
    (4, 2): {"crop": "CARROT", "planted": False, "harvest": False},
    (0, 3): {"crop": "WHEAT", "planted": False, "harvest": False},
    (1, 3): {"crop": "MELON", "planted": False, "harvest": False},
    (2, 3): {"crop": "CARROT", "planted": False, "harvest": False},
    (0, 4): {"crop": "STRAWBERRY", "planted": False, "harvest": False},
    (1, 4): {"crop": "CARROT", "planted": False, "harvest": False},
    (2, 4): {"crop": "CARROT", "planted": False, "harvest": False},
}

ANIMAL_STATE = {
    (3, 3): {"animal": "GOOSE", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0},
    (4, 3): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0},
    (3, 4): {"animal": "SHEEP", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0},
    (4, 4): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0},
}

ANIMAL_MAX_HELD = {"GOOSE": 4, "COW": 6, "SHEEP": 6}
LAND_COSTS = {1: 1000, 2: 2000, 3: 4000}
MAX_MARKET_ORDERS = 10
SALE_DAY = 5
SALE_DROP_HOUR = 22
SALE_HOUR = 23
LAND_BUY_DAY = 6

CROP_PRODUCTION = {
    "WHEAT": {"type": "ONE_TIME", "harvest_ages": [4]},
    "CARROT": {"type": "ONE_TIME", "harvest_ages": [3]},
    "TOMATO": {"type": "ONGOING", "harvest_ages": [8, 9, 10, 11]},
    "STRAWBERRY": {"type": "ONGOING", "harvest_ages": [10, 12, 14, 16]},
    "MELON": {"type": "ONE_TIME", "harvest_ages": [10]},
}

DAY_1_MARKET = {
    0: [
        ["BUY_SEED", "CARROT", 6], ["BUY_SEED", "STRAWBERRY", 2], ["BUY_ANIMAL", "GOOSE", 1],
        ["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 1], ["BUY_PRODUCT", "WHEAT", 16],
        ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
    ],
    1: [["BUY_SEED", "TOMATO", 1], ["BUY_SEED", "MELON", 2], ["BUY_SEED", "WHEAT", 10]],
}

FARMER_SETUP = [["BUILD_PASTURE"], ["PICKUP", "COW", 2], ["PICKUP", "GOOSE", 1], ["PICKUP", "SHEEP", 1], ["PICKUP", "WHEAT", 4]]

DAY_1_PATHS = {
    0: [["WEST"], ["NORTH"], ["EAST"]],
    1: [["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["SOUTH"]],
    2: [["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"]],
    3: [["WEST"], ["NORTH"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["SOUTH"], ["WEST"], ["SOUTH"]],
    4: [["NORTH"], ["WEST"], ["WEST"]],
}

HAND_SPAWNS_DAY0 = [(5, 4), (4, 5), (5, 5), (4, 4)]
HAND_SPAWNS = [(4, 4), (5, 4), (4, 5), (5, 5)]
FARMER_CAPACITY = 23
HAND_CAPACITY = 22
DAY_TICKS = 24
CENTER = (4, 4)
WORKER_ROUTES = {}
WORKER_STATE = {}
CURRENT_DAY = -1
HIRE_COUNT = 4
HIRES_SENT_DAY = -1
ROUTES_REBUILT_DAY = -1
REAL_WORKER_STARTS = {}
EXPANSION_ACTIVE = False

def get_sale_orders(obs):
    shed = obs["private"]["shed"]
    products = ["FERTILIZER"]
    if obs.get("day", 0) == SALE_DAY and obs.get("hour", 0) == SALE_HOUR:
        products += ["CARROT", "EGG", "WOOL"]
    return [["SELL", product, shed.get(product, 0)] for product in products if shed.get(product, 0) > 0]

def get_land_cash(obs):
    shed = obs["private"]["shed"]
    return obs["farms"][obs["player"]]["money"] + shed.get("FERTILIZER", 0) * obs["market"]["prices"].get("FERTILIZER", 0)

def get_next_land_cost(obs):
    unlocked = obs["farms"][obs["player"]].get("unlocked_quadrants", ["NW"])
    return LAND_COSTS.get(len(unlocked))

def can_buy_land(obs):
    cost = get_next_land_cost(obs)
    return cost is not None and get_land_cash(obs) >= cost

def reset_worker_state(worker_count):
    global WORKER_STATE
    WORKER_STATE = {i: {"path": 0, "stack": [], "done": set(), "target": 0, "pickup_done": False, "active_task": False} for i in range(worker_count)}
    WORKER_STATE[0]["setup"] = 0

def get_worker_position(obs, worker_id):
    farm = obs["farms"][obs["player"]]
    if worker_id == 0:
        return farm["farmer"]
    if worker_id - 1 < len(farm["hands"]):
        return farm["hands"][worker_id - 1]
    return None

def get_worker_spawn(worker_id):
    if worker_id in REAL_WORKER_STARTS:
        return REAL_WORKER_STARTS[worker_id]
    if worker_id == 0:
        return CENTER
    spawns = HAND_SPAWNS_DAY0 if CURRENT_DAY == 0 else HAND_SPAWNS
    return spawns[(worker_id - 1) % len(spawns)]

def get_worker_capacity(worker_id):
    base = FARMER_CAPACITY if worker_id == 0 else HAND_CAPACITY
    if CURRENT_DAY == SALE_DAY:
        base = SALE_DROP_HOUR - get_worker_start_delay(worker_id) - 1
    return base

def get_worker_start_delay(worker_id):
    return 0 if worker_id == 0 else 1

def get_path_action(plan, state):
    if state["path"] >= len(plan):
        return ["PASS"]
    action = plan[state["path"]]
    state["path"] += 1
    return action

def move_toward(current, target):
    x, y = current
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return None

def update_crop_state(obs):
    day = obs.get("day", 0)
    farm = obs["farms"][obs["player"]]
    for pos, data in CROP_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        data["sale_early_harvest"] = False
        data["weed"] = data["crop"] in ("TOMATO", "STRAWBERRY") and isinstance(tile, dict) and tile.get("kind") == "WEED"
        if data["weed"]:
            data["planted"] = False
            data["harvest"] = False
            continue
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or tile.get("crop") != data["crop"]:
            data["planted"] = False
            data["harvest"] = False
            continue
        data["planted"] = True
        age = day - tile["planted_day"]
        production = CROP_PRODUCTION[data["crop"]]
        if production["type"] == "ONE_TIME":
            normal_harvest = age >= production["harvest_ages"][0]
            data["sale_early_harvest"] = data["crop"] == "CARROT" and day == SALE_DAY and age >= 2 and not normal_harvest
            data["harvest"] = normal_harvest or data["sale_early_harvest"]
        else:
            data["harvest"] = age in production["harvest_ages"] or tile.get("yield_units", 0) > 0

def get_crop_actions(pos):
    data = CROP_STATE[pos]
    crop = data["crop"]
    if data.get("weed", False):
        return [["DIG"]] if EXPANSION_ACTIVE else [["DIG"], ["PLANT", crop], ["WATER"]]
    if not data["planted"]:
        return [] if EXPANSION_ACTIVE else [["PLANT", crop], ["WATER"]]
    if not data["harvest"]:
        return [["WATER"]]
    if data.get("sale_early_harvest", False):
        return [["WATER"], ["HARVEST"]]
    if EXPANSION_ACTIVE:
        return [["WATER"], ["HARVEST"]]
    if crop == "WHEAT":
        data["crop"] = "CARROT"
        return [["WATER"], ["HARVEST"], ["PLANT", "CARROT"], ["WATER"]]
    if CROP_PRODUCTION[crop]["type"] == "ONE_TIME":
        return [["WATER"], ["HARVEST"], ["PLANT", crop], ["WATER"]]
    return [["WATER"], ["HARVEST"]]

def update_animal_state(obs):
    farm = obs["farms"][obs["player"]]
    for pos, data in ANIMAL_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        if isinstance(tile, dict) and tile.get("animal") == data["animal"]:
            data["placed"] = True
            data["harvest"] = tile.get("yield_units", 0) > 0
            data["fertilizer"] = tile.get("fertilizer_available", False)
            data["pending_care_bonus"] = tile.get("pending_care_bonus", 0)
        else:
            data["placed"] = False
            data["harvest"] = False
            data["fertilizer"] = False
            data["pending_care_bonus"] = 0

def crop_action_cost(pos):
    data = CROP_STATE[pos]
    if data.get("weed", False):
        return 1 if EXPANSION_ACTIVE else 3
    if not data["planted"]:
        return 0 if EXPANSION_ACTIVE else 2
    if not data["harvest"]:
        return 1
    if data.get("sale_early_harvest", False) or EXPANSION_ACTIVE:
        return 2
    return 4 if CROP_PRODUCTION[data["crop"]]["type"] == "ONE_TIME" else 2

def animal_needs_care(pos):
    data = ANIMAL_STATE[pos]
    if data["animal"] == "GOOSE":
        return True
    return data["pending_care_bonus"] + 1 < ANIMAL_MAX_HELD[data["animal"]]

def get_animal_actions(obs, pos):
    farm = obs["farms"][obs["player"]]
    tile = farm["tiles"][pos[1]][pos[0]]
    data = ANIMAL_STATE[pos]
    animal = data["animal"]
    kind = "COOP" if animal == "GOOSE" else "PASTURE"
    actions = []
    if not isinstance(tile, dict) or tile.get("kind") != kind:
        actions.append(["BUILD_COOP"] if animal == "GOOSE" else ["BUILD_PASTURE"])
    if not data["placed"]:
        actions.append(["PLACE", animal])
    if data["harvest"]:
        actions.append(["HARVEST"])
    if data["fertilizer"]:
        actions.append(["COLLECT_FERTILIZER"])
    actions.append(["FEED"])
    if animal_needs_care(pos):
        actions.append(["CARE"])
    return actions

def get_task_actions(obs, task):
    kind = task[0]
    if kind == "WAIT_WHEAT":
        return []
    if kind == "SHED_DROP":
        return [["DROP"]]
    if kind == "WEED":
        return [["DIG"]]
    if kind == "WHEAT_SUPPLY":
        if EXPANSION_ACTIVE:
            return [["WATER"], ["HARVEST"]]
        CROP_STATE[task[1]]["crop"] = "CARROT"
        return [["WATER"], ["HARVEST"], ["PLANT", "CARROT"], ["WATER"]]
    if kind == "ANIMAL_PRE":
        data = ANIMAL_STATE[task[1]]
        actions = []
        if data["harvest"]:
            actions.append(["HARVEST"])
        if data["fertilizer"]:
            actions.append(["COLLECT_FERTILIZER"])
        if animal_needs_care(task[1]):
            actions.append(["CARE"])
        return actions
    if kind == "ANIMAL_FEED":
        return [["FEED"]]
    if kind == "CROP":
        return get_crop_actions(task[1])
    return get_animal_actions(obs, task[1])

def get_day_1_farmer_action(obs):
    state = WORKER_STATE[0]
    if state["stack"]:
        return state["stack"].pop()
    if state["setup"] < len(FARMER_SETUP):
        action = FARMER_SETUP[state["setup"]]
        state["setup"] += 1
        return action
    pos = get_worker_position(obs, 0)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    if pos in ANIMAL_STATE and pos not in state["done"]:
        state["done"].add(pos)
        state["stack"].extend(reversed(get_animal_actions(obs, pos)))
        return state["stack"].pop()
    return get_path_action(DAY_1_PATHS[0], state)

def get_day_1_hand_action(obs, worker_id):
    if obs.get("hour", 0) == 0:
        return ["PASS"]
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    state = WORKER_STATE[worker_id]
    if state["stack"]:
        return state["stack"].pop()
    if pos in CROP_STATE and pos not in state["done"]:
        state["done"].add(pos)
        state["stack"].extend(reversed(get_crop_actions(pos)))
        return state["stack"].pop()
    return get_path_action(DAY_1_PATHS[worker_id], state)

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def animal_action_cost(pos):
    data = ANIMAL_STATE[pos]
    cost = 1 + int(animal_needs_care(pos))
    if not data["placed"]:
        cost += 2
    if data["harvest"]:
        cost += 1
    if data["fertilizer"]:
        cost += 1
    return cost

def task_action_cost(task):
    kind = task[0]
    if kind == "WAIT_WHEAT":
        return 0
    if kind == "SHED_DROP":
        return 1
    if kind == "WEED":
        return 1
    if kind == "WHEAT_SUPPLY":
        return 2 if EXPANSION_ACTIVE else 4
    if kind == "ANIMAL_PRE":
        data = ANIMAL_STATE[task[1]]
        return int(animal_needs_care(task[1])) + int(data["harvest"]) + int(data["fertilizer"])
    if kind == "ANIMAL_FEED":
        return 1
    if kind == "CROP":
        return crop_action_cost(task[1])
    return animal_action_cost(task[1])

def nearest_task(current_pos, tasks):
    return min(tasks, key=lambda task: (distance(current_pos, task[1]), distance(CENTER, task[1]), -task_action_cost(task)))

def order_tasks(start, tasks):
    ordered = []
    remaining = tasks.copy()
    current = start
    while remaining:
        task = nearest_task(current, remaining)
        ordered.append(task)
        remaining.remove(task)
        current = task[1]
    return ordered

def route_end(start, route):
    return route[-1][1] if route else start

def sequence_cost(start, route):
    cost = 0
    pos = start
    for task in route:
        cost += distance(pos, task[1]) + task_action_cost(task)
        pos = task[1]
    return cost

def route_has_wait(route):
    return any(task[0] == "WAIT_WHEAT" for task in route)

def get_feed_count(route):
    return sum(1 for task in route if task[0] in ("ANIMAL", "ANIMAL_FEED"))

def route_cost(worker_id, route):
    start = get_worker_spawn(worker_id)
    cost = sequence_cost(start, route)
    if get_feed_count(route) and not route_has_wait(route):
        cost += 1
    if CURRENT_DAY == SALE_DAY:
        cost += distance(route_end(start, route), CENTER) + 1
    return cost

def get_expected_wheat_yield(obs, pos):
    tile = obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]]
    if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or tile.get("crop") != "WHEAT":
        return 0
    if CROP_STATE[pos]["harvest"]:
        return 4
    return tile.get("yield_units", 0)

def get_required_wheat_tasks(obs, needed):
    candidates = [("WHEAT_SUPPLY", pos) for pos, data in CROP_STATE.items() if data["crop"] == "WHEAT" and data["planted"] and data["harvest"]]
    candidates.sort(key=lambda task: (-get_expected_wheat_yield(obs, task[1]), distance(CENTER, task[1]), task[1][1], task[1][0]))
    selected = []
    total = 0
    for task in candidates:
        selected.append(task)
        total += get_expected_wheat_yield(obs, task[1])
        if total >= needed:
            return selected
    return None

def get_weed_tasks(obs):
    farm = obs["farms"][obs["player"]]
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "WEED":
                tasks.append(("WEED", (x, y)))
    return tasks

def get_animal_route(start):
    return order_tasks(start, [("ANIMAL", pos) for pos in ANIMAL_STATE])

def get_animal_feed_route():
    return order_tasks(CENTER, [("ANIMAL_FEED", pos) for pos in ANIMAL_STATE])

def assign_normal_routes(obs, hire_count):
    worker_count = hire_count + 1
    routes = {worker_id: [] for worker_id in range(worker_count)}
    crop_tasks = [("CROP", pos) for pos, data in CROP_STATE.items() if data["planted"] or data.get("weed", False) or not EXPANSION_ACTIVE]
    crop_positions = {task[1] for task in crop_tasks}
    weed_tasks = [task for task in get_weed_tasks(obs) if task[1] not in crop_positions]
    tasks = [("ANIMAL", pos) for pos in ANIMAL_STATE] + crop_tasks + weed_tasks
    tasks.sort(key=lambda task: (-task_action_cost(task), distance(CENTER, task[1]), task[1][1], task[1][0]))
    for task in tasks:
        best = None
        for worker_id in range(worker_count):
            route = routes[worker_id]
            candidate = order_tasks(get_worker_spawn(worker_id), route + [task])
            cost = route_cost(worker_id, candidate)
            capacity = get_worker_capacity(worker_id)
            if cost > capacity:
                continue
            unused = capacity - cost
            score = (unused, cost, worker_id)
            if best is None or score < best[0]:
                best = (score, worker_id, candidate)
        if best is None:
            return None
        _, worker_id, candidate = best
        routes[worker_id] = candidate
    return routes

def get_shortage_pair(obs, worker_count, wheat_tasks):
    feed_route = get_animal_feed_route()
    best = None
    for supplier_worker in range(worker_count):
        supply_route = order_tasks(get_worker_spawn(supplier_worker), wheat_tasks) + [("SHED_DROP", CENTER)]
        supply_cost = sequence_cost(get_worker_spawn(supplier_worker), supply_route)
        if supply_cost > get_worker_capacity(supplier_worker):
            continue
        supplier_drop_tick = get_worker_start_delay(supplier_worker) + supply_cost
        for feeder_worker in range(worker_count):
            if feeder_worker == supplier_worker:
                continue
            arrival = get_worker_start_delay(feeder_worker) + distance(get_worker_spawn(feeder_worker), CENTER)
            feeder_finish = max(arrival, supplier_drop_tick) + 1 + sequence_cost(CENTER, feed_route)
            if feeder_finish > DAY_TICKS:
                continue
            score = (max(supplier_drop_tick, feeder_finish), supplier_drop_tick + feeder_finish, supplier_worker, feeder_worker)
            if best is None or score < best[0]:
                best = (score, supplier_worker, feeder_worker, supply_route, supplier_drop_tick)
    return best

def get_feeder_prefix_arrival(worker_id, prefix):
    start = get_worker_spawn(worker_id)
    end = route_end(start, prefix)
    return get_worker_start_delay(worker_id) + sequence_cost(start, prefix) + distance(end, CENTER)

def feeder_prefix_fits(worker_id, prefix, supplier_drop_tick):
    arrival = get_feeder_prefix_arrival(worker_id, prefix)
    if arrival > supplier_drop_tick:
        return False
    route = prefix + [("WAIT_WHEAT", CENTER, len(ANIMAL_STATE))] + get_animal_feed_route()
    return route_cost(worker_id, route) + 1 <= get_worker_capacity(worker_id)

def fill_feeder_prefix(feeder_worker, remaining, supplier_drop_tick):
    prefix = []
    while True:
        best = None
        for task in remaining:
            candidate = order_tasks(get_worker_spawn(feeder_worker), prefix + [task])
            if not feeder_prefix_fits(feeder_worker, candidate, supplier_drop_tick):
                continue
            priority = 0 if task[0] == "ANIMAL_PRE" else 1
            arrival = get_feeder_prefix_arrival(feeder_worker, candidate)
            score = (priority, arrival, distance(CENTER, task[1]))
            if best is None or score < best[0]:
                best = (score, task, candidate)
        if best is None:
            break
        _, task, prefix = best
        remaining.remove(task)
    return prefix

def fill_supplier_suffix(supplier_worker, routes, remaining):
    while remaining:
        route = routes[supplier_worker]
        current = route_end(get_worker_spawn(supplier_worker), route)
        candidates = sorted(remaining, key=lambda task: (distance(current, task[1]), distance(CENTER, task[1]), -task_action_cost(task)))
        selected = None
        for task in candidates:
            candidate = route + [task]
            if route_cost(supplier_worker, candidate) <= get_worker_capacity(supplier_worker):
                selected = task
                break
        if selected is None:
            break
        routes[supplier_worker].append(selected)
        remaining.remove(selected)

def assign_shortage_routes(obs, hire_count):
    worker_count = hire_count + 1
    shed_wheat = obs["private"]["shed"].get("WHEAT", 0)
    needed = len(ANIMAL_STATE) - shed_wheat
    wheat_tasks = get_required_wheat_tasks(obs, needed)
    if wheat_tasks is None:
        return None
    pair = get_shortage_pair(obs, worker_count, wheat_tasks)
    if pair is None:
        return None

    _, supplier_worker, feeder_worker, supply_route, supplier_drop_tick = pair
    routes = {worker_id: [] for worker_id in range(worker_count)}
    routes[supplier_worker] = supply_route

    reserved_wheat = {task[1] for task in wheat_tasks}
    remaining = [("ANIMAL_PRE", pos) for pos in ANIMAL_STATE]
    remaining += [("CROP", pos) for pos, data in CROP_STATE.items() if pos not in reserved_wheat and (data["planted"] or data.get("weed", False) or not EXPANSION_ACTIVE)]
    crop_positions = {task[1] for task in remaining if task[0] == "CROP"} | reserved_wheat
    remaining += [task for task in get_weed_tasks(obs) if task[1] not in crop_positions]

    feeder_prefix = fill_feeder_prefix(feeder_worker, remaining, supplier_drop_tick)
    routes[feeder_worker] = feeder_prefix + [("WAIT_WHEAT", CENTER, len(ANIMAL_STATE))] + get_animal_feed_route()

    fill_supplier_suffix(supplier_worker, routes, remaining)

    while remaining:
        best = None
        for worker_id in range(worker_count):
            if worker_id == feeder_worker:
                continue
            route = routes[worker_id]
            current = route_end(get_worker_spawn(worker_id), route)
            for task in remaining:
                candidate = route + [task]
                cost = route_cost(worker_id, candidate)
                if cost > get_worker_capacity(worker_id):
                    continue
                score = (distance(current, task[1]), cost, worker_id)
                if best is None or score < best[0]:
                    best = (score, worker_id, task)
        if best is None:
            return None
        _, worker_id, task = best
        routes[worker_id].append(task)
        remaining.remove(task)

    return routes

def assign_routes(obs, hire_count):
    shed_wheat = obs["private"]["shed"].get("WHEAT", 0)
    wheat_planted = any(data["crop"] == "WHEAT" and data["planted"] for data in CROP_STATE.values())
    if shed_wheat >= len(ANIMAL_STATE) or not wheat_planted:
        return assign_normal_routes(obs, hire_count)
    return assign_shortage_routes(obs, hire_count)

def calculate_daily_paths(obs, max_hires=10):
    for hire_count in range(max_hires + 1):
        routes = assign_routes(obs, hire_count)
        if routes is None:
            continue
        valid = True
        for worker_id, route in routes.items():
            cost = route_cost(worker_id, route)
            if route_has_wait(route):
                cost += 1
            if cost > get_worker_capacity(worker_id):
                valid = False
                break
        if valid:
            return hire_count, routes
    return None

def complete_active_task(state):
    if state["active_task"] and not state["stack"]:
        state["target"] += 1
        state["active_task"] = False

def get_general_worker_action(obs, worker_id):
    state = WORKER_STATE[worker_id]
    route = WORKER_ROUTES.get(worker_id, [])

    if worker_id > 0 and obs.get("hour", 0) == 0:
        return ["PASS"]

    if state["stack"]:
        return state["stack"].pop()

    complete_active_task(state)

    if not state["pickup_done"] and get_feed_count(route) and not route_has_wait(route):
        feed_count = get_feed_count(route)
        if obs["private"]["shed"].get("WHEAT", 0) < feed_count:
            return ["PASS"]
        state["pickup_done"] = True
        return ["PICKUP", "WHEAT", feed_count]

    if not get_feed_count(route):
        state["pickup_done"] = True

    if state["target"] >= len(route):
        return ["PASS"]

    task = route[state["target"]]
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]

    pos = tuple(pos)
    target = task[1]

    if pos != target:
        return move_toward(pos, target)

    if task[0] == "WAIT_WHEAT":
        needed = task[2]
        if obs["private"]["shed"].get("WHEAT", 0) < needed:
            return ["PASS"]
        state["target"] += 1
        state["pickup_done"] = True
        return ["PICKUP", "WHEAT", needed]

    actions = get_task_actions(obs, task)
    if not actions:
        state["target"] += 1
        return ["PASS"]

    state["active_task"] = True
    state["stack"].extend(reversed(actions))
    return state["stack"].pop()

def get_sale_drop_action(obs, worker_id):
    if obs.get("day", 0) != SALE_DAY:
        return None
    hour = obs.get("hour", 0)
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    state = WORKER_STATE.get(worker_id)
    if state and state["stack"]:
        return None
    if hour < SALE_DROP_HOUR - distance(pos, CENTER):
        return None
    if pos != CENTER:
        return move_toward(pos, CENTER)
    if hour == SALE_DROP_HOUR:
        return ["DROP"]
    return ["PASS"]

def get_replant_orders(obs, worker_actions):
    if EXPANSION_ACTIVE:
        return []
    seeds = {}
    for worker_id, action in worker_actions.items():
        if not action:
            continue
        pos = get_worker_position(obs, worker_id)
        if pos is None:
            continue
        pos = tuple(pos)
        if pos not in CROP_STATE:
            continue
        data = CROP_STATE[pos]
        crop = data["crop"]
        if action[0] == "DIG" and data.get("weed", False):
            seeds[crop] = seeds.get(crop, 0) + 1
        elif action[0] == "WATER" and data["harvest"] and CROP_PRODUCTION[crop]["type"] == "ONE_TIME" and not data.get("sale_early_harvest", False):
            seeds[crop] = seeds.get(crop, 0) + 1
    return [["BUY_SEED", crop, amount] for crop, amount in seeds.items()]

def get_feed_orders(obs):
    wheat_planted = any(data["crop"] == "WHEAT" and data["planted"] for data in CROP_STATE.values())
    if wheat_planted:
        return []
    shed_wheat = obs["private"]["shed"].get("WHEAT", 0)
    needed = len(ANIMAL_STATE) - shed_wheat
    return [["BUY_PRODUCT", "WHEAT", needed]] if needed > 0 else []

def agent(obs):
    global CURRENT_DAY, WORKER_ROUTES, HIRE_COUNT, HIRES_SENT_DAY, ROUTES_REBUILT_DAY, REAL_WORKER_STARTS, EXPANSION_ACTIVE
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    farm = obs["farms"][obs["player"]]
    unlocked = farm.get("unlocked_quadrants", ["NW"])
    EXPANSION_ACTIVE = len(unlocked) > 1

    update_crop_state(obs)
    update_animal_state(obs)

    if day != CURRENT_DAY:
        CURRENT_DAY = day
        REAL_WORKER_STARTS = {}
        if day == 0:
            HIRE_COUNT = 4
            WORKER_ROUTES = {}
            reset_worker_state(5)
        else:
            result = calculate_daily_paths(obs)
            if result is None:
                HIRE_COUNT = 0
                WORKER_ROUTES = {0: []}
            else:
                HIRE_COUNT, WORKER_ROUTES = result
            reset_worker_state(HIRE_COUNT + 1)

    if day > 0 and hour == 1 and ROUTES_REBUILT_DAY != day:
        REAL_WORKER_STARTS = {0: tuple(farm["farmer"])}
        REAL_WORKER_STARTS.update({worker_id: tuple(pos) for worker_id, pos in enumerate(farm.get("hands", []), 1)})
        routes = assign_routes(obs, HIRE_COUNT)
        if routes is not None:
            WORKER_ROUTES = routes
            reset_worker_state(HIRE_COUNT + 1)
        ROUTES_REBUILT_DAY = day

    if day == 0:
        farmer_action = get_day_1_farmer_action(obs)
        hand_actions = [get_day_1_hand_action(obs, worker_id) for worker_id in range(1, 5)]
        worker_actions = {0: farmer_action}
        worker_actions.update({worker_id: action for worker_id, action in enumerate(hand_actions, 1)})
        market = DAY_1_MARKET.get(hour, []).copy()
    else:
        worker_actions = {}
        for worker_id in range(HIRE_COUNT + 1):
            sale_action = get_sale_drop_action(obs, worker_id)
            worker_actions[worker_id] = sale_action if sale_action is not None else get_general_worker_action(obs, worker_id)
        farmer_action = worker_actions[0]
        hand_actions = [worker_actions[worker_id] for worker_id in range(1, HIRE_COUNT + 1)]
        core_market = []
        if hour == 0 and day >= LAND_BUY_DAY and can_buy_land(obs):
            core_market.append(["BUY_LAND"])
        if hour == 0 and HIRES_SENT_DAY != day:
            core_market += [["HIRE"] for _ in range(HIRE_COUNT)]
            HIRES_SENT_DAY = day
        core_market += get_feed_orders(obs)
        core_market += get_replant_orders(obs, worker_actions)
        sale_slots = max(0, MAX_MARKET_ORDERS - len(core_market))
        market = get_sale_orders(obs)[:sale_slots] + core_market
        return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}

    market += get_replant_orders(obs, worker_actions)
    return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}
