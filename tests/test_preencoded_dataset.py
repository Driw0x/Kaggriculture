import torch

from src.learning.preencoded_dataset import (
    PreencodedBCDataset,
    split_preencoded_by_episode,
)


def create_dataset(path):
    torch.save({
        "state": torch.zeros((6, 3)),
        "hire": torch.zeros(6),
        "purchase_bundle": torch.zeros(6, dtype=torch.long),
        "occurrence": torch.zeros((6, 2)),
        "quantity": torch.zeros((6, 1)),
        "quantity_mask": torch.zeros((6, 1)),
        "sell_ratio": torch.zeros((6, 1)),
        "sell_mask": torch.zeros((6, 1)),
        "episode": torch.tensor([0, 0, 1, 1, 2, 2]),
    }, path)


def test_preencoded_dataset(tmp_path):
    path = tmp_path / "dataset.pt"
    create_dataset(path)

    dataset = PreencodedBCDataset(path)

    assert len(dataset) == 6
    assert dataset[0]["state"].shape == (3,)
    assert dataset[0]["hire"].dtype == torch.float32
    assert dataset[0]["purchase_bundle"].dtype == torch.long


def test_split_by_episode(tmp_path):
    path = tmp_path / "dataset.pt"
    create_dataset(path)

    dataset = PreencodedBCDataset(path)

    train_indices, val_indices = (
        split_preencoded_by_episode(
            dataset,
            val_ratio=1 / 3,
            seed=42,
        )
    )

    train_episodes = {
        int(dataset.episodes[index])
        for index in train_indices
    }

    val_episodes = {
        int(dataset.episodes[index])
        for index in val_indices
    }

    assert train_episodes
    assert val_episodes
    assert train_episodes.isdisjoint(
        val_episodes
    )
    assert len(train_indices) + len(
        val_indices
    ) == len(dataset)
