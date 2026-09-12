from pathlib import Path

from src.learning.policy import BCPolicy

ROOT = Path(__file__).resolve().parent.parent.parent

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
CROP_DATA = {
    "WHEAT": {"first_yield_day": 2, "max_yield_day": 4, "ongoing": False},
    "CARROT": {"first_yield_day": 2, "max_yield_day": 3, "ongoing": False},
    "TOMATO": {"first_yield_day": 8, "max_yield_day": 8, "ongoing": True},
    "STRAWBERRY": {"first_yield_day": 10, "max_yield_day": 10, "ongoing": True},
    "MELON": {"first_yield_day": 10, "max_yield_day": 12, "ongoing": False},
}
ANIMAL_DATA = {
    "GOOSE": {"first_yield_day": 4},
    "COW": {"first_yield_day": 8},
    "SHEEP": {"first_yield_day": 6},
}
ANIMAL_STRUCTURE = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}

POLICY = BCPolicy(ROOT / "models" / "bc_best.pt", ROOT / "models" / "bc_thresholds.json", device="cpu")

MAX_MARKET_ORDERS = 10
MAX_PENDING_TASKS = 200
MAX_HANDS = 12
FINAL_DAY = 29
ENDGAME_DAY = 28
FINAL_RETURN_HOUR = 21
FINAL_SELL_HOUR = 22

LAST_DAY = None
PENDING_TASKS = []
WORKER_TASKS = {}
ACTIVE_INTENTS = {}


def reset_day(day):
    global LAST_DAY, WORKER_TASKS, ACTIVE_INTENTS, PENDING_TASKS
    if LAST_DAY == day:
        return
    if day == 0 and LAST_DAY is not None:
        PENDING_TASKS = []
    else:
        for task in WORKER_TASKS.values():
            if task is not None and task["kind"] in ("PLANT", "PLACE", "BUILD_COOP", "BUILD_PASTURE", "FERTILIZE"):
                task = dict(task)
                task["target"] = None
                if len(PENDING_TASKS) < MAX_PENDING_TASKS:
                    PENDING_TASKS.append(task)
    LAST_DAY = day
    WORKER_TASKS = {}
    ACTIVE_INTENTS = {}


def shed_access_tiles(obs):
    size = len(obs["farms"][obs["player"]]["tiles"])
    half = size // 2
    return ((half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half))


def is_shed_access(obs, pos):
    return pos in shed_access_tiles(obs)


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def move_towards(position, target):
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
    return None


def closest(position, positions):
    if not positions:
        return None
    return min(positions, key=lambda pos: (distance(position, pos), pos[1], pos[0]))


def worker_positions(obs):
    farm = obs["farms"][obs["player"]]
    return [tuple(farm["farmer"]), *(tuple(pos) for pos in farm.get("hands", []))]


def worker_inventory(obs, worker_id):
    inventories = obs.get("private", {}).get("inventories", [])
    return inventories[worker_id] if worker_id < len(inventories) else {}


def inventory_count(obs, item):
    return sum(int(inv.get(item, 0)) for inv in obs.get("private", {}).get("inventories", []))


def inventory_total(obs, worker_id):
    return sum(int(value) for value in worker_inventory(obs, worker_id).values())


def get_tile(obs, pos):
    x, y = pos
    return obs["farms"][obs["player"]]["tiles"][y][x]


def unlocked_positions(obs):
    tiles = obs["farms"][obs["player"]]["tiles"]
    return [(x, y) for y, row in enumerate(tiles) for x, tile in enumerate(row) if tile != "LOCKED"]


def empty_positions(obs):
    return [pos for pos in unlocked_positions(obs) if get_tile(obs, pos) is None]


def plant_positions(obs):
    return [
        pos for pos in unlocked_positions(obs)
        if isinstance(get_tile(obs, pos), dict) and get_tile(obs, pos).get("kind") == "PLANT"
    ]


