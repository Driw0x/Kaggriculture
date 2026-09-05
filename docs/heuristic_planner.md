# Heuristic Planner

This document describes the successive versions of the Kaggriculture heuristic planner based on the implemented agents.

## 1. Objective

The planner follows an incremental approach:

1. define a deterministic day 1 opening;
2. convert fixed plans into reusable paths and action stacks;
3. maintain crop and animal production after day 1;
4. dynamically distribute daily tasks;
5. reduce movement and unnecessary hiring;
6. handle wheat shortages for animal feeding;
7. avoid unnecessary animal CARE actions.

The objective is to keep the agent deterministic and inspectable while progressively making its decisions depend on the actual farm state.

## 2. Initial prototype — `chi.py`

The initial version defines the complete day 1 opening directly as action sequences.

### Day 1 purchases

At hour 0:

- 10 Wheat seeds;
- 6 Carrot seeds;
- 2 Strawberry seeds;
- 1 Goose;
- 2 Cows;
- 1 Sheep;
- 16 Wheat;
- 3 farm hands.

At hour 1:

- 1 Tomato seed;
- 2 Melon seeds.

### Day 1 layout

The crop layout contains:

| Crop | Tiles |
| --- | ---: |
| Wheat | 10 |
| Carrot | 6 |
| Tomato | 1 |
| Strawberry | 2 |
| Melon | 2 |

The animal block occupies the bottom-right 2x2 area:

| Position | Animal |
| --- | --- |
| `(3, 3)` | Goose |
| `(4, 3)` | Cow |
| `(3, 4)` | Sheep |
| `(4, 4)` | Cow |

The farmer builds and initializes the animal area while three farm hands plant and water the crop area.

This prototype only executes day 1. From day 2 onward, every worker passes.

## 3. CHI 1 — Final fixed day 1 opening

CHI 1 keeps the same fixed farm layout but modifies the opening to use four hired farm hands.

### Main changes

- four farm hands instead of three;
- Wheat seeds are purchased at hour 1;
- the crop area is split into four fixed routes;
- the farmer remains dedicated to animal setup.

### Fixed worker roles

| Worker | Role |
| --- | --- |
| Farmer | Build the animal block, place animals, feed and care |
| Hand 1 | Right-side crop route |
| Hand 2 | Left-side crop route |
| Hand 3 | Inner crop route |
| Hand 4 | Short route to the remaining crop tile |

This becomes the fixed day 1 opening reused by later versions.

## 4. CHI 2 — Paths and action stacks

CHI 2 replaces the large hard-coded action sequences with a path-based representation.

The day 1 movement paths become:

```text
Farmer: W -> N -> E

Hand 1: W -> N -> N -> N -> N -> W -> W -> W -> S

Hand 2: N -> W -> W -> W -> W -> N -> N -> N -> N

Hand 3: W -> N -> W -> N -> N -> N -> W -> S -> W -> S

Hand 4: N -> W -> W
```

Instead of explicitly writing every `PLANT`, `WATER`, `PLACE`, `FEED` and `CARE` in the route, the planner derives actions from the tile reached by the worker.

For crops:

```text
reach crop tile
    -> PLANT
    -> WATER
```

For animals:

```text
reach animal tile
    -> BUILD if required
    -> PLACE
    -> FEED
    -> CARE
```

Actions are inserted into a stack and consumed one tick at a time.

This version establishes the execution model used by the following planners.

## 5. CHI 3 — Dynamic multi-day planner

CHI 3 extends the agent beyond day 1.

### Persistent farm state

The planner introduces explicit state for every crop and animal tile.

Crop state tracks:

- crop type;
- whether the crop is planted;
- whether it is ready for harvest.

Animal state tracks:

- animal type;
- whether the animal is placed;
- available production;
- available fertilizer.

The state is refreshed from the observation every tick.

### Crop production

The planner distinguishes one-time and ongoing crops.

| Crop | Type | Harvest age(s) |
| --- | --- | --- |
| Wheat | One-time | 4 |
| Carrot | One-time | 3 |
| Tomato | Ongoing | 8, 9, 10, 11 |
| Strawberry | Ongoing | 10, 12, 14, 16 |
| Melon | One-time | 10 |

Possible crop tasks now include:

```text
WATER
HARVEST
REPLANT
```

Seeds required for one-time crop replanting are automatically purchased.

### Animal production

Animal tasks can include:

```text
BUILD
PLACE
FEED
CARE
COLLECT_FERTILIZER
HARVEST
```

