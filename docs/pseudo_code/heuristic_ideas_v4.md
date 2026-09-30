# Heuristic Ideas v4 — Market-Aware Tactical Strategy

[← Previous version](./heuristic_ideas_v3.md) · [Final consolidated version →](./heuristic_ideas_final.md)

> **Series convention**
>
> `v4` is a **strict delta over `v3`**. It inherits `v3` in full and only adds, replaces,
> or corrects rules explicitly documented here. Earlier behavior is inherited transitively
> through `v3`; `v4` does not treat `v1` or `v2` as parallel parents.

## Identity

| Field | Value |
| --- | --- |
| Version | `v4` |
| Source | Kaggriculture strategy sheets + additional tactical notes |
| Associated agent | None — design only |
| Role | Strict delta over [`v3`](./heuristic_ideas_v3.md) |
| Improves | [`v3`](./heuristic_ideas_v3.md) |
| Consolidated by | [`final`](./heuristic_ideas_final.md) |
| Main focus | Market timing, opponent modeling, marginal economics, inventory policy, tactical land use, and hard operating constraints |
| Implementation status | Not implemented as a dedicated CHI agent |

## Inheritance rule

`v4` inherits [`v3`](./heuristic_ideas_v3.md) in full. Because `v3` already inherits `v2` (and therefore `v1`), all earlier behavior remains inherited transitively. Only rules written below modify the `v3` design.

This file intentionally does **not** repeat ideas already present in `v3`, including behavior that `v3` itself inherited transitively. The daily task planner, survival priorities, routing/logistics, planned `BUY_LAND`, shared forecast, local replanning, validated market calendar, and generic endgame feasibility therefore remain inherited from `v3`.

The rules below are the ideas from the later Kaggriculture notes that add new information or make a previous principle materially more specific.

---

## Main idea

Add a second strategic layer on top of the unified planner:

`shop demand -> own/opponent supply -> future inventory -> future price -> marginal value -> what to produce / hold / sell`

The planner should no longer ask only whether a production plan is feasible. It should also ask whether the **next unit**, **next tile**, **next worker**, **next land purchase**, or **next sale** improves expected profit after market impact, holding value, labor opportunity cost, and opponent timing.

---

## 1. Hard labor ceiling + marginal hiring

### Hard constraint

```text
worker_count <= 14
```

The planner must never create a plan requiring more than 14 workers.

### Economic stopping rule

Do not hire only because more work exists. Compare the incremental value created by one more worker with the price of the next hire.

```text
Va = Profit(A + 1 workers) - Profit(A workers)
```

Stop hiring when the marginal worker no longer pays for itself.

If an additional worker is not worth its cost, reallocate existing labor toward the highest-value land / production instead of expanding the workforce.

The source notes also describe labor opportunity cost as:

```text
LaborOpportunityCost_i = Va * required_actions_i
```

This is more specific than the v3 rule that a `HIRE` must merely make work feasible.

---

## 2. Spatial layout constraints

Use explicit placement zones in addition to the placement logic inherited from `v3`.

### Animal zone

Animals should be concentrated inside a triangular area of roughly `5 x 5` tiles close to the farm center / shed-access area.

Purpose:

- reduce repeated `FEED`, `CARE`, `HARVEST`, and fertilizer-collection travel;
- keep high-frequency production near the center;
- avoid scattering animal maintenance across expanded land.

### Central `2 x 2` reserve

Avoid using the central `2 x 2` area for long-duration crops.

The original note also specifies that this restriction becomes void after the relevant latest-payback cutoff. Therefore this is a **time-dependent placement restriction**, not a permanent ban.

### Effective land usage

For economic comparison, the notes use:

```text
plant effective land = 1 tile
poultry effective land = 5 / 3 tiles
```

This effective occupancy can be used when comparing marginal value per land-time unit.

---

## 3. Three strategic game phases

The notes divide the game into three broad phases:

