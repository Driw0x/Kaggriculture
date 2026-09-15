# Heuristic Planner

This document describes the successive versions of the Kaggriculture
heuristic planner based on the implemented agents.

## 1. Objective

The planner follows an incremental approach:

1.  define a deterministic day 1 opening;
2.  convert fixed plans into reusable paths and action stacks;
3.  maintain crop and animal production after day 1;
4.  dynamically distribute daily tasks;
5.  reduce movement and unnecessary hiring;
6.  handle wheat shortages for animal feeding;
7.  avoid unnecessary animal CARE actions;
8.  adapt routing to real worker spawn positions;
9.  coordinate harvest and sale timing;
10. stop automatic replanting after farm expansion;
11. clear weeds across unlocked land;
12. generalize land purchases up to the four quadrants.

The objective is to keep the agent deterministic and inspectable while
progressively making its decisions depend on the actual farm state.

## 2. Initial prototype --- `chi.py`

The initial version defines the complete day 1 opening directly as
action sequences.

### Day 1 purchases

At hour 0:

-   10 Wheat seeds;
-   6 Carrot seeds;
-   2 Strawberry seeds;
-   1 Goose;
-   2 Cows;
-   1 Sheep;
-   16 Wheat;
-   3 farm hands.

At hour 1:

-   1 Tomato seed;
-   2 Melon seeds.

### Day 1 layout

The crop layout contains:

  Crop           Tiles
  ------------ -------
  Wheat             10
  Carrot             6
  Tomato             1
  Strawberry         2
  Melon              2

The animal block occupies the bottom-right 2x2 area:

  Position   Animal
  ---------- --------
  `(3, 3)`   Goose
  `(4, 3)`   Cow
  `(3, 4)`   Sheep
  `(4, 4)`   Cow

The farmer builds and initializes the animal area while three farm hands
plant and water the crop area.

This prototype only executes day 1. From day 2 onward, every worker
passes.

## 3. CHI 1 --- Final fixed day 1 opening

CHI 1 keeps the same fixed farm layout but modifies the opening to use
four hired farm hands.

### Main changes

-   four farm hands instead of three;
-   Wheat seeds are purchased at hour 1;
-   the crop area is split into four fixed routes;
-   the farmer remains dedicated to animal setup.

### Fixed worker roles

  Worker   Role
  -------- ------------------------------------------------------
  Farmer   Build the animal block, place animals, feed and care
  Hand 1   Right-side crop route
  Hand 2   Left-side crop route
  Hand 3   Inner crop route
  Hand 4   Short route to the remaining crop tile

This becomes the fixed day 1 opening reused by later versions.

## 4. CHI 2 --- Paths and action stacks

CHI 2 replaces the large hard-coded action sequences with a path-based
representation.

The day 1 movement paths become:

``` text
Farmer: W -> N -> E

Hand 1: W -> N -> N -> N -> N -> W -> W -> W -> S

Hand 2: N -> W -> W -> W -> W -> N -> N -> N -> N

Hand 3: W -> N -> W -> N -> N -> N -> W -> S -> W -> S

Hand 4: N -> W -> W
```

Instead of explicitly writing every `PLANT`, `WATER`, `PLACE`, `FEED`
and `CARE` in the route, the planner derives actions from the tile
reached by the worker.

For crops:

``` text
reach crop tile
    -> PLANT
    -> WATER
```

For animals:

``` text
reach animal tile
    -> BUILD if required
    -> PLACE
    -> FEED
    -> CARE
```

Actions are inserted into a stack and consumed one tick at a time.

This version establishes the execution model used by the following
planners.

## 5. CHI 3 --- Dynamic multi-day planner

CHI 3 extends the agent beyond day 1.

### Persistent farm state

The planner introduces explicit state for every crop and animal tile.

Crop state tracks:

-   crop type;
-   whether the crop is planted;
-   whether it is ready for harvest.

Animal state tracks:

-   animal type;
-   whether the animal is placed;
-   available production;
-   available fertilizer.

The state is refreshed from the observation every tick.

### Crop production

