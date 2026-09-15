"""CHI 10 with bounded temporal scheduling and tick-by-tick replanning.

Standalone Kaggle agent; only the Python standard library is required.
"""

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
LAND_BUY_DAY = 6
LAST_4000_LAND_BUY_DAY = 19
LAST_SELL_DAY = 29
LAST_HARVEST_DAY = LAST_SELL_DAY
HIRE_COSTS = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368]
PRODUCTION_COSTS = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80, "GOOSE": 300, "COW": 400, "SHEEP": 500}
EFFECTIVE_SPACE = {"WHEAT": 1, "CARROT": 1, "TOMATO": 1, "STRAWBERRY": 1, "MELON": 1, "GOOSE": 5 / 3, "COW": 5 / 3, "SHEEP": 5 / 3}
CROP_EXPECTED_YIELD = {"WHEAT": 4, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}
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


def get_candidate_occupation_time(prod, day=None):
    day = CURRENT_DAY if day is None else day
    if prod in CROP_PRODUCTION:
        harvests = get_remaining_crop_harvests(prod, day)
        return harvests[-1] if harvests else 0
    days = get_animal_production_days(prod, day)
    return days[-1] - day + 1 if days else 0


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


def calculate_production_marginal_profit(obs, prod, pos):
    plans = tuple((p, d.get('next_prod')) for states in (CROP_STATE, ANIMAL_STATE, NEW_PRODUCTION_STATE) for p, d in states.items() if p != pos and d.get('next_prod'))
    tile = obs['farms'][obs['player']]['tiles'][pos[1]][pos[0]]
    kind = tile.get('kind') if isinstance(tile, dict) else tile
    key = ('economics', prod, distance_to_shed(pos), kind, plans)
    if key in TURN_CACHE:
        return TURN_CACHE[key]
    events = candidate_events(prod, obs['day'])
    if not events:
        return float('-inf')
    revenue = marginal_event_revenue(obs, events, max(events), pos)
    TURN_CACHE[key] = revenue - PRODUCTION_COSTS[prod] - candidate_running_cost(obs, prod, pos)
    return TURN_CACHE[key]


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
    kind, pos = task[:2]
    tile = CURRENT_OBS['farms'][CURRENT_OBS['player']]['tiles'][pos[1]][pos[0]]
    if not isinstance(tile, dict):
        return {}
    if kind == 'CROP' and tile.get('kind') == 'PLANT':
        crop = tile['crop']
        held = tile.get('yield_units', 0)
        if CROP_PRODUCTION[crop]['type'] == 'ONE_TIME' and CROP_STATE.get(pos, {}).get('harvest'):
            held = max(1, held)
            if crop_needs_water(pos):
                held = min({'WHEAT':6, 'CARROT':4, 'MELON':6}[crop], held + (2 if tile.get('fertilized_until_day', -1) >= CURRENT_DAY else 1))
        return {crop: held}
    if kind == 'ANIMAL' and tile.get('animal'):
        return {ANIMAL_PRODUCT[tile['animal']]: tile.get('yield_units', 0), 'FERTILIZER': int(tile.get('fertilizer_available', False))}
    return {}


def get_task_expected_value(obs, task):
    key = ('task', task)
    if key in TURN_CACHE:
        return TURN_CACHE[key]
    kind, pos = task[:2]
    production = get_task_expected_production(task)
    value = sum(sell_units(p, obs['market']['inventory'][p], n)[0] for p, n in production.items())
    data = CROP_STATE.get(pos, {})
    prod = NEW_PRODUCTION_STATE.get(pos, {}).get('next_prod') if kind == 'INSTALL' else data.get('next_prod') if kind == 'CROP' else None
    if kind == 'ANIMAL' and not ANIMAL_STATE[pos].get('placed'):
        prod = ANIMAL_STATE[pos].get('next_prod')
    if prod:
        value += max(0, calculate_production_marginal_profit(obs, prod, pos)) / max(1, get_candidate_occupation_time(prod))
    if kind == 'CROP_WATER' and crop_needs_survival_water(pos):
        value += PRODUCTION_COSTS[data['crop']]
    if kind == 'ANIMAL' and animal_needs_daily_feed(pos):
        value -= obs['market']['prices']['WHEAT']
        animal = ANIMAL_STATE[pos]['animal']
        value += obs['market']['prices'][ANIMAL_PRODUCT[animal]] / ANIMAL_PRODUCTION[animal]['interval']
    TURN_CACHE[key] = max(0, value)
    return TURN_CACHE[key]


def get_routes_expected_profit(obs, routes):
    seen = set()
    value = 0
    for route in routes.values():
        for task in route:
            if task not in seen:
                seen.add(task)
                value += get_task_expected_value(obs, task)
    return value


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


def animal_needs_feed_for_final_sale(pos):
    if CURRENT_DAY >= LAST_SELL_DAY:
        return False
    data = ANIMAL_STATE[pos]
    if not data.get('placed'):
        return False
    return bool(get_existing_animal_production_days(pos, CURRENT_DAY + 1))


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
REAL_WORKER_STARTS = {}
EXPANSION_ACTIVE = False
CURRENT_OBS = None
LAND_BUY_PLANNED = False
PENDING_MARKET_ORDERS = []