### Dynamic daily routing

After day 1, the planner:

1. creates crop and animal tasks;
2. estimates their action cost;
3. assigns them to available workers;
4. orders nearby tasks together;
5. converts task coordinates into movement paths;
6. searches for the minimum number of hires able to finish the work within worker capacity.

This is the first version where daily routes and hiring are calculated dynamically.

## 6. CHI 4 — Dedicated livestock block

CHI 4 changes task assignment so that all animal tasks are grouped on one worker.

Previously, animal tasks could be distributed between different workers by the generic allocator.

The new planner:

1. builds the complete animal route;
2. tests which worker can execute it;
3. assigns the livestock block to the cheapest valid worker;
4. distributes crop tasks over the remaining available capacity.

The animal route remains contiguous before additional crop tasks are appended to that worker.

### Purpose

This reduces fragmentation around the compact 2x2 animal area and makes animal management more predictable.

## 7. CHI 5 — Wheat-shortage and animal sequencing

CHI 5 addresses the case where the shed does not contain enough Wheat to feed all animals.

The planner now has two modes.

### Normal mode

Used when:

```text
shed Wheat >= number of animals
```

The regular dedicated-animal route is used.

### Wheat-shortage mode

When Wheat is insufficient, the animal workflow is split into separate task types:

```text
ANIMAL_PRE
WHEAT_SUPPLY
SHED_DROP
WAIT_WHEAT
ANIMAL_FEED
REPLANT_WHEAT
```

A supplier worker:

1. travels to mature Wheat;
2. waters and harvests the required Wheat;
3. returns to the center;
4. drops the Wheat in the shed.

A feeder worker:

1. reaches the center;
2. waits until enough Wheat is available;
3. picks up the Wheat;
4. follows the animal feeding route.

Animal work that does not require Wheat can be performed separately through `ANIMAL_PRE`.

The animal action order is also changed so available production and fertilizer are collected before the new feeding/care cycle:

```text
HARVEST if available
COLLECT_FERTILIZER if available
FEED
CARE
```

This version solves the dependency between crop production and animal feeding instead of treating every animal task as immediately executable.

## 8. CHI 6 — Hiring and shortage-route optimization

CHI 6 improves the shortage planner introduced in CHI 5.

The main objective is to avoid hiring additional workers simply because one worker is waiting for Wheat.

### Tick-aware planning

The planner introduces:

```text
DAY_TICKS = 24
```

and explicitly accounts for the one-tick start delay of hired farm hands.

The supplier/feeder pair is selected using the estimated time at which:

- the supplier can drop Wheat;
- the feeder can reach the shed;
- the complete feeding route can finish.

### Use waiting time productively

The feeder is no longer forced to remain idle until Wheat arrives.

Before `WAIT_WHEAT`, the planner attempts to insert tasks that can be completed while still reaching the shed before the supplier.

Priority is given to `ANIMAL_PRE` tasks.

The supplier can also execute:

- Wheat replanting after harvesting;
- additional nearby tasks if capacity remains.

### Result

Worker capacity is used more efficiently, allowing the planner to search from zero hires upward and keep the smallest valid workforce.

## 9. CHI 7 — CARE optimization

CHI 7 adds animal production-capacity awareness.

The planner now tracks:

```text
pending_care_bonus
```

for each animal.

Maximum held production is represented as:

| Animal | Maximum held production |
| --- | ---: |
| Goose | 4 |
| Cow | 6 |
| Sheep | 6 |

CARE is no longer automatically added to every animal visit.

The implemented condition is:

```text
pending_care_bonus + 1 < animal maximum held production
```

If this condition is false, the CARE action is omitted.

This condition is used both in:

- normal animal actions;
- `ANIMAL_PRE` shortage tasks.

The route-cost estimator also includes CARE only when the action is actually required, so hiring and route selection benefit from the reduced workload.

## 10. Version summary

| Version | Main improvement |
| --- | --- |
| `chi.py` | Initial fixed day 1 prototype with three farm hands |
| `chi1.py` | Final fixed day 1 opening with four farm hands |
| `chi2.py` | Fixed paths converted into generated action stacks |
| `chi3.py` | State tracking, harvest/replant logic and dynamic multi-day routing |
| `chi4.py` | Complete livestock block assigned to one worker |
| `chi5.py` | Wheat-shortage workflow and separated animal pre/feed tasks |
| `chi6.py` | Tick-aware shortage planning and reduced hiring |
| `chi7.py` | CARE actions adapted to pending bonus and animal production capacity |
