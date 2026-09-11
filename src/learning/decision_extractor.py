from src.learning.state_encoder import ANIMALS, CROPS, PRODUCTS

BUY_PRODUCTS = ("WHEAT", "FERTILIZER")


def decision_names():
    names = ["hire", "buy_land"]

    names += [f"buy_seed_{crop}" for crop in CROPS]
    names += [f"buy_animal_{animal}" for animal in ANIMALS]
    names += [f"buy_product_{item}" for item in BUY_PRODUCTS]
    names += [f"sell_{item}" for item in PRODUCTS]

    names += [f"plant_{crop}" for crop in CROPS]
    names += [f"place_{animal}" for animal in ANIMALS]

    names += [
        "fertilize",
        "build_coop",
        "build_pasture",
    ]

    return names


def _quantity(action):
    for value in reversed(action[1:]):
        if isinstance(value, (int, float)):
            return int(value)
    return 1


def _worker_actions(action):
    farmer = action.get("farmer")

    if isinstance(farmer, list) and farmer:
        yield farmer

    for hand_action in action.get("hands", []):
        if isinstance(hand_action, list) and hand_action:
            yield hand_action


def extract_decision(action):
    decision = {name: 0 for name in decision_names()}

    for market_action in action.get("market", []):
        if not market_action:
            continue

        kind = market_action[0]
        item = market_action[1] if len(market_action) > 1 else None
        quantity = _quantity(market_action)

        if kind == "HIRE":
            decision["hire"] += quantity

        elif kind == "BUY_LAND":
            decision["buy_land"] += 1

        elif kind == "BUY_SEED" and item in CROPS:
            decision[f"buy_seed_{item}"] += quantity

        elif kind == "BUY_ANIMAL" and item in ANIMALS:
            decision[f"buy_animal_{item}"] += quantity

        elif kind == "BUY_PRODUCT" and item in BUY_PRODUCTS:
            decision[f"buy_product_{item}"] += quantity

        elif kind == "SELL" and item in PRODUCTS:
            decision[f"sell_{item}"] += quantity

    for worker_action in _worker_actions(action):
        kind = worker_action[0]
        item = worker_action[1] if len(worker_action) > 1 else None

        if kind == "PLANT" and item in CROPS:
            decision[f"plant_{item}"] += 1

        elif kind == "PLACE" and item in ANIMALS:
            decision[f"place_{item}"] += 1

        elif kind == "FERTILIZE":
            decision["fertilize"] += 1

        elif kind == "BUILD_COOP":
            decision["build_coop"] += 1

        elif kind == "BUILD_PASTURE":
            decision["build_pasture"] += 1

    return decision


def decision_vector(action):
    decision = extract_decision(action)
    return [float(decision[name]) for name in decision_names()]