```text
Phase 1: T0  -> T3
Phase 2: T4  -> T20
Phase 3: T20 -> T30
```

The exact decisions remain state-dependent, but the intended roles are:

- **T0–T3:** establish the opening production base and survival/feed capacity;
- **T4–T20:** expand, react to revealed shop demand, and maximize productive land use;
- **T20–T30:** reduce long-payback commitments, manage inventory aggressively, and prepare liquidation.

This phase model is an additional tactical bias; the endgame feasibility inherited from `v3` still overrides any fixed schedule that is no longer profitable.

---

## 4. Historical opening templates

The notes contain multiple opening ideas. They should be kept as **alternative candidate openings for benchmark/testing**, not merged into one mandatory opening because they were written at different stages.

### Opening candidate A — fixed initial farm package

| Item | Quantity | Recorded cost |
| --- | ---: | ---: |
| Wheat crop (`W`) | 10 | 100 |
| Carrot (`C`) | 6 | 120 |
| Tomato (`T`) | 1 | 50 |
| Strawberry (`S`) | 2 | 200 |
| Melon (`M`) | 2 | 160 |
| Goose | 1 | 300 |
| Cow | 2 | 800 |
| Sheep | 1 | 500 |
| Wheat stock | 16 | 450 |
| Hires | 4 | 7 |

Recorded totals in the note:

```text
total cost = 2687
remaining cash = 313
```

Important opening intentions:

- plant and water the starting crops immediately;
- maintain enough Wheat to support animals;
- after the first early harvests, reassign freed land according to the shops that have appeared;
- use early Wheat harvesting to feed animals when useful;
- calculate how long current Wheat stock lasts and when new Wheat production becomes necessary.

### Opening candidate B — product-by-product day-1 quantities

Another strategy sheet records the following initial quantities:

| Product | Day-1 candidate quantity |
| --- | ---: |
| Melon | 2 |
| Carrot | 6 |
| Egg production | 1 |
| Wool production | 1 |
| Milk production | 2 |
| Strawberry | 2 |
| Wheat | 2 |
| Tomato | 2 |

These values are retained as historical candidate priors and should be re-evaluated against current shop demand, land, labor, and market forecasts rather than hard-coded blindly.

---

## 5. Tactical land-expansion schedules

The profitability and feasibility checks inherited from `v3` remain mandatory. `v4` adds **preferred timing and layout branches** that can be tested when those checks pass.

### Branch A — first two shops do not create meaningful animal demand

```text
T4: prefer buying NE as first expansion
T9: prefer buying SW as second expansion
```

After the NE purchase:

- if animal demand appears, prioritize animals plus Wheat support;
- if animal demand remains absent, keep roughly one Goose and use the rest for shop-demanded crops;
- fill the new land progressively instead of forcing immediate full utilization.

For the SW expansion, candidate fill patterns include:

- `4 x 4` triangle;
- `4 x 4` square;
- conditional partial fill according to demand and labor.

### Branch B — first two shops contain animal demand

Use earlier expansion:

```text
T4 : NE first expansion
T7 : SW second expansion
T12: SE third expansion
```

The notes additionally say to consider the fourth land when the first two shops have animal demand.

Candidate SE utilization includes:

- `4 x 4` triangle;
- `4 x 4` center-near subset;
- conditional fill according to demand and available labor.

### Historical timing ceiling

An earlier note also records:

```text
first land  < T7
second land < T12
third land  < T12
```

Keep this as an experimental timing prior, not as a replacement for the economic validation inherited from `v3`.

### Land cash floor

In addition to the cash-reserve logic inherited from `v3`, enforce the explicit lower bound:

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

A second formulation from the notes is:

```text
current_cash >=
    land_cost
    + immediate_deployment_cost_after_expansion
    + operating_reserve_until_first_harvest
```

Both express the same strategic intention: do not buy land if the purchase leaves the farm unable to operate until the next realizable income.

