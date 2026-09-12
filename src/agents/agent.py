PATH_STATE = {
    "day": None,
    "paths": {},
    "indices": {},
    "target_hands": 0,
}

FARM_MEMORY = {
    "plants": [],
    "animals": [],
}


def get_position(unit_index, farm):
    if unit_index == 0:
        return tuple(farm["farmer"])

    hand_index = unit_index - 1

    if hand_index < len(farm["hands"]):
        return tuple(farm["hands"][hand_index])

    return tuple(farm["farmer"])


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def move_toward(position, target):
    x, y = position
    tx, ty = target

    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]

    return ["PASS"]


def update_farm_memory(farm):
    plants = []
    animals = []

    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue

            if tile.get("kind") == "PLANT":
                plants.append({
                    "position": (x, y),
                    "crop": tile["crop"],
                    "planted_day": tile["planted_day"],
                    "watered_today": tile["watered_today"],
                    "consecutive_unwatered": tile["consecutive_unwatered"],
                    "yield_units": tile["yield_units"],
                    "fertilized_until_day": tile["fertilized_until_day"],
                })

            elif "animal" in tile:
                animals.append({
                    "position": (x, y),
                    "animal": tile["animal"],
                    "placed_day": tile["placed_day"],
                    "fed_today": tile["fed_today"],
                    "cared_today": tile["cared_today"],
                    "consecutive_unfed": tile["consecutive_unfed"],
                    "yield_units": tile["yield_units"],
                    "fertilizer_available": tile["fertilizer_available"],
                })

    FARM_MEMORY["plants"] = plants
    FARM_MEMORY["animals"] = animals


def build_tasks():
    tasks = []

    for plant in FARM_MEMORY["plants"]:
        actions = []

        if plant["yield_units"] > 0:
            actions.extend(["HARVEST", "PLANT", "WATER"])
        elif not plant["watered_today"]:
            actions.append("WATER")

        if actions:
            tasks.append({
                "position": plant["position"],
                "type": "PLANT",
                "actions": actions,
            })

    for animal in FARM_MEMORY["animals"]:
        actions = []

        if not animal["fed_today"]:
            actions.append("FEED")

        if not animal["cared_today"]:
            actions.append("CARE")

        if animal["yield_units"] > 0:
            actions.append("HARVEST")

        if animal["fertilizer_available"]:
            actions.append("COLLECT_FERTILIZER")

        if actions:
            tasks.append({
                "position": animal["position"],
                "type": "ANIMAL",
                "actions": actions,
            })

    return tasks


def task_action_cost(task):
    return len(task["actions"])


def get_task_orders(tasks, start=(0, 0)):
    return [
        sorted(tasks, key=task_action_cost, reverse=True),
        sorted(tasks, key=lambda task: (task["position"][1], task["position"][0])),
        sorted(tasks, key=lambda task: distance(start, task["position"])),
        sorted(tasks, key=lambda task: distance(start, task["position"]), reverse=True),
    ]


def path_tick_cost(start_position, path):
    cost = 0
    position = start_position

    for task in path:
        cost += distance(position, task["position"])
        cost += task_action_cost(task)
        position = task["position"]

    return cost


def split_path(tasks, unit_count, start_positions=None, ticks_available=24):
    paths = {i: [] for i in range(unit_count)}

    if not tasks:
        return paths

    if start_positions is None:
        start_positions = [(0, 0)] * unit_count

    for task in tasks:
        best_unit = None
        best_path = None
        best_score = None

        for unit_index in range(unit_count):
            current_path = paths[unit_index]
            current_cost = path_tick_cost(start_positions[unit_index], current_path)

            for insert_index in range(len(current_path) + 1):
                candidate_path = current_path[:insert_index] + [task] + current_path[insert_index:]
                candidate_cost = path_tick_cost(start_positions[unit_index], candidate_path)

                if candidate_cost > ticks_available:
                    continue

                added_cost = candidate_cost - current_cost
                remaining_ticks = ticks_available - candidate_cost
                score = (remaining_ticks, added_cost)

                if best_score is None or score < best_score:
                    best_score = score
                    best_unit = unit_index
                    best_path = candidate_path

        if best_unit is None:
            break

        paths[best_unit] = best_path

    return paths


