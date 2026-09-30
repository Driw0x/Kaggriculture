# Heuristic Ideas — Final Consolidated Strategy

[← Previous design delta](./heuristic_ideas_v4.md) · Final consolidated version

> **Series convention**
>
> `heuristic_ideas_final.md` is **not another delta**. It is the complete standalone
> strategic snapshot obtained after applying `v1 -> v2 -> v3 -> v4` and resolving the
> remaining contradictions. It is the canonical standalone design reference for the heuristic branch.

## Identity

| Field | Value |
| --- | --- |
| Version | `final` |
| Associated agent | None — design only |
| Role | Complete standalone strategy snapshot |
| Built from | [`v4`](./heuristic_ideas_v4.md), with the full `v1 -> v4` inheritance already resolved |
| Canonical status | **Complete standalone strategy reference** |
| Implementation status | Design only — project closed without a validated dedicated agent |

## Status

This document consolidates `heuristic_ideas_v1` through `v4`, removes duplicated ideas,
resolves contradictions, and separates verified mechanics, active strategic rules,
economic rules, and benchmark-only historical heuristics.

It is the **single complete strategic design reference** for the resolved heuristic strategy.
The project closed without a validated implementation of this full design; it is retained for
traceability rather than presented as implemented behavior. The active fixed opening, worker
cap, land-purchase schedule, land order, triangular layout, and central `2 x 2` restriction
defined below are part of the design baseline and are not benchmark-only priors.

Historical formulas and dated micro-schedules that are explicitly classified as
benchmark-only remain disabled by default.

---

## 0. Rule precedence

When two rules conflict, apply them in this order:

1. **Game-mechanic constraint** — must never be violated.
2. **Feasibility / safety constraint** — resources, survival, deadlines, routes, storage,
   market slots, executable cash and the land-purchase cash floor.
3. **Active strategic rule** — fixed opening, strategic worker cap, scheduled land purchase,
   fixed expansion order, triangular placement geometry, and central `2 x 2` restriction.
4. **Accepted-plan preservation** — protect assets/actions that are still worth keeping.
5. **Marginal economic value** — choose the best incremental non-mandatory action.
6. **Routing / spatial efficiency** — reduce worker usage and travel.
7. **Benchmark-only historical heuristic** — disabled unless explicitly enabled for an
   isolated experiment.

Active strategic rules are deliberate commitments. They are not downgraded to optional
priors by the generic marginal-value model. They remain subject to mechanics and feasibility.

---

# 1. Verified mechanical baseline

The planner must model the following facts explicitly.

## 1.1 Survival and production

- A plant becomes a weed after two successive days without water.
- A newly planted crop must be watered on its planting day.
- An animal escapes after two successive days without Wheat.
- A newly placed animal may survive its first day without feeding, but normal planning
  should still account for the next survival deadline.
- Animal product stored on the tile is capped by `max_held`.
- Every surviving animal can make one fertilizer available per day; uncollected fertilizer
  does not accumulate.
- `CARE` behavior has an observed anomaly in the current reference tests, so aggressive
  care-skipping based only on a theoretical `pending_care_bonus` model is unsafe until the
  behavior is fully explained.

## 1.2 Storage

```text
SHED_CAPACITY = 100 non-seed items
```

Seeds do not consume shed capacity.

The exact overflow condition for a planned drop is:

```text
ProjectedShedAfterDrop > 100
```

A one-slot safety buffer may optionally be used:

```text
SafetyTarget = 99
```

but `99` is a policy target, not the real capacity.

## 1.3 Market actions

- At most 10 market orders may be submitted in one tick.
- Orders beyond the limit can be silently dropped by the environment.
- `BUY`, `SELL`, `HIRE`, and `BUY_LAND` therefore share one validated market calendar.
- Market order sequencing matters.
- Player orders interact with the opponent's orders and the price curve during execution.

## 1.4 Land

Expansion costs are:

```text
1st expansion = 1000
2nd expansion = 2000
3rd expansion = 4000
```

The expansion order is fixed by the game and must not be optimized or permuted by the
strategy:

```text
1st expansion -> NE
2nd expansion -> SW
3rd expansion -> SE
```

A purchased quadrant provides physical tiles only after the purchase is observed as
confirmed.

---

## 1.5 Workers

Farm hands are hired for the current day and hiring cost increases according to the daily
Fibonacci sequence. The hire-cost sequence resets on a new day.

The game-engine worker limit and the strategy worker cap are separate concepts.

The baseline strategy uses the following **active hard strategic cap**:

```text
MAX_WORKERS = 14
```

The planner must never accept a `HIRE` that would make the controlled workforce exceed 14,
even if a 15th worker would have positive estimated marginal value. This is a strategy rule,
not a claim about the engine's maximum possible worker count.

---

## 1.6 Shop demand

Shop composition changes demand and should be represented explicitly. Multiple instances
stack their demand.

A normal demanded product contributes roughly 6 units/day per shop instance; ×2 shops
contribute roughly 12 units/day for their doubled product.

---

# 2. Planner architecture

Use one coherent planning state rather than separate approximations.

```text
OBSERVE REAL STATE
    -> UPDATE SHARED FORECAST
    -> UPDATE MARKET / OPPONENT SCENARIOS
    -> GENERATE ECONOMIC CANDIDATES
    -> GENERATE DEPENDENCY-AWARE TASK GROUPS
    -> ASSIGN ROUTES + LOGISTICS + OPTIONAL HIRES
    -> VALIDATE CASH / STOCK / MARKET CALENDAR
    -> EXECUTE
    -> LOCAL REPAIR WHEN MATERIAL STATE CHANGES
```

Every subsystem reads the same forecast and reservations.

---

# 3. Shared forecast

Maintain one derived physical/economic forecast from the current tick **through the end of the game**.

Track at least:

- crop age, water state, fertilizer state, next production and decay;
- animal feed, care, product held, next production and saturation risk;
- current and reserved seeds/products/animals/fertilizer;
- worker position, availability, route suffix and carried inventory;
- shed stock and time-indexed incoming drops;
- tile occupation and future release;
- cash and committed spending;
- shop demand;
- expected own market orders;
- expected opponent market behavior;
- market inventory and expected price path;
- end-of-game cash-out feasibility.

