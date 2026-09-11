import math

from src.learning.decision_extractor import BUY_PRODUCTS, extract_decision
from src.learning.state_encoder import ANIMALS, CROPS, PRODUCTS

HIRE_MAX = 10


def quantity_names():
    names = [f"buy_seed_{crop}" for crop in CROPS]
    names += [f"buy_animal_{animal}" for animal in ANIMALS]
    names += [f"buy_product_{item}" for item in BUY_PRODUCTS]
    names += [f"plant_{crop}" for crop in CROPS]
    names += [f"place_{animal}" for animal in ANIMALS]
    names += ["fertilize", "build_coop", "build_pasture"]
    return names


def sell_names():
    return [f"sell_{item}" for item in PRODUCTS]


def occurrence_names():
    return ["buy_land"] + quantity_names() + sell_names()


def _available_product(observation, item):
    return max(0, int(observation.get("private", {}).get("shed", {}).get(item, 0)))


def encode_target(action, observation):
    decision = extract_decision(action, observation)
    hire = int(decision["hire"])

    if hire < 0 or hire > HIRE_MAX:
        raise ValueError(f"Invalid hire count: {hire}")

    occurrence = [float(decision[name] > 0) for name in occurrence_names()]
    quantity = [math.log1p(decision[name]) if decision[name] > 0 else 0.0 for name in quantity_names()]

    sell_ratio = []
    for name in sell_names():
        item = name.removeprefix("sell_")
        sold = decision[name]
        available = _available_product(observation, item)
        ratio = sold / available if sold > 0 and available > 0 else 0.0
        sell_ratio.append(float(min(1.0, max(0.0, ratio))))

    return {
        "hire": hire,
        "occurrence": occurrence,
        "quantity": quantity,
        "sell_ratio": sell_ratio,
    }