def get_best_paths(tasks, unit_count, start_positions, ticks_available):
    best_paths = None
    best_score = None

    for ordered_tasks in get_task_orders(tasks, start_positions[0]):
        paths = split_path(ordered_tasks, unit_count, start_positions, ticks_available)
        assigned = sum(len(path) for path in paths.values())
        total_cost = sum(path_tick_cost(start_positions[i], paths[i]) for i in range(unit_count))
        score = (-assigned, total_cost)

        if best_score is None or score < best_score:
            best_score = score
            best_paths = paths

    return best_paths


def optimize_path_direction(path, position):
    if len(path) <= 1:
        return path

    forward = distance(position, path[0]["position"])
    backward = distance(position, path[-1]["position"])

    if backward < forward:
        return list(reversed(path))

    return path


def get_required_unit_count(farm, tasks, ticks_available):
    if not tasks:
        return 1

    for unit_count in range(1, len(tasks) + 1):
        start_positions = [get_position(i, farm) for i in range(unit_count)]
        paths = get_best_paths(tasks, unit_count, start_positions, ticks_available)
        assigned = sum(len(path) for path in paths.values())

        if assigned != len(tasks):
            continue

        valid = True

        for unit_index in range(unit_count):
            path = optimize_path_direction(paths[unit_index], start_positions[unit_index])

            if path_tick_cost(start_positions[unit_index], path) > ticks_available:
                valid = False
                break

        if valid:
            return unit_count

    return len(tasks)


def build_daily_plan(farm, ticks_available):
    tasks = build_tasks()
    target_units = get_required_unit_count(farm, tasks, ticks_available)
    start_positions = [get_position(i, farm) for i in range(target_units)]
    paths = get_best_paths(tasks, target_units, start_positions, ticks_available)

    for unit_index in range(target_units):
        paths[unit_index] = optimize_path_direction(paths[unit_index], start_positions[unit_index])

    PATH_STATE["paths"] = paths
    PATH_STATE["indices"] = {i: 0 for i in range(target_units)}
    PATH_STATE["target_hands"] = max(0, target_units - 1)


def get_current_task(unit_index):
    path = PATH_STATE["paths"].get(unit_index, [])
    index = PATH_STATE["indices"].get(unit_index, 0)

    if index >= len(path):
        return None

    return path[index]


def get_live_action(task):
    position = task["position"]

    for plant in FARM_MEMORY["plants"]:
        if plant["position"] != position:
            continue

        if "HARVEST" in task["actions"] and plant["yield_units"] > 0:
            return ["HARVEST"]

        if "WATER" in task["actions"] and not plant["watered_today"]:
            return ["WATER"]

        return None

    for animal in FARM_MEMORY["animals"]:
        if animal["position"] != position:
            continue

        if "FEED" in task["actions"] and not animal["fed_today"]:
            return ["FEED"]

        if "CARE" in task["actions"] and not animal["cared_today"]:
            return ["CARE"]

        if "HARVEST" in task["actions"] and animal["yield_units"] > 0:
            return ["HARVEST"]

        if "COLLECT_FERTILIZER" in task["actions"] and animal["fertilizer_available"]:
            return ["COLLECT_FERTILIZER"]

        return None

    return None


def get_unit_action(unit_index, farm):
    task = get_current_task(unit_index)

    if task is None:
        return ["PASS"]

    position = get_position(unit_index, farm)
    target = task["position"]

    if position != target:
        return move_toward(position, target)

    action = get_live_action(task)

    if action is not None:
        return action

    PATH_STATE["indices"][unit_index] += 1
    next_task = get_current_task(unit_index)

    if next_task is None:
        return ["PASS"]

    return move_toward(position, next_task["position"])


def agent(obs, config):
    player = obs.player
    farm = obs.farms[player]
    day = obs.day
    hour = obs.hour
    turns_per_day = getattr(config, "turnsPerDay", 24)
    ticks_available = turns_per_day - hour

    update_farm_memory(farm)

    if PATH_STATE["day"] != day:
        PATH_STATE["day"] = day
        build_daily_plan(farm, ticks_available)

    unit_count = 1 + len(farm["hands"])
    actions = [get_unit_action(unit_index, farm) for unit_index in range(unit_count)]
    market = []

    if hour == 0:
        missing_hands = PATH_STATE["target_hands"] - len(farm["hands"])
        max_orders = getattr(config, "maxMarketOrdersPerTurn", 10)

        for _ in range(min(max(0, missing_hands), max_orders)):
            market.append(["HIRE"])

    return {
        "farmer": actions[0],
        "hands": actions[1:],
        "market": market,
    }