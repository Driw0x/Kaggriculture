import importlib
import sys
import tempfile
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from kaggle_environments import make
import src.agents.chi6 as chi8

importlib.reload(chi8)
agent = chi8.agent

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent, "random"])

final = env.steps[-1]
for i, state in enumerate(final):
    print(f"Player {i}: reward={state.reward}, status={state.status}")

html = env.render(mode="html", width=1200, height=800)
html_path = Path(tempfile.gettempdir()) / "kaggriculture_replay.html"
html_path.write_text(html, encoding="utf-8")
webbrowser.open(html_path.as_uri())
