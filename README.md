# Kaggriculture

AI agent developed for the Kaggriculture competition on Kaggle.

## Competition

Kaggriculture is a turn-based strategy competition where participants develop autonomous agents to manage farms, resources, production, and market interactions.

The objective of this repository is to develop, evaluate, and iteratively improve an agent for the competition.

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/` | Agent implementation |
| `scripts/` | Local evaluation and utility scripts |
| `experiments/` | Experiment results and strategy comparisons |
| `submissions/` | Agents submitted to Kaggle |
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

- [`docs/game_rules.md`](docs/game_rules.md) — Complete game rules and mechanics
- [`docs/getting_started.md`](docs/getting_started.md) — Agent development, local testing, and Kaggle submission guide
- [`docs/game_mechanics_reference.md`](docs/game_mechanics_reference.md) — Reference for core game mechanics, production, animals, farm infrastructure, workers, town shops, and market behavior.

## License

This project is licensed under the Apache License 2.0.

See [`LICENSE`](LICENSE) for details.