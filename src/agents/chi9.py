CROP_STATE = {
    (0, 0): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (1, 0): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (2, 0): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (3, 0): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (4, 0): {"crop": "STRAWBERRY", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (0, 1): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (1, 1): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (2, 1): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (3, 1): {"crop": "MELON", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (4, 1): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (0, 2): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (1, 2): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (2, 2): {"crop": "TOMATO", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (3, 2): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (4, 2): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (0, 3): {"crop": "WHEAT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (1, 3): {"crop": "MELON", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (2, 3): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (0, 4): {"crop": "STRAWBERRY", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (1, 4): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
    (2, 4): {"crop": "CARROT", "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None},
}

ANIMAL_STATE = {
    (3, 3): {"animal": "GOOSE", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0, "consecutive_unfed": 0, "will_be_empty": False, "next_prod": None},
    (4, 3): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0, "consecutive_unfed": 0, "will_be_empty": False, "next_prod": None},
    (3, 4): {"animal": "SHEEP", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0, "consecutive_unfed": 0, "will_be_empty": False, "next_prod": None},
    (4, 4): {"animal": "COW", "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0, "consecutive_unfed": 0, "will_be_empty": False, "next_prod": None},
}

NEW_PRODUCTION_STATE = {}

ANIMAL_MAX_HELD = {"GOOSE": 4, "COW": 6, "SHEEP": 6}
LAND_COSTS = {1: 1000, 2: 2000, 3: 4000}
MAX_MARKET_ORDERS = 10
SALE_DAY = 5
SALE_HOUR = 23
FINAL_DROP_HOUR = 20
LAND_BUY_DAY = 6
LAST_4000_LAND_BUY_DAY = 19
DAILY_SALE_START_DAY = 6
DAILY_SALE_PRODUCTS = ["CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]
LAST_SELL_DAY = 29
LAST_HARVEST_DAY = LAST_SELL_DAY - 1
HIRE_COSTS = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368]
PRODUCTION_COSTS = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80, "GOOSE": 300, "COW": 400, "SHEEP": 500}
EFFECTIVE_SPACE = {"WHEAT": 1, "CARROT": 1, "TOMATO": 1, "STRAWBERRY": 1, "MELON": 1, "GOOSE": 5 / 3, "COW": 5 / 3, "SHEEP": 5 / 3}
CROP_EXPECTED_YIELD = {"WHEAT": 4, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}
DAILY_YIELD = {"WHEAT": 0.80, "CARROT": 0.75, "TOMATO": 0.33, "STRAWBERRY": 0.24, "MELON": 0.55, "EGG": 1.00, "MILK": 0.50, "WOOL": 0.33, "FERTILIZER": 1.00}
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
ANIMAL_PRODUCTION = {"GOOSE": {"first_yield_age": 4, "interval": 1}, "COW": {"first_yield_age": 8, "interval": 2}, "SHEEP": {"first_yield_age": 6, "interval": 3}}

MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

TURNS_PER_DAY = 24
TOWN_SHOP_SELL_INTERVAL = 4
TOWN_CENTER_SELL_INTERVAL = 24

SHOP_DEMAND = {
    "BAKERY": {"EGG": 1, "WHEAT": 1},
    "PIZZA_SHOP": {"MILK": 1, "TOMATO": 1, "WHEAT": 1},
    "BRUNCH_SPOT": {"EGG": 1, "WHEAT": 1, "STRAWBERRY": 1},
    "YARN_STORE": {"WOOL": 2},
    "ICE_CREAM_SHOP": {"STRAWBERRY": 1, "MILK": 1, "WHEAT": 1},
    "PET_CAFE": {"CARROT": 2},
    "SMOOTHIE_SHOP": {"STRAWBERRY": 1, "MILK": 1},
    "FARMERS_MARKET": {"WHEAT": 1, "CARROT": 1, "TOMATO": 1, "STRAWBERRY": 1},
}

def market_shape(name, x, T):
    if name == "linear":
        return x
    if name == "sq":
        return x * x
    if name == "sqrt":
        return x ** 0.5
    if name == "log":
        import math
        return math.log1p(x)
    if name == "log10":
        import math
        return math.log10(1 + x)
    if name == "hinge":
        u = x / T
        return u + 8 * max(0, u - 1) ** 2
    return x

def count_consumption_ticks(start_step, turns_ahead, interval):
    if turns_ahead <= 0:
        return 0
    first_step = start_step if start_step % interval == 0 else start_step + interval - start_step % interval
    end_step = start_step + turns_ahead
    if first_step >= end_step:
        return 0
    return 1 + (end_step - 1 - first_step) // interval

def get_future_consumption(obs, days_ahead=1):
    import math
    start_step = obs.get("step", obs.get("day", 0) * TURNS_PER_DAY + obs.get("hour", 0))
    turns_ahead = max(0, math.ceil(days_ahead * TURNS_PER_DAY))
    shop_ticks = count_consumption_ticks(start_step, turns_ahead, TOWN_SHOP_SELL_INTERVAL)
    center_ticks = count_consumption_ticks(start_step, turns_ahead, TOWN_CENTER_SELL_INTERVAL)
    consumption = {product: center_ticks for product in MARKET_PARAMS if product != "FERTILIZER"}
    for shop in obs.get("town", {}).get("unlocked_shops", []):
        for product, amount in SHOP_DEMAND.get(shop, {}).items():
            consumption[product] = consumption.get(product, 0) + amount * shop_ticks
    return consumption

def get_expected_market_price(obs, product, own_supply=0, opponent_supply=0, future_consumption=0):
    params = MARKET_PARAMS[product]
    inventory = obs["market"]["inventory"].get(product, params["I0"]) + own_supply + opponent_supply - future_consumption
    delta = inventory - params["I0"]
    if delta == 0:
        return params["base"]
    side = "below" if delta < 0 else "above"
    x = abs(delta)
    func = params[f"{side}_func"]
    target = params[f"{side}_target"]
    f_t = market_shape(func, params["T"], params["T"])
    amp = target * params["base"] / f_t
    move = amp * market_shape(func, x, params["T"])
    price = params["base"] + move if delta < 0 else params["base"] - move
    return max(1, round(price))

def get_expected_production_profit(obs, production, opponent_supply=None, days_ahead=1):
    opponent_supply = opponent_supply or {}
    consumption = get_future_consumption(obs, days_ahead)
    profit = 0
    prices = {}
    for product, units in production.items():
        if units <= 0 or product not in MARKET_PARAMS:
            continue
        price = get_expected_market_price(obs, product, units, opponent_supply.get(product, 0), consumption.get(product, 0))
        prices[product] = price
        profit += units * price
    return profit, prices

def make_crop_state(crop):
    return {"crop": crop, "planted": False, "harvest": False, "will_be_empty": False, "next_prod": None}

def make_animal_state(animal):
    return {"animal": animal, "placed": False, "harvest": False, "fertilizer": False, "pending_care_bonus": 0, "consecutive_unfed": 0, "will_be_empty": False, "next_prod": None}

def nearest_shed_tile(pos):
    return min(SHED_TILES, key=lambda tile: (distance(pos, tile), tile[1], tile[0]))

def distance_to_shed(pos):
    return min(distance(pos, tile) for tile in SHED_TILES)

def distance_to_center(pos):
    return min(abs(pos[0] - x) + abs(pos[1] - y) for x, y in SHED_TILES)

def sync_production_tiles(obs):
    farm = obs["farms"][obs["player"]]
    tiles = farm["tiles"]
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            pos = (x, y)
            if tile == "LOCKED":
                NEW_PRODUCTION_STATE.pop(pos, None)
                continue
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop = tile["crop"]
                if pos not in CROP_STATE or CROP_STATE[pos].get("crop") != crop:
                    CROP_STATE[pos] = make_crop_state(crop)
                ANIMAL_STATE.pop(pos, None)
                NEW_PRODUCTION_STATE.pop(pos, None)
                continue
            if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE") and tile.get("animal"):
                animal = tile["animal"]
                if pos not in ANIMAL_STATE or ANIMAL_STATE[pos].get("animal") != animal:
                    ANIMAL_STATE[pos] = make_animal_state(animal)
                CROP_STATE.pop(pos, None)
                NEW_PRODUCTION_STATE.pop(pos, None)
                continue
            if pos in CROP_STATE or pos in ANIMAL_STATE:
                continue
            if tile is None or (isinstance(tile, dict) and tile.get("kind") == "WEED") or (isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE") and not tile.get("animal")):
                NEW_PRODUCTION_STATE.setdefault(pos, {"next_prod": None})
            else:
                NEW_PRODUCTION_STATE.pop(pos, None)

def get_install_candidates(obs, pos):
    tile = obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]]
    if tile == "LOCKED":
        return []
    if tile is None or isinstance(tile, dict) and tile.get("kind") == "WEED":
        return list(CROP_PRODUCTION) + list(ANIMAL_PRODUCTION)
    if isinstance(tile, dict) and tile.get("kind") == "COOP" and not tile.get("animal"):
        return ["GOOSE"]
    if isinstance(tile, dict) and tile.get("kind") == "PASTURE" and not tile.get("animal"):
        return ["COW", "SHEEP"]
    return []

def get_planned_dynamic_supply(days_ahead):
    supply = {}
    for data in NEW_PRODUCTION_STATE.values():
        prod = data.get("next_prod")
        if not prod:
            continue
        production = get_candidate_production(prod, CURRENT_DAY)
        occupation = max(1, get_candidate_occupation_time(prod, CURRENT_DAY))
        ratio = min(1, days_ahead / occupation)
        for product, units in production.items():
            supply[product] = supply.get(product, 0) + units * ratio
    return supply

def get_base_daily_action_count():
    total = 0
    for pos, data in CROP_STATE.items():
        if data.get("weed", False):
            total += 1
        elif data.get("planted", False) and crop_has_future_sale(pos):
            total += int(crop_needs_water(pos)) + int(data.get("harvest", False))
    for pos, data in ANIMAL_STATE.items():
        if not data.get("placed", False):
            continue
        total += int(data.get("harvest", False)) + int(data.get("fertilizer", False))
        if animal_needs_feed_for_final_sale(pos):
            total += 1 + int(animal_needs_care(pos))
    return total

def get_hire_count_for_actions(action_count):
    if action_count <= FARMER_CAPACITY:
        return 0
    remaining = action_count - FARMER_CAPACITY
    return min(len(HIRE_COSTS), (remaining + HAND_CAPACITY - 1) // HAND_CAPACITY)

def get_labor_cost_for_actions(action_count):
    return sum(HIRE_COSTS[:get_hire_count_for_actions(action_count)])

def get_candidate_install_actions(obs, prod, pos):
    tile = obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]]
    weed = isinstance(tile, dict) and tile.get("kind") == "WEED"
    if prod in CROP_PRODUCTION:
        return int(weed) + 2
    kind = "COOP" if prod == "GOOSE" else "PASTURE"
    build = not isinstance(tile, dict) or tile.get("kind") != kind
    return int(weed) + 3 + int(build)

def get_remaining_crop_harvests(prod, day=None):
    day = CURRENT_DAY if day is None else day
    return [age for age in CROP_PRODUCTION[prod]["harvest_ages"] if day + age <= LAST_HARVEST_DAY]

def get_animal_production_days(prod, day=None):
    day = CURRENT_DAY if day is None else day
    spec = ANIMAL_PRODUCTION[prod]
    first = day + spec["first_yield_age"]
    if first > LAST_HARVEST_DAY:
        return []
    days = []
    d = first
    while d <= LAST_HARVEST_DAY:
        days.append(d)
        d += spec["interval"]
    return days

def get_animal_expected_product_units(prod, day=None):
    """Conservative CARE-aware production estimate for a newly installed animal.

    Daily FEED+CARE is already planned by this agent. The first production can bank
    care over the setup interval; later productions bank over the production interval.
    Each event is capped by max_held.
    """
    days = get_animal_production_days(prod, day)
    if not days:
        return 0
    spec = ANIMAL_PRODUCTION[prod]
    cap = ANIMAL_MAX_HELD[prod]
    units = 0
    for i, _ in enumerate(days):
        bank_days = spec["first_yield_age"] if i == 0 else spec["interval"]
        units += min(cap, 1 + bank_days)
    return units

def get_candidate_occupation_time(prod, day=None):
    day = CURRENT_DAY if day is None else day
    if prod in CROP_PRODUCTION:
        harvests = get_remaining_crop_harvests(prod, day)
        return harvests[-1] if harvests else 0
    days = get_animal_production_days(prod, day)
    return days[-1] - day + 1 if days else 0

def get_candidate_production(prod, day=None):
    day = CURRENT_DAY if day is None else day
    if prod in CROP_PRODUCTION:
        harvests = get_remaining_crop_harvests(prod, day)
        if not harvests:
            return {}
        if CROP_PRODUCTION[prod]["type"] == "ONE_TIME":
            return {prod: CROP_EXPECTED_YIELD[prod]}
        return {prod: len(harvests)}
    days = get_animal_production_days(prod, day)
    if not days:
        return {}
    useful_days = days[-1] - day + 1
    return {ANIMAL_PRODUCT[prod]: get_animal_expected_product_units(prod, day), "FERTILIZER": useful_days}

def get_existing_animal_production_days(pos, day=None, horizon_day=None):
    day = CURRENT_DAY if day is None else day
    horizon_day = LAST_HARVEST_DAY if horizon_day is None else min(horizon_day, LAST_HARVEST_DAY)
    data = ANIMAL_STATE[pos]
    if not data.get("placed", False):
        return []
    next_day = get_next_animal_production_day(pos, day)
    interval = ANIMAL_PRODUCTION[data["animal"]]["interval"]
    days = []
    while next_day <= horizon_day:
        days.append(next_day)
        next_day += interval
    return days

def get_existing_animal_feed_days(pos, day=None, horizon_day=None):
    day = CURRENT_DAY if day is None else day
    days = get_existing_animal_production_days(pos, day, horizon_day)
    return days[-1] - day + 1 if days else 0

def get_expected_farm_supply(days_ahead):
    horizon_day = min(LAST_HARVEST_DAY, CURRENT_DAY + max(0, int(days_ahead)))
    supply = {}
    for data in CROP_STATE.values():
        if not data.get("planted", False):
            prod = data.get("next_prod")
            if prod in CROP_PRODUCTION:
                for product, units in get_candidate_production(prod, CURRENT_DAY).items():
                    occupation = max(1, get_candidate_occupation_time(prod, CURRENT_DAY))
                    ratio = min(1, max(0, days_ahead) / occupation)
                    supply[product] = supply.get(product, 0) + units * ratio
            continue
        crop = data["crop"]
        planted_day = data.get("planted_day")
        if planted_day is None:
            continue
        spec = CROP_PRODUCTION[crop]
        if spec["type"] == "ONE_TIME":
            harvest_day = planted_day + spec["harvest_ages"][0]
            if CURRENT_DAY <= harvest_day <= horizon_day:
                supply[crop] = supply.get(crop, 0) + CROP_EXPECTED_YIELD[crop]
        else:
            for age in spec["harvest_ages"]:
                event_day = planted_day + age
                if CURRENT_DAY <= event_day <= horizon_day:
                    supply[crop] = supply.get(crop, 0) + 1
    for pos, data in ANIMAL_STATE.items():
        if not data.get("placed", False):
            prod = data.get("next_prod")
            if prod in ANIMAL_PRODUCTION:
                production = get_candidate_production(prod, CURRENT_DAY)
                occupation = max(1, get_candidate_occupation_time(prod, CURRENT_DAY))
                ratio = min(1, max(0, days_ahead) / occupation)
                for product, units in production.items():
                    supply[product] = supply.get(product, 0) + units * ratio
            continue
        animal = data["animal"]
        days = get_existing_animal_production_days(pos, CURRENT_DAY, horizon_day)
        if days:
            spec = ANIMAL_PRODUCTION[animal]
            cap = ANIMAL_MAX_HELD[animal]
            # Existing animals may already have a care bank; approximate each future event
            # with interval-sized daily CARE, capped by max_held.
            units = sum(min(cap, 1 + spec["interval"]) for _ in days)
            product = ANIMAL_PRODUCT[animal]
            supply[product] = supply.get(product, 0) + units
            useful_days = days[-1] - CURRENT_DAY + 1
            supply["FERTILIZER"] = supply.get("FERTILIZER", 0) + useful_days
    for product, units in get_planned_dynamic_supply(days_ahead).items():
        supply[product] = supply.get(product, 0) + units
    return supply

def get_marginal_expected_revenue(obs, candidate_production, occupation_time):
    base_supply = get_expected_farm_supply(occupation_time)
    consumption = get_future_consumption(obs, occupation_time)
    revenue = 0
    for product, added_units in candidate_production.items():
        base_units = base_supply.get(product, 0)
        before_price = get_expected_market_price(obs, product, base_units, 0, consumption.get(product, 0))
        after_price = get_expected_market_price(obs, product, base_units + added_units, 0, consumption.get(product, 0))
        revenue += (base_units + added_units) * after_price - base_units * before_price
    return revenue

def calculate_production_marginal_profit(obs, prod, pos):
    day = obs.get("day", 0)
    if prod in CROP_PRODUCTION and not can_plant_for_final_sale(day, prod):
        return float("-inf")
    if prod in ANIMAL_PRODUCTION and not animal_can_start_for_final_sale(prod, day):
        return float("-inf")
    occupation_time = get_candidate_occupation_time(prod, day)
    candidate_production = get_candidate_production(prod, day)
    if not candidate_production or occupation_time <= 0:
        return float("-inf")
    expected_revenue = get_marginal_expected_revenue(obs, candidate_production, occupation_time)
    production_cost = PRODUCTION_COSTS[prod]
    base_actions = get_base_daily_action_count()
    install_actions = get_candidate_install_actions(obs, prod, pos)
    labor_cost = get_labor_cost_for_actions(base_actions + install_actions) - get_labor_cost_for_actions(base_actions)
    return expected_revenue - production_cost - labor_cost

def calculate_production_score(obs, prod, pos):
    marginal_profit = calculate_production_marginal_profit(obs, prod, pos)
    if marginal_profit == float("-inf"):
        return marginal_profit
    occupation_time = get_candidate_occupation_time(prod, obs.get("day", 0))
    return marginal_profit / (EFFECTIVE_SPACE[prod] * occupation_time)

def choose_best_production(obs, pos, valid):
    if not valid:
        return None
    scores = [(calculate_production_score(obs, prod, pos), prod) for prod in valid]
    score, prod = max(scores)
    return prod if score > 0 else None

def get_existing_feed_units():
    return sum(
        get_existing_animal_feed_days(pos)
        for pos, data in ANIMAL_STATE.items()
        if data.get("placed", False) and animal_needs_feed_for_final_sale(pos)
    )

def get_budget_candidate_cost(obs, prod, feed_units, wheat_available):
    cost = PRODUCTION_COSTS[prod]
    next_feed_units = feed_units
    if prod in ANIMAL_PRODUCTION:
        days = get_animal_production_days(prod, obs.get("day", 0))
        if days:
            next_feed_units += days[-1] - obs.get("day", 0) + 1
    wheat_price = obs.get("market", {}).get("prices", {}).get("WHEAT", MARKET_PARAMS["WHEAT"]["base"])
    old_feed_cost = max(0, feed_units - wheat_available) * wheat_price
    new_feed_cost = max(0, next_feed_units - wheat_available) * wheat_price
    return cost + new_feed_cost - old_feed_cost, next_feed_units

def choose_budgeted_production(obs, pos, valid, reserved_cost, feed_units, wheat_available, available_money):
    affordable = []
    costs = {}
    next_feeds = {}
    for prod in valid:
        cost, next_feed = get_budget_candidate_cost(obs, prod, feed_units, wheat_available)
        if reserved_cost + cost <= available_money:
            affordable.append(prod)
            costs[prod] = cost
            next_feeds[prod] = next_feed
    prod = choose_best_production(obs, pos, affordable)
    if prod is None:
        return None, 0, feed_units
    return prod, costs[prod], next_feeds[prod]

def choose_next_productions(obs):
    farm = obs["farms"][obs["player"]]
    available_money = farm.get("money", 0)
    wheat_available = obs.get("private", {}).get("shed", {}).get("WHEAT", 0)
    feed_units = get_existing_feed_units()
    wheat_price = obs.get("market", {}).get("prices", {}).get("WHEAT", MARKET_PARAMS["WHEAT"]["base"])
    reserved_cost = max(0, feed_units - wheat_available) * wheat_price
    for data in CROP_STATE.values():
        data["next_prod"] = None
    for data in ANIMAL_STATE.values():
        data["next_prod"] = None
    for data in NEW_PRODUCTION_STATE.values():
        data["next_prod"] = None
    positions = set(CROP_STATE) | set(ANIMAL_STATE) | set(NEW_PRODUCTION_STATE)
    for pos in sorted(positions, key=lambda p: (distance_to_center(p), p[1], p[0])):
        tile = farm["tiles"][pos[1]][pos[0]]
        if tile == "LOCKED" or reserved_cost >= available_money:
            continue
        prod = None
        cost = 0
        next_feed = feed_units
        if pos in CROP_STATE:
            data = CROP_STATE[pos]
            if not (data.get("will_be_empty", False) or data.get("weed", False) or not data.get("planted", False)):
                continue
            valid = [crop for crop in CROP_PRODUCTION if can_plant_for_final_sale(CURRENT_DAY, crop)]
            prod, cost, next_feed = choose_budgeted_production(obs, pos, valid, reserved_cost, feed_units, wheat_available, available_money)
            data["next_prod"] = prod
        elif pos in ANIMAL_STATE:
            data = ANIMAL_STATE[pos]
            if data.get("placed", False):
                continue
            if isinstance(tile, dict) and tile.get("kind") == "COOP":
                valid = ["GOOSE"]
            elif isinstance(tile, dict) and tile.get("kind") == "PASTURE":
                valid = ["COW", "SHEEP"]
            else:
                valid = list(ANIMAL_PRODUCTION)
            valid = [animal for animal in valid if animal_can_start_for_final_sale(animal, CURRENT_DAY)]
            prod, cost, next_feed = choose_budgeted_production(obs, pos, valid, reserved_cost, feed_units, wheat_available, available_money)
            data["next_prod"] = prod
        else:
            valid = []
            for candidate in get_install_candidates(obs, pos):
                if candidate in CROP_PRODUCTION and can_plant_for_final_sale(CURRENT_DAY, candidate):
                    valid.append(candidate)
                elif candidate in ANIMAL_PRODUCTION and animal_can_start_for_final_sale(candidate, CURRENT_DAY):
                    valid.append(candidate)
            prod, cost, next_feed = choose_budgeted_production(obs, pos, valid, reserved_cost, feed_units, wheat_available, available_money)
            NEW_PRODUCTION_STATE[pos]["next_prod"] = prod
        if prod is not None:
            reserved_cost += cost
            feed_units = next_feed
    return reserved_cost, feed_units, wheat_available

def get_task_expected_production(task):
    kind = task[0]
    if kind == "INSTALL":
        prod = NEW_PRODUCTION_STATE.get(task[1], {}).get("next_prod")
        return get_candidate_production(prod, CURRENT_DAY) if prod else {}
    if kind == "CROP_WATER":
        return {}
    if kind in ("CROP", "WHEAT_SUPPLY"):
        crop = "WHEAT" if kind == "WHEAT_SUPPLY" else CROP_STATE[task[1]]["crop"]
        return {crop: DAILY_YIELD.get(crop, 0)}
    if kind in ("ANIMAL", "ANIMAL_PRE", "ANIMAL_FEED"):
        data = ANIMAL_STATE[task[1]]
        animal = data["animal"] if data.get("placed", False) else data.get("next_prod") or data["animal"]
        product = ANIMAL_PRODUCT[animal]
        return {product: DAILY_YIELD[product], "FERTILIZER": DAILY_YIELD["FERTILIZER"]}
    return {}

def get_task_expected_value(obs, task):
    production = get_task_expected_production(task)
    if not production:
        return 0
    profit, _ = get_expected_production_profit(obs, production)
    return profit

def get_task_profitability(obs, task):
    return get_task_expected_value(obs, task) / max(1, task_action_cost(task))

def get_routes_expected_production(routes):
    production = {}
    counted = set()
    for route in routes.values():
        for task in route:
            if task[0] in ("WAIT_WHEAT", "SHED_DROP", "WEED", "CROP_WATER"):
                continue
            key = (task[1], "ANIMAL" if task[0] in ("ANIMAL", "ANIMAL_PRE", "ANIMAL_FEED") else task[0])
            if key in counted:
                continue
            counted.add(key)
            for product, units in get_task_expected_production(task).items():
                production[product] = production.get(product, 0) + units
    return production

def get_routes_expected_profit(obs, routes):
    production = get_routes_expected_production(routes)
    profit, _ = get_expected_production_profit(obs, production)
    return profit

CROP_PRODUCTION = {
    "WHEAT": {"type": "ONE_TIME", "harvest_ages": [4], "bonus_start_age": 2},
    "CARROT": {"type": "ONE_TIME", "harvest_ages": [3], "bonus_start_age": 2},
    "TOMATO": {"type": "ONGOING", "harvest_ages": [8, 9, 10, 11]},
    "STRAWBERRY": {"type": "ONGOING", "harvest_ages": [10, 12, 14, 16]},
    "MELON": {"type": "ONE_TIME", "harvest_ages": [10], "bonus_start_age": 6},
}

def can_plant_for_final_sale(day, crop):
    return day + CROP_PRODUCTION[crop]["harvest_ages"][0] <= LAST_HARVEST_DAY

def crop_has_future_sale(pos):
    data = CROP_STATE[pos]
    if data.get("harvest", False):
        return True
    if not data.get("planted", False):
        return can_plant_for_final_sale(CURRENT_DAY, data["crop"])
    planted_day = data.get("planted_day", CURRENT_DAY)
    age = data.get("age", CURRENT_DAY - planted_day)
    production = CROP_PRODUCTION[data["crop"]]
    if production["type"] == "ONE_TIME":
        return planted_day + production["harvest_ages"][0] <= LAST_HARVEST_DAY
    return any(harvest_age >= age and planted_day + harvest_age <= LAST_HARVEST_DAY for harvest_age in production["harvest_ages"])

def get_next_animal_production_day(pos, day=None):
    day = CURRENT_DAY if day is None else day
    data = ANIMAL_STATE[pos]
    animal = data["animal"]
    production = ANIMAL_PRODUCTION[animal]
    if not data.get("placed", False):
        return day + production["first_yield_age"]
    placed_day = data.get("placed_day")
    if placed_day is None:
        return day + production["first_yield_age"]
    first_day = placed_day + production["first_yield_age"]
    if day <= first_day:
        return first_day
    interval = production["interval"]
    steps = (day - first_day + interval - 1) // interval
    return first_day + steps * interval

def animal_can_start_for_final_sale(animal, day=None):
    day = CURRENT_DAY if day is None else day
    return day + ANIMAL_PRODUCTION[animal]["first_yield_age"] <= LAST_HARVEST_DAY

def animal_has_future_sale(pos):
    data = ANIMAL_STATE[pos]
    if data.get("harvest", False):
        return True
    return get_next_animal_production_day(pos) <= LAST_HARVEST_DAY

def animal_needs_feed_for_final_sale(pos):
    data = ANIMAL_STATE[pos]
    if not data.get("placed", False):
        return False
    next_day = get_next_animal_production_day(pos)
    if data.get("harvest", False) and next_day <= CURRENT_DAY:
        next_day += ANIMAL_PRODUCTION[data["animal"]]["interval"]
    return next_day <= LAST_HARVEST_DAY

def get_active_feed_positions():
    return [pos for pos in ANIMAL_STATE if animal_needs_daily_feed(pos)]

DAY_1_MARKET = {
    0: [
        ["BUY_SEED", "CARROT", 6], ["BUY_SEED", "STRAWBERRY", 2], ["BUY_ANIMAL", "GOOSE", 1],
        ["BUY_ANIMAL", "COW", 2], ["BUY_ANIMAL", "SHEEP", 1], ["BUY_PRODUCT", "WHEAT", 16],
        ["HIRE"], ["HIRE"], ["HIRE"], ["HIRE"],
    ],
    1: [["BUY_SEED", "TOMATO", 1], ["BUY_SEED", "MELON", 2], ["BUY_SEED", "WHEAT", 10]],
}

FARMER_SETUP = [["BUILD_PASTURE"], ["PICKUP", "COW", 2], ["PICKUP", "GOOSE", 1], ["PICKUP", "SHEEP", 1], ["PICKUP", "WHEAT", 4]]

DAY_1_PATHS = {
    0: [["WEST"], ["NORTH"], ["EAST"]],
    1: [["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["SOUTH"]],
    2: [["NORTH"], ["WEST"], ["WEST"], ["WEST"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["NORTH"]],
    3: [["WEST"], ["NORTH"], ["WEST"], ["NORTH"], ["NORTH"], ["NORTH"], ["WEST"], ["SOUTH"], ["WEST"], ["SOUTH"]],
    4: [["NORTH"], ["WEST"], ["WEST"]],
}

HAND_SPAWNS_DAY0 = [(5, 4), (4, 5), (5, 5), (4, 4)]
HAND_SPAWNS = [(4, 4), (5, 4), (4, 5), (5, 5)]
FARMER_CAPACITY = 24
HAND_CAPACITY = 23
CENTER = (4, 4)
SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
WORKER_ROUTES = {}
WORKER_STATE = {}
CURRENT_DAY = -1
HIRE_COUNT = 4
WORKER_HIRE_TICKS = {}
ROUTES_REBUILT_DAY = -1
REAL_WORKER_STARTS = {}
EXPANSION_ACTIVE = False
CURRENT_OBS = None
LAND_BUY_PLANNED = False
PENDING_MARKET_ORDERS = []

SALE_BATCH_LIMIT = {
    "CARROT": 10, "TOMATO": 8, "STRAWBERRY": 6, "MELON": 3,
    "EGG": 10, "MILK": 6, "WOOL": 5, "FERTILIZER": 6,
}

def get_sale_batch(product, quantity):
    return min(quantity, SALE_BATCH_LIMIT.get(product, quantity))

def get_sale_orders(obs):
    shed = obs["private"]["shed"]
    products = ["FERTILIZER"]
    if obs.get("day", 0) == SALE_DAY and obs.get("hour", 0) == SALE_HOUR:
        products += ["CARROT", "EGG", "WOOL"]
    return [["SELL", product, get_sale_batch(product, shed.get(product, 0))] for product in products if shed.get(product, 0) > 0]

def get_daily_harvest_sale_orders(obs):
    if obs.get("day", 0) < DAILY_SALE_START_DAY:
        return []
    shed = obs["private"]["shed"]
    return [["SELL", product, get_sale_batch(product, shed.get(product, 0))] for product in DAILY_SALE_PRODUCTS if shed.get(product, 0) > 0]

def get_final_liquidation_orders(obs):
    if obs.get("day", 0) != LAST_SELL_DAY or obs.get("hour", 0) < 22:
        return []
    shed = obs["private"]["shed"]
    return [["SELL", product, shed.get(product, 0)] for product in MARKET_PARAMS if shed.get(product, 0) > 0]

def get_next_land_cost(obs):
    unlocked = obs["farms"][obs["player"]].get("unlocked_quadrants", ["NW"])
    return LAND_COSTS.get(len(unlocked))

def get_next_quadrant(obs):
    unlocked = set(obs["farms"][obs["player"]].get("unlocked_quadrants", ["NW"]))
    for quadrant in ("NE", "SW", "SE"):
        if quadrant not in unlocked:
            return quadrant
    return None

def get_quadrant_positions(quadrant):
    x0 = 0 if quadrant in ("NW", "SW") else 5
    y0 = 0 if quadrant in ("NW", "NE") else 5
    return [(x, y) for y in range(y0, y0 + 5) for x in range(x0, x0 + 5)]

def get_projected_land_obs(obs, quadrant):
    from copy import deepcopy
    projected = deepcopy(obs)
    farm = projected["farms"][projected["player"]]
    unlocked = list(farm.get("unlocked_quadrants", ["NW"]))
    if quadrant not in unlocked:
        unlocked.append(quadrant)
    farm["unlocked_quadrants"] = unlocked
    for x, y in get_quadrant_positions(quadrant):
        if farm["tiles"][y][x] == "LOCKED":
            farm["tiles"][y][x] = None
    return projected

def plan_land_before_pathing(obs, reserved_cost, feed_units, wheat_available):
    cost = get_next_land_cost(obs)
    quadrant = get_next_quadrant(obs)
    money = obs["farms"][obs["player"]].get("money", 0)
    if cost is None or quadrant is None or CURRENT_DAY < LAND_BUY_DAY or money <= cost + reserved_cost:
        return False
    if cost == 4000 and CURRENT_DAY > LAST_4000_LAND_BUY_DAY:
        return False
    projected = get_projected_land_obs(obs, quadrant)
    available_money = money - cost
    added = []
    candidate_profit = {}
    current_reserved = reserved_cost
    current_feed = feed_units
    valid_all = [prod for prod in list(CROP_PRODUCTION) + list(ANIMAL_PRODUCTION) if (prod in CROP_PRODUCTION and can_plant_for_final_sale(CURRENT_DAY, prod)) or (prod in ANIMAL_PRODUCTION and animal_can_start_for_final_sale(prod, CURRENT_DAY))]
    for pos in sorted(get_quadrant_positions(quadrant), key=lambda p: (distance_to_center(p), p[1], p[0])):
        if pos in CROP_STATE or pos in ANIMAL_STATE:
            continue
        if pos not in NEW_PRODUCTION_STATE:
            NEW_PRODUCTION_STATE[pos] = {"next_prod": None}
            added.append(pos)
        prod, budget_cost, next_feed = choose_budgeted_production(projected, pos, valid_all, current_reserved, current_feed, wheat_available, available_money)
        if prod is None:
            continue
        marginal_profit = calculate_production_marginal_profit(projected, prod, pos)
        feed_cost = max(0, budget_cost - PRODUCTION_COSTS[prod])
        adjusted_profit = marginal_profit - feed_cost
        if adjusted_profit <= 0:
            continue
        NEW_PRODUCTION_STATE[pos]["next_prod"] = prod
        candidate_profit[pos] = adjusted_profit
        current_reserved += budget_cost
        current_feed = next_feed
    if not candidate_profit:
        for pos in added:
            NEW_PRODUCTION_STATE.pop(pos, None)
        return False
    base_result = calculate_daily_paths(obs, optimize_extra_hires=False)
    if base_result is None:
        for pos in added:
            NEW_PRODUCTION_STATE.pop(pos, None)
        return False
    base_hires, _ = base_result
    result = calculate_daily_paths(projected, required_installs=set(candidate_profit), optimize_extra_hires=False)
    if result is None:
        for pos in added:
            NEW_PRODUCTION_STATE.pop(pos, None)
        return False
    hire_count, routes = result
    routed = {task[1] for route in routes.values() for task in route if task[0] == "INSTALL" and task[1] in candidate_profit}
    for pos in set(candidate_profit) - routed:
        NEW_PRODUCTION_STATE[pos]["next_prod"] = None
    if not routed:
        for pos in added:
            NEW_PRODUCTION_STATE.pop(pos, None)
        return False
    install_orders = get_install_market_orders_for_routes(projected, routes)
    install_orders = [order for order in install_orders if not (order[0] == "BUY_PRODUCT" and order[1] == "WHEAT")]
    wheat_orders = get_unified_wheat_order(projected, install_orders)
    production_cost = get_market_orders_cost(projected, install_orders + wheat_orders, 0)
    hire_cost = sum(HIRE_COSTS[:hire_count])
    required_cash = cost + production_cost + hire_cost
    extra_hire_cost = max(0, hire_cost - sum(HIRE_COSTS[:base_hires]))
    land_profit = sum(candidate_profit[pos] for pos in routed)
    affordable = money >= required_cash
    profitable = land_profit > cost + extra_hire_cost and land_profit >= 1.15 * cost
    if not affordable or not profitable:
        for pos in added:
            NEW_PRODUCTION_STATE.pop(pos, None)
        return False
    for pos in added:
        if pos not in routed:
            NEW_PRODUCTION_STATE.pop(pos, None)
    return True

def reset_worker_state(worker_count):
    global WORKER_STATE
    WORKER_STATE = {i: {"path": 0, "stack": [], "done": set(), "target": 0, "pickup_done": False, "pickup_pending": False, "animal_pickups": [], "animal_pickups_initialized": False, "active_task": False} for i in range(worker_count)}
    WORKER_STATE[0]["setup"] = 0

def get_worker_position(obs, worker_id):
    farm = obs["farms"][obs["player"]]
    if worker_id == 0:
        return farm["farmer"]
    if worker_id - 1 < len(farm["hands"]):
        return farm["hands"][worker_id - 1]
    return None

def get_worker_spawn(worker_id):
    if worker_id in REAL_WORKER_STARTS:
        return REAL_WORKER_STARTS[worker_id]
    if worker_id == 0:
        return CENTER
    spawns = HAND_SPAWNS_DAY0 if CURRENT_DAY == 0 else HAND_SPAWNS
    return spawns[(worker_id - 1) % len(spawns)]

def get_worker_capacity(worker_id):
    if worker_id == 0:
        return FARMER_CAPACITY
    hire_tick = WORKER_HIRE_TICKS.get(worker_id, 0)
    return max(0, TURNS_PER_DAY - (hire_tick + 1))

def get_path_action(plan, state):
    if state["path"] >= len(plan):
        return ["PASS"]
    action = plan[state["path"]]
    state["path"] += 1
    return action

def move_toward(current, target):
    x, y = current
    tx, ty = target
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return None

def update_crop_state(obs):
    day = obs.get("day", 0)
    farm = obs["farms"][obs["player"]]
    for pos, data in CROP_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        data["sale_early_harvest"] = False
        data["weed"] = data["crop"] in ("TOMATO", "STRAWBERRY") and isinstance(tile, dict) and tile.get("kind") == "WEED"
        if data["weed"]:
            data["planted"] = False
            data["harvest"] = False
            data["will_be_empty"] = EXPANSION_ACTIVE
            continue
        if not isinstance(tile, dict) or tile.get("kind") != "PLANT" or tile.get("crop") != data["crop"]:
            data["planted"] = False
            data["harvest"] = False
            data["will_be_empty"] = tile is None
            continue
        data["planted"] = True
        planted_day = tile["planted_day"]
        if data.get("planted_day") != planted_day:
            data["seed_ordered"] = False
        data["planted_day"] = planted_day
        data["watered_today"] = tile.get("watered_today", False)
        data["consecutive_unwatered"] = tile.get("consecutive_unwatered", 0)
        data["needs_water"] = not data["watered_today"] and data["consecutive_unwatered"] >= 1
        age = day - planted_day
        data["age"] = age
        production = CROP_PRODUCTION[data["crop"]]
        if production["type"] == "ONE_TIME":
            normal_harvest = age >= production["harvest_ages"][0]
            data["sale_early_harvest"] = False
            data["harvest"] = normal_harvest
            data["will_be_empty"] = data["harvest"]
        else:
            data["harvest"] = age in production["harvest_ages"] or tile.get("yield_units", 0) > 0
            data["will_be_empty"] = False

def crop_needs_survival_water(pos):
    data = CROP_STATE[pos]
    return data.get("planted", False) and not data.get("watered_today", False) and data.get("needs_water", False)

def crop_needs_harvest_water(pos):
    data = CROP_STATE[pos]
    return data.get("planted", False) and not data.get("watered_today", False) and data.get("harvest", False) and not data.get("needs_water", False)

def crop_needs_water(pos):
    data = CROP_STATE[pos]
    if crop_needs_survival_water(pos) or crop_needs_harvest_water(pos):
        return True
    if not data.get("planted", False) or data.get("watered_today", False):
        return False
    production = CROP_PRODUCTION[data["crop"]]
    if production["type"] != "ONE_TIME":
        return False
    age = data.get("age", 0)
    return production["bonus_start_age"] <= age <= production["harvest_ages"][0]

def get_crop_actions(pos):
    data = CROP_STATE[pos]
    crop = data["crop"]
    next_crop = data.get("next_prod") or crop
    if data.get("weed", False):
        if EXPANSION_ACTIVE and not data.get("next_prod"):
            return [["DIG"]]
        if not can_plant_for_final_sale(CURRENT_DAY, next_crop):
            return []
        data["pending_replant"] = next_crop
        data["crop"] = next_crop
        return [["DIG"], ["PLANT", next_crop], ["WATER"]]
    if not data["planted"]:
        if (EXPANSION_ACTIVE and not data.get("next_prod")) or not can_plant_for_final_sale(CURRENT_DAY, next_crop):
            return []
        data["pending_replant"] = next_crop
        data["crop"] = next_crop
        return [["PLANT", next_crop], ["WATER"]]
    if not crop_has_future_sale(pos):
        return []
    water = [["WATER"]] if crop_needs_water(pos) else []
    if not data["harvest"]:
        return water
    if data.get("sale_early_harvest", False) or EXPANSION_ACTIVE and not data.get("next_prod"):
        return water + [["HARVEST"]]
    if CROP_PRODUCTION[crop]["type"] == "ONE_TIME" and can_plant_for_final_sale(CURRENT_DAY, next_crop):
        data["pending_replant"] = next_crop
        data["crop"] = next_crop
        return water + [["HARVEST"], ["PLANT", next_crop], ["WATER"]]
    return water + [["HARVEST"]]

def update_animal_state(obs):
    farm = obs["farms"][obs["player"]]
    for pos, data in ANIMAL_STATE.items():
        tile = farm["tiles"][pos[1]][pos[0]]
        if isinstance(tile, dict) and tile.get("animal") == data["animal"]:
            data["placed"] = True
            data["harvest"] = tile.get("yield_units", 0) > 0
            data["fertilizer"] = tile.get("fertilizer_available", False)
            data["pending_care_bonus"] = tile.get("pending_care_bonus", 0)
            data["consecutive_unfed"] = tile.get("consecutive_unfed", 0)
            data["fed_today"] = tile.get("fed_today", False)
            data["cared_today"] = tile.get("cared_today", False)
            data["placed_day"] = tile.get("placed_day")
            data["will_be_empty"] = False
        else:
            data["placed"] = False
            data["harvest"] = False
            data["fertilizer"] = False
            data["pending_care_bonus"] = 0
            data["consecutive_unfed"] = 0
            data["fed_today"] = False
            data["cared_today"] = False
            data["placed_day"] = None
            data["will_be_empty"] = True

def crop_action_cost(pos):
    data = CROP_STATE[pos]
    crop = data["crop"]
    next_crop = data.get("next_prod") or crop
    if data.get("weed", False):
        if EXPANSION_ACTIVE and not data.get("next_prod"):
            return 1
        return 3 if can_plant_for_final_sale(CURRENT_DAY, next_crop) else 0
    if not data["planted"]:
        return 0 if (EXPANSION_ACTIVE and not data.get("next_prod")) or not can_plant_for_final_sale(CURRENT_DAY, next_crop) else 2
    if not crop_has_future_sale(pos):
        return 0
    water_cost = int(crop_needs_water(pos))
    if not data["harvest"]:
        return water_cost
    if data.get("sale_early_harvest", False) or EXPANSION_ACTIVE and not data.get("next_prod"):
        return water_cost + 1
    replant_cost = 2 if CROP_PRODUCTION[crop]["type"] == "ONE_TIME" and can_plant_for_final_sale(CURRENT_DAY, next_crop) else 0
    return water_cost + 1 + replant_cost

def animal_remaining_profit(pos):
    data = ANIMAL_STATE[pos]
    if not data.get("placed", False) or CURRENT_OBS is None:
        return 0
    animal = data["animal"]
    product = ANIMAL_PRODUCT[animal]
    days = get_existing_animal_production_days(pos)
    if not days:
        return 0
    spec = ANIMAL_PRODUCTION[animal]
    cap = ANIMAL_MAX_HELD[animal]
    product_units = sum(min(cap, 1 + spec["interval"]) for _ in days)
    product_price = CURRENT_OBS["market"]["prices"].get(product, MARKET_PARAMS[product]["base"])
    fertilizer_price = CURRENT_OBS["market"]["prices"].get("FERTILIZER", MARKET_PARAMS["FERTILIZER"]["base"])
    feed_days = days[-1] - CURRENT_DAY + 1
    wheat_price = CURRENT_OBS["market"]["prices"].get("WHEAT", MARKET_PARAMS["WHEAT"]["base"])
    return product_units * product_price + feed_days * fertilizer_price - feed_days * wheat_price

def animal_maintenance_active(pos):
    return CURRENT_DAY <= LAST_HARVEST_DAY and animal_has_future_sale(pos) and animal_remaining_profit(pos) > 0

def animal_needs_daily_feed(pos):
    data = ANIMAL_STATE[pos]
    return data.get("placed", False) and animal_maintenance_active(pos) and not data.get("fed_today", False)

def animal_needs_care(pos):
    data = ANIMAL_STATE[pos]
    if data.get("placed", False):
        return animal_maintenance_active(pos) and not data.get("cared_today", False)
    animal = data.get("next_prod") or data["animal"]
    if animal == "GOOSE":
        return True
    return data["pending_care_bonus"] + 1 < ANIMAL_MAX_HELD[animal]

def get_animal_actions(obs, pos):
    farm = obs["farms"][obs["player"]]
    tile = farm["tiles"][pos[1]][pos[0]]
    data = ANIMAL_STATE[pos]
    animal = data["animal"] if data["placed"] else data.get("next_prod") or data["animal"]
    kind = "COOP" if animal == "GOOSE" else "PASTURE"
    actions = []
    if not data["placed"] and not animal_can_start_for_final_sale(animal):
        return actions
    if not isinstance(tile, dict) or tile.get("kind") != kind:
        actions.append(["BUILD_COOP"] if animal == "GOOSE" else ["BUILD_PASTURE"])
    if not data["placed"]:
        actions.append(["PLACE", animal])
    if data["harvest"] and CURRENT_DAY <= LAST_HARVEST_DAY:
        actions.append(["HARVEST"])
    if data["fertilizer"]:
        actions.append(["COLLECT_FERTILIZER"])
    if data["placed"]:
        if animal_needs_daily_feed(pos):
            actions.append(["FEED"])
        if animal_needs_care(pos):
            actions.append(["CARE"])
    elif animal_can_start_for_final_sale(animal):
        actions.append(["FEED"])
        if animal_needs_care(pos):
            actions.append(["CARE"])
    return actions

def get_task_actions(obs, task):
    kind = task[0]
    if kind == "WAIT_WHEAT":
        return []
    if kind == "SHED_DROP":
        return [["DROP"]]
    if kind == "WEED":
        return [["DIG"]]
    if kind == "CROP_WATER":
        return [["WATER"]] if crop_needs_water(task[1]) else []
    if kind == "INSTALL":
        pos = task[1]
        prod = NEW_PRODUCTION_STATE.get(pos, {}).get("next_prod")
        if not prod:
            return []
        tile = obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]]
        actions = []
        if isinstance(tile, dict) and tile.get("kind") == "WEED":
            actions.append(["DIG"])
        if prod in CROP_PRODUCTION:
            actions += [["PLANT", prod], ["WATER"]]
            return actions
        kind_needed = "COOP" if prod == "GOOSE" else "PASTURE"
        if not isinstance(tile, dict) or tile.get("kind") != kind_needed:
            actions.append(["BUILD_COOP"] if prod == "GOOSE" else ["BUILD_PASTURE"] )
        actions += [["PLACE", prod], ["FEED"], ["CARE"]]
        return actions
    if kind == "WHEAT_SUPPLY":
        water = [["WATER"]] if crop_needs_water(task[1]) else []
        if EXPANSION_ACTIVE:
            return water + [["HARVEST"]]
        CROP_STATE[task[1]]["crop"] = "CARROT"
        return water + [["HARVEST"], ["PLANT", "CARROT"], ["WATER"]]
    if kind == "ANIMAL_PRE":
        data = ANIMAL_STATE[task[1]]
        actions = []
        if data["harvest"]:
            actions.append(["HARVEST"])
        if data["fertilizer"]:
            actions.append(["COLLECT_FERTILIZER"])
        if animal_needs_care(task[1]) and not animal_needs_daily_feed(task[1]):
            actions.append(["CARE"])
        return actions
    if kind == "ANIMAL_FEED":
        actions = []
        if animal_needs_daily_feed(task[1]):
            actions.append(["FEED"])
        if animal_needs_care(task[1]):
            actions.append(["CARE"])
        return actions
    if kind == "CROP":
        return get_crop_actions(task[1])
    return get_animal_actions(obs, task[1])

def get_day_1_farmer_action(obs):
    state = WORKER_STATE[0]
    if state["stack"]:
        return state["stack"].pop()
    if state["setup"] < len(FARMER_SETUP):
        action = FARMER_SETUP[state["setup"]]
        state["setup"] += 1
        return action
    pos = get_worker_position(obs, 0)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    if pos in ANIMAL_STATE and pos not in state["done"]:
        state["done"].add(pos)
        state["stack"].extend(reversed(get_animal_actions(obs, pos)))
        return state["stack"].pop()
    return get_path_action(DAY_1_PATHS[0], state)

def get_day_1_hand_action(obs, worker_id):
    if obs.get("hour", 0) == 0:
        return ["PASS"]
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    state = WORKER_STATE[worker_id]
    if state["stack"]:
        return state["stack"].pop()
    if pos in CROP_STATE and pos not in state["done"]:
        state["done"].add(pos)
        state["stack"].extend(reversed(get_crop_actions(pos)))
        return state["stack"].pop()
    return get_path_action(DAY_1_PATHS[worker_id], state)

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def animal_action_cost(pos):
    data = ANIMAL_STATE[pos]
    animal = data["animal"] if data["placed"] else data.get("next_prod") or data["animal"]
    if not data["placed"] and not animal_can_start_for_final_sale(animal):
        return 0
    feed = animal_needs_daily_feed(pos) if data["placed"] else animal_can_start_for_final_sale(animal)
    care = animal_needs_care(pos)
    cost = int(feed) + int(care)
    if not data["placed"]:
        tile = CURRENT_OBS["farms"][CURRENT_OBS["player"]]["tiles"][pos[1]][pos[0]] if CURRENT_OBS is not None else None
        kind = "COOP" if animal == "GOOSE" else "PASTURE"
        cost += 1 + int(not isinstance(tile, dict) or tile.get("kind") != kind)
    if data["harvest"]:
        cost += 1
    if data["fertilizer"]:
        cost += 1
    return cost

def task_action_cost(task):
    kind = task[0]
    if kind == "WAIT_WHEAT":
        return 0
    if kind == "SHED_DROP":
        return 1
    if kind == "WEED":
        return 1
    if kind == "CROP_WATER":
        return int(crop_needs_water(task[1]))
    if kind == "INSTALL":
        prod = NEW_PRODUCTION_STATE.get(task[1], {}).get("next_prod")
        return get_candidate_install_actions(CURRENT_OBS, prod, task[1]) if prod and CURRENT_OBS is not None else 0
    if kind == "WHEAT_SUPPLY":
        return int(crop_needs_water(task[1])) + (1 if EXPANSION_ACTIVE else 3)
    if kind == "ANIMAL_PRE":
        data = ANIMAL_STATE[task[1]]
        care = animal_needs_care(task[1]) and not animal_needs_daily_feed(task[1])
        return int(care) + int(data["harvest"]) + int(data["fertilizer"])
    if kind == "ANIMAL_FEED":
        return int(animal_needs_daily_feed(task[1])) + int(animal_needs_care(task[1]))
    if kind == "CROP":
        return max(0, crop_action_cost(task[1]) - int(crop_needs_water(task[1])))
    return animal_action_cost(task[1])

def nearest_task(current_pos, tasks):
    priority = {"CROP_WATER": 0}
    return min(tasks, key=lambda task: (distance(current_pos, task[1]), priority.get(task[0], 1), distance(CENTER, task[1]), -task_action_cost(task)))

def order_tasks(start, tasks):
    ordered = []
    remaining = tasks.copy()
    current = start
    while remaining:
        task = nearest_task(current, remaining)
        ordered.append(task)
        remaining.remove(task)
        current = task[1]
    return ordered

def route_end(start, route):
    return route[-1][1] if route else start

def sequence_cost(start, route):
    cost = 0
    pos = start
    for task in route:
        cost += distance(pos, task[1]) + task_action_cost(task)
        pos = task[1]
    return cost

def route_has_wait(route):
    return any(task[0] == "WAIT_WHEAT" for task in route)

def get_feed_count(route):
    count = 0
    for task in route:
        if task[0] == "ANIMAL_FEED" and animal_needs_feed_for_final_sale(task[1]):
            count += 1
        elif task[0] == "ANIMAL":
            data = ANIMAL_STATE[task[1]]
            animal = data["animal"] if data["placed"] else data.get("next_prod") or data["animal"]
            if (data["placed"] and animal_needs_daily_feed(task[1])) or (not data["placed"] and animal_can_start_for_final_sale(animal)):
                count += 1
        elif task[0] == "INSTALL":
            prod = NEW_PRODUCTION_STATE.get(task[1], {}).get("next_prod")
            if prod in ANIMAL_PRODUCTION:
                count += 1
    return count

def get_worker_wheat(obs, worker_id):
    inventories = obs.get("private", {}).get("inventories", [])
    if worker_id >= len(inventories):
        return 0
    return inventories[worker_id].get("WHEAT", 0)

def task_is_sacrificable(task, required_installs=None):
    required_installs = required_installs or set()
    if task[0] == "WEED":
        return True
    if task[0] == "INSTALL":
        return task[1] not in required_installs
    if task[0] != "CROP":
        return False
    data = CROP_STATE.get(task[1])
    if not data or data.get("harvest", False):
        return False
    return data.get("weed", False) or not data.get("planted", False)

def protect_critical_capacity(routes, required_installs=None):
    required_installs = required_installs or set()
    protected = {worker_id: route.copy() for worker_id, route in routes.items()}
    for worker_id, route in protected.items():
        if not any(task_is_critical(task) for task in route):
            continue
        capacity = get_worker_capacity(worker_id)
        while route_cost(worker_id, route) > capacity:
            removed = False
            for index in range(len(route) - 1, -1, -1):
                if task_is_sacrificable(route[index], required_installs):
                    route.pop(index)
                    route[:] = order_tasks(get_worker_spawn(worker_id), route)
                    removed = True
                    break
            if not removed:
                break
    return protected

def get_animal_pickups(route):
    pickups = {}
    for task in route:
        prod = None
        if task[0] == "INSTALL":
            prod = NEW_PRODUCTION_STATE.get(task[1], {}).get("next_prod")
        elif task[0] == "ANIMAL":
            data = ANIMAL_STATE[task[1]]
            if not data.get("placed", False):
                prod = data.get("next_prod") or data["animal"]
        if prod in ANIMAL_PRODUCTION:
            pickups[prod] = pickups.get(prod, 0) + 1
    return pickups

def route_cost(worker_id, route):
    start = get_worker_spawn(worker_id)
    cost = sequence_cost(start, route)
    cost += len(get_animal_pickups(route))
    if get_feed_count(route) and not route_has_wait(route):
        cost += 1
    if CURRENT_DAY == SALE_DAY:
        cost += distance_to_shed(route_end(start, route)) + 1
    return cost

def get_weed_tasks(obs):
    farm = obs["farms"][obs["player"]]
    tasks = []
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if isinstance(tile, dict) and tile.get("kind") == "WEED":
                tasks.append(("WEED", (x, y)))
    return tasks

def animal_task_is_critical(pos):
    data = ANIMAL_STATE[pos]
    if not data.get("placed", False) or not animal_maintenance_active(pos):
        return False
    return data.get("harvest", False) or animal_needs_daily_feed(pos) or animal_needs_care(pos)

def task_is_critical(task):
    if task[0] == "CROP_WATER":
        return True
    if task[0] == "ANIMAL":
        return animal_task_is_critical(task[1])
    if task[0] == "ANIMAL_PRE":
        return animal_maintenance_active(task[1]) and (ANIMAL_STATE[task[1]].get("harvest", False) or animal_needs_care(task[1]))
    if task[0] == "ANIMAL_FEED":
        return animal_maintenance_active(task[1])
    return False

def add_task_to_routes(routes, task):
    best = None
    for worker_id in routes:
        current = order_tasks(get_worker_spawn(worker_id), routes[worker_id])
        current_cost = route_cost(worker_id, current)
        candidate = order_tasks(get_worker_spawn(worker_id), routes[worker_id] + [task])
        cost = route_cost(worker_id, candidate)
        capacity = get_worker_capacity(worker_id)
        if cost > capacity:
            continue
        incremental = cost - current_cost
        score = (incremental, cost, -capacity + cost, worker_id)
        if best is None or score < best[0]:
            best = (score, worker_id, candidate)
    if best is None:
        return False
    _, worker_id, candidate = best
    routes[worker_id] = candidate
    return True

def assign_normal_routes(obs, hire_count, include_animals=True, required_installs=None):
    required_installs = required_installs or set()
    worker_count = hire_count + 1
    routes = {worker_id: [] for worker_id in range(worker_count)}
    animal_tasks = [("ANIMAL", pos) for pos in ANIMAL_STATE if animal_action_cost(pos) > 0] if include_animals else []
    water_tasks = [("CROP_WATER", pos) for pos, data in CROP_STATE.items() if data.get("planted", False) and crop_has_future_sale(pos) and crop_needs_water(pos)]
    install_tasks = [("INSTALL", pos) for pos, data in NEW_PRODUCTION_STATE.items() if data.get("next_prod") and task_action_cost(("INSTALL", pos)) > 0]
    required_install_tasks = [task for task in install_tasks if task[1] in required_installs]
    critical = water_tasks + [task for task in animal_tasks if task_is_critical(task)] + required_install_tasks
    def critical_priority(task):
        if task[0] == "CROP_WATER":
            return (0 if crop_needs_survival_water(task[1]) else 3, -distance(CENTER, task[1]), task[1][1], task[1][0])
        if task[0] == "ANIMAL":
            data = ANIMAL_STATE[task[1]]
            urgent_feed = data.get("placed", False) and data.get("consecutive_unfed", 0) >= 1
            return (0 if urgent_feed else 1 if data.get("harvest", False) else 2, -distance(CENTER, task[1]), task[1][1], task[1][0])
        return (4, -distance(CENTER, task[1]), task[1][1], task[1][0])
    critical.sort(key=critical_priority)
    for task in critical:
        if not add_task_to_routes(routes, task):
            return None
    crop_tasks = [("CROP", pos) for pos, data in CROP_STATE.items() if (data["planted"] or data.get("weed", False) or not EXPANSION_ACTIVE) and max(0, crop_action_cost(pos) - int(crop_needs_water(pos))) > 0]
    crop_positions = {task[1] for task in crop_tasks} | {task[1] for task in install_tasks}
    weed_tasks = [task for task in get_weed_tasks(obs) if task[1] not in crop_positions]
    critical_set = set(critical)
    tasks = crop_tasks + [task for task in install_tasks if task not in critical_set] + weed_tasks + [task for task in animal_tasks if task not in critical_set]
    tasks.sort(key=lambda task: (distance(CENTER, task[1]), -get_task_profitability(obs, task), -get_task_expected_value(obs, task), task[1][1], task[1][0]))
    for task in tasks:
        add_task_to_routes(routes, task)
    return protect_critical_capacity(routes, required_installs)

def assign_routes(obs, hire_count, required_installs=None):
    return assign_normal_routes(obs, hire_count, include_animals=True, required_installs=required_installs)


def assign_maintenance_routes(obs, hire_count):
    worker_count = hire_count + 1
    routes = {worker_id: [] for worker_id in range(worker_count)}
    tasks = []
    for pos, data in CROP_STATE.items():
        if data.get("planted", False) and crop_has_future_sale(pos) and crop_needs_survival_water(pos):
            tasks.append(("CROP_WATER", pos))
    for pos, data in ANIMAL_STATE.items():
        if not data.get("placed", False) or not animal_maintenance_active(pos):
            continue
        if data.get("consecutive_unfed", 0) >= 1 or data.get("harvest", False) or animal_needs_daily_feed(pos):
            tasks.append(("ANIMAL", pos))
    tasks.sort(key=lambda task: (0 if task[0] == "CROP_WATER" else 1, -distance(CENTER, task[1]), task[1][1], task[1][0]))
    for task in tasks:
        if not add_task_to_routes(routes, task):
            return None
    return routes

def calculate_maintenance_paths(obs, max_hires=None):
    max_hires = len(HIRE_COSTS) if max_hires is None else min(max_hires, len(HIRE_COSTS))
    for hire_count in range(max_hires + 1):
        routes = assign_maintenance_routes(obs, hire_count)
        if routes is not None:
            return hire_count, routes
    return None

def calculate_daily_paths(obs, max_hires=None, required_installs=None, optimize_extra_hires=True):
    max_hires = len(HIRE_COSTS) if max_hires is None else min(max_hires, len(HIRE_COSTS))
    hire_count = 0
    routes = None
    while hire_count <= max_hires and hire_count <= len(HIRE_COSTS):
        candidate = assign_routes(obs, hire_count, required_installs)
        if candidate is not None:
            routes = candidate
            break
        hire_count += 1
    if routes is None:
        return calculate_maintenance_paths(obs, max_hires)
    if not optimize_extra_hires:
        return hire_count, routes
    profit = get_routes_expected_profit(obs, routes)
    while hire_count < max_hires and hire_count < len(HIRE_COSTS):
        next_hires = hire_count + 1
        next_routes = assign_routes(obs, next_hires, required_installs)
        if next_routes is None:
            break
        next_profit = get_routes_expected_profit(obs, next_routes)
        va = next_profit - profit
        if va < HIRE_COSTS[hire_count]:
            break
        hire_count = next_hires
        routes = next_routes
        profit = next_profit
    return hire_count, routes

def complete_active_task(state):
    if state["active_task"] and not state["stack"]:
        state["target"] += 1
        state["active_task"] = False

def inventory_item_count(inv):
    return sum(v for k, v in inv.items() if k not in CROP_PRODUCTION) + sum(inv.get(k, 0) for k in CROP_PRODUCTION)

def get_total_nonseed_stock(obs):
    shed = obs.get("private", {}).get("shed", {})
    total = sum(shed.values())
    for inv in obs.get("private", {}).get("inventories", []):
        total += sum(inv.values())
    return total

def get_emergency_drop_action(obs, worker_id):
    # Avoid silent nightly destruction at shedCapacity=100 without turning normal
    # routing into constant shed shuttling.
    inventories = obs.get("private", {}).get("inventories", [])
    if worker_id >= len(inventories):
        return None
    inv_count = sum(inventories[worker_id].values())
    if inv_count < 4 or get_total_nonseed_stock(obs) < 92:
        return None
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return None
    pos = tuple(pos)
    target = nearest_shed_tile(pos)
    if pos != target:
        return move_toward(pos, target)
    return ["DROP"]

def get_general_worker_action(obs, worker_id):
    state = WORKER_STATE[worker_id]
    route = WORKER_ROUTES.get(worker_id, [])

    if worker_id > 0 and obs.get("hour", 0) == 0:
        return ["PASS"]

    emergency_drop = get_emergency_drop_action(obs, worker_id)
    if emergency_drop is not None:
        return emergency_drop

    if state["stack"]:
        action = state["stack"][-1]
        if action[0] == "FEED" and get_worker_wheat(obs, worker_id) <= 0:
            state["stack"].clear()
            state["active_task"] = False
            state["pickup_done"] = False
            state["pickup_pending"] = False
            return ["PASS"]
        return state["stack"].pop()

    complete_active_task(state)

    if not state["animal_pickups_initialized"]:
        state["animal_pickups"] = list(get_animal_pickups(route).items())
        state["animal_pickups_initialized"] = True
    if state["animal_pickups"]:
        if obs.get("hour", 0) == 0:
            return ["PASS"]
        animal, count = state["animal_pickups"][0]
        if has_pending_market_order("BUY_ANIMAL", animal) or obs["private"]["shed"].get(animal, 0) < count:
            return ["PASS"]
        state["animal_pickups"].pop(0)
        return ["PICKUP", animal, count]

    if not state["pickup_done"] and get_feed_count(route) and not route_has_wait(route):
        feed_count = get_feed_count(route)
        worker_wheat = get_worker_wheat(obs, worker_id)
        missing_wheat = max(0, feed_count - worker_wheat)
        if missing_wheat == 0:
            state["pickup_done"] = True
            state["pickup_pending"] = False
        else:
            if obs["private"]["shed"].get("WHEAT", 0) < missing_wheat:
                state["pickup_pending"] = False
                return ["PASS"]
            state["pickup_pending"] = True
            return ["PICKUP", "WHEAT", missing_wheat]

    if not get_feed_count(route):
        state["pickup_done"] = True
        state["pickup_pending"] = False

    if state["target"] >= len(route):
        return ["PASS"]

    task = route[state["target"]]
    seed = get_task_required_seed(task)
    if seed and has_pending_market_order("BUY_SEED", seed):
        return ["PASS"]
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]

    pos = tuple(pos)
    target = task[1]

    if pos != target:
        return move_toward(pos, target)

    if task[0] == "WAIT_WHEAT":
        needed = task[2]
        if obs["private"]["shed"].get("WHEAT", 0) < needed:
            return ["PASS"]
        state["target"] += 1
        state["pickup_done"] = True
        return ["PICKUP", "WHEAT", needed]

    actions = get_task_actions(obs, task)
    if not actions:
        state["target"] += 1
        return ["PASS"]

    state["active_task"] = True
    state["stack"].extend(reversed(actions))
    return state["stack"].pop()

def get_final_drop_action(obs, worker_id):
    if obs.get("day", 0) != LAST_SELL_DAY:
        return None
    hour = obs.get("hour", 0)
    pos = get_worker_position(obs, worker_id)
    if pos is None:
        return ["PASS"]
    pos = tuple(pos)
    shed_tile = nearest_shed_tile(pos)
    if hour < FINAL_DROP_HOUR - distance(pos, shed_tile):
        return None
    if pos != shed_tile:
        return move_toward(pos, shed_tile)
    if hour >= FINAL_DROP_HOUR:
        return ["DROP"]
    return None

def get_install_market_orders_for_routes(obs, routes):
    seeds = {}
    animals = {}
    animal_count = 0
    planned = [(task[0], task[1]) for route in routes.values() for task in route if task[0] in ("INSTALL", "ANIMAL", "CROP", "WHEAT_SUPPLY")]
    for kind, pos in planned:
        prod = None
        if kind == "INSTALL":
            prod = NEW_PRODUCTION_STATE.get(pos, {}).get("next_prod")
        elif kind == "ANIMAL":
            data = ANIMAL_STATE[pos]
            prod = None if data.get("placed", False) else data.get("next_prod") or data["animal"]
        elif kind == "WHEAT_SUPPLY":
            if not EXPANSION_ACTIVE and can_plant_for_final_sale(CURRENT_DAY, "CARROT"):
                prod = "CARROT"
        else:
            data = CROP_STATE[pos]
            next_crop = data.get("next_prod") or data["crop"]
            needs_seed = data.get("weed", False) or not data.get("planted", False)
            needs_seed = needs_seed or data.get("harvest", False) and not data.get("sale_early_harvest", False) and CROP_PRODUCTION[data["crop"]]["type"] == "ONE_TIME"
            if needs_seed and can_plant_for_final_sale(CURRENT_DAY, next_crop):
                prod = next_crop
        if prod in CROP_PRODUCTION:
            seeds[prod] = seeds.get(prod, 0) + 1
        elif prod in ANIMAL_PRODUCTION:
            animals[prod] = animals.get(prod, 0) + 1
            animal_count += 1
    seed_stock = obs.get("private", {}).get("seeds", {})
    orders = [["BUY_SEED", prod, max(0, count - seed_stock.get(prod, 0))] for prod, count in seeds.items() if count > seed_stock.get(prod, 0)]
    orders += [["BUY_ANIMAL", prod, count] for prod, count in animals.items()]
    if animal_count:
        shed_wheat = obs["private"]["shed"].get("WHEAT", 0)
        existing_feed = len(get_active_feed_positions())
        wheat_after_existing = max(0, shed_wheat - existing_feed)
        extra_wheat = max(0, animal_count - wheat_after_existing)
        if extra_wheat:
            orders.append(["BUY_PRODUCT", "WHEAT", extra_wheat])
    return orders

def get_install_market_orders(obs):
    return get_install_market_orders_for_routes(obs, WORKER_ROUTES)

def get_total_wheat_available(obs):
    total = obs.get("private", {}).get("shed", {}).get("WHEAT", 0)
    for inventory in obs.get("private", {}).get("inventories", []):
        total += inventory.get("WHEAT", 0)
    return total

def consolidate_market_orders(orders):
    merged = []
    index = {}
    for order in orders:
        if not order:
            continue
        if order[0] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT", "SELL") and len(order) >= 3:
            key = (order[0], order[1])
            if key in index:
                merged[index[key]][2] += order[2]
            else:
                index[key] = len(merged)
                merged.append(order.copy())
        else:
            merged.append(order.copy())
    return [order for order in merged if len(order) < 3 or order[2] > 0]

def get_unified_wheat_order(obs, install_orders):
    active_feed = len(get_active_feed_positions())
    new_animals = sum(order[2] for order in install_orders if order[0] == "BUY_ANIMAL")
    needed = active_feed + new_animals
    missing = max(0, needed - get_total_wheat_available(obs))
    return [["BUY_PRODUCT", "WHEAT", missing]] if missing > 0 else []

def get_worker_market_orders(obs, worker_id, seed_stock, animal_stock, wheat_stock):
    route = WORKER_ROUTES.get(worker_id, [])
    seeds = {}
    for task in route:
        seed = get_task_required_seed(task)
        if seed:
            seeds[seed] = seeds.get(seed, 0) + 1
    animals = get_animal_pickups(route)
    orders = []
    for seed, needed in seeds.items():
        available = seed_stock.get(seed, 0)
        bought = max(0, needed - available)
        seed_stock[seed] = max(0, available - needed)
        if bought:
            orders.append(["BUY_SEED", seed, bought])
    for animal, needed in animals.items():
        available = animal_stock.get(animal, 0)
        bought = max(0, needed - available)
        animal_stock[animal] = max(0, available - needed)
        if bought:
            orders.append(["BUY_ANIMAL", animal, bought])
    feed_needed = get_feed_count(route)
    bought_wheat = max(0, feed_needed - wheat_stock[0])
    wheat_stock[0] = max(0, wheat_stock[0] - feed_needed)
    if bought_wheat:
        orders.append(["BUY_PRODUCT", "WHEAT", bought_wheat])
    return consolidate_market_orders(orders)

def append_market_group(batches, group):
    group = filter_endgame_market_orders(CURRENT_OBS, consolidate_market_orders(group))
    if not group:
        return
    if len(group) > MAX_MARKET_ORDERS:
        raise ValueError("A worker market group exceeds the per-tick market limit")
    if not batches or len(batches[-1]) + len(group) > MAX_MARKET_ORDERS:
        batches.append([])
    batches[-1].extend(group)

def build_daily_market_queue(obs):
    global WORKER_HIRE_TICKS
    seed_stock = dict(obs.get("private", {}).get("seeds", {}))
    animal_stock = {animal: obs.get("private", {}).get("shed", {}).get(animal, 0) for animal in ANIMAL_PRODUCTION}
    wheat_stock = [obs.get("private", {}).get("shed", {}).get("WHEAT", 0)]
    batches = []
    WORKER_HIRE_TICKS = {}
    farmer_orders = get_worker_market_orders(obs, 0, seed_stock, animal_stock, wheat_stock)
    append_market_group(batches, farmer_orders)
    for worker_id in range(1, HIRE_COUNT + 1):
        worker_orders = get_worker_market_orders(obs, worker_id, seed_stock, animal_stock, wheat_stock)
        group = [["HIRE"]] + worker_orders
        if len(group) > MAX_MARKET_ORDERS:
            raise ValueError("A worker market group exceeds the per-tick market limit")
        hire_tick = len(batches) - 1 if batches and len(batches[-1]) + len(group) <= MAX_MARKET_ORDERS else len(batches)
        append_market_group(batches, group)
        WORKER_HIRE_TICKS[worker_id] = hire_tick
    if LAND_BUY_PLANNED:
        cost = get_next_land_cost(obs)
        all_orders = [order for batch in batches for order in batch if order[0] != "HIRE"]
        planned_spend = get_market_orders_cost(obs, all_orders, HIRE_COUNT)
        if cost is not None and obs["farms"][obs["player"]].get("money", 0) - planned_spend >= cost:
            append_market_group(batches, [["BUY_LAND"]])
    return batches

def has_pending_market_order(kind, product=None):
    for batch in PENDING_MARKET_ORDERS:
        for order in batch:
            if order[0] != kind:
                continue
            if product is None or len(order) > 1 and order[1] == product:
                return True
    return False

def get_task_required_seed(task):
    kind = task[0]
    if kind == "INSTALL":
        prod = NEW_PRODUCTION_STATE.get(task[1], {}).get("next_prod")
        return prod if prod in CROP_PRODUCTION else None
    if kind == "WHEAT_SUPPLY":
        return "CARROT" if not EXPANSION_ACTIVE and can_plant_for_final_sale(CURRENT_DAY, "CARROT") else None
    if kind != "CROP":
        return None
    data = CROP_STATE[task[1]]
    next_crop = data.get("next_prod") or data["crop"]
    needs_seed = data.get("weed", False) or not data.get("planted", False)
    needs_seed = needs_seed or data.get("harvest", False) and not data.get("sale_early_harvest", False) and CROP_PRODUCTION[data["crop"]]["type"] == "ONE_TIME"
    return next_crop if needs_seed and can_plant_for_final_sale(CURRENT_DAY, next_crop) else None

def get_market_orders_cost(obs, orders, hire_count=0):
    cost = sum(HIRE_COSTS[:hire_count])
    for order in orders:
        if order[0] == "BUY_SEED":
            cost += PRODUCTION_COSTS[order[1]] * order[2]
        elif order[0] == "BUY_ANIMAL":
            cost += PRODUCTION_COSTS[order[1]] * order[2]
        elif order[0] == "BUY_PRODUCT":
            cost += obs["market"]["prices"].get(order[1], 0) * order[2]
    return cost

def get_replant_orders(obs, worker_actions):
    if EXPANSION_ACTIVE:
        return []
    seeds = {}
    for worker_id, action in worker_actions.items():
        if not action:
            continue
        pos = get_worker_position(obs, worker_id)
        if pos is None:
            continue
        pos = tuple(pos)
        if pos not in CROP_STATE:
            continue
        data = CROP_STATE[pos]
        crop = data["crop"]
        if action[0] == "DIG" and data.get("weed", False) and can_plant_for_final_sale(CURRENT_DAY, crop):
            seeds[crop] = seeds.get(crop, 0) + 1
        elif action[0] in ("WATER", "HARVEST") and data["harvest"] and not data.get("sale_early_harvest", False) and not data.get("seed_ordered", False):
            next_crop = data.get("pending_replant") or data.get("next_prod")
            if next_crop and can_plant_for_final_sale(CURRENT_DAY, next_crop):
                seeds[next_crop] = seeds.get(next_crop, 0) + 1
                data["seed_ordered"] = True
    seed_stock = obs.get("private", {}).get("seeds", {})
    return [["BUY_SEED", crop, max(0, amount - seed_stock.get(crop, 0))] for crop, amount in seeds.items() if amount > seed_stock.get(crop, 0)]

def filter_endgame_market_orders(obs, orders):
    day = obs.get("day", 0)
    filtered = []
    for order in orders:
        if order[0] == "BUY_SEED" and not can_plant_for_final_sale(day, order[1]):
            continue
        if order[0] == "BUY_ANIMAL" and not animal_can_start_for_final_sale(order[1], day):
            continue
        filtered.append(order)
    return filtered

def agent(obs):
    global CURRENT_DAY, WORKER_ROUTES, HIRE_COUNT, WORKER_HIRE_TICKS, ROUTES_REBUILT_DAY, REAL_WORKER_STARTS, EXPANSION_ACTIVE, CURRENT_OBS, LAND_BUY_PLANNED, PENDING_MARKET_ORDERS
    day = obs.get("day", 0)
    hour = obs.get("hour", 0)
    farm = obs["farms"][obs["player"]]
    unlocked = farm.get("unlocked_quadrants", ["NW"])
    EXPANSION_ACTIVE = len(unlocked) > 1
    CURRENT_OBS = obs
    sync_production_tiles(obs)

    update_crop_state(obs)
    update_animal_state(obs)

    if day != CURRENT_DAY:
        CURRENT_DAY = day
        REAL_WORKER_STARTS = {0: tuple(farm["farmer"])}
        WORKER_HIRE_TICKS = {}
        PENDING_MARKET_ORDERS = []
        if day == 0:
            HIRE_COUNT = 4
            WORKER_ROUTES = {}
            reset_worker_state(5)
        else:
            LAND_BUY_PLANNED = False
            reserved_cost, feed_units, wheat_available = choose_next_productions(obs)
            LAND_BUY_PLANNED = plan_land_before_pathing(obs, reserved_cost, feed_units, wheat_available)
            result = calculate_daily_paths(obs)
            if result is None:
                HIRE_COUNT = 0
                WORKER_ROUTES = {0: []}
            else:
                HIRE_COUNT, WORKER_ROUTES = result
            reset_worker_state(HIRE_COUNT + 1)
            for _ in range(5):
                previous_hires = HIRE_COUNT
                previous_ticks = WORKER_HIRE_TICKS.copy()
                PENDING_MARKET_ORDERS = build_daily_market_queue(obs)
                result = calculate_daily_paths(obs)
                if result is None:
                    HIRE_COUNT = 0
                    WORKER_ROUTES = {0: []}
                    WORKER_HIRE_TICKS = {}
                    PENDING_MARKET_ORDERS = build_daily_market_queue(obs)
                    break
                HIRE_COUNT, WORKER_ROUTES = result
                reset_worker_state(HIRE_COUNT + 1)
                PENDING_MARKET_ORDERS = build_daily_market_queue(obs)
                if HIRE_COUNT == previous_hires and WORKER_HIRE_TICKS == previous_ticks:
                    break

    if day > 0 and hour == 1 and ROUTES_REBUILT_DAY != day:
        REAL_WORKER_STARTS = {0: tuple(farm["farmer"])}
        REAL_WORKER_STARTS.update({worker_id: tuple(pos) for worker_id, pos in enumerate(farm.get("hands", []), 1)})
        WORKER_ROUTES = {worker_id: order_tasks(REAL_WORKER_STARTS.get(worker_id, get_worker_spawn(worker_id)), route) for worker_id, route in WORKER_ROUTES.items()}
        reset_worker_state(HIRE_COUNT + 1)
        ROUTES_REBUILT_DAY = day

    if day == 0:
        farmer_action = get_day_1_farmer_action(obs)
        hand_actions = [get_day_1_hand_action(obs, worker_id) for worker_id in range(1, 5)]
        worker_actions = {0: farmer_action}
        worker_actions.update({worker_id: action for worker_id, action in enumerate(hand_actions, 1)})
        market = filter_endgame_market_orders(obs, DAY_1_MARKET.get(hour, []).copy())
        market += get_replant_orders(obs, worker_actions)
        market = filter_endgame_market_orders(obs, market)
        return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}

    worker_actions = {}
    for worker_id in range(HIRE_COUNT + 1):
        final_drop_action = get_final_drop_action(obs, worker_id)
        worker_actions[worker_id] = final_drop_action if final_drop_action is not None else get_general_worker_action(obs, worker_id)
    farmer_action = worker_actions[0]
    hand_actions = [worker_actions[worker_id] for worker_id in range(1, HIRE_COUNT + 1)]

    final_liquidation = get_final_liquidation_orders(obs)
    if final_liquidation:
        market = final_liquidation[:MAX_MARKET_ORDERS]
    else:
        market = PENDING_MARKET_ORDERS.pop(0) if PENDING_MARKET_ORDERS else []
        sale_slots = MAX_MARKET_ORDERS - len(market)
        if sale_slots > 0:
            sale_orders = consolidate_market_orders(get_daily_harvest_sale_orders(obs) + get_sale_orders(obs))
            market += sale_orders[:sale_slots]
    market = filter_endgame_market_orders(obs, market)
    return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}