The planner distinguishes one-time and ongoing crops.

  Crop         Type       Harvest age(s)
  ------------ ---------- ----------------
  Wheat        One-time   4
  Carrot       One-time   3
  Tomato       Ongoing    8, 9, 10, 11
  Strawberry   Ongoing    10, 12, 14, 16
  Melon        One-time   10

Possible crop tasks now include:

``` text
WATER
HARVEST
REPLANT
```

Seeds required for one-time crop replanting are automatically purchased.

### Animal production

Animal tasks can include:

``` text
BUILD
PLACE
FEED
CARE
COLLECT_FERTILIZER
HARVEST
```

### Dynamic daily routing

After day 1, the planner:

1.  creates crop and animal tasks;
2.  estimates their action cost;
3.  assigns them to available workers;
4.  orders nearby tasks together;
5.  converts task coordinates into movement paths;
6.  searches for the minimum number of hires able to finish the work
    within worker capacity.

This is the first version where daily routes and hiring are calculated
dynamically.

## 6. CHI 4 --- Dedicated livestock block

CHI 4 changes task assignment so that all animal tasks are grouped on
one worker.

Previously, animal tasks could be distributed between different workers
by the generic allocator.

The new planner:

1.  builds the complete animal route;
2.  tests which worker can execute it;
3.  assigns the livestock block to the cheapest valid worker;
4.  distributes crop tasks over the remaining available capacity.

The animal route remains contiguous before additional crop tasks are
appended to that worker.

### Purpose

This reduces fragmentation around the compact 2x2 animal area and makes
animal management more predictable.

## 7. CHI 5 --- Wheat-shortage and animal sequencing

CHI 5 addresses the case where the shed does not contain enough Wheat to
feed all animals.

The planner now has two modes.

### Normal mode

Used when:

``` text
shed Wheat >= number of animals
```

The regular dedicated-animal route is used.

### Wheat-shortage mode

When Wheat is insufficient, the animal workflow is split into separate
task types:

``` text
ANIMAL_PRE
WHEAT_SUPPLY
SHED_DROP
WAIT_WHEAT
ANIMAL_FEED
REPLANT_WHEAT
```

A supplier worker:

1.  travels to mature Wheat;
2.  waters and harvests the required Wheat;
3.  returns to the center;
4.  drops the Wheat in the shed.

A feeder worker:

1.  reaches the center;
2.  waits until enough Wheat is available;
3.  picks up the Wheat;
4.  follows the animal feeding route.

Animal work that does not require Wheat can be performed separately
through `ANIMAL_PRE`.

The animal action order is also changed so available production and
fertilizer are collected before the new feeding/care cycle:

``` text
HARVEST if available
COLLECT_FERTILIZER if available
FEED
CARE
```

This version solves the dependency between crop production and animal
feeding instead of treating every animal task as immediately executable.

## 8. CHI 6 --- Hiring and shortage-route optimization

CHI 6 improves the shortage planner introduced in CHI 5.

The main objective is to avoid hiring additional workers simply because
one worker is waiting for Wheat.

### Tick-aware planning

The planner introduces:

``` text
DAY_TICKS = 24
```

and explicitly accounts for the one-tick start delay of hired farm
hands.

The supplier/feeder pair is selected using the estimated time at which:

-   the supplier can drop Wheat;
-   the feeder can reach the shed;
-   the complete feeding route can finish.

### Use waiting time productively

The feeder is no longer forced to remain idle until Wheat arrives.

Before `WAIT_WHEAT`, the planner attempts to insert tasks that can be
completed while still reaching the shed before the supplier.

Priority is given to `ANIMAL_PRE` tasks.

The supplier can also execute:

-   Wheat replanting after harvesting;
-   additional nearby tasks if capacity remains.

### Result

Worker capacity is used more efficiently, allowing the planner to search
from zero hires upward and keep the smallest valid workforce.

## 9. CHI 7 --- CARE optimization

CHI 7 adds animal production-capacity awareness.

The planner now tracks:

``` text
pending_care_bonus
```

for each animal.

Maximum held production is represented as:

  Animal     Maximum held production
  -------- -------------------------
  Goose                            4
  Cow                              6
  Sheep                            6

CARE is no longer automatically added to every animal visit.

The implemented condition is:

``` text
pending_care_bonus + 1 < animal maximum held production
```

If this condition is false, the CARE action is omitted.

This condition is used both in:

-   normal animal actions;
-   `ANIMAL_PRE` shortage tasks.

The route-cost estimator also includes CARE only when the action is
actually required, so hiring and route selection benefit from the
reduced workload.

## 10. CHI 8 --- Sale, expansion and land management

CHI 8 extends the planner from production maintenance to farm expansion
and transition toward a future dynamic tile-allocation strategy.

### Real worker positions

Daily planning initially estimates worker starts from the known
shed-access spawn pattern.

At hour 1, once hired hands are visible in the observation, their real
positions are stored and the routes are rebuilt from those coordinates.

This avoids route-cost errors caused by assuming that every worker
starts from the same shed-access tile.

### Sale-day planning

A dedicated sale day is defined with:

``` text
SALE_DAY = 5
SALE_DROP_HOUR = 22
SALE_HOUR = 23
```

On that day, worker capacity and route cost account for the return to
the shed before the sale.

Workers return to the shed-access area and drop their inventory before
the market sale.

Carrots that reach age 2 on the sale day are harvested early:

``` text
WATER
HARVEST
```

They are not replanted.

### Expansion mode

Expansion mode becomes active as soon as more than the initial `NW`
quadrant is unlocked:

``` text
EXPANSION_ACTIVE = len(unlocked_quadrants) > 1
```

Before expansion, the original replanting strategy is preserved.

After expansion:

-   existing crops continue to be watered;
-   ready crops continue to be harvested;
-   one-time crops are not replanted after harvest;
-   replacement seeds are no longer purchased;
-   empty harvested tiles are ignored by the crop planner.

This leaves empty tiles available for the dynamic tile-scoring strategy
planned for CHI 9.

### Weed tasks

The planner scans the complete farm grid for visible weeds.

Every detected weed can generate an explicit task:

``` text
WEED
    -> DIG
```

Weeds are therefore included in route assignment even when they are not
located on one of the original crop positions.

After expansion, removing a weed does not trigger automatic replanting.

### Generalized land purchases

Land prices are represented explicitly:

``` text
1 -> 1000
2 -> 2000
3 -> 4000
```

where the key is the number of quadrants already unlocked.

The next land cost is therefore:

    Quadrants already unlocked        Next land cost
  ---------------------------- ---------------------
                             1                  1000
                             2                  2000
                             3                  4000

The planner uses dedicated functions to determine the next price and
whether the current available cash is sufficient.

This removes the previous logic tied specifically to the second `NE`
quadrant and allows the same purchase mechanism to handle the second,
third and fourth quadrants.


## 11. CHI 9 --- Dynamic production, labor and endgame optimization

CHI 9 extends the heuristic planner with a more dynamic economic and
endgame strategy.

### Dynamic worker-count calculation

The number of hired farm hands is no longer based only on whether the
daily task set fits within worker capacity.

The planner first searches for the minimum valid workforce, then checks
whether hiring one additional worker creates enough extra expected
production value to justify the next hiring cost.

Additional hiring stops when:

``` text
additional expected profit < next hire cost
```

This allows the planner to avoid both under-hiring and unnecessary
workers when the extra capacity would not pay for itself.

### Conditional crop watering

Crops are no longer watered automatically every day.

The planner tracks:

``` text
watered_today
consecutive_unwatered
needs_water
```

and only creates a WATER action when watering is required for crop
survival or when a harvest-ready crop still needs watering before its
harvest action.

This removes unnecessary WATER actions and reduces daily route cost.

### Endgame planting constraints

Planting and replanting decisions now use the crop production schedule
together with the current day.

A crop is only planted if its first harvest can still occur before the
last useful harvest day:

``` text
planting day + first harvest age <= last harvest day
```

The same principle is applied to new animals using their first
production age.

Production that cannot generate a harvest in time for the final sale is
therefore excluded from:

-   new planting;
-   replanting;
-   animal placement;
-   production scoring;
-   market purchase orders.

### Dynamic production purchasing

The previous fixed post-opening production strategy is replaced by a
budget-aware production selection system.