def get_daily_harvest_sale_orders(obs):
    return adaptive_sale_orders(with_pending_deposits(obs))


def get_final_liquidation_orders(obs):
    if obs['day'] != LAST_SELL_DAY or obs['hour'] < 20:
        return []
    shed = with_pending_deposits(obs)['private']['shed']
    return [['SELL', p, shed[p]] for p in MARKET_PARAMS if shed.get(p, 0)>0]


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
        adjusted_profit = marginal_profit
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
    """State used only by the fixed opening."""
    global WORKER_STATE
    WORKER_STATE = {i: {"path": 0, "stack": [], "done": set()} for i in range(worker_count)}
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
    return HAND_SPAWNS[(worker_id - 1) % len(HAND_SPAWNS)]


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
        data["weed"] = isinstance(tile, dict) and tile.get("kind") == "WEED"
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
        data["planted_day"] = planted_day
        data["watered_today"] = tile.get("watered_today", False)
        data["consecutive_unwatered"] = tile.get("consecutive_unwatered", 0)
        data["needs_water"] = not data["watered_today"] and data["consecutive_unwatered"] >= 1
        age = day - planted_day
        data["age"] = age
        production = CROP_PRODUCTION[data["crop"]]
        if production["type"] == "ONE_TIME":
            data["harvest"] = age >= production["harvest_ages"][0]
            data["will_be_empty"] = data["harvest"]
        else:
            data["harvest"] = tile.get("yield_units", 0) > 0
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
    """Describe a crop chain without mutating the observed production state."""
    data = CROP_STATE[pos]
    crop = data["crop"]
    next_crop = data.get("next_prod") or crop
    plant = (
        can_plant_for_final_sale(CURRENT_DAY, next_crop)
        and (not EXPANSION_ACTIVE or bool(data.get("next_prod")))
    )
    if data.get("weed"):
        return [["DIG"]] + ([["PLANT", next_crop], ["WATER"]] if plant else [])
    if not data["planted"]:
        return [["PLANT", next_crop], ["WATER"]] if plant else []
    if not crop_has_future_sale(pos):
        return []
    actions = [["WATER"]] if crop_needs_water(pos) else []
    if data["harvest"]:
        actions.append(["HARVEST"])
        if CROP_PRODUCTION[crop]["type"] == "ONE_TIME" and plant:
            actions += [["PLANT", next_crop], ["WATER"]]
    return actions

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
    return CURRENT_DAY < LAST_SELL_DAY and animal_needs_feed_for_final_sale(pos) and animal_remaining_profit(pos) > 0


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
        if isinstance(tile, dict) and tile.get("kind") == "WEED":
            actions.append(["DIG"])
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
    kind, pos = task
    if kind == "WEED":
        return [["DIG"]]
    if kind == "CROP_WATER":
        return [["WATER"]] if crop_needs_water(pos) else []
    if kind == "CROP":
        return get_crop_actions(pos)
    if kind == "INSTALL":
        prod = NEW_PRODUCTION_STATE.get(pos, {}).get("next_prod")
        if not prod:
            return []
        tile = obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]]
        actions = [["DIG"]] if isinstance(tile, dict) and tile.get("kind") == "WEED" else []
        if prod in CROP_PRODUCTION:
            return actions + [["PLANT", prod], ["WATER"]]
        kind_needed = "COOP" if prod == "GOOSE" else "PASTURE"
        if not isinstance(tile, dict) or tile.get("kind") != kind_needed:
            actions.append(["BUILD_COOP"] if prod == "GOOSE" else ["BUILD_PASTURE"])
        return actions + [["PLACE", prod, 1], ["FEED"], ["CARE"]]
    return get_animal_actions(obs, pos)

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


def get_feed_count(route):
    return sum(action[0] == "FEED" for task in route for action in get_task_actions(CURRENT_OBS, task))


def get_animal_pickups(route):
    pickups = {}
    for task in route:
        for action in get_task_actions(CURRENT_OBS, task):
            if action[0] == "PLACE" and action[1] in ANIMAL_PRODUCTION:
                pickups[action[1]] = pickups.get(action[1], 0) + 1
    return pickups


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


def assign_routes(obs, hire_count, required_installs=None):
    plans = tuple((pos, data.get("next_prod"))
                  for states in (CROP_STATE, ANIMAL_STATE, NEW_PRODUCTION_STATE)
                  for pos, data in states.items() if data.get("next_prod"))
    key = ("temporal_routes", hire_count,
           tuple(obs["farms"][obs["player"]]["unlocked_quadrants"]), plans,
           tuple(WORKER_HIRE_TICKS.get(i, 0) for i in range(1, hire_count + 1)),
           tuple(sorted(required_installs or ())))
    if key in TURN_CACHE:
        return TURN_CACHE[key]
    tasks = build_temporal_tasks(obs, required_installs, planning=True)
    plan = schedule_temporal_tasks(obs, tasks, hire_count + 1, planning=True, width=2)
    if any(task["required"] and task["key"] not in plan["finished"] for task in tasks):
        TURN_CACHE[key] = None
        return None
    routes = {i: list(worker["route"]) for i, worker in enumerate(plan["workers"])}
    TURN_CACHE[key] = routes
    return routes

