import math

from src.learning.decision_extractor import BUY_PRODUCTS, extract_decision
from src.learning.state_encoder import ANIMALS, CROPS, PRODUCTS

PURCHASE_NAMES = ["buy_land"]
PURCHASE_NAMES += [f"buy_seed_{crop}" for crop in CROPS]
PURCHASE_NAMES += [f"buy_animal_{animal}" for animal in ANIMALS]
PURCHASE_NAMES += [f"buy_product_{item}" for item in BUY_PRODUCTS]
PURCHASE_BUNDLE_COUNT = 1 << len(PURCHASE_NAMES)


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
    names = [f"plant_{crop}" for crop in CROPS]
    names += [f"place_{animal}" for animal in ANIMALS]
    names += ["fertilize", "build_coop", "build_pasture"]
    names += sell_names()
    return names


def encode_purchase_bundle(decision):
    bundle = 0
    for index, name in enumerate(PURCHASE_NAMES):
        if decision[name] > 0:
            bundle |= 1 << index
    return bundle


def decode_purchase_bundle(bundle):
    return [name for index, name in enumerate(PURCHASE_NAMES) if bundle & (1 << index)]


def _available_product(observation, item):
    return max(0, int(observation.get("private", {}).get("shed", {}).get(item, 0)))


def encode_target(action, observation):
    decision = extract_decision(action, observation)
    hire = max(0, int(decision["hire"]))
    occurrence = [float(decision[name] > 0) for name in occurrence_names()]
    quantity = [math.log1p(decision[name]) if decision[name] > 0 else 0.0 for name in quantity_names()]
    quantity_mask = [float(decision[name] > 0) for name in quantity_names()]

    sell_ratio = []
    sell_mask = []
    for name in sell_names():
        item = name.removeprefix("sell_")
        sold = decision[name]
        available = _available_product(observation, item)
        ratio = sold / available if sold > 0 and available > 0 else 0.0
        sell_ratio.append(float(min(1.0, max(0.0, ratio))))
        sell_mask.append(float(sold > 0 and available > 0))

    return {
        "hire": math.log1p(hire),
        "purchase_bundle": encode_purchase_bundle(decision),
        "occurrence": occurrence,
        "quantity": quantity,
        "quantity_mask": quantity_mask,
        "sell_ratio": sell_ratio,
        "sell_mask": sell_mask,
    }