---

## 6. Explicit market-demand and opponent forecast

### Market gap

For each product, estimate future shortage as:

```text
MarketGap =
    shop_demand
    + town_center_demand
    - own_expected_supply
    - opponent_expected_supply
```

Do **not** assume that completely filling this gap is always profit-maximizing. The economically optimal quantity may be smaller because extra supply can depress the price.

### Opponent supply model

Track visible opponent production:

- planted crop type and quantity;
- animal type and quantity;
- expected production / maturity time;
- expected production amount;
- likely market-release time.

Approximate uncertain opponent supply as:

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

The source notes explicitly suggest low / medium / high probability levels when opponent execution is uncertain.

When market inventory changes, use it as evidence to update the estimated opponent inventory state.

### Demand certainty

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

Confirmed shop demand should therefore influence production more strongly than uncertain future demand.

---

## 7. Future inventory -> future price

Use the market price curve instead of treating current price as permanent.

### Short-term inventory forecast

```text
FutureInventory =
    CurrentMarketInventory
    + FutureOwnSupply
    + FutureOpponentSupply
    - FutureShopConsumption
    - FutureTownConsumption
```

Then:

```text
ExpectedFuturePrice = PriceFunction(FutureInventory)
```

### Long-term approximation

The notes also propose:

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

This is useful when an exact event-by-event projection is not worth the cost.

### Supply timing

Distinguish:

- synchronized supply;
- staggered supply;
- smoothed supply.

Two plans with the same total output can have different value if one avoids selling into the same price trough as the opponent.

---

## 8. Marginal production economics

Production selection should compare the **next incremental unit of capacity**, not only total-project profit.

### Expected revenue

For a one-shot crop:

```text
ER_i = ExpectedFuturePrice_at_harvest * ExpectedYield
```

For repeated production, sum each future output at the expected price of its own production date:

```text
ER_i = sum_t(ExpectedPrice_t * ExpectedYield_t)
```

### Plant direct cost

```text
PlantCost = SeedCost * Quantity + LaborCost
```

### Animal direct cost

The notes model animal cost as:

```text
AnimalCost =
    PurchaseCost
    + FeedOpportunityCost
    + LaborCost
```

with feed opportunity cost including the value of Wheat that could otherwise have been sold.

### Marginal value

```text
MV_i = DeltaER_i - DeltaC_i - DeltaFeed_i - DeltaLabor_i
```

A more complete strategic score also allows:

```text
MV_i += DeltaStrategic_i - DeltaRisk_i
```

### Value per land-time

Compare products by the incremental value they produce per effective occupied land and lock duration:

```text
MarginalScore_i =
    MV_i
    / (AddedEffectiveLand_i * LandLockTime_i)
```

The notes also express the same idea as:

```text
Expected lifecycle profit per tile =
    (future sales revenue
     - seed/direct cost
     - labor cost
     - inventory/holding cost)
    / occupied land-days
```

### Additional strategic terms

Candidate ranking may also include:

- market-risk coefficient;
- price-crash coefficient;
- strategic value;
- option value from preserving / improving future layout;
- fertilization optimization;
- whether Wheat should be self-produced or bought externally.

---

## 9. Historical product score formulas

One early strategy sheet used product-specific score approximations. Their notation is retained here because they are useful experimental priors, but the exact parenthesization was not fully defined in the source.

| Product | Recorded score idea |
| --- | --- |
| Melon | `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
| Carrot | `sum(q * dynamic_price) - 20 - labor / land_occupation` |
| Egg | `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
| Wool | `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
| Milk | `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
| Strawberry | `sum(q * dynamic_price) - 100 - labor / land_occupation` |
| Wheat | `sum(q * dynamic_price) - 10 - labor / land_occupation` |
| Tomato | `sum(q * dynamic_price) - 50 - labor / land_occupation` |

These formulas predate the more general marginal-value model above. They should therefore be treated as candidate calibration rules rather than a second independent economy engine.