def assign_maintenance_routes(obs, hire_count):
    tasks = [task for task in build_temporal_tasks(obs, planning=True) if task["required"]]
    plan = schedule_temporal_tasks(obs, tasks, hire_count + 1, planning=True, width=2)
    if any(task["key"] not in plan["finished"] for task in tasks):
        return None
    return {i: list(worker["route"]) for i, worker in enumerate(plan["workers"])}

def calculate_maintenance_paths(obs, max_hires=None):
    max_hires = len(HIRE_COSTS) if max_hires is None else min(max_hires, len(HIRE_COSTS))
    for hire_count in range(max_hires + 1):
        routes = assign_maintenance_routes(obs, hire_count)
        if routes is not None:
            return hire_count, routes
    return None

def calculate_daily_paths(obs, max_hires=None, required_installs=None, optimize_extra_hires=True):
    affordable = 0
    money = obs["farms"][obs["player"]]["money"]
    while affordable < len(HIRE_COSTS) and sum(HIRE_COSTS[:affordable+1]) <= money:
        affordable += 1
    max_hires = affordable if max_hires is None else min(max_hires, affordable)
    max_hires = min(max_hires, len(HIRE_COSTS))
    hire_count = 0
    # Even with free travel, mandatory actions must fit in worker time.
    mandatory = sum(len(t["actions"]) for t in build_temporal_tasks(obs, required_installs, planning=True)
                    if t["required"])
    capacity = temporal_deadline(obs) - obs["hour"]
    while capacity < mandatory and hire_count < max_hires:
        hire_count += 1
        capacity += max(0, temporal_deadline(obs) - max(obs["hour"], WORKER_HIRE_TICKS.get(hire_count, 0) + 1))
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


def get_total_nonseed_stock(obs):
    shed = obs.get("private", {}).get("shed", {})
    total = sum(shed.values())
    for inv in obs.get("private", {}).get("inventories", []):
        total += sum(inv.values())
    return total


def get_install_market_orders_for_routes(obs, routes):
    seeds = {}
    animals = {}
    for route in routes.values():
        for task in route:
            seed = get_task_required_seed(task)
            if seed:
                seeds[seed] = seeds.get(seed, 0) + 1
        for animal, count in get_animal_pickups(route).items():
            animals[animal] = animals.get(animal, 0) + count
    seed_stock = obs["private"]["seeds"]
    orders = [["BUY_SEED", seed, count - seed_stock.get(seed, 0)]
              for seed, count in seeds.items() if count > seed_stock.get(seed, 0)]
    for animal, count in animals.items():
        owned = obs["private"]["shed"].get(animal, 0)
        owned += sum(inv.get(animal, 0) for inv in obs["private"]["inventories"])
        if count > owned:
            orders.append(["BUY_ANIMAL", animal, count - owned])
    return orders


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


def get_task_required_seed(task):
    for action in get_task_actions(CURRENT_OBS, task):
        if action[0] == "PLANT":
            return action[1]
    return None

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


INITIAL_CROPS = {p: d["crop"] for p, d in CROP_STATE.items()}
INITIAL_ANIMALS = {p: d["animal"] for p, d in ANIMAL_STATE.items()}
TURN_CACHE = {}
TURN_TRANSFERS = {}
PRICE_CACHE = {}

def begin_turn(obs):
    global CURRENT_DAY, LAST_SCHEDULE
    TURN_CACHE.clear()
    TURN_TRANSFERS.clear()
    if obs.get("day", 0) == 0 and obs.get("hour", 0) == 0:
        CROP_STATE.clear()
        CROP_STATE.update({p: make_crop_state(c) for p, c in INITIAL_CROPS.items()})
        ANIMAL_STATE.clear()
        ANIMAL_STATE.update({p: make_animal_state(a) for p, a in INITIAL_ANIMALS.items()})
        NEW_PRODUCTION_STATE.clear()
        PRICE_CACHE.clear()
        LAST_SCHEDULE = {}
        CURRENT_DAY = -1

def unit_price(product, inventory):
    key = (product, inventory)
    if key not in PRICE_CACHE:
        p = MARKET_PARAMS[product]
        delta = inventory - p['I0']
        side = 'below' if delta < 0 else 'above'
        shape = p[side + '_func']
        amplitude = p[side + '_target'] * p['base'] / market_shape(shape, p['T'], p['T'])
        movement = amplitude * market_shape(shape, abs(delta), p['T'])
        PRICE_CACHE[key] = max(1, round(p['base'] + (movement if delta < 0 else -movement)))
    return PRICE_CACHE[key]


def sell_units(product, inventory, quantity):
    """Exact per-unit quote, including the engine's non-incrementing $1 floor."""
    revenue = 0.0
    while quantity > 0:
        take = min(1, quantity)
        price = unit_price(product, inventory)
        revenue += take * price
        if price > 1:
            inventory += take
        quantity -= take
    return revenue, inventory


def add_event(events, day, product, quantity):
    if quantity > 0 and day <= LAST_SELL_DAY:
        goods = events.setdefault(day, {})
        goods[product] = goods.get(product, 0) + quantity


