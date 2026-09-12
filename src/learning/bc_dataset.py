import random

import torch
from torch.utils.data import Dataset

from src.learning.state_encoder import encode_state
from src.learning.target_encoder import encode_target


class BCDataset(Dataset):
    def __init__(self, replay_dataset, indices=None):
        self.replay_dataset = replay_dataset
        self.indices = list(range(len(replay_dataset))) if indices is None else list(indices)

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        sample = self.replay_dataset[self.indices[index]]
        state = encode_state(sample["observation"])
        target = encode_target(sample["action"], sample["observation"])

        return {
            "state": torch.tensor(state, dtype=torch.float32),
            "hire": torch.tensor(target["hire"], dtype=torch.float32),
            "purchase_bundle": torch.tensor(target["purchase_bundle"], dtype=torch.long),
            "occurrence": torch.tensor(target["occurrence"], dtype=torch.float32),
            "quantity": torch.tensor(target["quantity"], dtype=torch.float32),
            "quantity_mask": torch.tensor(target["quantity_mask"], dtype=torch.float32),
            "sell_ratio": torch.tensor(target["sell_ratio"], dtype=torch.float32),
            "sell_mask": torch.tensor(target["sell_mask"], dtype=torch.float32),
        }


def split_by_episode(replay_dataset, val_ratio=0.2, seed=42):
    if not 0 < val_ratio < 1:
        raise ValueError("val_ratio must be between 0 and 1")

    episodes = {}
    for index in range(len(replay_dataset)):
        episode = replay_dataset[index].get("episode")
        if episode is None:
            raise ValueError("Sample without episode id")
        episodes.setdefault(episode, []).append(index)

    episode_ids = list(episodes)
    if len(episode_ids) < 2:
        raise ValueError("At least two episodes are required")

    random.Random(seed).shuffle(episode_ids)
    val_count = max(1, int(len(episode_ids) * val_ratio))
    val_count = min(val_count, len(episode_ids) - 1)
    val_episodes = set(episode_ids[:val_count])

    train_indices = []
    val_indices = []
    for episode, indices in episodes.items():
        if episode in val_episodes:
            val_indices.extend(indices)
        else:
            train_indices.extend(indices)

    return train_indices, val_indices