After a change, update only affected forecast components when possible.

---

# 4. Separate farm production from market inventory

This is a critical correction retained by the consolidated economic model.

A crop becoming harvestable does **not** directly add units to global market inventory.
Production first becomes farm/worker/shed inventory. Global market inventory changes only
when units actually enter or leave the market or are consumed.

Use two separate forecasts.

## 4.1 Farm-side supply forecast

```text
FarmOutput(t) = expected harvest / animal production available to us at t
```

This determines what we may later hold, consume, or sell.

## 4.2 Market-inventory forecast

```text
MarketInventory(t + 1) =
    MarketInventory(t)
    + ExpectedOurSales(t)
    + ExpectedOpponentSales(t)
    - ExpectedOurPurchases(t)
    - ExpectedOpponentPurchases(t)
    - ShopConsumption(t)
```

Only include any other consumption source if it is explicitly represented by the current
environment/rules.

Then:

```text
ExpectedPrice(t) = PriceFunction(ExpectedMarketInventory(t))
```

This prevents the planner from pricing unsold produce as if it had already flooded the
market.

---

# 5. Opponent model: scenarios, not false precision

Track visible opponent capacity:

- planted crop type / count / age;
- animal type / count;
- expected maturity and production dates;
- visible harvest events;
- observed market inventory changes consistent with opponent buying/selling.

Maintain three bounded scenarios without inventing probability weights:

```text
LOW opponent supply
BASE opponent supply
HIGH opponent supply
```

Baseline convention:

- use `BASE` as the central scenario for expected-value ranking;
- use `LOW` and `HIGH` to expose sensitivity and market-crash risk;
- do not compute an arbitrary weighted mean unless explicit scenario weights are later
  configured and benchmarked;
- do not invent a numeric `RiskPenalty` coefficient.

When two choices have equal `BASE` value, prefer the one that remains feasible and
less fragile across `LOW/HIGH` scenarios before applying the global tie-break rules.

Confirmed observations receive full confidence. Unrevealed future shop/opponent behavior
must remain scenario-based rather than being converted into false precision.

---

# 6. Economic acceptance rule

A non-mandatory economic candidate is accepted only if its **complete incremental cash-out chain** is feasible and
valuable. Active strategic commitments defined by this document are handled by their own gates.

For a candidate `i`:

```text
IncrementalValue_i =
    IncrementalExpectedSalesRevenue
    - IncrementalDirectCashCost
    - IncrementalFeedOpportunityCost
    - IncrementalHireCost
    - IncrementalHolding / StorageCost
    - IncrementalRoutingOpportunityCost
```

Optional strategic terms may be added only when they represent a real future option:

```text
+ LayoutOptionValue
+ DemandHedgeValue
+ ResourceSecurityValue
```

Acceptance gate:

```text
IncrementalValue_i > 0
AND all feasibility constraints pass
AND cash-out can occur before the game ends
```

Do not accept a candidate merely because it has a high ratio score if its absolute value is
negative.

---

# 7. Land scarcity and land-time value

Land-time efficiency is useful only when land is actually scarce.

For ranking feasible positive-value candidates under land pressure:

```text
LandEfficiency_i =
    IncrementalValue_i
    / EffectiveOccupiedLandTime_i
```

Do not use this ratio as the universal objective. When land is not binding, absolute
incremental value matters more.

Distinguish:

```text
PhysicalOccupancy = real map tiles reserved over time
EconomicEffectiveLand = optional comparison metric
```

For example, the historical `5/3` poultry-equivalent land value may remain an experimental
economic weight, but it must never replace real tile reservations.

---

# 8. Labor economics

## 8.1 Feasibility first

Existing workers are assigned first. A new hire is tested only when useful accepted work
cannot otherwise be completed economically.

## 8.2 Correct marginal hire test

Let:

```text
ProfitWithoutHire = best feasible plan with A workers
ProfitWithHire    = best feasible plan with A + 1 workers
MarginalWorkerValue = ProfitWithHire - ProfitWithoutHire
```

Hire only if:

```text
MarginalWorkerValue > NextHireCost
```

and the new worker actually makes the relevant work feasible.

## 8.3 Labor shadow cost

Do **not** use:

```text
Va * required_actions
```

when `Va` is already the total value of another whole worker; this mixes units and can
massively double-count labor.

Instead estimate a per-tick / per-action opportunity cost from scarce worker capacity:

```text
LaborShadowCostPerTick ~=
    value of the best displaced task per scarce worker tick
```

or use the exact delta between the best schedule with and without the candidate.

The exact schedule delta is preferred when cheap enough.

## 8.4 Active worker cap

```text
MAX_WORKERS = 14
```

This cap is **ON by default** and is part of the baseline strategy.

Hiring still requires positive marginal value and real schedule feasibility, but even a
profitable hire is rejected if it would create worker 15 or above.

---

# 9. Asset preservation is conditional, not absolute

Survival priorities apply only to assets the accepted plan still intends to keep.

Define:

```text
KeepAsset(asset) = remaining expected value of preserving asset > abandonment alternative
```

Then:

- survival `WATER` is `CRITICAL` only for a plant worth preserving;
- survival `FEED` is `CRITICAL` only for an animal worth preserving;
- late fertilizer / care / feed with no cashable future effect should be removed;
- an existing sunk-cost asset may be abandoned if its remaining operating value is
  negative.

This resolves the conflict between early-game survival priorities and endgame liquidation.

---

# 10. TaskGroup model

Generate stable dependency-aware `TaskGroup` objects directly.

```text
TaskGroup:
    id
    position
    ordered_actions[]
    priority
    deadline
    required_resources
    expected_incremental_value
    dependencies
    assigned_worker_or_none
```

Stable IDs must prevent duplicate planning when generation runs twice without a material
state change.

Prerequisites inherit the urgency of their dependent task.

---

# 11. Action priority

Use a conditional priority hierarchy.

## CRITICAL

Only when the underlying asset/action remains part of the accepted plan:

- survival watering;
- survival feeding;
- harvest before decay / saturation / irreversible loss;
- mandatory planting-day watering;
- storage release required before a mandatory incoming drop;
- market dependency required before a hard deadline.

## PRODUCTION

