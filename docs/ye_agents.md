# Ye Agents

This document covers the retained public V58 Ye agent and the Ye1 execution
improvements built directly on top of it.

## 1. Ye — Current V58 Agent

`src/agents/ye.py` is the retained standalone V58 public agent published by
[Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop).
The repository retains the executable Python artifact itself, not a downloaded
notebook archive.

The current integrity contract is:

- file size: **315,484 bytes**;
- SHA-256: `b041058ec187a8d0a01edc0eab8de068b53deca3e6c1973faf74ace6916ddcb9`;
- entry points: `agent`, `_kaggle_submission_entrypoint`, and
  `kaggle_agent_v58`;
- runtime dependencies: Python standard library only;
- policy set: ten routes, each containing 719 actions.

### 1.1 Runtime architecture

Ye dynamically reconstructs its packaged controller modules in memory and
exposes ten policy routes:

| Policy | Current role |
| --- | --- |
| `base_backbone` | Default route |
| `base_yarn` | First-shop YARN branch |
| `base_pet` | PET continuation selected from the second public shop |
| `recovery` | Public-state recovery branch |
| `smoothie` | FARMERS-to-SMOOTHIE continuation |
| `clone` | Persistent public-mirror continuation |
| `known_yarn` | Exact known-YARN public-state continuation |
| `ice_minimax` | ICE recovery/minimax continuation |
| `bakery_yarn` | BAKERY-to-YARN continuation |
| `pizza_recovery` | PIZZA-to-PET recovery continuation |

One controller is constructed on each early call. Its missed observation prefix
is replayed before it becomes available. After warm-up, all constructed
controllers are evaluated and the router returns the action from the selected
mode.

### 1.2 Public-state routing

Routing depends only on visible configuration and observations:

| Tick | Public signal | Possible result |
| ---: | --- | --- |
| 72 | First shop, both public money values, WHEAT market inventory, and visible opponent assets | Recovery, ICE minimax, second-shop wait, or base route |
| 96 | Exact public signatures following a YARN opening | `known_yarn` continuation |
| 144 | Second unlocked shop | SMOOTHIE, BAKERY/YARN, or PIZZA/PET continuation |
| 360 | At least 240 consecutive ticks of exact public-farm equality | `clone` continuation |

The active router does not consult opponent identity, submission IDs, a hidden
seed, private opponent state, or future opponent actions.

### 1.3 Current limitations

- All available controllers are evaluated after warm-up, including controllers
  that are not selected. This increases runtime cost and lets an unused
  controller failure affect the whole tick.
- A broad exception handler falls back to `_v51_safe_action` without exposing a
  diagnostic counter.
- Several route gates require exact money, inventory, and asset signatures. A
  small trajectory or engine divergence therefore keeps the agent on its base
  route rather than selecting a nearby recovery.
- Dynamic module registration in `sys.modules` is suitable for an isolated
  submission worker but may collide with other agents in a long-lived research
  process.
- The retained repository proves artifact integrity and import behavior; it
  does not contain the original evaluation notebook or an independently
  reproducible strategic benchmark for Ye.

## 2. Ye1 — Hardened V58 Execution

`src/agents/ye1.py` keeps `src/agents/ye.py` as the unchanged public V58
reference and adds bounded execution, safety, and engine-parity improvements.
It preserves the V58 routes, signatures, thresholds, and public-state-only
routing contract.

Ye1 warms the V58 route candidates through the hidden-shop opening, then selects
the `known_yarn` controller at the first public shop checkpoint. This controller
produced the highest paired final-money mean in the retained local screen and
is advanced alone for the rest of the episode.

Each required controller is isolated behind its own exception boundary. A
controller failure is counted in `_YE1_TELEMETRY` and falls back to that
controller's aligned route action instead of collapsing the whole tick to the
global PASS fallback. The telemetry records total calls, policy calls, policy
errors, outer errors, and fallback uses.

Disabled market-maker helpers are represented by a lazy no-op object, avoiding
their route copies and state allocation. Terminal liquidation uses the current
`episodeSteps`, `shedCapacity`, and `maxMarketOrdersPerTurn`, and projects
PICKUP, DROP, and PLACE before constructing the final SELL queue. Market value
calculations merge sparse `configuration.marketParams` overrides and effective
observation parameters, with observation values taking precedence.

The retained aggregate screen used seeds 11, 22, 33, and 44 in both seats
against Ye. Mean final money increased from 62,120.25 for the initial Ye1 to
75,230.25 for the optimized variant; its paired Ye opponents averaged 66,657.50.
Ye1 won six of eight paired games, with no ties. Clean-process import,
fault-isolation, terminal PICKUP projection, sparse market parameters, and all
eight full-game completions passed. These are local results, not a leaderboard
claim. `src/agents/ye.py` remains the unchanged public V58 reference.

## 3. Verification and provenance

`src/agents/ye.py` remains the unchanged public V58 reference published by
[Kaito Fukami](https://www.kaggle.com/code/kaitofukami/238-238-known-streams-v58-minimax-closed-loop).

The repository retains the executable Python artifact itself. Structural checks
include clean-process import, the documented Ye file size and SHA-256 digest,
its callable entry points, and the ten 719-action policy routes.

These checks establish artifact integrity and runtime structure. They do not
constitute a leaderboard claim or an independently reproducible strategic
benchmark for the original Ye agent.
