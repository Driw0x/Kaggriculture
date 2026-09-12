import json
from pathlib import Path


class ReplayDataset:
    def __init__(self, replay_dir):
        self.replay_dir = Path(replay_dir)
        self.metadata = self._load_metadata()
        self.paths = [
            path for path in sorted(self.replay_dir.rglob("*.json"))
            if path.name != "metadata.json"
        ]

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

    def iter_replay_samples(self, path):
        with path.open(encoding="utf-8") as f:
            replay = json.load(f)

        player = self._get_expert_player(replay, path)

        if player is None:
            return

        steps = replay.get("steps", [])
        team_names = replay.get("info", {}).get("TeamNames", [])
        episode = replay.get("info", {}).get("EpisodeId")

        for index in range(len(steps) - 1):
            current_step = steps[index]
            next_step = steps[index + 1]

            if player >= len(current_step) or player >= len(next_step):
                continue

            current_record = current_step[player]
            next_record = next_step[player]

            observation = current_record.get("observation")
            action = next_record.get("action")

            if observation is None or action is None:
                continue

            if observation.get("player") != player:
                continue

            yield {
                "observation": observation,
                "action": action,
                "player": player,
                "team": team_names[player],
                "episode": episode,
            }

    def iter_samples(self):
        for path in self.paths:
            yield from self.iter_replay_samples(path)

    def __iter__(self):
        return self.iter_samples()

    def __len__(self):
        return len(self.paths)
