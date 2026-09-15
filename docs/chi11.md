# CHI 11 — Public-Meta Shop and Market Overlay

`src/agents/chi11.py` is an experimental CHI 10 variant informed by public
high-scoring Kaggriculture work. It deliberately transfers general mechanisms
instead of copying replay action tapes.

For the complete CHI version history and the place of CHI 11 in the retained
heuristic family, see [`heuristic_planner.md`](heuristic_planner.md).

## Public references

- Kaito Fukami's public v48 notebook (historical public score 3009.0):
  https://www.kaggle.com/code/kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes
- GzmCR's scenario-aware economic policy:
  https://github.com/GzmCR/Kaggriculture
- lonespear's replay, market and routing analysis:
  https://github.com/lonespear/kaggriculture

Kaito's v48 routes on the order of publicly visible shop unlocks, selects only
one child controller per turn, and gives collision-sensitive sales explicit
priority. CHI 11 adapts those ideas to CHI 10's closed-loop planner.

## Changes from CHI 10

1. The first and second unlocked shops apply small 8% and 3% demand priors to
   otherwise unchanged marginal production scores.
2. A public farm signature tracks whether both farms remain nearly identical
   for 24 consecutive turns. No identity, rating, episode ID, hidden inventory,
   replay lookup or future action is used.
3. Existing `SELL` slots are reordered by estimated price impact while every
   non-sale order keeps its original slot.
4. During a sustained clone state, ordinary sale batches are capped at ten to
   reduce simultaneous market collision. Final-day liquidation is never capped.
5. CHI 10 is called exactly once per observation.

The current `chi11.py` submission file embeds the retained CHI 10 base
implementation directly and has no project-local dependency. It can therefore
be submitted as a standalone Kaggle agent.

## Relationship with Jet

`jet.py` and `jet1.py` are a separate experimental branch and are not CHI 11
successors.

CHI 11 transfers selected public ideas into the project's own closed-loop
heuristic planner. Jet instead keeps a strong public fixed action route as its
baseline so the route can be inspected and improved directly.

- `jet.py`: readable, behavior-preserving expansion of the 719-step public
  route.
- `jet1.py`: same route with staged runtime fallbacks and observation-based
  final liquidation.

Keeping the two families separate makes CHI improvements and route-derived
improvements independently measurable.

## Preliminary local validation

The deterministic comparison uses seeds 1101 and 1102 in both seats:

| Seed | CHI 11 seat | CHI 11 | CHI 10 | Margin |
| ---: | ---: | ---: | ---: | ---: |
| 1101 | 0 | 102,843 | 91,104 | +11,739 |
| 1101 | 1 | 104,727 | 100,928 | +3,799 |
| 1102 | 0 | 82,811 | 82,009 | +802 |
| 1102 | 1 | 84,203 | 79,258 | +4,945 |

Result: 4/4 wins, mean margin +5,321.2. This is a small development screen,
not evidence of leaderboard improvement. Run it with:

```powershell
.\.venv\Scripts\python.exe experiments\compare_chi11.py
```

Focused unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_chi11.py -q -p no:cacheprovider
```

