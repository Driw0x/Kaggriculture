import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) != 2:
    print(f"Usage: python {Path(__file__).name} <agent>")
    sys.exit(1)

AGENT_NAME = sys.argv[1]

N_GAMES = 1000

record_dir = (
    ROOT
    / "experiments"
    / "runs"
    / AGENT_NAME
)

record_dir.mkdir(
    parents=True,
    exist_ok=True,
)

reward_sum = 0.0
reward_min = float("inf")
reward_max = float("-inf")

run_one_script = (
    ROOT
    / "experiments"
    / "run_one_game.py"
)

for game in range(1, N_GAMES + 1):
    result = subprocess.run(
        [
            sys.executable,
            str(run_one_script),
            AGENT_NAME,
            str(game),
            str(record_dir),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    # run_one_game.py affiche uniquement le reward
    reward = float(result.stdout.strip())

    reward_sum += reward
    reward_min = min(reward_min, reward)
    reward_max = max(reward_max, reward)

    print(
        f"Game {game}/{N_GAMES}: "
        f"reward={reward}"
    )

avg = reward_sum / N_GAMES

print()
print(f"Agent: {AGENT_NAME}")
print(f"Games: {N_GAMES}")
print(f"Min reward: {reward_min:.2f}")
print(f"Max reward: {reward_max:.2f}")
print(f"Mean reward: {avg:.2f}")