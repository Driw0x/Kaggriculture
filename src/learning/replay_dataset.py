import json
from pathlib import Path


class ReplayDataset:
    def __init__(self, replay_dir, player=None):
        self.replay_dir = Path(replay_dir)
        self.player = player
        self.samples = []

        for path in sorted(self.replay_dir.rglob("*.json")):
            self._load_replay(path)

    def _load_replay(self, path):
        with path.open(encoding="utf-8") as f:
            replay = json.load(f)

        team_names = replay.get("info", {}).get("TeamNames", [])

        player_id = self.player

        if isinstance(player_id, str):
            if player_id not in team_names:
                return
            player_id = team_names.index(player_id)

        if player_id is None:
            rewards = replay.get("rewards", [])
            if not rewards:
                return
            player_id = max(range(len(rewards)), key=rewards.__getitem__)

        for step in replay.get("steps", []):
            if player_id >= len(step):
                continue

            record = step[player_id]

            observation = record.get("observation")
            action = record.get("action")

            if observation is None or action is None:
                continue

            if observation.get("player") != player_id:
                continue

            self.samples.append(
                {
                    "observation": observation,
                    "action": action,
                    "player": player_id,
                    "team": team_names[player_id] if player_id < len(team_names) else None,
                    "episode": replay.get("info", {}).get("EpisodeId"),
                }
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]