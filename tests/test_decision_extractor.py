from src.learning.decision_extractor import extract_decision, decision_vector, decision_names


def test_decision_extractor():
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
            ["SELL", "EGG", 4],
        ],
    }

    decision = extract_decision(action)

    assert decision["hire"] == 1
    assert decision["buy_seed_WHEAT"] == 3
    assert decision["buy_animal_GOOSE"] == 2
    assert decision["sell_EGG"] == 4
    assert decision["plant_WHEAT"] == 1
    assert decision["place_GOOSE"] == 1
    assert decision["fertilize"] == 1
    assert len(decision_vector(action)) == len(decision_names())
    