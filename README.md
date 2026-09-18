# Kaggriculture

AI agent developed for the Kaggriculture competition on Kaggle.

## Competition

Kaggriculture is a turn-based strategy competition where participants
develop autonomous agents to manage farms, resources, production, and
market interactions.

The objective of this repository is to develop, evaluate, and
iteratively improve an agent for the competition.

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
  CHI heuristic-planner family, strategy evolution, economic planning,
  execution improvements, and validation history.

* [`docs/learning_agent.md`](docs/learning_agent.md) ---
  Learning-based agent architecture, expert replay dataset, imitation
  learning, and reinforcement learning roadmap.

* [`docs/jet_agents.md`](docs/jet_agents.md) ---
  Jet public-route agent family, runtime safeguards, market experiments,
  and incremental route-based improvements.

* [`docs/ye_agents.md`](docs/ye_agents.md) ---
  Ye V58 public agent reference and Ye1 execution, robustness, and
  final-money improvements.


## License

This project is licensed under the Apache License 2.0.

See [`LICENSE`](LICENSE) for details.
