from src.learning.decision_extractor import decision_names, decision_vector, extract_decision


def test_decision_extractor():
    observation = {
        "private": {
            "shed": {
                "EGG": 4,
            }
        }
    }

    action = {
        "farmer": ["PLANT", "WHEAT"],
        "hands": [
            ["FERTILIZE"],
            ["PLACE", "GOOSE"],
            ["WEST"],
        ],
        "market": [
            ["HIRE"],
            ["BUY_SEED", "WHEAT", 3],
            ["BUY_ANIMAL", "GOOSE", 2],
            ["SELL", "EGG", 999999],
        ],
    }

    decision = extract_decision(action, observation)

    assert decision["hire"] == 1
    assert decision["buy_seed_WHEAT"] == 3
    assert decision["buy_animal_GOOSE"] == 2
    assert decision["sell_EGG"] == 4
    assert decision["plant_WHEAT"] == 1
    assert decision["place_GOOSE"] == 1
    assert decision["fertilize"] == 1
    assert len(decision_vector(action, observation)) == len(decision_names())