- profitable planned harvest;
- required plant/build/place;
- required productive feed;
- required resource pickup / purchase.

## YIELD

- profitable fertilizer;
- profitable care;
- yield-increasing water.

## PREPARATION

- dig blocking accepted production;
- installation for accepted future production.

## SECONDARY

- non-urgent fertilizer collection;
- optional weed removal;
- optional route-local work.

---

# 12. Action ordering: use dependencies, not one universal sequence

Avoid a universal animal sequence such as:

```text
FEED -> HARVEST -> CARE -> COLLECT
```

for every visit.

Instead enforce only dependencies that matter in the current state.

Examples:

- `FEED -> CARE` when care requires the animal to be fed that day;
- `HARVEST` before the next production event when `max_held` saturation would lose output;
- `HARVEST` before endgame return/sale deadlines;
- `COLLECT_FERTILIZER` only when its value exceeds the action/travel opportunity cost;
- for crops, `FERTILIZE -> WATER` when fertilizer must already be active for that watering
  event to improve yield;
- `WATER -> HARVEST` only when same-day watering changes the harvestable yield being taken.

This avoids spending actions simply to respect a historical fixed ordering.

---

# 13. Animal CARE policy

Because current reference tests report an unresolved care anomaly, use conservative CARE
logic.

CARE is allowed when:

```text
expected additional saleable yield
    * expected marginal sale value
>
CARE action/travel opportunity cost
```

but do not aggressively skip care solely because a simplified `pending_care_bonus`
calculation predicts no benefit.

Candidate CARE schedules such as `skip T5` or `skip T5-T7` remain benchmark-only until the
production anomaly is explained and reproduced reliably.

---

# 14. Animal HARVEST policy

Harvest animal output when at least one condition holds:

```text
1. saturation risk before the next opportunity to harvest
2. planned near-term sale requires the output
3. an existing route passes close enough that marginal labor/travel cost is low
4. endgame requires collection now to allow return + DROP + SELL in time
```

Otherwise defer harvest to save labor.

Endgame rule:

- if the final useful animal production must be sold on the last playable day, schedule the
  harvest early enough — potentially the previous day — to guarantee return, drop, and sale.

---

# 15. Placement policy

Placement first obeys hard geometry, then uses economic/routing tie-breaks. Do not invent
weighted placement coefficients.

## 15.1 Mandatory center-facing `5 x 5` triangular animal layout

Rows below are written north-to-south and columns west-to-east.

`1` = allowed animal-placement cell under the triangular layout.  
`*` = not an animal-placement cell.

For the NW quadrant, use exactly:

```text
NW
* * * * 1
* * * 1 1
* * 1 1 1
* 1 1 1 1
1 1 1 1 1
```

Apply exact symmetry for the other quadrants:

```text
NE
1 * * * *
1 1 * * *
1 1 1 * *
1 1 1 1 *
1 1 1 1 1
```

```text
SW
1 1 1 1 1
* 1 1 1 1
* * 1 1 1
* * * 1 1
* * * * 1
```

```text
SE
1 1 1 1 1
1 1 1 1 *
1 1 1 * *
1 1 * * *
1 * * * *
```

Animals must be placed inside the `1` cells of the corresponding center-facing triangle.
When several eligible cells exist, fill/choose within the triangle using the global
tie-break order rather than an arbitrary weighted score.

## 15.2 Central `2 x 2` long-term-crop exclusion

The central `2 x 2` high-connectivity area has an **absolute baseline prohibition** on
long-term crops:

```text
if tile in CENTRAL_2X2 and crop is LONG_TERM_CROP:
    placement is forbidden
```

This is an active strategic layout constraint, not an opportunity-cost preference.
Short-term production and non-crop uses remain governed by their own feasibility rules.
The implementation must use the project's explicit long-term-crop classification if one
exists; it must not invent a duration threshold silently.

## 15.3 Placement tie-break without arbitrary weights

After hard geometry and feasibility are satisfied, compare placements in this order:

```text
1. higher expected economic value
2. smaller deadline slack
3. fewer worker/labor ticks required
4. less travel
```

If still tied, use a stable deterministic coordinate order so repeated planning produces
the same result.

---

# 16. Land purchase

Land purchase has two modes: **scheduled strategic expansion** and **unscheduled economic
expansion**.

## 16.1 Scheduled strategic expansion

The baseline schedule is active and uses the game-defined order `NE -> SW -> SE`.
Here `Tn` denotes **day n**; submit the purchase at the earliest legal market tick of that day.

```text
T4:
    BUY NE

AT T7, once the first two shops are known:

    IF the first two shops contain animal demand:
        T7  -> BUY SW
        T12 -> BUY SE

    ELSE:
        T9 -> BUY SW
        no mandatory T12 SE purchase
```

The first `NE` purchase is therefore independent of the first-two-shop branch.
The branch changes the timing of `SW` and whether `SE` is mandatory at `T12`.

Each scheduled purchase is executed when all of the following hold:

```text
purchase is legal and executable
AND required market slot is available
AND cash-floor / operating-reserve constraint passes
```

Use the explicit cash floor:

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

When a more exact operating-reserve calculation is available, it may additionally verify:

```text
CashAfterPurchase >=
    ImmediateDeploymentCost
    + RequiredOperatingSpendUntilNextReliableIncome
```

A scheduled purchase is an active strategic commitment; it is **not cancelled solely
because the generic no-land marginal-value comparison would prefer not to expand**.
Mechanics and cash/feasibility still override it.

If a scheduled purchase cannot execute at its target time because the cash floor or a hard
mechanical dependency fails, keep it pending and re-evaluate at the earliest legal tick;
do not silently delete the commitment.

## 16.2 Unscheduled / additional expansion

Any land purchase not required by the schedule above uses the economic land gate:

1. compute the best no-purchase plan;
2. simulate the next legal expansion on a copied state;
3. reserve exact future use of the new tiles;
4. include deployment, maintenance, worker capacity, routing, stock and sales;
5. validate the market calendar and cash reserve;
6. require positive incremental realizable final cash.

After any purchase is confirmed, its cost is sunk. Future production on that land is
re-evaluated from remaining costs and value only.

---

# 17. Shop-dependent expansion branch

The first two shops are used only when the branch becomes observable at `T7`.
They do **not** retroactively affect the mandatory `T4 -> NE` purchase.

