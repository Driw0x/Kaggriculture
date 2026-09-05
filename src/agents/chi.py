DAY_1_MARKET = {
    0: [
        ["BUY_SEED", "WHEAT", 10],
        ["BUY_SEED", "CARROT", 6],
        ["BUY_SEED", "STRAWBERRY", 2],
        ["BUY_ANIMAL", "GOOSE", 1],
        ["BUY_ANIMAL", "COW", 2],
        ["BUY_ANIMAL", "SHEEP", 1],
        ["BUY_PRODUCT", "WHEAT", 16],
        ["HIRE"],
        ["HIRE"],
        ["HIRE"],
    ],
    1: [
        ["BUY_SEED", "TOMATO", 1],
        ["BUY_SEED", "MELON", 2],
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
    (4, 3): "COW",
    (4, 4): "COW",
    (3, 3): "GOOSE",
    (3, 4): "SHEEP",
}

FARMER_PLAN = [
    ["BUILD_PASTURE"],
    ["PICKUP", "COW", 2],
    ["PICKUP", "GOOSE", 1],
    ["PICKUP", "SHEEP", 1],
    ["PICKUP", "WHEAT", 4],
    ["PLACE"], # place cow 1
    ["FEED"], # feed cow 1
    ["CARE"], # care cow 1
    ["WEST"],
    ["BUILD_PASTURE"],
    ["PLACE"], # place sheep
    ["FEED"], # feed sheep
    ["CARE"], # care sheep
    ["NORTH"],
    ["BUILD_COOP"],
    ["PLACE"], # place goose
    ["CARE"], # care goose
    ["FEED"], # feed goose
    ["EAST"],
    ["BUILD_PASTURE"],
    ["PLACE"], # place cow 2
    ["CARE"], # care cow 2
    ["FEED"], # feed cow 2
]

HAND_1_PLAN = [
    ["PASS"],
    ["WEST"],
    ["NORTH"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
]

HAND_2_PLAN = [
    ["PASS"],
    ["NORTH"],
    ["WEST"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"]
]

HAND_3_PLAN = [
    ["PASS"],
    ["WEST"],
    ["NORTH"],
    ["WEST"],
    ["NORTH"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["NORTH"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["WEST"],
    ["PLANT"],
    ["WATER"],
    ["SOUTH"],
    ["PLANT"],
    ["WATER"],
    ["SOUTH"],
    ["PLANT"],
    ["WATER"],
]


def get_worker_position(obs, worker_id):
    farm = obs["farms"][obs["player"]]
    if worker_id == 0:
        return farm["farmer"]
    if worker_id - 1 < len(farm["hands"]):
        return farm["hands"][worker_id - 1]
    return None

def get_action(plan, hour, obs, worker_id):
    if hour >= len(plan):
        return ["PASS"]

    # Day 1
    action = plan[hour]
    if action[0] in ["NORTH", "WEST", "SOUTH", "EAST"]:
        return action
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    if action[0] == "PLACE":
        return action + [DAY_1_ANIMALS[pos]]
    if action[0] == "PLANT":
        return action + [DAY_1_CROPS[pos]]
    return action

def agent(obs):
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)

    if day > 0:
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": [],
        }

    return {
        "farmer": get_action(FARMER_PLAN, hour, obs, 0),
        "hands": [
            get_action(HAND_1_PLAN, hour, obs, 1),
            get_action(HAND_2_PLAN, hour, obs, 2),
            get_action(HAND_3_PLAN, hour, obs, 3),
        ],
        "market": DAY_1_MARKET.get(hour, []),
    }