def candidate_events(prod, day):
    events = {}
    if prod in CROP_PRODUCTION:
        for age in get_remaining_crop_harvests(prod, day):
            add_event(events, day + age, prod, CROP_EXPECTED_YIELD[prod] if CROP_PRODUCTION[prod]['type'] == 'ONE_TIME' else 1)
    else:
        days = get_animal_production_days(prod, day)
        if days:
            for i, d in enumerate(days):
                # At refresh, production consumes the old bank BEFORE today's CARE is banked.
                bank = ANIMAL_PRODUCTION[prod]['first_yield_age'] - 1 if i == 0 else ANIMAL_PRODUCTION[prod]['interval']
                add_event(events, d, ANIMAL_PRODUCT[prod], min(ANIMAL_MAX_HELD[prod], 1 + bank))
            for d in range(day + 1, days[-1] + 1):
                add_event(events, d, 'FERTILIZER', 1)
    return events


def public_supply_events(obs, player, horizon):
    """Estimate public yields; never read the opponent's hidden shed or inventory."""
    key = ('public', player, horizon)
    if key in TURN_CACHE:
        return TURN_CACHE[key]
    events = {}
    day = obs['day']
    if player >= len(obs['farms']):
        return events
    for row in obs['farms'][player]['tiles']:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get('kind') == 'PLANT':
                crop = tile['crop']
                spec = CROP_PRODUCTION[crop]
                planted = tile['planted_day']
                held = tile.get('yield_units', 0)
                if spec['type'] == 'ONE_TIME':
                    harvest = max(day, planted + spec['harvest_ages'][0])
                    if harvest <= horizon:
                        add_event(events, harvest, crop, max(held, CROP_EXPECTED_YIELD[crop]))
                else:
                    add_event(events, day, crop, held)
                    for age in spec['harvest_ages']:
                        if day < planted + age <= horizon:
                            add_event(events, planted + age, crop, 1)
            elif tile.get('animal') in ANIMAL_PRODUCTION:
                animal = tile['animal']
                spec = ANIMAL_PRODUCTION[animal]
                add_event(events, day, ANIMAL_PRODUCT[animal], tile.get('yield_units', 0))
                add_event(events, day, 'FERTILIZER', int(tile.get('fertilizer_available', False)))
                bank = tile.get('pending_care_bonus', 0)
                for d in range(day + 1, horizon + 1):
                    age = d - tile['placed_day']
                    if age >= spec['first_yield_age'] and (age - spec['first_yield_age']) % spec['interval'] == 0:
                        add_event(events, d, ANIMAL_PRODUCT[animal], min(ANIMAL_MAX_HELD[animal], 1 + bank))
                        bank = 0
                    bank += 1
                    add_event(events, d, 'FERTILIZER', 1)
    TURN_CACHE[key] = events
    return events


def own_supply_events(obs, horizon, exclude=None):
    events = {d: dict(goods) for d, goods in public_supply_events(obs, obs['player'], horizon).items()}
    for product, quantity in obs['private']['shed'].items():
        if product in MARKET_PARAMS and product != 'WHEAT':
            add_event(events, obs['day'], product, quantity)
    for inventory in obs['private']['inventories']:
        for product, quantity in inventory.items():
            if product in MARKET_PARAMS and product != 'WHEAT':
                add_event(events, obs['day'], product, quantity)
    for states in (CROP_STATE, ANIMAL_STATE, NEW_PRODUCTION_STATE):
        for pos, data in states.items():
            prod = data.get('next_prod')
            if pos == exclude or not prod:
                continue
            # Planned replacement is a separate future generation, even on a harvested tile.
            if data.get('planted') and not data.get('will_be_empty'):
                continue
            if data.get('placed'):
                continue
            for d, goods in candidate_events(prod, obs['day']).items():
                if d <= horizon:
                    for product, quantity in goods.items():
                        add_event(events, d, product, quantity)
    return events


def simulate_cashflows(obs, own, opponent, horizon, opponent_factor=1, delay=0):
    inventory = dict(obs['market']['inventory'])
    money = 0
    previous = {p: 0 for p in MARKET_PARAMS}
    for day in range(obs['day'], horizon + 1):
        elapsed = max(0, day - obs['day'] - obs.get('hour', 0) / 24)
        consumed = get_future_consumption(obs, elapsed)
        for product in MARKET_PARAMS:
            inventory[product] = max(0, inventory[product] - consumed.get(product, 0) + previous.get(product, 0))
        previous = consumed
        for product, quantity in opponent.get(day - delay, {}).items():
            _, inventory[product] = sell_units(product, inventory[product], int(round(quantity * opponent_factor)))
        for product, quantity in own.get(day, {}).items():
            revenue, inventory[product] = sell_units(product, inventory[product], quantity)
            money += revenue
    return money


def marginal_event_revenue(obs, events, horizon, exclude=None):
    base = own_supply_events(obs, horizon, exclude)
    added = {d: dict(goods) for d, goods in base.items()}
    for d, goods in events.items():
        for product, quantity in goods.items():
            add_event(added, d, product, quantity)
    opponent = public_supply_events(obs, 1 - obs['player'], horizon)
    # Unknown sales timing and future care: average a smaller/delayed and larger/immediate supply.
    return sum(simulate_cashflows(obs, added, opponent, horizon, scale, lag) - simulate_cashflows(obs, base, opponent, horizon, scale, lag)
               for scale, lag in ((0.5, 2), (1.5, 0))) / 2


