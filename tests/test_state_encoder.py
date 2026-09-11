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
                "tiles": [[{
                    "plant": "WHEAT",
                    "yield_units": 2,
                    "consecutive_unwatered": 1,
                    "watered_today": False,
                    "fertilized_until_day": 2,
                }]],
            }
        ],
        "private": {
            "shed": {"WHEAT": 5},
            "seeds": {"WHEAT": 2},
            "inventories": [{"WHEAT": 3}],
        },
        "market": {
            "inventory": {"WHEAT": 9900},
            "prices": {"WHEAT": 30},
        },
        "town": {
            "unlocked_shops": ["BAKERY"],
        },
    }

    state = encode_state(observation)

    assert len(state) == len(feature_names())
    assert all(isinstance(value, float) for value in state)