def animal_positions(obs):
    return [
        pos for pos in unlocked_positions(obs)
        if isinstance(get_tile(obs, pos), dict)
        and get_tile(obs, pos).get("kind") in ("COOP", "PASTURE")
        and get_tile(obs, pos).get("animal")
    ]


def empty_structure_positions(obs, animal):
    kind = ANIMAL_STRUCTURE[animal]
    return [
        pos for pos in unlocked_positions(obs)
        if isinstance(get_tile(obs, pos), dict)
        and get_tile(obs, pos).get("kind") == kind
        and not get_tile(obs, pos).get("animal")
    ]


def count_empty_structures(obs, kind):
    return sum(
        1 for pos in unlocked_positions(obs)
        if isinstance(get_tile(obs, pos), dict)
        and get_tile(obs, pos).get("kind") == kind
        and not get_tile(obs, pos).get("animal")
    )



def latest_plant_day(crop):
    return FINAL_DAY - CROP_DATA[crop]["first_yield_day"]


def latest_animal_day(animal):
    return FINAL_DAY - ANIMAL_DATA[animal]["first_yield_day"]


def crop_viable(obs, crop):
    return obs["day"] <= latest_plant_day(crop)


def animal_viable(obs, animal):
    return obs["day"] <= latest_animal_day(animal)


def endgame_mode(obs):
    return obs["day"] >= ENDGAME_DAY


def terminal_mode(obs):
    return obs["day"] == FINAL_DAY


def sellable_inventory(obs, worker_id):
    inventory = worker_inventory(obs, worker_id)
    return sum(int(inventory.get(product, 0)) for product in PRODUCTS)


def distance_to_shed(obs, pos):
    return min(distance(pos, shed) for shed in shed_access_tiles(obs))


def standing_task(task, position):
    return task.get("target") == position


def task_route_cost(obs, position, task):
    target = task.get("target")
    if target is not None:
        base = distance(position, target)
    else:
        base = 2

    required = requires_pickup(task)
    if required:
        shed = closest(position, shed_access_tiles(obs))
        base += distance(position, shed) + 1
        if target is not None:
            base += distance(shed, target)
    return base + 1


def estimated_workload(obs, decision):
    positions = worker_positions(obs)
    tasks = list(active_tasks()) + build_maintenance_tasks(obs)
    action_cost = 0

    for task in tasks:
        target = task.get("target")
        if target is not None and positions:
            action_cost += min(distance(position, target) for position in positions) + 1
        else:
            action_cost += 3
        if requires_pickup(task):
            action_cost += 2

    for crop in CROPS:
        if crop_viable(obs, crop):
            action_cost += 2 * max(0, int(decision.get(f"buy_seed_{crop}", 0)))
    for animal in ANIMALS:
        if animal_viable(obs, animal):
            quantity = max(0, int(decision.get(f"buy_animal_{animal}", 0)))
            action_cost += 5 * quantity

    if terminal_mode(obs):
        action_cost = sum(
            task_route_cost(obs, positions[0] if positions else (0, 0), task)
            for task in tasks
            if task["kind"] in ("WATER", "HARVEST", "COLLECT_FERTILIZER")
        )

    return action_cost


def maintenance_target_hands(obs):
    plants = len(plant_positions(obs))
    animals = len(animal_positions(obs))
    harvestable = sum(1 for pos in plant_positions(obs) + animal_positions(obs) if harvest_ready(obs, pos))
    fertilizer_ready = sum(
        1 for pos in animal_positions(obs)
        if get_tile(obs, pos).get("fertilizer_available", False)
    )

    maintenance_load = plants + 2 * animals + harvestable + fertilizer_ready
    if maintenance_load <= 0:
        return 0

    desired_hands = (maintenance_load + 7) // 8
    return min(6, max(1, desired_hands))


def needed_hires(obs, decision):
    farm = obs["farms"][obs["player"]]
    current_hands = len(farm.get("hands", []))

    if obs["day"] == FINAL_DAY and obs["hour"] >= FINAL_RETURN_HOUR:
        return 0

    target_hands = maintenance_target_hands(obs)
    return max(0, target_hands - current_hands)


