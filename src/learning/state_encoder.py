import math

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
SHED_ITEMS = PRODUCTS + ANIMALS
QUADRANTS = ("NW", "NE", "SW", "SE")
SHOPS = ("BAKERY", "PIZZA", "BRUNCH", "YARN", "ICE_CREAM", "PET_CAFE", "SMOOTHIE", "FARMERS_MARKET")

BASE_PRICES = {
    "WHEAT": 25,
    "CARROT": 35,
    "TOMATO": 60,
    "STRAWBERRY": 120,
    "MELON": 250,
    "EGG": 50,
    "MILK": 160,
    "WOOL": 200,
    "FERTILIZER": 100,
}


def _tiles(farm):
    for row in farm.get("tiles", []):
        for tile in row:
            if isinstance(tile, dict):
                yield tile


def _inventory_total(inventories, item):
    return sum(inv.get(item, 0) for inv in inventories if isinstance(inv, dict))


def feature_names():
    names = [
        "day",
        "hour",
        "money_log",
        "hires_today",
        "hands",
    ]

    names += [f"quadrant_{q}" for q in QUADRANTS]
    names += [f"shed_{item}" for item in SHED_ITEMS]
    names += [f"seed_{crop}" for crop in CROPS]
    names += [f"carried_{item}" for item in PRODUCTS]
    names += [f"market_inventory_{item}" for item in PRODUCTS]
    names += [f"market_price_{item}" for item in PRODUCTS]
    names += [f"shop_{shop}" for shop in SHOPS]

    for crop in CROPS:
        names += [
            f"{crop}_count",
            f"{crop}_yield",
            f"{crop}_unwatered",
            f"{crop}_watered",
            f"{crop}_fertilized",
        ]

    for animal in ANIMALS:
        names += [
            f"{animal}_count",
            f"{animal}_yield",
            f"{animal}_unfed",
            f"{animal}_fed",
            f"{animal}_cared",
            f"{animal}_fertilizer",
            f"{animal}_care_bonus",
        ]

    return names


def encode_state(observation):
    player = observation["player"]
    farm = observation["farms"][player]

    private = observation.get("private", {})
    shed = private.get("shed", {})
    seeds = private.get("seeds", {})
    inventories = private.get("inventories", [])

    market = observation.get("market", {})
    market_inventory = market.get("inventory", {})
    market_prices = market.get("prices", {})

    unlocked_quadrants = set(farm.get("unlocked_quadrants", []))
    unlocked_shops = set(observation.get("town", {}).get("unlocked_shops", []))

    day = observation.get("day", 0)
    tiles = list(_tiles(farm))

    features = [
        day / 29.0,
        observation.get("hour", 0) / 23.0,
        math.log1p(max(0, farm.get("money", 0))),
        farm.get("hires_today", 0),
        len(farm.get("hands", [])),
    ]

    features += [float(q in unlocked_quadrants) for q in QUADRANTS]
    features += [shed.get(item, 0) for item in SHED_ITEMS]
    features += [seeds.get(crop, 0) for crop in CROPS]
    features += [_inventory_total(inventories, item) for item in PRODUCTS]

    features += [
        (market_inventory.get(item, 10000) - 10000) / 1000.0
        for item in PRODUCTS
    ]

    features += [
        market_prices.get(item, BASE_PRICES[item]) / BASE_PRICES[item]
        for item in PRODUCTS
    ]

    features += [float(shop in unlocked_shops) for shop in SHOPS]

    for crop in CROPS:
        crop_tiles = [tile for tile in tiles if tile.get("plant") == crop]

        features += [
            len(crop_tiles),
            sum(tile.get("yield_units", 0) for tile in crop_tiles),
            sum(tile.get("consecutive_unwatered", 0) >= 1 for tile in crop_tiles),
            sum(bool(tile.get("watered_today")) for tile in crop_tiles),
            sum(tile.get("fertilized_until_day", -1) >= day for tile in crop_tiles),
        ]

    for animal in ANIMALS:
        animal_tiles = [tile for tile in tiles if tile.get("animal") == animal]

        features += [
            len(animal_tiles),
            sum(tile.get("yield_units", 0) for tile in animal_tiles),
            sum(tile.get("consecutive_unfed", 0) >= 1 for tile in animal_tiles),
            sum(bool(tile.get("fed_today")) for tile in animal_tiles),
            sum(bool(tile.get("cared_today")) for tile in animal_tiles),
            sum(bool(tile.get("fertilizer_available")) for tile in animal_tiles),
            sum(tile.get("pending_care_bonus", 0) for tile in animal_tiles),
        ]

    return [float(value) for value in features]