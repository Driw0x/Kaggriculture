from collections import Counter
from copy import deepcopy

import pytest
from kaggle_environments import make
from kaggle_environments.envs.kaggriculture import kaggriculture as engine

from src.agents import chi3, chi12


def observation(day=0, hour=0, position=(4, 4)):
    own = engine._new_farm(10, 3000)
    own["farmer"] = list(position)
    return dict(day=day, hour=hour, step=24 * day + hour, player=0,
                farms=[own, engine._new_farm(10, 3000)],
                private=engine._new_private(), market=engine._new_market(),
                town={"unlocked_shops": []})


def plant(obs, pos, crop, age, **values):
    tile = engine._new_plant(crop, obs["day"] - age, 24)
    tile.update(values)
    obs["farms"][0]["tiles"][pos[1]][pos[0]] = tile
    return tile


def animal(obs, pos, kind="COW", **values):
    tile = engine._new_animal(kind, 0)
    tile.update(values)
    obs["farms"][0]["tiles"][pos[1]][pos[0]] = tile
    return tile


def execute_route(obs, route):
    for step in route["steps"]:
        engine._apply_unit_action(obs["farms"][0], obs["private"], 0,
                                  step["action"], 10, obs["day"], 24)


def test_new_seed_is_watered_same_day_and_bundle_cannot_be_truncated():
    obs = observation()
    obs["private"]["seeds"]["WHEAT"] = 1
    tasks = chi12.generate_tasks(obs, {(4, 4): "WHEAT"})
    route = chi12.compile_route(obs, tasks, (4, 4), 22)
    assert [s["action"] for s in route["steps"]] == [["PLANT", "WHEAT"], ["WATER"]]
    assert chi12.compile_route(obs, tasks, (4, 4), 23) is None
    execute_route(obs, route)
    engine._daily_refresh_plants(obs["farms"][0], 0, 24)
    assert obs["farms"][0]["tiles"][4][4]["kind"] == "PLANT"


def test_three_feeds_load_three_wheat_before_leaving_shed():
    obs = observation(day=2)
    for pos in ((3, 4), (3, 3), (4, 3)):
        animal(obs, pos, cared_today=True, consecutive_unfed=1)
    obs["private"]["shed"]["WHEAT"] = 3
    tasks = chi12.generate_tasks(obs, {})
    route = chi12.compile_route(obs, tasks, (4, 4), 0)
    assert route["steps"][0]["action"] == ["PICKUP", "WHEAT", 3]
    execute_route(obs, route)
    assert all(obs["farms"][0]["tiles"][y][x]["fed_today"] for x, y in ((3, 4), (3, 3), (4, 3)))
    assert obs["private"]["inventories"][0].get("WHEAT", 0) == 0


def test_multiple_fertilizers_and_carried_stock_are_counted():
    obs = observation(day=7)
    for pos in ((4, 4), (4, 3), (3, 3)):
        plant(obs, pos, "TOMATO", 7)
    obs["private"]["shed"]["FERTILIZER"] = 2
    obs["private"]["inventories"][0]["FERTILIZER"] = 1
    tasks = chi12.generate_tasks(obs, {})
    route = chi12.compile_route(obs, tasks, (4, 4), 0, {"FERTILIZER": 1})
    assert route["steps"][0]["action"] == ["PICKUP", "FERTILIZER", 2]
    execute_route(obs, route)
    assert all(obs["farms"][0]["tiles"][y][x]["fertilized_until_day"] == 9
               for x, y in ((4, 4), (4, 3), (3, 3)))


@pytest.mark.parametrize("kind", ["GOOSE", "COW", "SHEEP"])
def test_new_animal_loads_before_departure_then_build_place_feed(kind):
    obs = observation()
    obs["private"]["shed"].update({kind: 1, "WHEAT": 1})
    tasks = chi12.generate_tasks(obs, {(3, 4): kind})
    route = chi12.compile_route(obs, tasks, (4, 4), 0)
    assert [s["action"] for s in route["steps"][:2]] == [["PICKUP", kind, 1], ["PICKUP", "WHEAT", 1]]
    execute_route(obs, route)
    tile = obs["farms"][0]["tiles"][4][3]
    assert tile["animal"] == kind and tile["fed_today"] and tile["cared_today"]