For available or soon-to-be-empty tiles, the planner evaluates possible
crops and animals using:

-   expected marginal market revenue;
-   production purchase cost;
-   expected animal feed cost;
-   additional labor cost;
-   tile occupation time;
-   effective space usage.

Candidates are scored using marginal profit per effective occupied space
and time.

Only positive and affordable production choices are retained.

The resulting plan is then converted into the required market orders for
seeds, animals and Wheat.

### Land-purchase profitability

Land expansion is also evaluated using projected production.

Before purchasing a new quadrant, the planner estimates:

-   production that can still be installed on the new land;
-   expected marginal profit;
-   resulting worker requirements;
-   seed, animal and feed costs;
-   extra hiring cost.

The purchase is only kept when the projected production remains
affordable and sufficiently profitable relative to the land price.

The 4000-cost final expansion is also disabled after day 19.

### Continuous sales

From day 6 onward, harvested non-Wheat products can be sold directly from
the shed instead of waiting for a single later liquidation.

The daily sale set includes:

``` text
CARROT
TOMATO
STRAWBERRY
MELON
EGG
MILK
WOOL
```

Fertilizer remains independently sellable.

### Final liquidation

On day 29, workers start returning toward the shed-access center before
the final market liquidation.

From hour 22 onward, every remaining sellable product in the shed is
submitted to the market:

``` text
SELL all remaining market products
```

This ensures that products still held near the end of the match are
converted into money before the game finishes.



### Additional retained improvements

The main additions are intentionally limited to:

- event- and market-aware production valuation;
- CARE-aware animal production estimates;
- shed-overflow protection;
- metered sales for price-sensitive products;
- nearest-shed logistics using the four valid shed-access tiles;
- extended Fibonacci hiring costs without an artificial 10-hand cap;
- safer production-state synchronization when the production type of a tile
  changes.

These changes keep the existing greedy route allocator while improving the
economic model and execution robustness.


## 12. CHI 10 --- Observation-checked execution and cash-flow planning

CHI 10 keeps the CHI 9 planner structure and focuses on making execution and
economic estimates closer to the real game state.

The main additions are:

- event-based own and public opponent supply projections;
- per-unit market-price simulation for projected sales;
- cash-flow-aware production and hiring decisions;
- validation of queued worker actions against the current observation before
  execution;
- adaptive sales and shed-capacity handling, including products deposited
  during the current turn;
- tighter endgame routing and liquidation handling.

CHI 10 keeps the same greedy-pathing architecture while improving execution
validation and economic planning.

### CHI 10 Temporal — experimental rolling-horizon scheduler

`src/agents/chi10_temporal.py` is a standalone variant with the CHI 10
opening and economic model. After the opening, it rebuilds a timed schedule
from the observed worker positions, tiles and inventories at every tick.

The scheduler keeps up to four alternative assignments (two during the
daily hiring estimates). It can skip an optional task to leave time for a
more valuable chain. Tasks are processed in a fixed precedence-compatible
priority order; this is a bounded heuristic, not a globally optimal solver.

The schedule accounts for:

- one action or movement per worker per tick;
- watering before harvesting, and planting followed by mandatory watering;
- shared seed reservations, animal pickups and wheat availability;
- wheat harvest/deposit/pickup dependencies across workers;
- hired workers and purchased resources becoming available on the next tick;
- return travel and deposits before the end of the horizon.

Daily purchase estimates assume the required supplies can be bought. Live
execution uses only observed stock, checks actions in worker order, caps
deposits to the available shed room and includes same-turn transfers in sales.
Failed purchases or unexpected state changes are handled by replanning.
Shed congestion and future sale prices remain approximate in the search.

With the default 720-step game, the last actionable observation is day 29,
hour 22. The final schedule reserves time to deposit before that action ends;
automatic end-of-day deposits cannot be relied on for the final sale.

Unused greedy routing, queued execution, old sale settings and obsolete
production-estimation helpers have been removed from this variant. The agent
uses the Python standard library only and supports the default game settings.

