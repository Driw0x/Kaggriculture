import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path


class GameRecorder:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = None
        self.data = None
        self.new_session()

    def new_session(self):
        index = 1
        while (self.directory / f"game_{index:03d}.json").exists():
            index += 1
        self.path = self.directory / f"game_{index:03d}.json"
        self.data = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "episode_steps": 720,
            "player": 0,
            "opponent": "pass",
            "ticks": [],
        }
        self.save()
        return self.path.name

    def record(self, step, observation, action, result):
        self.data["ticks"].append({
            "step": step,
            "observation": deepcopy(observation),
            "action": deepcopy(action),
            "result": deepcopy(result),
        })
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