def test_fertilize_water_harvest_order_matches_real_yield():
    obs = observation(day=2)
    obs["market"]["prices"]["WHEAT"] = 100
    tile = plant(obs, (4, 4), "WHEAT", 2, max_lifespan_step=72)
    obs["private"]["shed"]["FERTILIZER"] = 1
    task = chi12.generate_tasks(obs, {})[0]
    assert task["actions"] == [["FERTILIZE"], ["WATER"], ["HARVEST"]]
    route = chi12.compile_route(obs, [task], (4, 4), 0)
    execute_route(obs, route)
    assert obs["private"]["shed"]["WHEAT"] == 3


@pytest.mark.parametrize("crop,age", [("TOMATO", 11), ("STRAWBERRY", 16)])
def test_ongoing_replacement_digs_between_harvest_and_plant(crop, age):
    obs = observation(day=age)
    plant(obs, (4, 4), crop, age, watered_today=True, yield_units=2)
    obs["private"]["seeds"][crop] = 1
    task = chi12.generate_tasks(obs, {(4, 4): crop})[0]
    assert task["actions"] == [["HARVEST"], ["DIG"], ["PLANT", crop], ["WATER"]]
    execute_route(obs, chi12.compile_route(obs, [task], (4, 4), 0))
    assert obs["farms"][0]["tiles"][4][4]["planted_day"] == age
    assert obs["farms"][0]["tiles"][4][4]["watered_today"]


def test_return_distance_and_drop_are_part_of_route_cost():
    obs = observation(day=4)
    plant(obs, (2, 4), "WHEAT", 4, watered_today=True, yield_units=4)
    tasks = chi12.generate_tasks(obs, {})
    route = chi12.compile_route(obs, tasks, (4, 4), 0)
    assert route["cost"] == 2 + 1 + 2 + 1
    assert route["steps"][-1]["action"] == ["DROP"]
    assert chi12.compile_route(obs, tasks, (4, 4), 19) is None


def test_existing_weed_generates_dig_without_a_plant_branch():
    obs = observation()
    obs["farms"][0]["tiles"][4][4] = {"kind": "WEED"}
    assert chi12.generate_tasks(obs, {(4, 4): "CARROT"})[0]["actions"] == [
        ["DIG"], ["PLANT", "CARROT"], ["WATER"]]


@pytest.mark.parametrize("crop,age", [("WHEAT", 1), ("CARROT", 1), ("MELON", 9)])
def test_positive_yield_is_not_enough_to_harvest(crop, age):
    obs = observation(day=age)
    plant(obs, (4, 4), crop, age, yield_units=6)
    assert not chi12.harvestable(obs["farms"][0]["tiles"][4][4], age)
    assert ["HARVEST"] not in chi12.generate_tasks(obs, {})[0]["actions"]


def test_assigned_bundles_are_unique_and_hires_start_next_tick():
    obs = observation()
    plan = chi12.build_plan(obs, chi12.choose_placements(obs))
    assigned = [task["position"] for route in plan["routes"].values() for task in route["tasks"]]
    assert len(assigned) == len(set(assigned)) == 25
    assert not plan["unassigned"]
    for worker, route in plan["routes"].items():
        assert route["finish"] <= 24
        if worker:
            assert route["available"] == route["hire_hour"] + 1
    assert all(len(orders) <= 10 for orders in plan["market"].values())


def test_market_merge_keeps_hires_separate_and_counts_all_order_types():
    orders = [["SELL", "MILK", 2], ["SELL", "MILK", 3], ["BUY_SEED", "WHEAT", 2],
              ["BUY_SEED", "WHEAT", 1], ["BUY_PRODUCT", "FERTILIZER", 2],
              ["BUY_ANIMAL", "COW", 1], ["BUY_LAND"]] + [["HIRE"]] * 8
    merged = chi12.merge_orders(orders)
    assert len(merged) == 10
    assert merged[:2] == [["SELL", "MILK", 5], ["BUY_SEED", "WHEAT", 3]]
    assert merged.count(["HIRE"]) == 5