Define `animal demand` exactly as: at least one of the first two shops consumes
`EGG`, `MILK`, or `WOOL`.

Decision summary:

```text
T4 -> NE always

At T7:
    first two shops contain animal demand
        -> SW at T7
        -> SE at T12

    first two shops contain no animal demand
        -> SW at T9
        -> no mandatory SE at T12
```

The expansion direction itself is not a choice: the engine order is `NE -> SW -> SE`.
The strategy chooses only whether/when the scheduled purchase is triggered according to the
rule above.

---

# 18. Event-driven phases instead of hard phase boundaries

The historical phases:

```text
T0-T3
T4-T20
T20-T30
```

are useful descriptive priors but should not be hard strategy switches.

Prefer event-driven regime changes:

```text
OPENING:
    little shop information, establish resilient production

EXPANSION / ADAPTATION:
    new shop information materially changes marginal values

CAPACITY-LIMITED MIDGAME:
    land/labor/storage become binding constraints

LIQUIDATION HORIZON:
    new investments fail full cash-out feasibility
```

The exact transition tick emerges from the forecast rather than a fixed date.

---

# 19. Inventory reservations

For each product maintain:

```text
AvailableStock
ReservedForOperations
ReservedForConfirmedDemand
ReservedForPlannedProduction
UncommittedStock
```

Do not use product-specific fixed reserve quantities when a dated forecast can calculate the
need directly.

Historical reserves remain fallback priors:

- Wheat: feed + emergency reserve;
- Egg: small reserve with Bakery/Brunch demand;
- Carrot: short reserve with PetCafe/Farmers Market demand;
- Strawberry/Milk: larger reserve when a near-term shortage is confirmed;
- Wool: reserve when Yarn demand is active or highly likely;
- Melon/Fertilizer: generally avoid long holding under weak demand.

---

# 20. Shed overflow

Use a time-indexed projection.

For every future drop event `d`:

```text
ProjectedShed(d) =
    current shed
    + all prior planned drops
    - all prior planned sells / uses / purchases from shed
```

Required emergency liquidation:

```text
RequiredNeedSell = max(0, ProjectedShed(d) - 100)
```

Optional one-slot safety version:

```text
SafetyNeedSell = max(0, ProjectedShed(d) - 99)
```

Do not blindly add all workers' carried inventory: count only inventory expected to reach the
shed before the relevant capacity event.

---

# 21. Selling: exact marginal simulation

The historical split-sale equation using `P1/P3/P4/P5` is retained only as intuition. The
baseline sale engine enumerates every realizable quantity.

For each product with `stock` currently sellable units:

```text
for q in 0 .. stock:
    simulate selling exactly q units
    compute the exact marginal revenue sequence
    propagate market inventory / price effects
    propagate enabled cash-dependent BUY / HIRE actions
    evaluate retained stock value

choose q with the highest resulting expected final value
```

`stock` here means **uncommitted sellable stock after operational, production and confirmed
demand reservations**, not raw shed inventory.

When opponent behavior matters, run the same sale quantities through `LOW / BASE / HIGH`
opponent scenarios. Baseline ranking uses `BASE`; `LOW/HIGH` are robustness checks without
invented probability weights.

Revenue must be computed from the actual marginal price path, not `q * initial_price`.
All candidate sales remain subject to the 10-market-orders-per-tick calendar and liquidity
requirements.

---

# 22. Sell versus hold

For each next unit:

```text
MarginalSellValue(unit) = simulated cash received if this unit is sold now
```

Compare against:

```text
RetentionValue(unit) = max(
    FutureExpectedResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

Sell while:

```text
MarginalSellValue > RetentionValue
```

However, when selling now unlocks a more profitable constrained action, include that
liquidity value explicitly.

---

# 23. Liquidity value instead of arbitrary financial discounting

Do not rely on the experimental formula:

```text
FuturePrice / (1 + r)^h
```

with an inferred `r` unless it is validated empirically.

Kaggriculture has a short finite horizon. The main cost of delayed cash is the **best action
that cannot be financed while waiting**.

Prefer:

```text
LiquidityOpportunityCost =
    Profit(best feasible plan with cash now)
    - Profit(best feasible plan without that cash until t+h)
```

Then:

```text
FutureResaleValueAdjusted =
    ExpectedFutureSaleRevenue
    - LiquidityOpportunityCost
    - HoldingRisk
```

A simpler bounded approximation may be used if exact comparison is too expensive.

---

# 24. Cash urgency

Avoid unbounded or negative urgency coefficients.

```text
NearTermShortfall = max(
    0,
    RequiredCommittedSpendBeforeNextReliableIncome
    - LiquidCashAvailable
)

CashUrgency =
    NearTermShortfall
    / max(1, RequiredCommittedSpendBeforeNextReliableIncome)
```

Therefore:

```text
0 <= CashUrgency <= 1
```

Use this as a liquidity bonus in sale evaluation, not as an independent reason to sell a
large batch at a terrible price.

---

# 25. Price impact and opponent timing

Do not fill the entire estimated market shortage automatically.

Evaluate the next sale unit against its marginal price.

When opponent supply is expected soon:

- consider selling profitable units before the opponent's maturity/release;
- retain units only when expected recovery/demand is worth the delay;
- avoid synchronized dumping of oversupply-sensitive products;
- use observed opponent actions to update the scenario immediately.

The exact market simulator should replace fixed rules like "always clear before opponent
maturity" whenever enough information is available.

---

# 26. Production quantity

For every candidate product, grow production **one incremental unit at a time**.

```text
k = current_quantity + 1

while k is physically and operationally feasible:
    MV = marginal value of adding unit/tile/animal k

    if MV <= 0:
        stop

    accept k
    k += 1
```

Stop immediately when either:

- `MV <= 0`; or
- a binding constraint prevents the next unit: land/tile-time, worker cap/capacity, cash,
  feed, storage, deadline, market slot, or endgame cash-out feasibility.

Do not jump directly to a demand-gap quantity and do not invent a fixed production cap
unless another active rule explicitly defines one.

---

# 27. Wheat as an operating resource

Wheat has both sale value and feed value.

Compute a dated feed requirement:

```text
RequiredWheat(t0..t1) =
    feed actions required by accepted animal plan
    + safety reserve for survival risk
