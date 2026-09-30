from collections import Counter

from kaggle_environments.envs.kaggriculture import kaggriculture as engine

from src.agents import chi13


def observation(day=0, hour=0, money=3000, hands=0):
    own = engine._new_farm(10, money)
    own["hands"] = [[4, 4] for _ in range(hands)]
    private = engine._new_private()
    private["inventories"].extend({} for _ in range(hands))
    return dict(day=day, hour=hour, step=24 * day + hour, player=0,
                farms=[own, engine._new_farm(10, 3000)], private=private,
                market=engine._new_market(), town={"unlocked_shops": []})


def test_land_requires_profit_cash_time_and_worker_capacity():
    obs = observation(money=999)
    assert chi13.plan_land_expansion(obs) is None
    obs = observation(day=29, money=10000, hands=4)
    assert chi13.plan_land_expansion(obs) is None
    obs = observation(money=10000)
    saturated = {"routes": {0: {"cost": 23}}, "market": {}}
    assert chi13.plan_land_expansion(obs, saturated, {"farmHandCostMult": 10000}) is None
    obs = observation(money=10000, hands=4)
    plan = chi13.plan_land_expansion(obs)
    assert plan and plan["layout"] and plan["expected_profit"] > 0
    assert set(plan["layout"]) <= set(chi13.quadrant_positions("NE"))


def test_confirmed_land_plan_is_integrated_into_tasks():
    obs = observation(money=10000, hands=4)
    chi13.STATES.clear()
    first = chi13.agent(obs)
    assert ["BUY_LAND"] in first["market"]
    pending = chi13.STATES[0]["land_plan"]
    obs = chi13.projected_land(obs, pending["quadrant"])
    obs["hour"] = 1
    chi13.agent(obs)
    state = chi13.STATES[0]
    assert "land_plan" not in state
    assert set(pending["layout"]) <= set(state["layout"])
    assert any(task["position"] in pending["layout"]
               for route in state["plan"]["routes"].values() for task in route["tasks"])


def test_failed_land_order_releases_pending_plan():
    obs = observation(money=10000, hands=4)
    chi13.STATES.clear()
    action = chi13.agent(obs)
    assert ["BUY_LAND"] in action["market"]
    obs["hour"] = 1
    obs["step"] = 1
    chi13.agent(obs)
    assert "land_plan" not in chi13.STATES[0]


def test_future_shed_and_market_consolidation():
    obs = observation()
    obs["private"]["shed"]["WHEAT"] = 10
    route = dict(cargo=Counter(CARROT=3), steps=[
        dict(hour=1, action=["PICKUP", "WHEAT", 2]),
        dict(hour=2, action=["DROP"]),
    ])
    market = {1: [["SELL", "WHEAT", 3], ["SELL", "WHEAT", 2]]}
    assert chi13.future_shed(obs, {0: route}, market, 2) == Counter(WHEAT=3, CARROT=3)
    orders = {0: [["BUY_SEED", "WHEAT", 1], ["BUY_SEED", "WHEAT", 2]] + [["HIRE"]] * 10}
    merged = chi13.consolidate_market_orders(orders, 0, 2)
    assert merged[0][0] == ["BUY_SEED", "WHEAT", 3]
    assert all(len(batch) <= 10 for batch in merged.values())


def test_existing_workers_are_considered_before_hire():
    obs = observation(day=4, money=0, hands=1)
    for pos in ((4, 4), (3, 4)):
        tile = engine._new_plant("WHEAT", 0, 24)
        tile.update(watered_today=True, yield_units=2)
        obs["farms"][0]["tiles"][pos[1]][pos[0]] = tile
    plan = chi13.build_plan(obs, {})
    assert not any(order == ["HIRE"] for orders in plan["market"].values() for order in orders)
    assigned = [task["position"] for route in plan["routes"].values() for task in route["tasks"]]
    assert len(assigned) == len(set(assigned)) == 2
