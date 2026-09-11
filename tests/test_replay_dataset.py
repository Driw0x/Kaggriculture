import json

from src.learning.replay_dataset import ReplayDataset


def test_replay_dataset(tmp_path):
    replay = {
        "info": {
            "EpisodeId": 1,
            "TeamNames": ["Expert", "Opponent"],
        },
        "rewards": [100, 50],
        "steps": [
            [
                {
                    "observation": {
                        "player": 0,
                        "day": 0,
                        "hour": 0,
                    },
                    "action": {
                        "farmer": ["PASS"],
                        "hands": [],
                        "market": [],
                    },
                },
                {
                    "observation": {
                        "player": 1,
                        "day": 0,
                        "hour": 0,
                    },
                    "action": {
                        "farmer": ["WEST"],
                        "hands": [],
                        "market": [],
                    },
                },
            ]
        ],
    }

    path = tmp_path / "replay.json"

    with path.open("w", encoding="utf-8") as f:
        json.dump(replay, f)

    dataset = ReplayDataset(tmp_path)

    assert len(dataset) == 1

    sample = dataset[0]

    assert sample["player"] == 0
    assert sample["team"] == "Expert"
    assert sample["episode"] == 1
    assert sample["observation"]["day"] == 0
    assert sample["action"]["farmer"] == ["PASS"]