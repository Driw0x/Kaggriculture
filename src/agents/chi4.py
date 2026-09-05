DAY_1_MARKET = {
    0: [
        ["BUY_SEED", "CARROT", 6],
        ["BUY_SEED", "STRAWBERRY", 2],
        ["BUY_ANIMAL", "GOOSE", 1],
        ["BUY_ANIMAL", "COW", 2],
        ["BUY_ANIMAL", "SHEEP", 1],
        ["BUY_PRODUCT", "WHEAT", 16],
        ["HIRE"],
        ["HIRE"],
        ["HIRE"],
        ["HIRE"],
    ],
    1: [
        ["BUY_SEED", "TOMATO", 1],
        ["BUY_SEED", "MELON", 2],
        ["BUY_SEED", "WHEAT", 10],
    ],
}

CROP_PRODUCTION = {
    "WHEAT": {"type": "ONE_TIME", "harvest_ages": [4]},
    "CARROT": {"type": "ONE_TIME", "harvest_ages": [3]},
    "TOMATO": {"type": "ONGOING", "harvest_ages": [8, 9, 10, 11]},
    "STRAWBERRY": {"type": "ONGOING", "harvest_ages": [10, 12, 14, 16]},
    "MELON": {"type": "ONE_TIME", "harvest_ages": [10]},
}

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
    (3, 3): {"animal": "GOOSE", "placed": False, "harvest": False, "fertilizer": False},
    (4, 3): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False},
    (3, 4): {"animal": "SHEEP", "placed": False, "harvest": False, "fertilizer": False},
    (4, 4): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False},
}

FARMER_SETUP = [
    ["BUILD_PASTURE"],
    ["PICKUP", "COW", 2],
    ["PICKUP", "GOOSE", 1],
    ["PICKUP", "SHEEP", 1],
    ["PICKUP", "WHEAT", 4],
]