---

## 10. Historical demand formulas

The notes also contain product-specific demand estimates. Their abbreviations (`Dm`, `Npc`, `Nfm`, `Nb`, `Nbs`, `Ny`, `Np`, `Ni`, `Ns`, `Nic`, `q`) were not fully defined in the source, so the formulas are preserved rather than reinterpreted.

| Product | Recorded `Dtotal` formula |
| --- | --- |
| Melon | `Dtotal = 1/day` |
| Carrot | `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
| Egg | `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
| Wool | `Dtotal = Dm + 12 * Ny * q` |
| Milk | `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
| Strawberry | `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
| Wheat | `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
| Tomato | `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

Repeated terms are left exactly as recorded rather than silently corrected.

---

## 11. Production quantity should react to opponent supply

For a product the opponent is not producing, compare the product score once enough land becomes available.

If the opponent is already producing it:

```text
AdjustedGap = MarketGap - OpponentSupply
```

and re-evaluate how much additional production is still valuable.

Track the opponent's next harvest date and quantity before choosing our own production and sale timing.

The notes also define a competitive margin concept:

```text
MarginMax = OurProfit - OpponentProfit
```

This can be used as a secondary strategic signal, but it should not replace absolute profitability.

---

## 12. Sell decision = current marginal value vs retention value

Do not sell only because inventory exists.

For each additional unit under consideration:

```text
CurrentMarginalSalePrice =
    P(CurrentMarketInventory + considered_unit_index - 1)
```

Compare it with the value of keeping the unit:

```text
RetentionValue = max(
    FutureResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

Sell while:

```text
CurrentMarginalSaleValue > RetentionValue
```

and stop when the marginal sale value falls below the marginal value of holding the next unit.

---

## 13. Time-discounted future resale value

A future sale should be discounted because cash received later is less useful than cash available now.

The notes propose:

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h
```

with an experimental opportunity-rate estimate:

```text
r = ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h) - 1
```

The source mentions evaluating more than one `h` horizon, including the next and latest relevant sale opportunities; its exact averaging convention is not fully specified.

---

## 14. Cash urgency changes the sell threshold

Define near-term cash pressure from required spending:

```text
CashUrgency =
    (NearTermRequiredSpend - CurrentCash)
    / NearTermRequiredSpend
```

Then reduce the normal hold/sell threshold as cash becomes more urgent:

```text
AdjustedSellThreshold =
    BaseSellThreshold - CashUrgencyAdjustment
```

The older notes also refer to a coefficient `lambda` as a cash-need factor.

This lets the planner sell earlier when cash is strategically more valuable than waiting for the theoretical best market price.

---

## 15. Control price impact and sale quantity

Estimate the price damage created by a sale:

```text
PriceImpactRate =
    (PriceBeforeSale - PriceAfterSale)
    / PriceBeforeSale
```

Do not dump more than the short-term market can absorb:

```text
SaleQuantity <= ShortTermAbsorbableDemand
```

Choose the largest sale quantity for which marginal selling value remains above marginal holding value **without crashing the price unnecessarily**.

This explicitly addresses the note that filling the whole market gap is not always the profit-maximizing action.

---

## 16. Sell before expected opponent supply when profitable

Opponent maturity dates create sale windows.

General tactic:

- estimate the opponent's next harvest / production date;
- consider selling part of our inventory before that supply arrives;
- avoid waiting into a predictable opponent-driven price drop;
- if both sides produce at the same time, consider matching / reacting quickly to the opponent's release rather than waiting blindly.

Historical rule from the product sheet:

```text
if combined supply < shop consumption:
    sell n units before opponent's next maturity,
    subject to value constraints

if combined supply > shop consumption:
    prefer selling around maturity rather than accumulating excess stock
```

Melon had an especially aggressive historical rule: clear inventory before opponent maturity, and if both planted at the same time, react immediately when the opponent sells.