def candidate_running_cost(obs, prod, pos):
    events = candidate_events(prod, obs['day'])
    if not events:
        return 0
    duration = max(events) - obs['day']
    base_actions = get_base_daily_action_count()
    travel = max(1, distance_to_shed(pos) / 3)
    feed = 0
    labor = 0
    for offset in range(duration + 1):
        if prod in ANIMAL_PRODUCTION:
            actions = 4 if offset < duration else 2
            if offset < duration:
                # Includes opportunity cost when wheat was grown rather than purchased.
                consumption = get_future_consumption(obs, offset).get('WHEAT', 0)
                feed += unit_price('WHEAT', obs['market']['inventory']['WHEAT'] - consumption - offset - 1)
        else:
            spec = CROP_PRODUCTION[prod]
            actions = int(offset % 2 == 0 or (spec['type'] == 'ONE_TIME' and offset >= spec['bonus_start_age']))
            actions += int(offset in spec['harvest_ages'])
        if offset == 0:
            actions = get_candidate_install_actions(obs, prod, pos)
        added = int(actions + travel + 0.999)
        labor += get_labor_cost_for_actions(base_actions + added) - get_labor_cost_for_actions(base_actions)
    return feed + labor


def adaptive_sale_orders(obs):
    shed = obs['private']['shed']
    pressure = get_total_nonseed_stock(obs) >= 80
    cash_needed = obs['farms'][obs['player']]['money'] < max(200, len(get_active_feed_positions()) * obs['market']['prices']['WHEAT'] * 2)
    next_consumption = get_future_consumption(obs, 4 / 24)
    opponent = public_supply_events(obs, 1-obs['player'], obs['day'])
    orders = []
    for product in MARKET_PARAMS:
        quantity = shed.get(product, 0)
        if product == 'WHEAT' and obs['day'] < LAST_SELL_DAY:
            quantity = max(0, quantity - 2 * len(get_active_feed_positions()) - 4)
        if quantity <= 0:
            continue
        inventory = obs['market']['inventory'][product]
        sell = 0
        for index in range(quantity):
            now = unit_price(product, inventory + index)
            future = unit_price(product, inventory + index - next_consumption.get(product, 0) + opponent.get(obs['day'], {}).get(product, 0))
            if pressure or cash_needed or obs['day'] == LAST_SELL_DAY or now >= future:
                sell += 1
            else:
                break
        if sell:
            orders.append(['SELL', product, sell])
    orders.sort(key=lambda order: (shed.get(order[1], 0), obs['market']['prices'].get(order[1], 0)), reverse=True)
    return orders


def with_pending_deposits(obs):
    # Worker actions execute before market actions. These deposits can be sold this turn.
    projected = dict(obs)
    projected['private'] = dict(obs['private'])
    projected['private']['shed'] = dict(obs['private']['shed'])
    for product, count in TURN_TRANSFERS.items():
        projected['private']['shed'][product] = projected['private']['shed'].get(product, 0) + count
    return projected


# The beam keeps a few alternative assignments. Each worker has a timed action
# sequence; shared stock is represented by (availability_tick, quantity) lots.
LAST_SCHEDULE = {}


def temporal_task(key, actions, value=0, required=False, predecessors=()):
    return {"key": key, "pos": key[1], "actions": tuple(tuple(a) for a in actions),
            "value": value, "required": required, "predecessors": predecessors,
            "delivery": False, "owner": None}


def build_temporal_tasks(obs, required_installs=None, planning=False):
    required_installs = required_installs or set()
    tasks = []
    live_wheat = get_total_wheat_available(obs)
    harvest_wheat = sum(get_task_expected_production(("CROP", pos)).get("WHEAT", 0)
                        for pos, data in CROP_STATE.items() if data.get("harvest"))
    shortage = not planning and obs["private"]["shed"].get("WHEAT", 0) < len(get_active_feed_positions())
    for pos, data in sorted(CROP_STATE.items()):
        water_key = ("CROP_WATER", pos)
        water = data.get("planted") and crop_has_future_sale(pos) and crop_needs_water(pos)
        if water:
            tasks.append(temporal_task(water_key, [["WATER"]],
                         get_task_expected_value(obs, water_key), True))
        actions = get_crop_actions(pos)
        if water and actions and actions[0] == ["WATER"]:
            actions = actions[1:]
        # Missing seed must not block a harvest or weed removal. The remaining
        # planting chain will be generated again after the purchase is observed.
        if not planning:
            for index, action in enumerate(actions):
                if action[0] == "PLANT" and obs["private"]["seeds"].get(action[1], 0) <= 0:
                    actions = actions[:index]
                    break
        if actions:
            key = ("CROP", pos)
            task = temporal_task(key, actions, get_task_expected_value(obs, key),
                                 predecessors=(water_key,) if water else ())
            task["delivery"] = shortage and data["crop"] == "WHEAT" and any(a[0] == "HARVEST" for a in actions)
            tasks.append(task)
    for pos, data in sorted(ANIMAL_STATE.items()):
        actions = get_animal_actions(obs, pos)
        if not planning and live_wheat + harvest_wheat == 0:
            actions = [a for a in actions if a[0] != "FEED"
                       and (a[0] != "CARE" or data.get("fed_today"))]
        if actions:
            key = ("ANIMAL", pos)
            tasks.append(temporal_task(key, actions, get_task_expected_value(obs, key),
                                      animal_task_is_critical(pos)))
    for pos, data in sorted(NEW_PRODUCTION_STATE.items()):
        if data.get("next_prod") and obs["farms"][obs["player"]]["tiles"][pos[1]][pos[0]] != "LOCKED":
            key = ("INSTALL", pos)
            actions = get_task_actions(obs, key)
            if actions:
                tasks.append(temporal_task(key, actions, get_task_expected_value(obs, key),
                                          pos in required_installs))
    occupied = {task["pos"] for task in tasks}
    for key in get_weed_tasks(obs):
        if key[1] not in occupied:
            tasks.append(temporal_task(key, [["DIG"]]))
    # A worker already carrying wheat can supply a different worker.
    if shortage:
        for worker_id, inv in enumerate(obs["private"]["inventories"]):
            if inv.get("WHEAT", 0):
                pos = tuple(get_worker_position(obs, worker_id))
                task = temporal_task(("DELIVER", pos, worker_id), [])
                task["delivery"] = True
                task["owner"] = worker_id
                tasks.append(task)
    # Topological order: water -> harvest/supply -> feeding/other jobs.
    def priority(task):
        if task["key"][0] == "CROP_WATER":
            return (0, -distance_to_shed(task["pos"]))
        if task["delivery"]:
            return (1, distance_to_shed(task["pos"]))
        return (2 if task["required"] else 3,
                -task["value"] / max(1, len(task["actions"])), task["pos"])
    return sorted(tasks, key=priority)