```

Subtract Wheat already held and Wheat that will mature before each feed deadline.

Only excess Wheat is freely sellable.

Compare self-production against market purchase using the same marginal-value framework:

```text
cost of Wheat land + labor + delayed cash-out
vs
expected market purchase cost at feed date
```

This replaces a fixed `5 * animal_q - next5day_maturity` reserve when a more accurate dated
forecast is available.

---

# 28. Fertilizer

Because animal fertilizer does not accumulate, collecting it is not automatically valuable.

Collect only when at least one is true:

- a profitable fertilization task needs it;
- expected sale value exceeds collection/travel opportunity cost;
- collection fits nearly free into an existing route;
- failing to collect now destroys meaningful value that cannot be recovered later.

Fertilize only when incremental future cashable yield/timing benefit exceeds fertilizer,
labor, travel and alternative-use costs.

---

# 29. Product-specific behavior is a fallback, not the economy engine

Keep broad product characteristics as priors:

- Wheat: operating/feed reserve first;
- Carrot: fast-turnover and scarcity-sensitive;
- Tomato: ongoing output, scarcity-sensitive;
- Strawberry: high price but highly oversupply-sensitive;
- Melon: large unit value but highly oversupply-sensitive;
- Egg: frequent animal output and relatively oversupply-resistant;
- Milk: high value, oversupply-sensitive;
- Wool: high value, strongly oversupply-sensitive;
- Fertilizer: use or sell when collection is worthwhile.

Historical product-specific fixed schedules and score formulas must not override the shared
marginal model.

---

# 30. Routing, logistics and hires

For every unassigned `TaskGroup`, test insertion into existing routes.

Insertion cost includes:

```text
travel
+ actions
+ pickup / resource acquisition
+ waiting
+ return / DROP
+ deadline risk
+ inventory effect
+ market dependency effect
```

Choose the cheapest feasible insertion.

If important accepted work remains unassigned, test a new worker using the exact marginal
hire logic.

After obtaining feasible routes, use only small local moves/swaps. Do not introduce a
complex global VRP solver unless benchmark evidence justifies it.

---

# 31. Resource reservations

Every accepted task reserves the resources it will need at the relevant time.

Examples:

- seeds;
- Wheat feed;
- fertilizer;
- purchased animal;
- shed capacity;
- market order slot;
- worker-time;
- physical tile-time.

A delayed/failed purchase, hire, land purchase, or sale invalidates dependent reservations
and triggers local repair.

---

# 32. Deployment capacity: use time-indexed tile reservations

Do not use the static historical constraint:

```text
sum(seed_units) + animals <= currently_free_tiles
```

as the final rule.

Instead validate physical occupancy over time:

```text
for each placement interval [start, release):
    reserve exact tile
    reject overlapping incompatible reservations