def test_real_engine_buy_hire_and_last_tick_timing():
    env = make("kaggriculture", configuration={"seed": 0, "episodeSteps": 4}, debug=True)
    env.step([{"farmer": ["PLANT", "WHEAT"], "hands": [["WEST"]],
               "market": [["BUY_SEED", "WHEAT", 1], ["HIRE"]]}, {}])
    obs = env.state[0].observation
    assert obs.farms[0]["tiles"][4][4] is None
    assert obs.farms[0]["hands"] == [[5, 4]]
    env.step([{"farmer": ["PLANT", "WHEAT"], "hands": [["WEST"]]}, {}])
    assert env.state[0].observation.farms[0]["tiles"][4][4]["kind"] == "PLANT"
    assert env.state[0].observation.farms[0]["hands"] == [[4, 4]]
    env.step([{}, {}])
    assert env.done and len(env.steps) == 4
    assert chi12.limits(observation(day=29))[2] == 22


def test_full_shed_sells_before_drop_without_delaying_harvest():
    obs = observation(day=4)
    plant(obs, (4, 4), "WHEAT", 4, watered_today=True, yield_units=6)
    obs["private"]["shed"]["MILK"] = 99
    chi12.STATES.clear()
    chi12.STATES[0] = dict(day=-1, tick=-1, layout={}, replans=0,
                          daily_plans=0, blocked_actions=0, storage_waits=0)
    action = chi12.agent(obs)
    assert action["farmer"] == ["HARVEST"]
    assert ["SELL", "MILK", 99] in action["market"]
    engine._apply_unit_action(obs["farms"][0], obs["private"], 0, action["farmer"], 10, 4, 24)
    obs["private"]["shed"]["MILK"] = 0  # Engine market phase of the previous tick.
    obs["hour"] = 1
    action = chi12.agent(obs)
    assert action["farmer"] == ["DROP"]
    assert ["SELL", "WHEAT", 6] in action["market"]


def test_final_route_and_sale_finish_at_hour_22():
    obs = observation(day=29, hour=20)
    plant(obs, (4, 4), "WHEAT", 2, yield_units=2)
    chi12.STATES.clear()
    action = chi12.agent(obs)
    assert action["farmer"] == ["WATER"]
    for hour, expected in [(21, "HARVEST"), (22, "DROP")]:
        engine._apply_unit_action(obs["farms"][0], obs["private"], 0, action["farmer"], 10, 29, 24)
        obs["hour"] = hour
        action = chi12.agent(obs)
        assert action["farmer"] == [expected]
    assert ["SELL", "WHEAT", 3] in action["market"]
    assert all(s["hour"] <= 22 for r in chi12.STATES[0]["plan"]["routes"].values() for s in r["steps"])


def test_local_replan_retains_valid_routes_and_paid_workers():
    obs = observation(day=2)
    obs["farms"][0]["hands"] = [[3, 4]]
    obs["farms"][0]["hires_today"] = 1
    obs["private"]["inventories"].append({})
    plant(obs, (4, 4), "WHEAT", 1)
    plant(obs, (3, 4), "CARROT", 1)
    tasks = chi12.generate_tasks(obs, {})
    routes = {i: chi12.compile_route(obs, [tasks[i]], tasks[i]["position"], 0) for i in range(2)}
    kept = {1: routes[1]}
    replanned = chi12.build_plan(obs, {}, kept=kept)
    assert replanned["routes"][1] is kept[1]
    assert not any(order == ["HIRE"] for orders in replanned["market"].values() for order in orders)


def test_simultaneous_returns_reserve_shed_space_before_final_tick():
    obs = observation(day=29)
    other = dict(cargo=Counter(WHEAT=60), steps=[dict(hour=21, action=["DROP"])])
    route = dict(cargo=Counter(CARROT=50), steps=[dict(hour=20, action=["HARVEST"]),
                                               dict(hour=21, action=["DROP"])], finish=22, cost=2)
    protected = chi12.protect_storage(obs, route, {0: other}, {})
    assert protected["steps"][0]["hour"] == 20  # Harvest stays where planned.
    assert protected["steps"][-1]["hour"] == 22
    assert protected["cost"] == 3
    other["steps"][0]["hour"] = 22
    assert chi12.protect_storage(obs, protected, {0: other}, {}) is None


