import math

from src.learning.target_encoder import decode_purchase_bundle, encode_target, occurrence_names, quantity_names, sell_names


def test_target_encoder():
    observation = {
        "private": {
            "shed": {
                "EGG": 4,
                "WHEAT": 10,
            }
        }
    }

    action = {
        "farmer": ["PLANT", "WHEAT"],
        "hands": [
            ["FERTILIZE"],
            ["PLACE", "GOOSE"],
            ["BUILD_PASTURE"],
        ],
        "market": [
            ["HIRE"],
            ["HIRE"],
            ["HIRE"],
            ["BUY_LAND"],
            ["BUY_SEED", "WHEAT", 3],
            ["BUY_ANIMAL", "GOOSE", 2],
            ["SELL", "EGG", 999999],
            ["SELL", "WHEAT", 5],
        ],
    }

    target = encode_target(action, observation)
    occurrence = dict(zip(occurrence_names(), target["occurrence"]))
    quantity = dict(zip(quantity_names(), target["quantity"]))
    sell_ratio = dict(zip(sell_names(), target["sell_ratio"]))

    assert target["hire"] == math.log1p(3)

    assert set(decode_purchase_bundle(target["purchase_bundle"])) == {
        "buy_land",
        "buy_seed_WHEAT",
        "buy_animal_GOOSE",
    }
    assert occurrence["plant_WHEAT"] == 1.0
    assert occurrence["place_GOOSE"] == 1.0
    assert occurrence["fertilize"] == 1.0
    assert occurrence["build_pasture"] == 1.0
    assert occurrence["sell_EGG"] == 1.0
    assert occurrence["sell_WHEAT"] == 1.0
    assert occurrence["sell_MILK"] == 0.0

    assert quantity["buy_seed_WHEAT"] == math.log1p(3)
    assert quantity["buy_animal_GOOSE"] == math.log1p(2)
    assert quantity["plant_WHEAT"] == math.log1p(1)
    assert quantity["place_GOOSE"] == math.log1p(1)
    assert quantity["fertilize"] == math.log1p(1)
    assert quantity["build_pasture"] == math.log1p(1)

    assert sell_ratio["sell_EGG"] == 1.0
    assert sell_ratio["sell_WHEAT"] == 0.5
    assert sell_ratio["sell_MILK"] == 0.0
