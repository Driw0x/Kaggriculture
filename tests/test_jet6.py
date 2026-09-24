import copy

import src.agents.jet6 as jet6


CONFIGURATION = {"episodeSteps": 720, "boardSize": 10}


def observation(step, positions=((5, 2),), inventories=None):
    tiles = [[None for _ in range(10)] for _ in range(10)]
    tiles[2][5] = {"kind": "PASTURE"}
    return {
        "step": step,
        "player": 0,
        "farms": [
            {
                "farmer": list(positions[0]),
                "hands": [list(position) for position in positions[1:]],
                "tiles": tiles,
            },
            {},
        ],
        "private": {
            "inventories": inventories or [{} for _ in positions],
        },
    }


def animal(fertilizer=True):
    return {
        "kind": "PASTURE",
        "animal": "COW",
        "fertilizer_available": fertilizer,
    }


def test_dead_terminal_collect_moves_toward_collectable_animal():
    obs = observation(714)
    obs["farms"][0]["tiles"][2][4] = animal()
    action = {"farmer": ["COLLECT_FERTILIZER"], "hands": [], "market": []}

    result = jet6._jet6_recover_terminal_fertilizer(obs, action, CONFIGURATION)

    assert result["farmer"] == ["WEST"]


def test_terminal_care_is_replaced_by_advanced_collection():
    obs = observation(715, positions=((4, 2),))
    obs["farms"][0]["tiles"][2][4] = animal()
    action = {"farmer": ["CARE"], "hands": [], "market": []}

    result = jet6._jet6_recover_terminal_fertilizer(obs, action, CONFIGURATION)

    assert result["farmer"] == ["COLLECT_FERTILIZER"]


def test_collection_without_time_to_return_is_unchanged():
    obs = observation(715, positions=((0, 0),))
    obs["farms"][0]["tiles"][0][0] = animal()
    action = {"farmer": ["CARE"], "hands": [], "market": []}

    assert jet6._jet6_recover_terminal_fertilizer(
        obs, action, CONFIGURATION
    ) == action


def test_other_actions_and_market_orders_remain_intact():
    obs = observation(714, positions=((1, 1), (5, 2)))
    obs["farms"][0]["tiles"][2][4] = animal()
    action = {
        "farmer": ["EAST"],
        "hands": [["COLLECT_FERTILIZER"]],
        "market": [["SELL", "WHEAT", 3]],
    }

    result = jet6._jet6_recover_terminal_fertilizer(obs, action, CONFIGURATION)

    assert result == {
        "farmer": ["EAST"],
        "hands": [["WEST"]],
        "market": [["SELL", "WHEAT", 3]],
    }


def test_missing_information_preserves_jet5_action():
    action = {"farmer": ["CARE"], "hands": [], "market": []}
    assert jet6._jet6_recover_terminal_fertilizer(
        {"step": 715}, copy.deepcopy(action), None
    ) == action


def test_early_sale_uses_free_slot_and_records_telemetry():
    obs = {"private": {"shed": {"MILK": 4}}}
    action = {"farmer": ["PASS"], "hands": [], "market": []}
    for key in jet6._JET6_EARLY_SALE_TELEMETRY:
        jet6._JET6_EARLY_SALE_TELEMETRY[key] = 0

    result = jet6._jet6_sell_available_products(obs, action, CONFIGURATION)

    assert result["market"] == [["SELL", "MILK", 4]]
    assert jet6._JET6_EARLY_SALE_TELEMETRY == {
        "opportunities": 1,
        "orders_added": 1,
        "units_offered": 4,
        "full_market_skips": 0,
    }


def test_early_sale_preserves_inputs_and_existing_orders():
    obs = {"private": {"shed": {"WHEAT": 8, "FERTILIZER": 3, "WOOL": 5}}}
    action = {"market": [["SELL", "WOOL", 2], ["HIRE"]]}

    result = jet6._jet6_sell_available_products(obs, action, CONFIGURATION)

    assert result["market"] == [
        ["SELL", "WOOL", 2],
        ["HIRE"],
        ["SELL", "WOOL", 3],
    ]


def test_early_sale_does_not_overflow_market_limit():
    obs = {"private": {"shed": {"MILK": 4}}}
    action = {"market": [["HIRE"]]}

    result = jet6._jet6_sell_available_products(
        obs, action, {"maxMarketOrdersPerTurn": 1}
    )

    assert result == action


def test_early_sale_missing_private_information_is_unchanged():
    action = {"market": [["SELL", "WOOL", 2]]}

    assert jet6._jet6_sell_available_products({}, action, CONFIGURATION) is action
