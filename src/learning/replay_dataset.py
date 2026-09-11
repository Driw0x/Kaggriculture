import json
from pathlib import Path


class ReplayDataset:
    def __init__(self, replay_dir):
        self.replay_dir = Path(replay_dir)
        self.samples = []
        self.metadata = self._load_metadata()

        for path in sorted(self.replay_dir.rglob("*.json")):
            if path.name != "metadata.json":
                self._load_replay(path)

    def _load_metadata(self):
        path = self.replay_dir / "metadata.json"
        if not path.exists():
            return {}
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def _get_expert_player(self, replay, path):
        info = self.metadata.get(path.parent.name)
        if info is None:
            return None

        team_name = info["team_name"]
        team_names = replay.get("info", {}).get("TeamNames", [])
        if team_name not in team_names:
            return None

        return team_names.index(team_name)

    def _load_replay(self, path):
        with path.open(encoding="utf-8") as f:
            replay = json.load(f)

        player = self._get_expert_player(replay, path)
        if player is None:
            return

        team_names = replay.get("info", {}).get("TeamNames", [])

        for step in replay.get("steps", []):
            if player >= len(step):
                continue

            record = step[player]
            observation = record.get("observation")
            action = record.get("action")

            if observation is None or action is None:
                continue
            if observation.get("player") != player:
                continue

            self.samples.append({
                "observation": observation,
                "action": action,
                "player": player,
                "team": team_names[player],
                "episode": replay.get("info", {}).get("EpisodeId"),
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]