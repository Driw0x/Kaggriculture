# Kaggriculture

AI agent developed for the Kaggriculture competition on Kaggle.

## Competition

Kaggriculture is a turn-based strategy competition where participants
develop autonomous agents to manage farms, resources, production, and
market interactions.

The objective of this repository was to develop, evaluate, and iteratively improve agents for the competition.

## Project Status

This repository is now a **closed project snapshot**. The retained outcomes are:

- **Heuristic planner:** `chi14.py` is the last validated implementation of the rebuilt heuristic branch. `heuristic_ideas_v4` and `heuristic_ideas_final` remain design-only references; later implementation attempts, including `CHI16` / `chi_final`, were not retained as validated successors.
- **Learning agent:** Behavioral Cloning and the hybrid executor are preserved as an experimental track, but the learning agent was not retained for autonomous competition use.
- **Public-derived branch:** `jet6.py` (Public Agent 10) is the final retained local baseline of that branch.

No `CHI16` or `chi_final` source agent is part of the final repository state.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/agents/` | Agent implementations |
| `src/learning/` | Behavioral cloning models, datasets, encoders and policies |
| `scripts/` | Training, evaluation and utility scripts |
| `experiments/` | Experiment results and strategy comparisons |
| `submissions/` | Agents submitted to Kaggle |
| `data/` | Replay data and processed learning datasets |
| `models/` | Trained model checkpoints and inference configuration |
| `tests/` | Automated tests |
| `docs/` | Game rules and agent development documentation |
| `requirements.txt` | Python dependencies |
| `LICENSE` | Apache License 2.0 |

## Setup

Clone the repository:

```bash
git clone https://github.com/Driw0x/kaggriculture.git
cd kaggriculture
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Documentation

* [`docs/game_rules.md`](docs/game_rules.md) --- Complete game rules
  and mechanics

* [`docs/getting_started.md`](docs/getting_started.md) --- Agent
  development, local testing, and Kaggle submission guide

* [`docs/game_mechanics_reference.md`](docs/game_mechanics_reference.md)
  --- Reference for core game mechanics, production, animals, farm
  infrastructure, workers, town shops, and market behavior.

* [`docs/chi_agents.md`](docs/chi_agents.md) ---
  Original CHI heuristic-planner lineage through CHI10 and the temporal experiment.

* [`docs/heuristic_agents.md`](docs/heuristic_agents.md) ---
  Rebuilt heuristic-planner branch from CHI12 to the final retained CHI14 implementation,
  plus the archived v4/final design-only continuation.

* [`docs/learning_agent.md`](docs/learning_agent.md) ---
  Learning-based experimental track, offline results, autonomous evaluation,
  and the decision not to retain it for further development.

* [`docs/public_agent.md`](docs/public_agent.md) ---
  Public-derived/reference agent families, provenance, local benchmarks, rejected
  experiments, and the final retained Public Agent 10 baseline.

* [`docs/agent_ideas.md`](docs/agent_ideas.md) ---
  Historical inventory of agent ideas and their implementation status.


## License

This project is licensed under the Apache License 2.0.

See [`LICENSE`](LICENSE) for details.
