import random
from pathlib import Path

import torch
from torch.utils.data import Dataset


class PreencodedBCDataset(Dataset):
    def __init__(self, path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} not found. Run: python scripts/preencode_bc.py")

        self.data = torch.load(self.path, map_location="cpu", weights_only=False)
        required = ("state", "hire", "purchase_bundle", "occurrence", "quantity", "quantity_mask", "sell_ratio", "sell_mask", "episode")

        for key in required:
            if key not in self.data:
                raise ValueError(f"Missing field in preencoded dataset: {key}")

        size = len(self.data["state"])
        for key in required:
            if len(self.data[key]) != size:
                raise ValueError(f"Invalid size for field: {key}")

    def __len__(self):
        return len(self.data["state"])

    def __getitem__(self, index):
        return {
            "state": self.data["state"][index],
            "hire": self.data["hire"][index],
            "purchase_bundle": self.data["purchase_bundle"][index],
            "occurrence": self.data["occurrence"][index],
            "quantity": self.data["quantity"][index],
            "quantity_mask": self.data["quantity_mask"][index],
            "sell_ratio": self.data["sell_ratio"][index],
            "sell_mask": self.data["sell_mask"][index],
        }

    @property
    def episodes(self):
        return self.data["episode"]


def split_preencoded_by_episode(dataset, val_ratio=0.2, seed=42):
    if not 0 < val_ratio < 1:
        raise ValueError("val_ratio must be between 0 and 1")

    episodes = dataset.episodes.tolist()
    episode_ids = list(dict.fromkeys(episodes))

    if len(episode_ids) < 2:
        raise ValueError("At least two episodes are required")

    random.Random(seed).shuffle(episode_ids)
    val_count = max(1, int(len(episode_ids) * val_ratio))
    val_count = min(val_count, len(episode_ids) - 1)
    val_episodes = set(episode_ids[:val_count])

    train_indices = []
    val_indices = []
    for index, episode in enumerate(episodes):
        if episode in val_episodes:
            val_indices.append(index)
        else:
            train_indices.append(index)

    return train_indices, val_indices