DAY_1_PATHS = {
    0: [["WEST"], ["NORTH"], ["EAST"]],
    1: [["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["SOUTH"]],
    2: [["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"]],
    3: [["WEST"], ["NORTH"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["SOUTH"], ["WEST"], ["SOUTH"]],
    4: [["NORTH"], ["WEST"], ["WEST"]],
}

HAND_SPAWNS = [(5, 4), (4, 5), (5, 5), (4, 4)]
FARMER_CAPACITY = 24
HAND_CAPACITY = 23
CENTER = (4, 4)
GENERAL_PATHS = {}
WORKER_ROUTES = {}
WORKER_STATE = {}
CURRENT_DAY = -1
HIRE_COUNT = 4

def reset_worker_state(worker_count):
    global WORKER_STATE
    WORKER_STATE = {i: {"path": 0, "stack": [], "done": set(), "target": 0, "pickup_done": False} for i in range(worker_count)}
    WORKER_STATE[0]["setup"] = 0

def get_worker_position(obs, worker_id):
    farm = obs["farms"][obs["player"]]
    if worker_id == 0:
        return farm["farmer"]
    if worker_id - 1 < len(farm["hands"]):
        return farm["hands"][worker_id - 1]
    return None

def get_worker_spawn(worker_id):
    if worker_id == 0:
        return CENTER
    return HAND_SPAWNS[(worker_id - 1) % len(HAND_SPAWNS)]

def get_worker_capacity(worker_id):
    return FARMER_CAPACITY if worker_id == 0 else HAND_CAPACITY

def get_path(day, worker_id):
    if day == 0:
        return DAY_1_PATHS.get(worker_id, [])
    return GENERAL_PATHS.get(worker_id, [])

def get_path_action(plan, state):
    if state["path"] >= len(plan):
        return ["PASS"]
    action = plan[state["path"]]
    state["path"] += 1
    return action

def update_crop_state(obs):
    day = obs.get("day", 0)
    farm = obs["farms"][obs["player"]]
    for pos, data in CROP_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT":
            data["planted"] = False
            data["harvest"] = False
            continue
        data["planted"] = True
        age = day - tile["planted_day"]
        production = CROP_PRODUCTION[data["crop"]]
        if production["type"] == "ONE_TIME":
            data["harvest"] = age >= production["harvest_ages"][0]
        else:
            data["harvest"] = age in production["harvest_ages"] or tile.get("yield_units", 0) > 0

def update_animal_state(obs):
    farm = obs["farms"][obs["player"]]
    for pos, data in ANIMAL_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        if isinstance(tile, dict) and tile.get("animal") == data["animal"]:
            data["placed"] = True
            data["harvest"] = tile.get("yield_units", 0) > 0
            data["fertilizer"] = tile.get("fertilizer_available", False)
        else:
            data["placed"] = False
            data["harvest"] = False
            data["fertilizer"] = False

def get_crop_actions(pos):
    data = CROP_STATE[pos]
    crop = data["crop"]
    if not data["planted"]:
        return [["PLANT", crop], ["WATER"]]
    if not data["harvest"]:
        return [["WATER"]]
    if CROP_PRODUCTION[crop]["type"] == "ONE_TIME":
        return [["WATER"], ["HARVEST"], ["PLANT", crop], ["WATER"]]
    return [["WATER"], ["HARVEST"]]

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
    actions += [["FEED"], ["CARE"]]
    if data["fertilizer"]:
        actions.append(["COLLECT_FERTILIZER"])
    if data["harvest"]:
        actions.append(["HARVEST"])
    return actions

def get_task_actions(obs, task):
    if task[0] == "CROP":
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

def get_general_worker_action(obs, worker_id):
    state = WORKER_STATE[worker_id]
    route = WORKER_ROUTES.get(worker_id, [])
    if worker_id > 0 and obs.get("hour", 0) == 0:
        return ["PASS"]
    if not state["pickup_done"]:
        feed_count = get_feed_count(route)
        state["pickup_done"] = True
        if feed_count:
            return ["PICKUP", "WHEAT", feed_count]
    if state["stack"]:
        return state["stack"].pop()
    if state["target"] < len(route):
        task = route[state["target"]]
        pos = get_worker_position(obs, worker_id)
        if pos is not None and tuple(pos) == task[1]:
            state["target"] += 1
            state["stack"].extend(reversed(get_task_actions(obs, task)))
            return state["stack"].pop()
    return get_path_action(GENERAL_PATHS.get(worker_id, []), state)

def get_replant_orders(obs, worker_actions):
    seeds = {}
    for worker_id, action in worker_actions.items():
        if not action or action[0] != "WATER":
            continue
        pos = get_worker_position(obs, worker_id)
        if pos is None:
            continue
        pos = tuple(pos)
        if pos not in CROP_STATE:
            continue
        data = CROP_STATE[pos]
        crop = data["crop"]
        if data["harvest"] and CROP_PRODUCTION[crop]["type"] == "ONE_TIME":
            seeds[crop] = seeds.get(crop, 0) + 1
    return [["BUY_SEED", crop, amount] for crop, amount in seeds.items()]

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def crop_action_cost(pos):
    data = CROP_STATE[pos]
    crop = data["crop"]
    if not data["planted"]:
        return 2
    if not data["harvest"]:
        return 1
    if CROP_PRODUCTION[crop]["type"] == "ONE_TIME":
        return 4
    return 2

def animal_action_cost(pos):
    data = ANIMAL_STATE[pos]
    cost = 2
    if not data["placed"]:
        cost += 2
    if data["fertilizer"]:
        cost += 1
    if data["harvest"]:
        cost += 1
    return cost

def task_action_cost(task):
    if task[0] == "CROP":
        return crop_action_cost(task[1])
    return animal_action_cost(task[1])

def get_feed_count(route):
    return sum(1 for task in route if task[0] == "ANIMAL")

def route_cost(worker_id, route):
    cost = 1 if get_feed_count(route) else 0
    pos = get_worker_spawn(worker_id)
    for task in route:
        target = task[1]
        cost += distance(pos, target) + task_action_cost(task)
        pos = target
    return cost

def get_daily_tasks():
    tasks = [("CROP", pos) for pos in CROP_STATE]
    tasks += [("ANIMAL", pos) for pos in ANIMAL_STATE]
    return sorted(tasks, key=lambda task: (distance(CENTER, task[1]), -task_action_cost(task), task[1][1], task[1][0]))

def nearest_task(current_pos, tasks):
    return min(tasks, key=lambda task: (distance(current_pos, task[1]), distance(CENTER, task[1]), -task_action_cost(task)))

def order_tasks(start, tasks):
    ordered = []
    remaining = tasks.copy()
    current_pos = start
    while remaining:
        task = nearest_task(current_pos, remaining)
        ordered.append(task)
        remaining.remove(task)
        current_pos = task[1]
    return ordered

def assign_routes(hire_count):
    worker_count = hire_count + 1
    routes = {worker_id: [] for worker_id in range(worker_count)}
    animal_tasks = [("ANIMAL", pos) for pos in ANIMAL_STATE]
    animal_worker = None
    best_animal_cost = None

    for worker_id in range(worker_count):
        animal_route = order_tasks(get_worker_spawn(worker_id), animal_tasks)
        cost = route_cost(worker_id, animal_route)
        if cost <= get_worker_capacity(worker_id) and (best_animal_cost is None or cost < best_animal_cost):
            best_animal_cost = cost
            animal_worker = worker_id
            routes[worker_id] = animal_route

    if animal_worker is None:
        return None

    remaining = [("CROP", pos) for pos in CROP_STATE]

    while remaining:
        best = None
        for worker_id in range(worker_count):
            route = routes[worker_id]
            current_pos = route[-1][1] if route else get_worker_spawn(worker_id)
            for task in remaining:
                candidate = route + [task]
                total_cost = route_cost(worker_id, candidate)
                if total_cost > get_worker_capacity(worker_id):
                    continue
                outward = distance(CENTER, task[1])
                travel = distance(current_pos, task[1])
                candidate_score = (outward, travel, total_cost, worker_id)
                if best is None or candidate_score < best[0]:
                    best = (candidate_score, worker_id, task)

        if best is None:
            return None

        _, worker_id, task = best
        routes[worker_id].append(task)
        remaining.remove(task)

    for worker_id, route in routes.items():
        if len(route) <= 1:
            continue

        if worker_id == animal_worker:
            animal_count = len(animal_tasks)
            prefix = route[:animal_count]
            crops = route[animal_count:]
            start = prefix[-1][1]
            routes[worker_id] = prefix + order_tasks(start, crops)
        else:
            routes[worker_id] = order_tasks(get_worker_spawn(worker_id), route)

    return routes

def coordinates_to_path(start, route):
    path = []
    x, y = start
    for _, target in route:
        tx, ty = target
        while x < tx:
            path.append(["EAST"])
            x += 1
        while x > tx:
            path.append(["WEST"])
            x -= 1
        while y < ty:
            path.append(["SOUTH"])
            y += 1
        while y > ty:
            path.append(["NORTH"])
            y -= 1
    return path

def calculate_daily_paths(max_hires=10):
    for hire_count in range(max_hires + 1):
        routes = assign_routes(hire_count)
        if routes is None:
            continue
        valid = True
        for worker_id, route in routes.items():
            if route_cost(worker_id, route) > get_worker_capacity(worker_id):
                valid = False
                break
        if not valid:
            continue
        paths = {}
        for worker_id, route in routes.items():
            paths[worker_id] = coordinates_to_path(get_worker_spawn(worker_id), route)
        return hire_count, paths, routes
    return None

def agent(obs):
    global CURRENT_DAY, GENERAL_PATHS, WORKER_ROUTES, HIRE_COUNT
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)

    update_crop_state(obs)
    update_animal_state(obs)

    if day != CURRENT_DAY:
        CURRENT_DAY = day

        if day == 0:
            HIRE_COUNT = 4
            GENERAL_PATHS = DAY_1_PATHS
            WORKER_ROUTES = {}
            reset_worker_state(5)
        else:
            result = calculate_daily_paths()
            if result is None:
                HIRE_COUNT = 0
                GENERAL_PATHS = {0: []}
                WORKER_ROUTES = {0: []}
            else:
                HIRE_COUNT, GENERAL_PATHS, WORKER_ROUTES = result
            reset_worker_state(HIRE_COUNT + 1)

    if day == 0:
        farmer_action = get_day_1_farmer_action(obs)
        hand_actions = [get_day_1_hand_action(obs, worker_id) for worker_id in range(1, 5)]
        worker_actions = {0: farmer_action}
        worker_actions.update({worker_id: action for worker_id, action in enumerate(hand_actions, 1)})
        market = DAY_1_MARKET.get(hour + day * 24, []).copy()
    else:
        worker_actions = {worker_id: get_general_worker_action(obs, worker_id) for worker_id in range(HIRE_COUNT + 1)}
        farmer_action = worker_actions[0]
        hand_actions = [worker_actions[worker_id] for worker_id in range(1, HIRE_COUNT + 1)]
        market = [["HIRE"] for _ in range(HIRE_COUNT)] if hour == 0 else []

    market += get_replant_orders(obs, worker_actions)

    return {
        "farmer": farmer_action,
        "hands": hand_actions,
        "market": market,
    }