def reserve_temporal_stock(stock, product, quantity, tick):
    """Reserve a resource once, waiting for every consumed lot to exist."""
    lots = stock.get(product, ())
    if sum(count for _, count in lots) < quantity:
        return None
    remaining = []
    for ready, count in sorted(lots):
        take = min(count, quantity)
        if take:
            tick = max(tick, ready)
            quantity -= take
        if count > take:
            remaining.append((ready, count - take))
    stock[product] = tuple(remaining)
    return tick


def temporal_move(worker, target):
    if not worker["record"]:
        worker["time"] += distance(worker["pos"], target)
        worker["pos"] = target
        return
    while worker["pos"] != target:
        action = move_toward(worker["pos"], target)
        temporal_append(worker, action)
        x, y = worker["pos"]
        dx, dy = {"EAST": (1, 0), "WEST": (-1, 0),
                  "SOUTH": (0, 1), "NORTH": (0, -1)}[action[0]]
        worker["pos"] = (x + dx, y + dy)


def temporal_append(worker, action):
    if worker["record"]:
        worker["actions"] += ((worker["time"], worker["pos"], tuple(action)),)
    worker["time"] += 1


def temporal_goods(worker, final=False):
    return {p: n for p, n in worker["inventory"].items()
            if n > 0 and p in MARKET_PARAMS and (final or p != "WHEAT")}


def temporal_deadline(obs):
    # With episodeSteps=720 the last actionable observation is step 718,
    # i.e. day 29 / hour 22. End-of-day automatic deposits cannot be sold then.
    return TURNS_PER_DAY - int(obs["day"] == LAST_SELL_DAY)


def extend_temporal_plan(obs, state, task, worker_id):
    previous = state["workers"][worker_id]
    if task["owner"] is not None and task["owner"] != worker_id:
        return None
    if any(key not in state["finished"] for key in task["predecessors"]):
        return None
    earliest = max([previous["time"] + distance(previous["pos"], task["pos"])]
                   + [state["finished"][key] for key in task["predecessors"]])
    if earliest + len(task["actions"]) > temporal_deadline(obs):
        return None
    worker = dict(previous)
    worker["inventory"] = dict(previous["inventory"])
    stock = dict(state["stock"])
    actions = task["actions"]
    pickups = {}
    for item, quantity in task["needed"].items():
        if not item.startswith("SEED:"):
            quantity = max(0, quantity - worker["inventory"].get(item, 0))
        if quantity:
            ready = reserve_temporal_stock(stock, item, quantity, worker["time"])
            if ready is None:
                return None
            if item.startswith("SEED:"):
                worker["time"] = ready
            else:
                pickups[item] = (quantity, ready)
    if pickups:
        # The closest access to the worker need not minimize the complete trip.
        shed = min(SHED_TILES, key=lambda p: distance(worker["pos"], p) + distance(p, task["pos"]))
        temporal_move(worker, shed)
        for item, (quantity, ready) in pickups.items():
            worker["time"] = max(worker["time"], ready)
            temporal_append(worker, ("PICKUP", item, quantity))
            worker["inventory"][item] = worker["inventory"].get(item, 0) + quantity
    temporal_move(worker, task["pos"])
    worker["time"] = max([worker["time"]] + [state["finished"][key] for key in task["predecessors"]])
    for action in actions:
        temporal_append(worker, action)
        if action[0] == "FEED":
            worker["inventory"]["WHEAT"] -= 1
        elif action[0] == "PLACE" and action[1] in ANIMAL_PRODUCTION:
            worker["inventory"][action[1]] -= 1
    for product, quantity in task["production"].items():
        worker["inventory"][product] = worker["inventory"].get(product, 0) + quantity
    if task["delivery"]:
        quantity = worker["inventory"].get("WHEAT", 0)
        if not quantity:
            return None
        temporal_move(worker, nearest_shed_tile(worker["pos"]))
        temporal_append(worker, ("PLACE", "WHEAT", quantity))
        worker["inventory"]["WHEAT"] = 0
        # Conservatively require the deposit to be visible in the next observation.
        stock["WHEAT"] = stock.get("WHEAT", ()) + ((worker["time"], quantity),)
    final = obs["day"] == LAST_SELL_DAY
    goods = temporal_goods(worker, final)
    return_cost = distance_to_shed(worker["pos"]) + len(goods) if goods else 0
    if worker["time"] + return_cost > temporal_deadline(obs):
        return None
    worker["route"] += (task["key"],)
    workers = list(state["workers"])
    workers[worker_id] = worker
    finished = dict(state["finished"])
    finished[task["key"]] = worker["time"]
    return {"workers": workers, "stock": stock, "finished": finished,
            "required": state["required"] + int(task["required"]),
            "value": state["value"] + task["value"]}


