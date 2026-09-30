# Heuristic Ideas v2 — Planned Land Expansion

[← Previous version](./heuristic_ideas_v1.md) · [Next version →](./heuristic_ideas_v3.md)

> **Series convention**
>
> `v2` is a **strict delta over `v1`**. It inherits `v1` in full and changes only the rules
> explicitly documented here. Later inheritance is transitive through `v2`.

## Identity

| Field | Value |
| --- | --- |
| Version | `v2` |
| Original source | `detail_improve` |
| Associated agent | `chi13.py` |
| Role | Strict delta over [`v1`](./heuristic_ideas_v1.md) |
| Improves | [`v1`](./heuristic_ideas_v1.md) |
| Improved by | [`v3`](./heuristic_ideas_v3.md) |

## Main idea

Do not buy land because the current field looks full. Buy land only when additional profitable production cannot fit on existing land and a concrete exploitation plan proves that the purchase remains feasible and profitable after land cost, labor, logistics, maintenance, and game-end constraints.

`v2` inherits [`v1`](./heuristic_ideas_v1.md) in full. Only the additions, replacements, and corrections written in this file change the inherited design.

## Core ideas added in v2

### 1. Separate land purchase from placement

`CHOOSE_PLACEMENTS()` should only place production on land that is already available.

It must no longer decide by itself to buy land when no tile is found. Land expansion becomes an explicit strategic decision made before normal daily task generation.

This avoids turning a local placement failure into an automatic expensive purchase.

### 2. Compare expansion against a no-purchase baseline

Before considering new land, construct the best plan that uses only currently unlocked land.

That baseline should include:

- free tiles;
- useful digging;
- compatible empty structures;
- tiles that will become free after harvest or end of life;
- feasible rotations before game end;
- required hires;
- maintenance;
- realizable sales.

Only production that is still profitable but cannot fit into this baseline creates a real land need.

### 3. A full field is not enough to justify `BUY_LAND`

Two explicit anti-patterns are rejected:

- the field being visually full does not prove more land is needed;
- a worker shortage does not prove a land shortage.

Expansion should answer a production-capacity problem, not hide a routing or labor problem.

### 4. Reserve a concrete exploitation plan before purchase

For the next legal quadrant, simulate the purchase on a copied state and reserve how the new tiles would actually be used.

The simulated plan must include:

- exact future production;
- seeds or animals;
- installation timing;
- future maintenance;
- required hires;
- routing and travel;
- expected sales before game end;
- full land cost.

The purchase is valid only if this plan is feasible and produces positive net gain compared with staying on current land.

### 5. Validate cash, labor, routing, and deadlines together

A profitable-looking crop list is insufficient.

The expansion must be rejected when:

- installation happens too late;
- maintenance cannot be serviced;
- cash becomes insufficient;
- labor capacity is insufficient;
- routes do not fit;
- expected value does not repay the land cost.

This turns `BUY_LAND` into a fully planned commitment instead of a speculative purchase.

### 6. Do not place production on unconfirmed land

Production depending on a pending `BUY_LAND` remains only a reservation.

No actual placement or route may target a `LOCKED` tile before the purchase is observed as confirmed.

If no valid placement exists on currently available land, postpone or cancel that production instead of pretending the future land already exists.

### 7. Confirm expansion from observations, not assumptions

A land purchase is considered real only when newly unlocked tiles appear in the observed state.

After confirmation:

- detect the new tiles;
- record the actual cost;
- revalidate the reserved exploitation plan;
- remove uses whose assumptions are no longer valid;
- immediately integrate the new tiles into normal planning.

If the purchase was not confirmed, delete the dependent reservations and replan.

### 8. Treat sunk land cost correctly

After the purchase is confirmed, do not keep an unprofitable production merely to justify the money already spent on land.

The original purchase decision and the best decision after purchase are separate questions. Once the cost is sunk, future production should still be judged on its remaining value.

### 9. `BUY_LAND` is a real market dependency

`BUY_LAND` consumes one of the 10 market-order slots and must not be merged with another order.

Before sending it, verify:

- cash safety reserve;
- prerequisites;
- dependent production plan.

If `BUY_LAND`, another `BUY`, or a `HIRE` is delayed or removed, every dependent plan must be revalidated.

### 10. Reevaluate land only when its assumptions matter

Land evaluation does not need to run blindly every tick.

Recompute it when an economic change or placement requirement changes the conditions that justified or rejected expansion.

## Key invariants

- No implicit `BUY_LAND` from placement failure.
- No purchase without a concrete dated exploitation plan.
- No purchase unless it improves on the best no-land plan.
- No production action may target a locked tile.
- Land cost, seeds/animals, hires, maintenance, routing, and realizable sales must all be included.
- A pending purchase does not count as confirmed capacity.
- A confirmed but now-unprofitable use may be cancelled even though the land cost is already sunk.
- `BUY_LAND` consumes a market slot and propagates dependencies like other purchases.

## What v2 changes relative to v1

`v2` keeps the daily planner from `v1` but makes land expansion a separate, planned economic decision. The main improvement is replacing reactive expansion with simulated, reserved, and observation-confirmed expansion.


---

## Navigation

[← Previous version](./heuristic_ideas_v1.md) · [Next version →](./heuristic_ideas_v3.md)