---

## 17. Explicit split-sale comparison

The later notes define a concrete test for selling now versus splitting the sale.

Definitions:

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

Prefer the split-sale path when:

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

Interpretation: compare the strategic value of dumping `n + m` now with selling `n` now and `m` later after accounting for the opponent's price interaction.

---

## 18. Inventory overflow formula

Before storage becomes full, estimate required liquidation explicitly:

```text
NeedSell = Shed + Carry + Incoming - 99
```

If `NeedSell > 0`, at least that amount must be sold or otherwise removed before the incoming stock reaches the shed.

This refines the storage-feasibility logic inherited from `v3` with a direct liquidation quantity.

---

## 19. Product-specific inventory policy

### Fertilizer

- prefer immediate sale when not needed for profitable near-term fertilization;
- avoid long-term storage because it is continuously produced and external demand is weak.

### Melon

- avoid long-term storage;
- sell immediately or time the sale against the opponent;
- the historical notes cap combined Melon production around `120`;
- fertilization is allowed / encouraged in the historical Melon strategy.

### Wheat

Reserve mainly for feed and emergency operation:

```text
WheatReserve =
    5 * animal_q
    - WheatExpectedToMatureInNext5Days
```

Sell excess Wheat instead of permanently occupying large shed capacity.

Also compare self-producing Wheat against buying it from the market.

### Egg

- if there is no relevant shop, do not keep unnecessary Egg inventory;
- with Bakery / Brunch demand, keep roughly one day of demand;
- historical animal policy used daily `CARE`.

### Carrot

- no PetCafe demand -> sell rather than hold;
- with PetCafe / FarmersMarket demand -> keep roughly two days of demand;
- avoid large long-term stock;
- treat as a short-turnover product;
- historical rule: no fertilization.

### Tomato

- if mature Tomato plants already guarantee replenishment, inventory can be sold more aggressively;
- historical schedule idea: fertilize around `T8`, harvest around `T9` and `T11`.

### Strawberry

- with relevant shops, reserve roughly two days of **net** demand;
- prefer smaller sale batches to avoid unnecessary price damage;
- historical timing idea: fertilize around `T10`, harvest `T12`, fertilize `T14`, harvest `T16`.

### Milk

- with relevant demand, keep roughly two days of net demand;
- without relevant shops, if a Cow is close to producing more Milk, increase current Milk selling priority;
- prefer small batches;
- historical rule: sell at high prices;
- historical care schedule skipped `CARE` around `T5–T7`.

### Wool

- keep Wool when waiting for Yarn demand;
- without Yarn demand, consider selling;
- historical care schedule used daily care except around `T5`.

---

## 20. Inventory priority classes

The notes also group stock into five broad classes.

### Class 1 — operating inventory only

`Wheat`

Keep feed + emergency reserve, but do not let excess Wheat occupy the shed for long periods.

### Class 2 — fast turnover

`Carrot`

Default to short holding periods; increase short-term stock only when strong shop demand exists.

### Class 3 — balanced

`Tomato`, `Egg`

May be stored, but usually do not receive highest shed priority. Retention depends mainly on the next demand window.

### Class 4 — high-value timing inventory

`Strawberry`, `Milk`, `Wool`

When demand is confirmed and a future shortage is predictable, give these products more storage priority and avoid low-price mass liquidation.

### Class 5 — avoid long holding

`Melon`, `Fertilizer`

Prefer turnover because Melon lacks a stable shop sink and Fertilizer is continuously regenerated.

---

## 21. Seed / animal deployment capacity constraint

Do not buy more immediately deployable production than the available placement capacity can absorb.

Historical constraint:

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

The exact conversion from seed units / structures to occupied tiles still depends on the production type and the placement model inherited from `v3`.

---

## 22. Animal action ordering

When an animal is due for a productive visit, the notes prefer:

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

