import importlib
import json
import sys
import tempfile
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kaggle_environments import make
import src.agents.chi10_spec as chi

importlib.reload(chi)
agent = chi.agent

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent, "random"])

final = env.steps[-1]
for i, state in enumerate(final):
    print(f"Player {i}: reward={state.reward}, status={state.status}")

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
    states.append({"step": step, "states": step_states})

states_path = ROOT / "experiments" / "run_states.json"
states_path.write_text(json.dumps(states, indent=2), encoding="utf-8")
print(f"States saved to: {states_path}")

html = env.render(mode="html", width=1200, height=800)
html_path = Path(tempfile.gettempdir()) / "kaggriculture_replay.html"
html_path.write_text(html, encoding="utf-8")
webbrowser.open(html_path.as_uri())