def final_liquidation_orders(obs):
    shed = obs.get("private", {}).get("shed", {})
    orders = []
    for product in PRODUCTS:
        quantity = int(shed.get(product, 0))
        if quantity > 0:
            orders.append(["SELL", product, quantity])
    return orders[:MAX_MARKET_ORDERS]



def consume_intent(name, value):
    value = int(value or 0)
    previous = ACTIVE_INTENTS.get(name)
    ACTIVE_INTENTS[name] = value
    if value <= 0 or previous == value:
        return 0
    return value


def build_market_orders(obs, decision):
    farm = obs["farms"][obs["player"]]
    shed = obs.get("private", {}).get("shed", {})

    if obs["day"] == FINAL_DAY and obs["hour"] >= FINAL_SELL_HOUR:
        return final_liquidation_orders(obs)

    orders = []
    bought_products = set()

    buy_land = consume_intent("buy_land", decision.get("buy_land", 0))
    if buy_land and obs["day"] < ENDGAME_DAY and len(farm.get("unlocked_quadrants", [])) < 4:
        orders.append(["BUY_LAND"])

    for crop in CROPS:
        name = f"buy_seed_{crop}"
        quantity = consume_intent(name, decision.get(name, 0))
        if quantity > 0 and crop_viable(obs, crop):
            orders.append(["BUY_SEED", crop, quantity])

    for animal in ANIMALS:
        name = f"buy_animal_{animal}"
        quantity = consume_intent(name, decision.get(name, 0))
        if quantity > 0 and animal_viable(obs, animal):
            orders.append(["BUY_ANIMAL", animal, quantity])

    if obs["day"] < FINAL_DAY:
        wheat = consume_intent("buy_product_WHEAT", decision.get("buy_product_WHEAT", 0))
        fertilizer = consume_intent("buy_product_FERTILIZER", decision.get("buy_product_FERTILIZER", 0))
        if wheat > 0:
            orders.append(["BUY_PRODUCT", "WHEAT", wheat])
            bought_products.add("WHEAT")
        if fertilizer > 0:
            orders.append(["BUY_PRODUCT", "FERTILIZER", fertilizer])
            bought_products.add("FERTILIZER")
    else:
        consume_intent("buy_product_WHEAT", decision.get("buy_product_WHEAT", 0))
        consume_intent("buy_product_FERTILIZER", decision.get("buy_product_FERTILIZER", 0))

    for product in PRODUCTS:
        name = f"sell_{product}"
        quantity = consume_intent(name, decision.get(name, 0))
        if product in bought_products:
            continue
        quantity = min(quantity, int(shed.get(product, 0)))
        if quantity > 0:
            orders.append(["SELL", product, quantity])

    minimum_hire = needed_hires(obs, decision)
    predicted_hire = consume_intent("hire", decision.get("hire", 0))
    hire = predicted_hire if predicted_hire > 0 else minimum_hire
    hire = min(hire, MAX_HANDS - len(farm.get("hands", [])), MAX_MARKET_ORDERS - len(orders))
    for _ in range(max(0, hire)):
        orders.append(["HIRE"])

    return orders[:MAX_MARKET_ORDERS]


def append_task(kind, item=None, target=None, front=False):
    if len(PENDING_TASKS) >= MAX_PENDING_TASKS:
        return False
    task = {"kind": kind, "item": item, "target": target}
    if front:
        PENDING_TASKS.insert(0, task)
    else:
        PENDING_TASKS.append(task)
    return True


def active_tasks():
    return PENDING_TASKS + [task for task in WORKER_TASKS.values() if task is not None]


def count_tasks(kind, item=None):
    return sum(
        1 for task in active_tasks()
        if task["kind"] == kind and (item is None or task.get("item") == item)
    )


