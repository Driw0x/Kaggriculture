import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kaggle_environments import make

if len(sys.argv) != 4:
    print(
        f"Usage: python {Path(__file__).name} "
        "<agent> <game_index> <output_dir>"
    )
    sys.exit(1)

AGENT_NAME = sys.argv[1]
GAME_INDEX = int(sys.argv[2])
OUTPUT_DIR = Path(sys.argv[3])

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

chi = importlib.import_module(f"src.agents.{AGENT_NAME}")
agent = chi.agent

env = make(
    "kaggriculture",
    configuration={"episodeSteps": 720},
    debug=False,
)

env.run([agent, "random"])

reward = env.steps[-1][0].reward

record_path = (
    OUTPUT_DIR
    / f"game_{GAME_INDEX}_reward_{reward}.json"
)

with record_path.open("w", encoding="utf-8") as f:
    f.write("[")

    for step, env_step in enumerate(env.steps):
        if step > 0:
            f.write(",")

        data = {
            "step": step,
            "states": [
                {
                    "player": player,
                    "observation": state.observation,
                    "action": state.action,
                    "reward": state.reward,
                    "status": state.status,
                }
                for player, state in enumerate(env_step)
            ],
        }

        json.dump(
            data,
            f,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    f.write("]")

# Important :
# le parent récupère uniquement cette ligne.
print(reward)