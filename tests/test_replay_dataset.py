import json

from src.learning.replay_dataset import ReplayDataset


def test_replay_dataset(tmp_path):
    replay_dir = tmp_path / "expert_replays"
    team_dir = replay_dir / "top_01"
    team_dir.mkdir(parents=True)

    metadata = {
        "top_01": {
            "rank": 1,
            "team_id": 123,
            "team_name": "Expert",
            "submission_id": 456,
        }
    }

    replay = {
        "info": {
            "EpisodeId": 1,
            "TeamNames": ["Opponent", "Expert"],
        },
        "rewards": [200, 100],
        "steps": [
            [
                {
                    "observation": {"player": 0, "day": 0, "hour": 0},
                    "action": {"farmer": ["WEST"], "hands": [], "market": []},
                },
                {
                    "observation": {"player": 1, "day": 0, "hour": 0},
                    "action": {"farmer": ["PASS"], "hands": [], "market": []},
                },
            ],
            [
                {
                    "observation": {"player": 0, "day": 0, "hour": 1},
                    "action": {"farmer": ["WEST"], "hands": [], "market": []},
                },
                {
                    "observation": {"player": 1, "day": 0, "hour": 1},
                    "action": {"farmer": ["PASS"], "hands": [], "market": []},
                },
            ],
        ],
    }

    with (replay_dir / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f)

    with (team_dir / "1.json").open("w", encoding="utf-8") as f:
        json.dump(replay, f)

    dataset = ReplayDataset(replay_dir)

    assert len(dataset) == 1

    sample = next(iter(dataset))
    assert sample["player"] == 1
    assert sample["team"] == "Expert"
    assert sample["episode"] == 1
    assert sample["observation"]["day"] == 0
    assert sample["action"]["farmer"] == ["PASS"]
