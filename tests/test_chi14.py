from copy import deepcopy

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

from src.agents import chi14


def observation(day=0, hour=0, money=10000, hands=4):
    own = engine._new_farm(10, money)
    own["hands"] = [[4, 4] for _ in range(hands)]
    private = engine._new_private()
    private["inventories"].extend({} for _ in range(hands))
    return dict(day=day, hour=hour, step=24 * day + hour, player=0,
                farms=[own, engine._new_farm(10, money)], private=private,
                market=engine._new_market(), town={"unlocked_shops": []})


def plant(obs, player, position, crop, planted_day, **updates):
    tile = engine._new_plant(crop, planted_day, 24)
    tile.update(updates)
    obs["farms"][player]["tiles"][position[1]][position[0]] = tile
    return tile


def test_chi13_static_crop_profit_is_not_part_of_chi14():
    assert not hasattr(chi14, "_crop_profit")


def test_dated_sales_do_not_reuse_one_spot_price():
    obs = observation(hands=0)
    early = chi14.project_market(obs, [dict(tick=0, item="WHEAT", quantity=1, owner="self")])
    late = chi14.project_market(obs, [dict(tick=24, item="WHEAT", quantity=1, owner="self")])
    assert late["revenue"]["self"] > early["revenue"]["self"]


def test_successive_melons_recompute_marginal_value_without_quota():
    obs = chi14.projected_land(observation(), "NE")
    layout = {}
    contributions = []
    for position in chi14.quadrant_positions("NE")[:12]:
        result = chi14.marginal_crop_contribution(obs, layout, "MELON", position)
        contributions.append(result["contribution_prudent"])
        layout[position] = "MELON"
    assert all(value > 0 for value in contributions)
    assert len(set(contributions)) > 1


def test_market_saturation_can_make_another_crop_better():
    obs = chi14.projected_land(observation(), "NE")
    positions = chi14.quadrant_positions("NE")
    layout = {position: "MELON" for position in positions[:-1]}
    last = positions[-1]
    values = {crop: chi14.marginal_crop_contribution(obs, layout, crop, last)[
        "contribution_prudent"] for crop in chi14.SEED_COST}
    assert max(values, key=values.get) != "MELON"


def test_visible_opponent_supply_only_affects_later_own_sale():
    obs = observation(hands=0)
    plant(obs, 1, (4, 4), "MELON", -10, yield_units=6)
    layout = {(0, 0): "MELON"}
    central = chi14.production_lots(obs, layout)
    prudent = chi14.production_lots(obs, layout, include_opponent=True)
    assert chi14.project_market(obs, prudent)["revenue"]["self"] < chi14.project_market(
        obs, central)["revenue"]["self"]

    obs = observation(day=10, hands=0)
    own = plant(obs, 0, (4, 4), "MELON", 0, yield_units=6)
    own["watered_today"] = True
    plant(obs, 1, (4, 4), "MELON", 10)
    central = chi14.production_lots(obs)
    prudent = chi14.production_lots(obs, include_opponent=True)
    own_tick = next(lot["tick"] for lot in central if lot["owner"] == "self")
    assert chi14.project_market(obs, central)["quotes"][own_tick, "MELON"] == chi14.project_market(
        obs, prudent)["quotes"][own_tick, "MELON"][:6]


def test_land_cost_is_once_and_prefix_can_repay_it_collectively():
    obs = observation()
    virtual = chi14.projected_land(obs, "NE")
    one = {(5, 4): "MELON"}
    no_land = chi14.evaluate_layout(virtual, one)
    with_land = chi14.evaluate_layout(virtual, one, land_cost=1000)
    assert no_land["coins_final_prudent"] - with_land["coins_final_prudent"] == 1000
    assert no_land["coins_final_prudent"] - obs["farms"][0]["money"] < 1000

    plan = chi14.build_plan(obs, chi14.choose_placements(obs))
    expansion = chi14.plan_land_expansion(obs, plan)
    assert expansion and len(expansion["layout"]) > 1 and expansion["prudent_profit"] > 0


def test_unprofitable_prefix_does_not_buy_land():
    obs = observation(day=29)
    assert chi14.plan_land_expansion(obs) is None


def test_rejected_candidate_leaves_no_state_and_confirmation_does_not_double():
    obs = chi14.projected_land(observation(), "NE")
    layout = {(5, 4): "MELON"}
    before = deepcopy(layout)
    chi14.marginal_crop_contribution(obs, layout, "STRAWBERRY", (6, 4))
    assert layout == before

    plant(obs, 0, (5, 4), "MELON", 0)
    lots = chi14.production_lots(obs, layout)
    assert {lot["source"][0] for lot in lots if lot["position"] == (5, 4)} == {"existing"}


def test_unsellable_harvest_has_zero_value():
    obs = observation(day=29, hour=20, hands=0)
    obs["step"] = 29 * 24 + 20
    assert chi14.production_lots(obs, {(0, 0): "WHEAT"}) == []


def test_price_floor_sell_matches_engine_and_does_not_add_inventory():
    obs = observation(hands=0)
    inventory = obs["market"]["inventory"]
    inventory["MELON"] += 10000
    obs["market"]["prices"]["MELON"] = engine.market_price("MELON", inventory["MELON"])
    # Keep all observed quotes consistent so projection remains valid.
    for item in engine.PRODUCTS:
        obs["market"]["prices"][item] = engine.market_price(item, inventory[item])
    result = chi14.project_market(
        obs, [dict(tick=0, item="MELON", quantity=3, owner="self")])
    assert result["revenue"]["self"] == 3
    assert result["trajectory"][0]["MELON"] == inventory["MELON"] - 1


def test_agent_respects_market_limit_and_returns_valid_actions():
    obs = observation()
    chi14.STATES.clear()
    action = chi14.agent(obs, {"maxMarketOrdersPerTurn": 3})
    assert len(action["market"]) <= 3
    assert len(action["hands"]) == len(obs["farms"][0]["hands"])
    own, private = deepcopy(obs["farms"][0]), deepcopy(obs["private"])
    for worker, command in enumerate([action["farmer"], *action["hands"]]):
        if command != ["PASS"]:
            previous = deepcopy((own, private))
            engine._apply_unit_action(own, private, worker, command, 10, 0, 24)
            assert (own, private) != previous