def schedule_temporal_tasks(obs, tasks, worker_count, planning=False, width=4):
    """Bounded beam search over timed assignments; no state is shared by branches."""
    hour = obs["hour"]
    tasks = [dict(task) for task in tasks]
    for task in tasks:
        task["needed"] = {}
        for action in task["actions"]:
            item = ("SEED:" + action[1] if action[0] == "PLANT" else
                    "WHEAT" if action[0] == "FEED" else
                    action[1] if action[0] == "PLACE" and action[1] in ANIMAL_PRODUCTION else None)
            if item:
                task["needed"][item] = task["needed"].get(item, 0) + 1
        produced = get_task_expected_production(task["key"]) if task["key"][0] != "DELIVER" else {}
        ops = {a[0] for a in task["actions"]}
        task["production"] = {p: n for p, n in produced.items()
                              if ("COLLECT_FERTILIZER" if p == "FERTILIZER" else "HARVEST") in ops}
    inventories = obs["private"]["inventories"]
    workers = []
    for i in range(worker_count):
        position = get_worker_position(obs, i)
        ready = hour if position is not None else max(hour, WORKER_HIRE_TICKS.get(i, 0) + 1)
        workers.append({"pos": tuple(position) if position is not None else get_worker_spawn(i),
                        "time": ready, "inventory": dict(inventories[i]) if i < len(inventories) else {},
                        "actions": (), "route": (), "record": not planning})
    stock = {p: ((hour, n),) for p, n in obs["private"]["shed"].items() if n > 0}
    stock.update({"SEED:" + p: ((hour, n),) for p, n in obs["private"]["seeds"].items() if n > 0})
    if planning:
        # Strategic hiring/land estimates assume purchases at the next tick.
        # The live schedule only uses observed stock and actual worker positions.
        demand = {}
        for task in tasks:
            for item, count in task["needed"].items():
                demand[item] = demand.get(item, 0) + count
        for item, count in demand.items():
            available = sum(n for _, n in stock.get(item, ()))
            if not item.startswith("SEED:"):
                available += sum(inv.get(item, 0) for inv in inventories)
            if count > available:
                stock[item] = stock.get(item, ()) + ((hour + 1, count - available),)
    beam = [{"workers": workers, "stock": stock, "finished": {}, "required": 0, "value": 0}]
    def rank(state):
        return state["required"], state["value"], -sum(w["time"] for w in state["workers"])
    for task in tasks:
        candidates = list(beam)  # Skipping an optional task can enable a better suffix.
        for state in beam:
            for worker_id in range(worker_count):
                candidate = extend_temporal_plan(obs, state, task, worker_id)
                if candidate is not None:
                    candidates.append(candidate)
        # With a fixed task order, identical partial assignments have identical
        # resource reservations and completion times.
        unique = {}
        for candidate in candidates:
            signature = tuple(w["route"] for w in candidate["workers"])
            if signature not in unique or rank(candidate) > rank(unique[signature]):
                unique[signature] = candidate
        beam = sorted(unique.values(), key=rank, reverse=True)[:width]
    return beam[0]