def sync_inventory_tasks(obs):
    private = obs.get("private", {})
    seeds = private.get("seeds", {})
    shed = private.get("shed", {})

    for crop in CROPS:
        if not crop_viable(obs, crop):
            continue
        missing = max(0, int(seeds.get(crop, 0)) - count_tasks("PLANT", crop))
        for _ in range(missing):
            append_task("PLANT", crop)

    for animal in ANIMALS:
        if not animal_viable(obs, animal):
            continue
        available = int(shed.get(animal, 0)) + inventory_count(obs, animal)
        missing = max(0, available - count_tasks("PLACE", animal))
        for _ in range(missing):
            append_task("PLACE", animal)

    goose_unplaced = 0
    if animal_viable(obs, "GOOSE"):
        goose_unplaced = int(shed.get("GOOSE", 0)) + inventory_count(obs, "GOOSE")

    pasture_unplaced = 0
    for animal in ("COW", "SHEEP"):
        if animal_viable(obs, animal):
            pasture_unplaced += int(shed.get(animal, 0)) + inventory_count(obs, animal)

    coop_missing = max(0, goose_unplaced - count_empty_structures(obs, "COOP") - count_tasks("BUILD_COOP"))
    pasture_missing = max(
        0, pasture_unplaced - count_empty_structures(obs, "PASTURE") - count_tasks("BUILD_PASTURE")
    )
    for _ in range(coop_missing):
        append_task("BUILD_COOP", front=True)
    for _ in range(pasture_missing):
        append_task("BUILD_PASTURE", front=True)


def add_bc_tasks(obs, decision):
    if obs["day"] < FINAL_DAY:
        for _ in range(consume_intent("fertilize", decision.get("fertilize", 0))):
            append_task("FERTILIZE")
    else:
        consume_intent("fertilize", decision.get("fertilize", 0))

    consume_intent("build_coop", decision.get("build_coop", 0))
    consume_intent("build_pasture", decision.get("build_pasture", 0))

    for crop in CROPS:
        consume_intent(f"plant_{crop}", decision.get(f"plant_{crop}", 0))

    for animal in ANIMALS:
        consume_intent(f"place_{animal}", decision.get(f"place_{animal}", 0))


def task_viable(obs, task):
    if task["kind"] == "PLANT":
        return crop_viable(obs, task["item"])
    if task["kind"] == "PLACE":
        return animal_viable(obs, task["item"])
    if task["kind"] == "BUILD_COOP":
        return animal_viable(obs, "GOOSE")
    if task["kind"] == "BUILD_PASTURE":
        return animal_viable(obs, "COW") or animal_viable(obs, "SHEEP")
    if terminal_mode(obs) and task["kind"] in ("CARE", "FEED", "FERTILIZE"):
        return False
    return True


def prune_unviable_tasks(obs):
    global PENDING_TASKS
    PENDING_TASKS = [task for task in PENDING_TASKS if task_viable(obs, task)]
    for worker_id, task in list(WORKER_TASKS.items()):
        if task is not None and not task_viable(obs, task):
            WORKER_TASKS[worker_id] = None


def harvest_ready(obs, pos):
    tile = get_tile(obs, pos)
    if not isinstance(tile, dict) or tile.get("yield_units", 0) <= 0:
        return False
    if "animal" in tile:
        return True
    if tile.get("kind") != "PLANT":
        return False
    crop = tile.get("crop")
    data = CROP_DATA.get(crop)
    if data is None:
        return False
    age = obs["day"] - int(tile.get("planted_day", obs["day"]))
    if data["ongoing"]:
        return age >= data["first_yield_day"]
    return age >= data["max_yield_day"]


