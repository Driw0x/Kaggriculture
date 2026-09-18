import torch

from src.learning.bc_dataset import BCDataset, split_by_episode
from src.learning.state_encoder import feature_names
from src.learning.target_encoder import occurrence_names, quantity_names, sell_names


class FakeReplayDataset:
    def __init__(self):
        self.samples = [
            self._sample(1, 0),
            self._sample(1, 1),
            self._sample(2, 2),
            self._sample(2, 3),
            self._sample(3, 4),
            self._sample(3, 5),
            self._sample(4, 6),
            self._sample(4, 7),
        ]

    def _sample(self, episode, hour):
        return {
            "episode": episode,
            "observation": {
                "player": 0,
                "day": 0,
                "hour": hour,
                "farms": [
                    {
                        "money": 1000,
                        "hires_today": 0,
                        "hands": [],
                        "unlocked_quadrants": ["NW"],
                        "tiles": [[None] * 10 for _ in range(10)],
                    }
                ],
                "private": {
                    "shed": {"WHEAT": 10},
                    "seeds": {},
                    "inventories": [],
                },
                "market": {
                    "inventory": {},
                    "prices": {},
                },
                "town": {
                    "unlocked_shops": [],
                },
            },
            "action": {
                "farmer": ["PASS"],
                "hands": [],
                "market": [
                    ["HIRE"],
                    ["BUY_SEED", "WHEAT", 2],
                    ["SELL", "WHEAT", 5],
                ],
            },
        }

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]


def test_bc_dataset():
    replay_dataset = FakeReplayDataset()
    dataset = BCDataset(replay_dataset)
    sample = dataset[0]

    assert sample["state"].shape == (len(feature_names()),)
    assert sample["hire"].shape == ()
    assert sample["purchase_bundle"].shape == ()
    assert sample["occurrence"].shape == (len(occurrence_names()),)
    assert sample["quantity"].shape == (len(quantity_names()),)
    assert sample["sell_ratio"].shape == (len(sell_names()),)

    assert sample["hire"].dtype == torch.float32
    assert sample["purchase_bundle"].dtype == torch.long
    assert sample["state"].dtype == torch.float32
    assert sample["quantity_mask"].sum() == 1
    assert sample["sell_mask"].sum() == 1


def test_split_by_episode():
    replay_dataset = FakeReplayDataset()
    train_indices, val_indices = split_by_episode(replay_dataset, val_ratio=0.25, seed=42)

    train_episodes = {replay_dataset[index]["episode"] for index in train_indices}
    val_episodes = {replay_dataset[index]["episode"] for index in val_indices}

    assert train_indices
    assert val_indices
    assert train_episodes.isdisjoint(val_episodes)
    assert len(train_indices) + len(val_indices) == len(replay_dataset)
