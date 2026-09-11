import math

from src.learning.state_encoder import encode_state, feature_names


def test_state_encoder():
    observation = {
        "player": 0,
        "day": 1,
        "hour": 12,
        "farms": [
            {
                "money": 1000,
                "hires_today": 2,
                "hands": [{}, {}],
                "unlocked_quadrants": ["NW"],
                "tiles": [
                    [
                        {
                            "crop": "WHEAT",
                            "yield_units": 2,
                            "consecutive_unwatered": 1,
                            "watered_today": False,
                            "fertilized_until_day": 2,
                        },
                        {
                            "animal": "COW",
                            "yield_units": 1,
                            "consecutive_unfed": 0,
                            "fed_today": True,
                            "cared_today": True,
                            "fertilizer_available": True,
                            "pending_care_bonus": 1,
                        },
                    ]
                ],
            }
        ],
        "private": {
            "shed": {
                "WHEAT": 5,
                "MILK": 2,
                "COW": 1,
            },
            "seeds": {
                "WHEAT": 2,
            },
            "inventories": [
                {
                    "WHEAT": 3,
                    "MILK": 1,
                }
            ],
        },
        "market": {
            "inventory": {
                "WHEAT": 9900,
                "MILK": 10100,
            },
            "prices": {
                "WHEAT": 30,
                "MILK": 150,
            },
        },
        "town": {
            "unlocked_shops": ["BAKERY", "PIZZA_SHOP"],
        },
    }

    state = encode_state(observation)
    names = feature_names()

    assert len(state) == len(names)
    assert all(isinstance(value, float) for value in state)

    assert state[names.index("day")] == 1 / 29
    assert state[names.index("hour")] == 12 / 23
    assert state[names.index("money_log")] == math.log1p(1000)
    assert state[names.index("hires_today")] == math.log1p(2)
    assert state[names.index("hands")] == math.log1p(2)

    assert state[names.index("quadrant_NW")] == 1.0
    assert state[names.index("quadrant_NE")] == 0.0

    assert state[names.index("shed_WHEAT")] == math.log1p(5)
    assert state[names.index("shed_MILK")] == math.log1p(2)
    assert state[names.index("shed_COW")] == math.log1p(1)

    assert state[names.index("seed_WHEAT")] == math.log1p(2)
    assert state[names.index("carried_WHEAT")] == math.log1p(3)
    assert state[names.index("carried_MILK")] == math.log1p(1)

    assert state[names.index("market_inventory_WHEAT")] == -0.1
    assert state[names.index("market_inventory_MILK")] == 0.1
    assert state[names.index("market_price_WHEAT")] == 30 / 25
    assert state[names.index("market_price_MILK")] == 150 / 160

    assert state[names.index("shop_BAKERY")] == 1.0
    assert state[names.index("shop_PIZZA_SHOP")] == 1.0
    assert state[names.index("shop_BRUNCH_SPOT")] == 0.0

    assert state[names.index("WHEAT_count")] == math.log1p(1)
    assert state[names.index("WHEAT_yield")] == math.log1p(2)
    assert state[names.index("WHEAT_unwatered")] == math.log1p(1)
    assert state[names.index("WHEAT_watered")] == 0.0
    assert state[names.index("WHEAT_fertilized")] == math.log1p(1)

    assert state[names.index("COW_count")] == math.log1p(1)
    assert state[names.index("COW_yield")] == math.log1p(1)
    assert state[names.index("COW_unfed")] == 0.0
    assert state[names.index("COW_fed")] == math.log1p(1)
    assert state[names.index("COW_cared")] == math.log1p(1)
    assert state[names.index("COW_fertilizer")] == math.log1p(1)
    assert state[names.index("COW_care_bonus")] == math.log1p(1)