def build_maintenance_tasks(obs):
    tasks = []

    for pos in plant_positions(obs):
        tile = get_tile(obs, pos)
        crop = tile.get("crop")
        data = CROP_DATA.get(crop, {})
        age = obs["day"] - int(tile.get("planted_day", obs["day"]))
        needs_bonus_water = (
            not tile.get("watered_today", False)
            and not data.get("ongoing", False)
            and age <= data.get("max_yield_day", -1)
            and age >= (data.get("max_yield_day", 0) + 1) // 2
        )

        if terminal_mode(obs):
            if harvest_ready(obs, pos):
                if needs_bonus_water:
                    tasks.append({"kind": "WATER", "item": None, "target": pos})
                else:
                    tasks.append({"kind": "HARVEST", "item": None, "target": pos})
            continue

        if not tile.get("watered_today", False) and tile.get("consecutive_unwatered", 0) >= 1:
            tasks.append({"kind": "WATER", "item": None, "target": pos})
        if harvest_ready(obs, pos) and not needs_bonus_water:
            tasks.append({"kind": "HARVEST", "item": None, "target": pos})

    for pos in animal_positions(obs):
        tile = get_tile(obs, pos)
        if harvest_ready(obs, pos):
            tasks.append({"kind": "HARVEST", "item": None, "target": pos})
        if tile.get("fertilizer_available", False):
            tasks.append({"kind": "COLLECT_FERTILIZER", "item": None, "target": pos})

        if terminal_mode(obs):
            continue

        if not tile.get("fed_today", False):
            tasks.append({"kind": "FEED", "item": "WHEAT", "target": pos})
        if tile.get("fed_today", False) and not tile.get("cared_today", False):
            tasks.append({"kind": "CARE", "item": None, "target": pos})

    return tasks


def task_priority(obs, task):
    if terminal_mode(obs):
        priorities = {
            "WATER": 0,
            "HARVEST": 1,
            "COLLECT_FERTILIZER": 2,
            "PLACE": 20,
            "PLANT": 20,
            "BUILD_COOP": 20,
            "BUILD_PASTURE": 20,
            "FEED": 20,
            "CARE": 20,
            "FERTILIZE": 20,
        }
    elif endgame_mode(obs):
        priorities = {
            "HARVEST": 0,
            "COLLECT_FERTILIZER": 1,
            "WATER": 2,
            "FEED": 3,
            "CARE": 4,
            "PLACE": 8,
            "PLANT": 8,
            "BUILD_COOP": 9,
            "BUILD_PASTURE": 9,
            "FERTILIZE": 10,
        }
    else:
        priorities = {
            "WATER": 0,
            "FEED": 0,
            "HARVEST": 1,
            "CARE": 2,
            "COLLECT_FERTILIZER": 3,
            "BUILD_COOP": 4,
            "BUILD_PASTURE": 4,
            "PLACE": 5,
            "PLANT": 6,
            "FERTILIZE": 7,
        }
    return priorities.get(task["kind"], 99)


def choose_target(obs, task, position, reserved=None):
    reserved = reserved or set()
    kind = task["kind"]

    if kind == "PLANT":
        candidates = [pos for pos in empty_positions(obs) if pos not in reserved]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda pos: (
                distance(position, pos) + distance_to_shed(obs, pos),
                distance_to_shed(obs, pos),
                pos[1],
                pos[0],
            ),
        )

    if kind == "PLACE":
        candidates = [pos for pos in empty_structure_positions(obs, task["item"]) if pos not in reserved]
    elif kind in ("BUILD_COOP", "BUILD_PASTURE"):
        candidates = [pos for pos in empty_positions(obs) if pos not in reserved]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda pos: (
                distance_to_shed(obs, pos),
                distance(position, pos),
                pos[1],
                pos[0],
            ),
        )
    elif kind == "FERTILIZE":
        candidates = [
            pos for pos in plant_positions(obs)
            if pos not in reserved and get_tile(obs, pos).get("fertilized_until_day", -1) < obs["day"]
        ]
    else:
        candidates = []

    return closest(position, candidates)


def task_valid(obs, task):
    target = task.get("target")
    if target is None:
        return True
    tile = get_tile(obs, target)
    kind = task["kind"]

    if kind in ("PLANT", "BUILD_COOP", "BUILD_PASTURE"):
        return tile is None
    if kind == "PLACE":
        return (
            isinstance(tile, dict)
            and tile.get("kind") == ANIMAL_STRUCTURE[task["item"]]
            and not tile.get("animal")
        )
    if kind == "WATER":
        return isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today", False)
    if kind == "FERTILIZE":
        return isinstance(tile, dict) and tile.get("kind") == "PLANT"
    if kind == "FEED":
        return isinstance(tile, dict) and tile.get("animal") and not tile.get("fed_today", False)
    if kind == "CARE":
        return isinstance(tile, dict) and tile.get("animal") and not tile.get("cared_today", False)
    if kind == "COLLECT_FERTILIZER":
        return isinstance(tile, dict) and tile.get("animal") and tile.get("fertilizer_available", False)
    if kind == "HARVEST":
        return harvest_ready(obs, target)
    return True