def test_critical_harvest_can_drop_optional_care_to_meet_deadline():
    obs = observation(day=4, hour=21)
    animal(obs, (4, 4), "GOOSE", yield_units=4, fed_today=True,
           fertilizer_available=True)
    obs["farms"][0]["money"] = 0
    plan = chi12.build_plan(obs, {})
    assert plan["routes"][0]["steps"][0]["action"] == ["HARVEST"]
    assert plan["routes"][0]["finish"] <= 24


@pytest.mark.parametrize("failed_op", ["HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT"])
def test_failed_market_order_triggers_local_repair(failed_op):
    chi12.STATES.clear()
    env = make("kaggriculture", configuration={"seed": 0}, debug=True)
    obs = env.state[0].observation
    action = chi12.agent(obs)
    action["market"] = [order for order in action["market"] if order[0] != failed_op]
    env.step([action, {}])
    obs = env.state[0].observation
    paid = len(obs.farms[0]["hands"])
    chi12.agent(obs)
    assert chi12.STATES[0]["replans"] == 1
    assert len(obs.farms[0]["hands"]) == paid


def test_unexpected_weed_and_changed_yield_invalidate_only_affected_route():
    obs = observation(day=4)
    plant(obs, (2, 4), "WHEAT", 4, watered_today=True, yield_units=4)
    plant(obs, (4, 2), "CARROT", 3, watered_today=True, yield_units=3)
    tasks = chi12.generate_tasks(obs, {})
    routes = {i: chi12.compile_route(obs, [task], (4, 4), 0) for i, task in enumerate(tasks)}
    pos = routes[0]["tasks"][0]["position"]
    obs["farms"][0]["tiles"][pos[1]][pos[0]]["yield_units"] += 1
    assert chi12.changed_routes(obs, {"routes": routes}) == {0}
    obs["farms"][0]["tiles"][pos[1]][pos[0]] = {"kind": "WEED"}
    assert chi12.changed_routes(obs, {"routes": routes}) == {0}


def test_full_episode_has_valid_actions_no_overflow_and_final_liquidation():
    before = deepcopy((chi3.CROP_STATE, chi3.ANIMAL_STATE))
    chi12.STATES.clear()
    violations = []

    def audited(obs, config):
        action = chi12.agent(obs, config)
        assert len(action["market"]) <= 10
        own, private = deepcopy(obs["farms"][obs["player"]]), deepcopy(obs["private"])
        for worker, command in enumerate([action["farmer"], *action["hands"]]):
            if command[0] == "DROP":
                assert sum(private["shed"].values()) + sum(private["inventories"][worker].values()) <= 100
            if command[0] != "PASS":
                previous = deepcopy((own, private))
                engine._apply_unit_action(own, private, worker, command, 10, obs["day"], 24)
                if (own, private) == previous:
                    violations.append((obs["day"], obs["hour"], command))
        if obs["hour"] == 23:
            assert all(tile.get("watered_today") for row in own["tiles"] for tile in row
                       if isinstance(tile, dict) and tile.get("kind") == "PLANT"
                       and tile["planted_day"] == obs["day"])
        return action

    env = make("kaggriculture", configuration={"seed": 0}, debug=True)
    env.run([audited, "pass"])
    assert all(state.status == "DONE" for state in env.steps[-1])
    assert not violations
    private = env.steps[-1][0].observation.private
    assert not any(private["shed"].get(item, 0) for item in chi12.PRODUCTS)
    assert not any(sum(inv.values()) for inv in private["inventories"])
    assert (chi3.CROP_STATE, chi3.ANIMAL_STATE) == before
    assert chi12.STATES[0]["daily_plans"] == 30
    assert chi12.STATES[0]["replans"] < 10