Run the focused tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_chi10_temporal.py -q -p no:cacheprovider
```

Full-game checks are opt-in. They use two seeds in both player positions
against CHI 10, verify completion and check worker actions with the real
engine. JUnit output records rewards and maximum measured action time:

```powershell
$env:RUN_KAGGRICULTURE = "1"
.\.venv\Scripts\python.exe -m pytest tests/test_chi10_temporal.py -q -p no:cacheprovider -o junit_family=xunit1 --junitxml=experiments/chi10_temporal_validation.xml
Remove-Item Env:RUN_KAGGRICULTURE
```

These checks cover execution in the tested scenarios; they do not establish
a competitive improvement over CHI 10.


## 13. CHI 11 --- Public-meta shop and market overlay

For implementation details, public references, validation results and focused
tests, see [`chi11.md`](chi11.md).

CHI 11 keeps the CHI 10 economic planner and adds a small observation-only
overlay based on public game state.

### Shop-order production prior

The order of unlocked shops is used as a mild production prior.

The first unlocked shop applies an 8% multiplier and the second a 3%
multiplier to production whose output matches the corresponding public shop
demand.

These multipliers are applied on top of the existing CHI 10 production score:

``` text
CHI 11 score = CHI 10 score × public shop multiplier
```

The adjustment remains deliberately small so the existing marginal-profit
calculation stays decisive unless candidate productions are already close.

### Public farm-similarity detection

CHI 11 builds a compact signature from information already visible in the
observation:

- crop counts;
- animal counts;
- number of unlocked quadrants;
- number of farm hands.

The two farms are considered persistently similar only after repeated
near-equality of these public signatures.

The retained thresholds are:

``` text
detection starts at step 48
signature distance <= 2
24 consecutive matching turns
overlay can become active from step 160
```

No opponent identity, rating, episode identifier, hidden inventory, replay
lookup or future action is used.

### Market-impact-aware SELL ordering

CHI 11 does not create a separate sale strategy. It only reorders SELL orders
that already exist in the CHI 10 action.

For every existing sale, the planner estimates the immediate price impact from
the quantity being sold:

``` text
impact = quantity × max(current price - post-sale price, 0)
```

SELL slots with the largest estimated impact are executed first, while every
non-SELL market slot keeps its original position.

During a sustained public clone state, ordinary sale quantities are capped at
10 units to reduce simultaneous market collision. Final-day liquidation is
never capped.

### Standalone submission

CHI 11 embeds the CHI 10 implementation directly in the same module.

The final `agent(obs)`:

1. detects the public-meta state;
2. temporarily applies the shop-order production multiplier;
3. calls the embedded CHI 10 agent exactly once;
4. restores the original production scoring function;
5. reorders the resulting SELL slots.

No project-local import is required, so `chi11.py` can be submitted directly
as a single Kaggle agent file.


## 14. Version summary


  -----------------------------------------------------------------------
  Version                             Main improvement
  ----------------------------------- -----------------------------------
  `chi.py`                            Initial fixed day 1 prototype with
                                      three farm hands

  `chi1.py`                           Final fixed day 1 opening with four
                                      farm hands

  `chi2.py`                           Fixed paths converted into
                                      generated action stacks

  `chi3.py`                           State tracking, harvest/replant
                                      logic and dynamic multi-day routing

  `chi4.py`                           Complete livestock block assigned
                                      to one worker

  `chi5.py`                           Wheat-shortage workflow and
                                      separated animal pre/feed tasks

  `chi6.py`                           Tick-aware shortage planning and
                                      reduced hiring

  `chi7.py`                           CARE actions adapted to pending
                                      bonus and animal production
                                      capacity

  `chi8.py`                           Sale-day routing, real worker
                                      starts, no-replant expansion mode,
                                      weed clearing and generalized land
                                      purchases

  `chi9.py`                           Dynamic production purchasing,
                                      event/market-aware valuation,
                                      profit-aware hiring, shed protection,
                                      metered sales, safer logistics and
                                      endgame production cutoffs

  `chi10.py`                          Observation-checked execution,
                                      event-based cash-flow valuation and
                                      adaptive sale handling

  `chi11.py`                          CHI 10 plus public shop-order production
                                      priors, persistent public farm-similarity
                                      detection, market-impact-aware SELL
                                      ordering and single-file submission

  -----------------------------------------------------------------------