def requires_pickup(task):
    if task["kind"] == "PLACE":
        return task["item"]
    if task["kind"] == "FEED":
        return "WHEAT"
    if task["kind"] == "FERTILIZE":
        return "FERTILIZER"
    return None


def pickup_available(obs, item):
    return int(obs.get("private", {}).get("shed", {}).get(item, 0)) > 0


def task_action(task):
    kind = task["kind"]
    if kind == "PLANT":
        return ["PLANT", task["item"]]
    if kind == "PLACE":
        return ["PLACE", task["item"], 1]
    if kind == "BUILD_COOP":
        return ["BUILD_COOP"]
    if kind == "BUILD_PASTURE":
        return ["BUILD_PASTURE"]
    if kind == "WATER":
        return ["WATER"]
    if kind == "HARVEST":
        return ["HARVEST"]
    if kind == "FEED":
        return ["FEED"]
    if kind == "CARE":
        return ["CARE"]
    if kind == "FERTILIZE":
        return ["FERTILIZE"]
    if kind == "COLLECT_FERTILIZER":
        return ["COLLECT_FERTILIZER"]
    return ["PASS"]


def task_finished(obs, task):
    target = task.get("target")
    if target is None:
        return False
    tile = get_tile(obs, target)
    kind = task["kind"]

    if kind == "PLANT":
        return isinstance(tile, dict) and tile.get("kind") == "PLANT" and tile.get("crop") == task["item"]
    if kind == "BUILD_COOP":
        return isinstance(tile, dict) and tile.get("kind") == "COOP"
    if kind == "BUILD_PASTURE":
        return isinstance(tile, dict) and tile.get("kind") == "PASTURE"
    if kind == "PLACE":
        return isinstance(tile, dict) and tile.get("animal") == task["item"]
    if kind == "WATER":
        return isinstance(tile, dict) and tile.get("watered_today", False)
    if kind == "FEED":
        return isinstance(tile, dict) and tile.get("fed_today", False)
    if kind == "CARE":
        return isinstance(tile, dict) and tile.get("cared_today", False)
    if kind == "FERTILIZE":
        return isinstance(tile, dict) and tile.get("fertilized_until_day", -1) >= obs["day"]
    if kind == "HARVEST":
        return not harvest_ready(obs, target)
    if kind == "COLLECT_FERTILIZER":
        return not isinstance(tile, dict) or not tile.get("fertilizer_available", False)
    return False


def task_key(task):
    return task["kind"], task.get("item"), task.get("target")


def cleanup_tasks(obs):
    prune_unviable_tasks(obs)
    for worker_id, task in list(WORKER_TASKS.items()):
        if task is not None and (task_finished(obs, task) or not task_valid(obs, task)):
            WORKER_TASKS[worker_id] = None


def assign_maintenance_tasks(obs, positions):
    maintenance = build_maintenance_tasks(obs)
    used = {task_key(task) for task in WORKER_TASKS.values() if task is not None}

    for worker_id, position in enumerate(positions):
        if WORKER_TASKS.get(worker_id) is not None:
            continue
        standing = [
            task for task in maintenance
            if task_key(task) not in used and standing_task(task, position)
        ]
        if standing:
            task = min(standing, key=lambda value: task_priority(obs, value))
            WORKER_TASKS[worker_id] = task
            used.add(task_key(task))

    while True:
        idle_workers = [
            (worker_id, position) for worker_id, position in enumerate(positions)
            if WORKER_TASKS.get(worker_id) is None
        ]
        candidates = [task for task in maintenance if task_key(task) not in used]
        if not idle_workers or not candidates:
            break

        pairs = [
            (worker_id, position, task)
            for worker_id, position in idle_workers
            for task in candidates
            if task.get("target") is not None
        ]
        if not pairs:
            break

        worker_id, _, task = min(
            pairs,
            key=lambda value: (
                task_priority(obs, value[2]),
                distance(value[1], value[2]["target"]),
                value[2]["target"][1],
                value[2]["target"][0],
                value[0],
            ),
        )

        WORKER_TASKS[worker_id] = task
        used.add(task_key(task))


