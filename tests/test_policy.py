import json
import math

import torch

from src.learning.policy import decode_output, decode_quantity, load_thresholds, market_orders_from_decision
from src.learning.target_encoder import PURCHASE_BUNDLE_COUNT, PURCHASE_NAMES, occurrence_names, quantity_names, sell_names

OCCURRENCE_NAMES = occurrence_names()
QUANTITY_NAMES = quantity_names()
SELL_NAMES = sell_names()


def make_observation():
    return {
        "player": 0,
        "farms": [{"hires_today": 2, "unlocked_quadrants": ["NW"]}],
        "private": {
            "shed": {
                "WHEAT": 10,
                "CARROT": 0,
                "TOMATO": 0,
                "STRAWBERRY": 0,
                "MELON": 0,
                "EGG": 0,
                "MILK": 0,
                "WOOL": 0,
                "FERTILIZER": 4,
            }
        },
    }


def make_output():
    output = {
        "hire": torch.zeros(1),
        "purchase_bundle": torch.full((1, PURCHASE_BUNDLE_COUNT), -10.0),
        "occurrence": torch.full((1, len(OCCURRENCE_NAMES)), -10.0),
        "quantity": torch.zeros((1, len(QUANTITY_NAMES))),
        "sell_ratio": torch.zeros((1, len(SELL_NAMES))),
    }
    output["purchase_bundle"][0, 0] = 10.0
    return output


def make_thresholds():
    return {name: 0.5 for name in OCCURRENCE_NAMES}


def activate(output, name, probability=0.99):
    index = OCCURRENCE_NAMES.index(name)
    output["occurrence"][0, index] = math.log(probability / (1 - probability))


def select_purchase_bundle(output, *names):
    bundle = sum(1 << PURCHASE_NAMES.index(name) for name in names)
    output["purchase_bundle"].fill_(-10.0)
    output["purchase_bundle"][0, bundle] = 10.0


def test_decode_quantity():
    assert decode_quantity(0.0) == 1
    assert decode_quantity(math.log1p(3)) == 3
    assert decode_quantity(math.log1p(10)) == 10


def test_load_thresholds(tmp_path):
    path = tmp_path / "thresholds.json"
    thresholds = make_thresholds()
    path.write_text(json.dumps(thresholds), encoding="utf-8")
    assert load_thresholds(path) == thresholds


def test_hire_decoding():
    observation = make_observation()
    output = make_output()
    output["hire"][0] = math.log1p(8)
    decision, _ = decode_output(output, observation, make_thresholds())
    assert decision["hire"] == 8


def test_quantity_decoding():
    observation = make_observation()
    output = make_output()
    select_purchase_bundle(output, "buy_seed_WHEAT")
    output["quantity"][0, QUANTITY_NAMES.index("buy_seed_WHEAT")] = math.log1p(6)
    decision, _ = decode_output(output, observation, make_thresholds())
    assert decision["buy_seed_WHEAT"] == 6


def test_inactive_occurrence_is_zero():
    decision, _ = decode_output(make_output(), make_observation(), make_thresholds())
    assert decision["buy_seed_WHEAT"] == 0
    assert decision["plant_WHEAT"] == 0


def test_sell_is_limited_by_available_inventory():
    observation = make_observation()
    output = make_output()
    activate(output, "sell_WHEAT")
    output["sell_ratio"][0, SELL_NAMES.index("sell_WHEAT")] = 0.8
    decision, _ = decode_output(output, observation, make_thresholds())
    assert decision["sell_WHEAT"] == 8


def test_sell_without_inventory_is_zero():
    observation = make_observation()
    output = make_output()
    activate(output, "sell_CARROT")
    output["sell_ratio"][0, SELL_NAMES.index("sell_CARROT")] = 1.0
    decision, _ = decode_output(output, observation, make_thresholds())
    assert decision["sell_CARROT"] == 0


def test_buy_land_disabled_when_all_land_unlocked():
    observation = make_observation()
    observation["farms"][0]["unlocked_quadrants"] = ["NW", "NE", "SW", "SE"]
    output = make_output()
    select_purchase_bundle(output, "buy_land")
    decision, _ = decode_output(output, observation, make_thresholds())
    assert decision["buy_land"] == 0


def test_market_orders():
    decision = {"hire": 2, "buy_land": 1, "buy_seed_WHEAT": 4, "sell_WHEAT": 3}
    assert market_orders_from_decision(decision) == [
        ["HIRE"],
        ["HIRE"],
        ["BUY_LAND"],
        ["BUY_SEED", "WHEAT", 4],
        ["SELL", "WHEAT", 3],
    ]


def test_market_orders_respect_limit():
    decision = {"hire": 10, "buy_land": 1, "buy_seed_WHEAT": 5}
    assert len(market_orders_from_decision(decision, max_orders=10)) == 10
