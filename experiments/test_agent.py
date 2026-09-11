import gc
import importlib
import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kaggle_environments import make

if len(sys.argv) != 2:
    print(f"Usage: python {Path(__file__).name} <agent>")
    sys.exit(1)

AGENT_NAME = sys.argv[1]
chi = importlib.import_module(f"src.agents.{AGENT_NAME}")

N_GAMES = 1000
rewards = []

record_dir = ROOT / "experiments" / "runs" / AGENT_NAME
record_dir.mkdir(parents=True, exist_ok=True)

for game in range(N_GAMES):
    # Reset complet entre chaque game
    chi = importlib.reload(chi)
    agent = chi.agent

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720},
        debug=False
    )

    env.run([agent, "random"])

    reward = env.steps[-1][0].reward
    rewards.append(reward)

    states = []

    for step, env_step in enumerate(env.steps):
        step_states = []

        for player, state in enumerate(env_step):
            step_states.append({
                "player": player,
                "observation": state.observation,
                "action": state.action,
                "reward": state.reward,
                "status": state.status
            })

        states.append({
            "step": step,
            "states": step_states
        })

    # Sauvegarde immédiate
    record_path = record_dir / f"game_{game + 1}_reward_{reward}.json"
    record_path.write_text(
        json.dumps(states),
        encoding="utf-8"
    )

    print(
        f"Game {game + 1}/{N_GAMES}: "
        f"reward={reward} -> {record_path.name}"
    )

    # Libération de la RAM
    del states
    del env

    if (game + 1) % 50 == 0:
        gc.collect()

avg = mean(rewards)

print()
print(f"Agent: {AGENT_NAME}")
print(f"Games: {N_GAMES}")
print(f"Min reward: {min(rewards):.2f}")
print(f"Max reward: {max(rewards):.2f}")
print(f"Mean reward: {avg:.2f}")