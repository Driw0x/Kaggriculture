from unittest.mock import patch

import src.agents.jet5 as jet5


def observation(fertilizer=0, carried=0):
    return {
        "step": 100,
        "private": {
            "shed": {"FERTILIZER": fertilizer},
            "inventories": [{"FERTILIZER": carried}],
        },
    }


def action(quantity):
    return {
        "farmer": ["PASS"],
        "hands": [],
        "market": [["BUY_PRODUCT", "FERTILIZER", quantity]],
    }


def filtered(quantity, need, fertilizer=0, carried=0, obs=None):
    with patch.object(jet5, "_jet5_future_fertilize_need", return_value=need):
        return jet5._jet5_filter_dead_fertilizer_buys(
            observation(fertilizer, carried) if obs is None else obs,
            action(quantity),
        )


def test_entirely_necessary_purchase_is_unchanged():
    assert filtered(3, need=5, fertilizer=1, carried=1) == action(3)


def test_partially_excess_purchase_is_reduced():
    assert filtered(4, need=5, fertilizer=2, carried=1)["market"] == [
        ["BUY_PRODUCT", "FERTILIZER", 2]
    ]


def test_purchase_is_removed_without_future_need():
    assert filtered(2, need=0)["market"] == []


def test_purchase_is_removed_when_observed_stock_is_sufficient():
    assert filtered(2, need=3, fertilizer=2, carried=1)["market"] == []


def test_missing_inventory_information_preserves_purchase():
    incomplete = {"step": 100, "private": {"shed": {"FERTILIZER": 0}}}
    assert filtered(4, need=0, obs=incomplete) == action(4)
