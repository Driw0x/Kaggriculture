MARKET = {
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

DAY_1_CROPS = {
    (0, 0): "WHEAT",
    (1, 0): "WHEAT",
    (2, 0): "WHEAT",
    (3, 0): "WHEAT",
    (4, 0): "STRAWBERRY",
    (0, 1): "WHEAT",
    (1, 1): "WHEAT",
    (2, 1): "WHEAT",
    (3, 1): "MELON",
    (4, 1): "CARROT",
    (0, 2): "WHEAT",
    (1, 2): "WHEAT",
    (2, 2): "TOMATO",
    (3, 2): "CARROT",
    (4, 2): "CARROT",
    (0, 3): "WHEAT",
    (1, 3): "MELON",
    (2, 3): "CARROT",
    (0, 4): "STRAWBERRY",
    (1, 4): "CARROT",
    (2, 4): "CARROT",
}

DAY_1_ANIMALS = {
    (3, 3): "GOOSE",
    (4, 3): "COW",
    (3, 4): "SHEEP",
    (4, 4): "COW",
}

DAY_1_PATHS = {
    0: [["WEST"], ["NORTH"], ["EAST"]],
    1: [["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["SOUTH"]],
    2: [["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"]],
    3: [["WEST"], ["NORTH"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["SOUTH"], ["WEST"], ["SOUTH"]],
    4: [["NORTH"], ["WEST"], ["WEST"]],
}

FARMER_SETUP = [
    ["BUILD_PASTURE"],
    ["PICKUP", "COW", 2],
    ["PICKUP", "GOOSE", 1],
    ["PICKUP", "SHEEP", 1],
    ["PICKUP", "WHEAT", 4],
]

STACKS = {}

def move(pos, action):
    x, y = pos
    if action[0] == "NORTH":
        y -= 1
    elif action[0] == "SOUTH":
        y += 1
    elif action[0] == "WEST":
        x -= 1
    elif action[0] == "EAST":
        x += 1
    return x, y

def crop_actions(pos):
    crop = DAY_1_CROPS.get(pos)
    return [["PLANT", crop], ["WATER"]] if crop else []

def animal_actions(pos, build=True):
    animal = DAY_1_ANIMALS.get(pos)
    if not animal:
        return []
    actions = []
    if build:
        actions.append(["BUILD_COOP"] if animal == "GOOSE" else ["BUILD_PASTURE"])
    return actions + [["PLACE", animal], ["FEED"], ["CARE"]]

def build_stack(obs, worker_id):
    farm = obs["farms"][obs["player"]]
    pos = tuple(farm["farmer"] if worker_id == 0 else farm["hands"][worker_id - 1])
    actions = []

    if worker_id == 0:
        actions += FARMER_SETUP
        actions += animal_actions(pos, False)
    else:
        actions += crop_actions(pos)

    for action in DAY_1_PATHS[worker_id]:
        actions.append(action)
        pos = move(pos, action)
        actions += animal_actions(pos) if worker_id == 0 else crop_actions(pos)

    STACKS[worker_id] = list(reversed(actions))

def worker_action(obs, worker_id):
    if worker_id > 0 and obs["hour"] == 0:
        return ["PASS"]
    if worker_id not in STACKS:
        build_stack(obs, worker_id)
    return STACKS[worker_id].pop() if STACKS[worker_id] else ["PASS"]

def agent(obs):
    return {
        "farmer": worker_action(obs, 0),
        "hands": [worker_action(obs, i) for i in range(1, 5)],
        "market": MARKET.get(obs["hour"] + obs["day"] * 24, []),
    }