def assign_pending_tasks(obs, positions):
    reserved = {
        task["target"] for task in WORKER_TASKS.values()
        if task is not None and task.get("target") is not None
    }

    while True:
        idle_workers = [
            (worker_id, position) for worker_id, position in enumerate(positions)
            if WORKER_TASKS.get(worker_id) is None
        ]
        if not idle_workers or not PENDING_TASKS:
            break

        best = None
        for worker_id, position in idle_workers:
            for index, task in enumerate(PENDING_TASKS):
                target = choose_target(obs, task, position, reserved)
                if target is None:
                    continue
                score = (
                    task_priority(obs, task),
                    distance(position, target),
                    distance_to_shed(obs, target),
                    worker_id,
                    index,
                )
                if best is None or score < best[0]:
                    best = (score, worker_id, index, target)

        if best is None:
            break

        _, worker_id, index, target = best
        task = PENDING_TASKS.pop(index)
        task["target"] = target
        WORKER_TASKS[worker_id] = task
        reserved.add(target)


def execute_task(obs, worker_id, position, task):
    if terminal_mode(obs) and sellable_inventory(obs, worker_id) > 0:
        turns_left = max(0, FINAL_SELL_HOUR - obs["hour"])
        must_return = obs["hour"] >= FINAL_RETURN_HOUR or distance_to_shed(obs, position) >= turns_left
        if must_return:
            shed_target = closest(position, shed_access_tiles(obs))
            if position != shed_target:
                return move_towards(position, shed_target)
            return ["DROP"]

    if task is None:
        if inventory_total(obs, worker_id) > 0:
            shed_target = closest(position, shed_access_tiles(obs))
            if position != shed_target:
                return move_towards(position, shed_target)
            return ["DROP"]
        return ["PASS"]

    required_item = requires_pickup(task)
    inventory = worker_inventory(obs, worker_id)

    if required_item and int(inventory.get(required_item, 0)) <= 0:
        shed_target = closest(position, shed_access_tiles(obs))
        if position != shed_target:
            return move_towards(position, shed_target)
        if not pickup_available(obs, required_item):
            return ["PASS"]
        return ["PICKUP", required_item, 1]

    target = task["target"]
    if position != target:
        return move_towards(position, target)
    return task_action(task)


def worker_actions(obs):
    positions = worker_positions(obs)
    cleanup_tasks(obs)
    sync_inventory_tasks(obs)
    assign_maintenance_tasks(obs, positions)
    assign_pending_tasks(obs, positions)
    return [
        execute_task(obs, worker_id, position, WORKER_TASKS.get(worker_id))
        for worker_id, position in enumerate(positions)
    ]


def agent(obs, configuration=None):
    reset_day(obs["day"])
    decision, scores = POLICY.predict(obs)

    if obs["day"] == 0 and obs["hour"] <= 5:
        print(f"day={obs['day']} hour={obs['hour']}")
        print("decision:", {k: v for k, v in decision.items() if v})
        print("purchase_bundle:", scores["purchase_bundle"])
        print("purchase_actions:", scores["purchase_actions"])
        print("bundle_confidence:", scores["purchase_bundle_confidence"])

    market = build_market_orders(obs, decision)
    add_bc_tasks(obs, decision)
    actions = worker_actions(obs)

    farmer = actions[0] if actions else ["PASS"]
    hands = actions[1:] if len(actions) > 1 else []
    return {"farmer": farmer, "hands": hands, "market": market}