def checked_temporal_actions(obs, schedule):
    """Check shared seeds, pickups, tile mutations and shed room in engine order."""
    stock = dict(obs["private"]["shed"])
    seeds = dict(obs["private"]["seeds"])
    farm = obs["farms"][obs["player"]]
    tiles = {(x, y): dict(tile) if isinstance(tile, dict) else tile
             for y, row in enumerate(farm["tiles"]) for x, tile in enumerate(row)}
    result = {}
    for worker_id in range(1 + len(farm["hands"])):
        position = tuple(get_worker_position(obs, worker_id))
        inv = obs["private"]["inventories"][worker_id]
        entries = schedule.get(worker_id, ())
        entry = next((entry for entry in entries if entry[0] == obs["hour"]), None)
        action = list(entry[2]) if entry is not None and entry[1] == position else ["PASS"]
        op = action[0]
        tile = tiles[position]
        valid = True
        if op == "PLANT":
            valid = tile is None and seeds.get(action[1], 0) > 0
            if valid:
                seeds[action[1]] -= 1
                tiles[position] = {"kind": "PLANT", "crop": action[1], "watered_today": False}
        elif op == "PICKUP":
            quantity = min(action[2], stock.get(action[1], 0))
            valid = position in SHED_TILES and quantity > 0
            if valid:
                action[2] = quantity
                stock[action[1]] -= quantity
                TURN_TRANSFERS[action[1]] = TURN_TRANSFERS.get(action[1], 0) - quantity
        elif op == "PLACE":
            item = action[1]
            if item in ANIMAL_PRODUCTION:
                kind = "COOP" if item == "GOOSE" else "PASTURE"
                valid = isinstance(tile, dict) and tile.get("kind") == kind and not tile.get("animal") and inv.get(item, 0) > 0
                if valid:
                    tile["animal"] = item
            else:
                quantity = min(action[2], inv.get(item, 0), max(0, 100 - sum(stock.values())))
                valid = position in SHED_TILES and quantity > 0
                if valid:
                    action[2] = quantity
                    stock[item] = stock.get(item, 0) + quantity
                    TURN_TRANSFERS[item] = TURN_TRANSFERS.get(item, 0) + quantity
        elif op == "WATER":
            valid = isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today")
            if valid:
                tile["watered_today"] = True
        elif op in ("FEED", "CARE", "COLLECT_FERTILIZER"):
            field = {"FEED": "fed_today", "CARE": "cared_today", "COLLECT_FERTILIZER": "fertilizer_available"}[op]
            valid = isinstance(tile, dict) and bool(tile.get("animal"))
            valid = valid and (bool(tile.get(field)) if op == "COLLECT_FERTILIZER" else not tile.get(field))
            valid = valid and (op != "FEED" or inv.get("WHEAT", 0) > 0)
            if valid:
                tile[field] = op != "COLLECT_FERTILIZER"
        elif op == "HARVEST":
            valid = isinstance(tile, dict) and tile.get("yield_units", 0) > 0
            if valid:
                tile["yield_units"] = 0
                if tile.get("crop") in CROP_PRODUCTION and CROP_PRODUCTION[tile["crop"]]["type"] == "ONE_TIME":
                    tiles[position] = None
        elif op == "DIG":
            valid = isinstance(tile, dict) and tile.get("kind") == "WEED"
            if valid:
                tiles[position] = None
        elif op.startswith("BUILD_"):
            valid = tile is None
            if valid:
                tiles[position] = {"kind": "COOP" if op == "BUILD_COOP" else "PASTURE"}
        result[worker_id] = action if valid else ["PASS"]
    return result


def temporal_worker_actions(obs):
    global LAST_SCHEDULE
    tasks = build_temporal_tasks(obs)
    plan = schedule_temporal_tasks(obs, tasks, 1 + len(obs["farms"][obs["player"]]["hands"]))
    LAST_SCHEDULE = {}
    for worker_id, worker in enumerate(plan["workers"]):
        goods = temporal_goods(worker, obs["day"] == LAST_SELL_DAY)
        if goods:
            temporal_move(worker, nearest_shed_tile(worker["pos"]))
            for product in sorted(goods, key=lambda p: -obs["market"]["prices"].get(p, 0)):
                if worker["time"] >= temporal_deadline(obs):
                    break
                temporal_append(worker, ("PLACE", product, goods[product]))
        LAST_SCHEDULE[worker_id] = worker["actions"]
    return checked_temporal_actions(obs, LAST_SCHEDULE)

def agent(obs):
    global CURRENT_DAY, WORKER_ROUTES, HIRE_COUNT, WORKER_HIRE_TICKS, REAL_WORKER_STARTS, EXPANSION_ACTIVE, CURRENT_OBS, LAND_BUY_PLANNED, PENDING_MARKET_ORDERS
    begin_turn(obs)
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
                PENDING_MARKET_ORDERS = build_daily_market_queue(obs)
                if HIRE_COUNT == previous_hires and WORKER_HIRE_TICKS == previous_ticks:
                    break

    if day == 0:
        farmer_action = get_day_1_farmer_action(obs)
        hand_actions = [get_day_1_hand_action(obs, worker_id) for worker_id in range(1, 5)]
        market = filter_endgame_market_orders(obs, DAY_1_MARKET.get(hour, []).copy())
        return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}

    worker_actions = temporal_worker_actions(obs)
    farmer_action = worker_actions[0]
    hand_actions = [worker_actions[i] for i in range(1, len(worker_actions))]

    final_liquidation = get_final_liquidation_orders(obs)
    if final_liquidation:
        market = final_liquidation[:MAX_MARKET_ORDERS]
    else:
        market = PENDING_MARKET_ORDERS.pop(0) if PENDING_MARKET_ORDERS else []
        sale_slots = MAX_MARKET_ORDERS - len(market)
        if sale_slots > 0:
            sale_orders = consolidate_market_orders(get_daily_harvest_sale_orders(obs))
            market += sale_orders[:sale_slots]
    market = filter_endgame_market_orders(obs, market)
    return {"farmer": farmer_action, "hands": hand_actions, "market": market[:MAX_MARKET_ORDERS]}