```

This allows production to use tiles that will be freed before deployment and prevents the
economic `effective land` metric from being confused with physical occupancy.

---

# 33. Local replanning

Replan only when a change affects feasibility, expected-value sign, or the chosen economic
action.

Relevant changes include:

- new shop;
- meaningful market price/inventory movement;
- opponent planting, harvesting, buying or selling;
- unexpected weed / escaped animal;
- production different from forecast;
- failed or delayed market action;
- route delay;
- stock/cash conflict;
- land confirmation;
- endgame horizon crossing.

Preserve:

- confirmed facts;
- completed actions;
- paid workers;
- still-valid route prefixes;
- still-valid reservations.

Release only affected future reservations and route suffixes.

---

# 34. Endgame

Endgame is evaluated inside every new decision, not only in a cleanup pass.

A new crop, animal, land purchase, fertilizer use, or hire is rejected if the full chain:

```text
install
-> maintain
-> produce
-> harvest
-> return
-> DROP
-> SELL
```

cannot create positive realizable final cash before the last executable sale.

Plan backward from the final sale:

```text
last SELL
<- required DROP
<- required return travel
<- required HARVEST
<- required maintenance / production
```

If the configured environment uses the known `episodeSteps = 720` schedule, keep an explicit
regression test that final liquidation is completed by the last actually executable tick
(current project convention: day 29, hour 22).

Never rely on an automatic post-game deposit.

---

# 35. Fixed opening strategy

The baseline uses the fixed opening package below. It is **ON by default** and is
not merely a benchmark seed.

Target opening quantities:

| Item | Quantity |
| --- | ---: |
| Wheat crop | 10 |
| Carrot | 6 |
| Tomato | 1 |
| Strawberry | 2 |
| Melon | 2 |
| Goose | 1 |
| Cow | 2 |
| Sheep | 1 |
| Wheat stock | 16 |
| Initial farm-hand hires | 4 |

Opening rules:

- create/place/plant the target package as early as mechanics and action capacity allow;
- mandatory same-day watering for newly planted crops remains non-negotiable;
- animals obey the mandatory center-facing triangular placement mask;
- long-term crops may not occupy the central `2 x 2`;
- acquire and reserve enough Wheat to support the fixed animal package;
- do not replace the fixed counts with marginal-search quantities during the opening build;
- once the opening package is established, normal shared-forecast and marginal planning takes
  over for additional production.

Use actual observed prices/costs and game state during execution. Recorded historical total
costs are not treated as mechanics constants.

---

# 36. Objective

The game objective is final bank money.

Therefore the core planner objective should remain:

```text
maximize expected final realizable cash
```

Opponent modeling is useful because the opponent changes prices and winning depends on the
relative final result, but do not replace absolute value with the historical heuristic:

```text
MarginMax = OurProfit - OpponentProfit
```

unless a separate competitive policy is deliberately benchmarked.

Primary production and operating decisions should not destroy our own expected cash merely
to reduce an estimated opponent profit.

---

# 37. Historical ideas retained only for benchmark

The following remain **disabled by default** and must not affect the baseline agent unless an
isolated benchmark explicitly enables them:

- fixed CARE skip days such as `T5` or `T5-T7`;
- fixed fertilizer / harvest dates such as `T8`, `T10`, `T12`, `T14`, `T16`;
- historical product score formulas with ambiguous parentheses;
- historical `Dtotal` formulas with undefined/repeated abbreviations;
- `Va * required_actions` as labor cost;
- the inferred financial discount rate `r`;
- raw farm production directly added to global market inventory;
- the `P1/P3/P4/P5` split-sale inequality as the final sale engine;
- `NeedSell = Shed + Carry + Incoming - 99` as the exact storage equation;
- static `seeds + animals <= free tiles` as deployment capacity;
- rigid `T0-T3 / T4-T20 / T20-T30` strategy-mode switches.

The following are **no longer benchmark-only** and are active baseline rules:

- worker cap `14`;
- fixed opening package;
- scheduled land purchases `T4/T7/T9/T12` with the shop branch defined in §16-17;
- fixed expansion order `NE -> SW -> SE`;
- mandatory symmetric `5 x 5` triangular animal layout;
- absolute central `2 x 2` prohibition for long-term crops.


### 37.1 Historical alternative opening

The following day-1 quantities were recorded as an alternative opening candidate and remain
available only for isolated benchmark comparison:

| Product | Historical day-1 candidate quantity |
| --- | ---: |
| Melon | 2 |
| Carrot | 6 |
| Egg production | 1 |
| Wool production | 1 |
| Milk production | 2 |
| Strawberry | 2 |
| Wheat | 2 |
| Tomato | 2 |

They do not override the active fixed opening in §35.

### 37.2 Historical phase boundaries

The fixed descriptive phases are preserved as historical priors:

```text
T0-T3   -> opening
T4-T20  -> expansion / adaptation
T20-T30 -> liquidation-oriented play
```

The active planner uses the event-driven regimes in §18 instead of treating these boundaries
as hard switches.

### 37.3 Historical expansion timing and fill patterns

Older notes recorded the timing ceiling:

```text
first land  < T7
second land < T12
third land  < T12
```

They also proposed candidate new-land fill patterns:

- SW: `4 x 4` triangle, `4 x 4` square, or conditional partial fill;
- SE: `4 x 4` triangle, center-near `4 x 4` subset, or conditional partial fill.

These remain benchmark-only. The active expansion schedule and geometry are defined in
§15-17.

### 37.4 Historical effective-land weight

The old economic comparison used:

```text
plant effective land   = 1 tile
poultry effective land = 5 / 3 tiles
```

This can be benchmarked as an economic comparison weight, but it must never replace the exact
physical tile-time reservations in §32.

### 37.5 Historical opponent and demand approximations

The older opponent model proposed:

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

and demand confidence:

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

The final baseline instead keeps `LOW / BASE / HIGH` opponent scenarios without inventing
probability weights. These formulas are preserved only as possible experimental approximations.

### 37.6 Historical long-horizon market approximation

When an event-by-event projection was considered too expensive, the notes proposed:

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

This approximation is benchmark-only. The active model keeps farm-side output separate from
global market inventory and prefers the dated inventory path in §4.

### 37.7 Historical product score formulas

The following score ideas are preserved exactly as strategy notes. Their original
parenthesization was not fully specified, so they must not silently become baseline formulas.

| Product | Historical score idea |
| --- | --- |
| Melon | `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
| Carrot | `sum(q * dynamic_price) - 20 - labor / land_occupation` |
| Egg | `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
| Wool | `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
| Milk | `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
| Strawberry | `sum(q * dynamic_price) - 100 - labor / land_occupation` |
| Wheat | `sum(q * dynamic_price) - 10 - labor / land_occupation` |
| Tomato | `sum(q * dynamic_price) - 50 - labor / land_occupation` |

### 37.8 Historical demand formulas

The original abbreviations were not fully defined. Repeated terms are intentionally preserved
rather than silently corrected.

| Product | Historical `Dtotal` formula |
| --- | --- |
| Melon | `Dtotal = 1/day` |
| Carrot | `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
| Egg | `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
| Wool | `Dtotal = Dm + 12 * Ny * q` |
| Milk | `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
| Strawberry | `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
| Wheat | `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
| Tomato | `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

### 37.9 Historical competitive-margin signal

The notes proposed:

```text
MarginMax = OurProfit - OpponentProfit
```

It may be benchmarked as a secondary signal, but §36 keeps expected final realizable cash as
the baseline objective.

### 37.10 Historical financial discounting

The old sell/hold model proposed:

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h

r =
    ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h)
    - 1
```

The exact horizon aggregation was not fully specified. The final baseline therefore uses the
liquidity-opportunity-cost model in §23 unless a discount-rate experiment is explicitly enabled.

### 37.11 Historical split-sale comparison

The older tactical notes compared selling `n + m` immediately with splitting the sale:

```text
P  = average price
n  = quantity sold now
P1 = current price
D  = shop consumption
m  = later quantity we may sell before opponent maturity
x  = opponent quantity sold one day before our later sale
P3 = opponent sale price before our later sale
P4 = our resulting price after that opponent sale
P5 = opponent's later price after our n + m sales and before our next maturity
```

Historical split-sale condition:

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

This remains intuition/benchmark material. The active sale engine in §21 enumerates realizable
sale quantities directly.

### 37.12 Historical overflow and deployment shortcuts

Older notes used:

```text
NeedSell = Shed + Carry + Incoming - 99
```

and:

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

They are retained only as shortcuts for experiments. The active planner uses true shed
capacity `100`, time-indexed incoming inventory, and exact tile-time reservations.

### 37.13 Historical animal action ordering

The old productive-visit sequence was:

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

The final baseline does not enforce this universally. §12 keeps only dependencies that matter
for the current state.

### 37.14 Historical product-level inventory and timing heuristics

The following product rules remain available as benchmark priors, not baseline overrides:

- Fertilizer: prefer immediate sale when not needed for profitable near-term fertilization.
- Melon: avoid long holding; an old note capped combined production around `120`.
- Wheat: old reserve estimate `5 * animal_q - WheatExpectedToMatureInNext5Days`.
- Egg: with Bakery/Brunch demand, keep roughly one day of demand; old policy used daily `CARE`.
- Carrot: with PetCafe/FarmersMarket demand, keep roughly two days of demand; old rule used no fertilization.
- Tomato: historical fertilize/harvest idea around `T8`, `T9`, and `T11`.
- Strawberry: historical fertilize/harvest idea around `T10`, `T12`, `T14`, and `T16`.
- Milk: with relevant demand, keep roughly two days of net demand; old CARE schedule skipped around `T5-T7`.
- Wool: keep when waiting for Yarn demand; old CARE schedule skipped around `T5`.