This is more specific than the dependency-aware animal task grouping inherited from `v3`.

Late-game maintenance should stop when the animal has no remaining profitable production. A specific historical criterion is:

```text
if next useful production is beyond the remaining horizon
and fertilizer value < maintenance cost:
    stop FEED / CARE
```

The generic v3 endgame rule still decides the final feasibility.

---

## 23. Abandonment / liquidation trigger from expected price

Do not maintain a production merely because it already exists.

If:

```text
ExpectedMarketValue
< MaintenanceCost + HarvestCost + CleanupCost
```

start liquidating or abandoning the production instead of continuing to spend labor on it.

The historical notes also propose beginning broad liquidation from the penultimate day. v3's exact final cash-out feasibility remains the stronger hard constraint.

---

## 24. Recompute on new shops

When a new shop appears, immediately recompute product demand and economics for all affected products.

This includes:

- target production quantity;
- expected shortage;
- inventory reserve;
- sell timing;
- land usage;
- animal-vs-crop allocation.

`v3` already replans on economically relevant shop changes; `v4` adds the requirement that the **market-demand and marginal-value models themselves** be recomputed.

---

## 25. Market-aware product-specific sell behavior

Historical strategy notes include the following product-level biases:

- Carrot / Egg / Wheat / Tomato: sell earlier when cash is needed;
- Wool: wait for Yarn when plausible;
- Milk / Strawberry: prefer high-price windows;
- Melon: sell immediately or before opponent supply;
- all products: when shed capacity is tight, sell in profit-priority order rather than FIFO / arbitrary order.

These are fallback heuristics for cases where the full marginal sell model is too expensive or uncertain.

---

## 26. Core strategic chain

The v4 economic layer can be summarized as:

```text
shops define demand
-> own + opponent production define future supply
-> future supply and demand define future market inventory
-> market inventory defines expected price
-> expected price defines marginal revenue
-> marginal revenue minus direct/feed/labor/land/risk costs defines marginal value
-> marginal value decides what to produce, how much to produce, what to hold, and what to sell
```

This chain is the central new idea of v4.

---

## Key invariants added by v4

- Never exceed `14` workers.
- Do not hire a worker whose marginal economic value is below its marginal hire cost.
- Keep high-maintenance animals inside the preferred center-near animal zone when feasible.
- Preserve the central `2 x 2` from long-duration crops while that reservation rule is active.
- Do not let a preferred land-purchase date bypass the profitability, cash, route, or endgame feasibility inherited from `v3`.
- Do not buy land if the explicit operating cash floor would be violated.
- Forecast opponent production and market timing when deciding production and sales.
- Do not assume filling the entire market shortage maximizes profit.
- Compare the marginal value of selling a unit with the marginal value of holding it.
- Limit sale size when additional units would cause excessive price impact.
- Keep product-specific safety stock only when it has feed, demand, or strategic value.
- Use `NeedSell = Shed + Carry + Incoming - 99` to quantify emergency liquidation.
- Stop maintaining production whose remaining expected market value cannot pay its remaining operating cost.

---

## What v4 changes relative to v3

`v3` made the planner internally coherent. `v4` adds a more explicit **economic policy** on top of that coherent planner:

1. hard worker and spatial-layout constraints;
2. tactical opening and land-expansion priors;
3. explicit opponent production forecasting;
4. future-inventory-based price prediction;
5. marginal production value per land-time unit;
6. marginal labor value for hiring;
7. retention value and time-discounted selling;
8. price-impact-aware partial sales;
9. product-specific inventory reserves and turnover classes;
10. concrete cash-floor, overflow, and liquidation rules.

The fixed timings and quantities recorded in the historical sheets are **candidate heuristics to benchmark**, while the feasibility and profitability rules inherited from `v3` remain the final gate.


---

## Navigation

[← Previous version](./heuristic_ideas_v3.md) · [Final consolidated version →](./heuristic_ideas_final.md)