The associated historical inventory classes were:

```text
Class 1 — operating inventory only: Wheat
Class 2 — fast turnover: Carrot
Class 3 — balanced: Tomato, Egg
Class 4 — high-value timing inventory: Strawberry, Milk, Wool
Class 5 — avoid long holding: Melon, Fertilizer
```

The active planner instead derives reservations from the dated forecast and uses the broad
product characteristics in §29 only as fallback priors.

### 37.15 Historical market-aware sale biases

When the full marginal simulator is disabled for an isolated benchmark, the old notes suggested:

- Carrot / Egg / Wheat / Tomato: sell earlier under cash pressure;
- Wool: wait for Yarn when plausible;
- Milk / Strawberry: prefer high-price windows;
- Melon: sell immediately or before expected opponent supply;
- under shed pressure: sell in profit-priority order rather than FIFO.

These rules must not override the baseline sell/hold and exact quantity logic in §21-25.


---

# 38. Final hard / near-hard invariants

1. Never violate an actual game-mechanic limit.
2. Never exceed the active strategic worker cap of `14`.
3. Never leave a newly planted crop without required same-day water.
4. Never miss survival maintenance for an asset that the accepted plan intends to keep.
5. Never spend maintenance on an asset whose best remaining plan is abandonment.
6. Never route work without its required resources and dependencies.
7. Never allow a required drop to exceed the true shed capacity `100`.
8. Never submit more than 10 market orders in one tick.
9. Never assume pending land is already unlocked.
10. Never count unsold farm production as global market inventory.
11. Never place animals outside the active quadrant's center-facing triangular `1` mask.
12. Never place a long-term crop in the central `2 x 2`.
13. Preserve the fixed opening counts during the opening build unless mechanics make a
    requested action temporarily impossible.
14. Preserve the scheduled land commitment: `T4 NE`; then at `T7`, animal-demand branch ->
    `T7 SW` + `T12 SE`, otherwise `T9 SW` and no mandatory `T12 SE`.
15. A scheduled land purchase may be delayed by mechanics/cash-floor failure, but must not be
    silently dropped.
16. Never accept a non-mandatory hire merely because work exists; require positive marginal
    value and worker count `< 14` before the hire.
17. Never accept an unscheduled land purchase merely because the field is full; require
    positive incremental final cash versus the no-land plan.
18. Never accept a non-mandatory new investment that cannot complete its full cash-out chain
    before game end.
19. Never silently truncate a dependency because of market-slot pressure.
20. Never duplicate task groups/reservations after a no-change replan.
21. Preserve committed valid work and repair only affected future suffixes.

---

# 39. Verification suite for the final design

Any implementation claiming to follow the final strategy should not be considered faithful until these cases pass.

## Mechanics

- newly planted crop with no same-day water -> planner rejects route;
- retained animal at survival deadline -> FEED is scheduled;
- abandoned/unprofitable late animal -> survival FEED may be intentionally omitted;
- shed at 95 with incoming drop 10 -> at least 5 capacity must be freed before drop;
- safety-buffer mode for the same case -> free 6 to target 99;
- seeds do not count toward shed capacity;
- market calendar never emits >10 orders in one tick.

## Market model

- farm harvest without sale -> global market inventory unchanged;
- our sale -> global inventory increases and next marginal sale price is recomputed;
- our purchase -> global inventory decreases;
- shop consumption -> global inventory decreases;
- two-player simultaneous sale scenario -> revenue uses the environment's sequential /
  interleaved marginal prices, not `quantity * initial_price`;
- LOW/BASE/HIGH opponent scenarios can change sale quantity without breaking feasibility.

## Labor

- new worker that only executes negative-value optional work -> no HIRE;
- new worker that saves a profitable deadline-critical task and covers hire cost -> HIRE;
- a 15th worker is rejected by the active strategic cap even when its isolated marginal value is positive.

## Land

- full current field but no additional positive-value production -> no BUY_LAND;
- profitable production with infeasible maintenance -> no BUY_LAND;
- profitable expansion that violates operating cash reserve -> no BUY_LAND;
- confirmed land with a now-bad reserved crop -> cancel crop despite sunk land cost;
- `T4 -> NE` is scheduled independently of shop demand;
- at `T7`, animal demand in the first two shops schedules `SW` immediately and `SE` at `T12`;
- at `T7`, no animal demand schedules `SW` at `T9` and does not force `SE` at `T12`;
- a scheduled purchase failing the cash floor is delayed/pending rather than silently dropped;
- expansion direction is never permuted away from `NE -> SW -> SE`.

## Opening and placement

- fixed opening target counts match §35;
- opening planner does not substitute marginally preferred quantities before the fixed package is built;
- NW/NE/SW/SE triangle masks are exact symmetries of the specified `5 x 5` template;
- animal placement outside a `1` cell is rejected;
- long-term crop placement inside `CENTRAL_2X2` is rejected.

## Inventory

- only inventory scheduled to reach shed before a target drop contributes to that capacity
  event;
- Wheat required before future feed deadlines cannot be sold as uncommitted stock;
- future shop demand reserves affect sell/hold value;
- storage pressure can force a sale even when waiting has higher standalone unit price.

## Endgame

- investment whose first realizable sale is after game end -> rejected;
- animal harvest that must be sold on final day -> harvested early enough to guarantee
  return/drop/sale;
- no final worker carries valuable unsold inventory;
- no planner decision assumes post-game automatic liquidation.

## Replanning

- repeated generation with unchanged state -> identical task IDs, no duplicates;
- delayed HIRE invalidates only dependent future route capacity;
- failed BUY invalidates dependent pickup/plant tasks;
- new shop recomputes affected demand, prices, reserves and production quantities;
- unrelated price movement does not rebuild unaffected routes.

---

# 40. Benchmark protocol for uncertain heuristics

For every optional heuristic, compare against the same final baseline with paired seeds and
the same opponent policy.

Record at least:

```text
mean final money
median final money
minimum final money
win rate / money difference if relevant to the evaluation setup
mean hires per day
land purchase timing
idle worker ticks
missed critical tasks
shed overflow incidents
market-order truncation incidents
unrealized final inventory
runtime
```

Promote an experimental heuristic only when:

```text
1. it improves the chosen primary metric,
2. it does not introduce a clear tail-risk regression,
3. the gain survives more than a tiny seed sample,
4. the implementation does not duplicate an existing planner mechanism.
```

---

# 41. Final strategy summary

The final planner should behave as follows:

```text
1. Execute the fixed opening package.
2. Observe the real game state and maintain one forecast through game end.
3. Keep farm inventory and global market inventory separate.
4. Model opponent supply with LOW / BASE / HIGH scenarios without arbitrary weights.
5. Enforce MAX_WORKERS = 14.
6. Enforce the center-facing 5x5 triangular animal masks and central 2x2 long-crop ban.
7. Follow the active land schedule:
       T4 -> NE
       at T7: animal-demand branch -> SW T7 + SE T12
              no-animal-demand branch -> SW T9, no mandatory SE T12
8. Generate non-mandatory production one unit at a time until MV <= 0 or a constraint binds.
9. Reserve exact tile-time, stock, cash, market slots and worker-time.
10. Protect valuable assets; abandon negative-value sunk assets.
11. Route existing workers first; hire only on positive marginal schedule delta and below cap 14.
12. Enumerate sale quantities q = 0..sellable_stock with the exact market simulator.
13. Use the deterministic tie-break: value -> smallest slack -> less labor -> less travel.
14. Replan locally when observations materially change feasibility or value.
15. Plan final harvest/drop/sale backward so value becomes cash before game end.
```

The key design principle is:

> **Mechanics define what is possible; active strategy defines the committed baseline;
> feasibility defines what can execute; marginal final cash optimizes everything that remains
> optional.**


---

# 42. Version-to-final traceability

The historical idea documents are now a strict lineage, while this file is the complete
standalone result:

| Design version | Associated agent | Main contribution carried into this final design |
| --- | --- | --- |
| [`v1`](./heuristic_ideas_v1.md) | `chi12.py` | Daily planning, priorities, logistics, routing, storage protection, local replanning, liquidation |
| [`v2`](./heuristic_ideas_v2.md) | `chi13.py` | Explicit planned land expansion, no-land baseline, confirmation and dependency handling |
| [`v3`](./heuristic_ideas_v3.md) | `chi14.py` | Shared forecast, stable `TaskGroup`, integrated routing/HIRE, one market calendar, local repair, endgame integration |
| [`v4`](./heuristic_ideas_v4.md) | — | Market/opponent-aware economics, marginal production/sales, labor/space constraints, tactical priors |
| `final` | — | Complete resolved strategy, active-vs-benchmark precedence, corrected market model and implementation contract |

The final strategy is specified so that an implementation could be derived from this file alone; the versioned documents remain
useful for design history and attribution of changes. No such validated successor is retained in the closed project.


# 43. Implementation Contract

This section removes implementation freedom that could otherwise cause two agents to claim
the same strategy while behaving differently.

## 43.1 Active vs benchmark-only rules

All rules explicitly marked active in this document are ON by default.

Historical / benchmark-only rules are OFF by default and must not influence the baseline
unless an experiment enables them explicitly.

The active rules include, at minimum:

```text
MAX_WORKERS = 14
fixed opening package from §35
fixed expansion order = NE -> SW -> SE
active land schedule from §16-17
mandatory 5x5 triangular animal masks
absolute central 2x2 long-term-crop exclusion
```

## 43.2 Storage

```text
SHED_CAPACITY = 100
```

Use `100` for feasibility and overflow checks.

`99` is only an optional safety target and must not be treated as the engine capacity. The
baseline may expose a configuration flag for this margin; no rule may require it to prove
basic feasibility.

## 43.3 Forecast horizon

The physical/economic forecast runs from the current tick through the end of the game.
Shorter cached approximations may be used internally only if they provably preserve the
same decisions for the affected scope.

## 43.4 Marginal production search

For non-mandatory production, test exactly one additional unit/tile/animal at a time and stop
when:

```text
MV <= 0
OR a binding constraint prevents the next unit
```

Do not skip directly to a guessed target quantity.

## 43.5 Sale-quantity search

For every product, after reservations:

```text
sellable_stock = uncommitted stock
for q in 0 .. sellable_stock:
    simulate q exactly
choose q maximizing expected final value
```

Do not use a fixed batch size as the baseline decision rule.

## 43.6 Deterministic tie-break

Whenever two feasible choices are equal under the primary objective, apply:

```text
1. higher value
2. smaller deadline slack
3. fewer labor / worker ticks
4. less travel
5. stable deterministic ID / coordinate order
```

`smaller slack` means the more urgent feasible task wins.

## 43.7 No arbitrary economic coefficients

Do not invent unexplained constants for:

- `RiskPenalty`;
- LOW/BASE/HIGH probabilities;
- placement weights;
- liquidity discount rates;
- strategic-value multipliers.

Baseline conventions:

- rank expected outcomes with the `BASE` opponent scenario;
- use `LOW/HIGH` only as robustness/sensitivity checks unless explicit probabilities are
  later configured;
- use hard placement geometry plus the deterministic tie-break instead of weighted placement
  scoring;
- use direct schedule/cash deltas instead of an invented financial discount coefficient.

If a numerical coefficient is still unavoidable, expose it as a named configuration value
and mark it as **unspecified by strategy**. It must not silently become part of the baseline.

## 43.8 Mechanical execution contract

Strategic code must read exact execution semantics from the game rules / environment rather
than invent them. In particular verify in tests:

- exact worker availability after `HIRE`;
- actual worker spawn position;
- exact `PICKUP` quantity after subtracting inventory already carried;
- exact market-order processing/interleaving;
- shop-consumption timing;
- daily production/refresh timing;
- last actually executable tick.

These are mechanics, not strategy parameters.

## 43.9 Traceability requirement

Every strategic branch in any implementation claiming this final design must be traceable to a section of this document.
If a behavior cannot be justified by this file or by a verified game mechanic, Codex must
not silently add it.


---

## Navigation

[← Previous design delta](./heuristic_ideas_v4.md) · Final consolidated design
