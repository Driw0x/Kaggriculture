import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.bc_dataset import QUANTITY_OCCURRENCE_INDICES, SELL_OCCURRENCE_INDICES
from src.learning.replay_dataset import ReplayDataset
from src.learning.state_encoder import encode_state, feature_names
from src.learning.target_encoder import encode_target, occurrence_names, quantity_names, sell_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/bc_dataset.pt"))
    parser.add_argument("--progress", type=int, default=10000)
    args = parser.parse_args()

    print("Loading replays...")
    replay_dataset = ReplayDataset(args.replays)

    sample_count = len(replay_dataset)
    state_size = len(feature_names())
    occurrence_size = len(occurrence_names())
    quantity_size = len(quantity_names())
    sell_size = len(sell_names())

    print(f"Samples: {sample_count}")
    print(f"State features: {state_size}")
    print("Encoding...")

    states = torch.empty((sample_count, state_size), dtype=torch.float32)
    hires = torch.empty(sample_count, dtype=torch.long)
    occurrences = torch.empty((sample_count, occurrence_size), dtype=torch.float32)
    quantities = torch.empty((sample_count, quantity_size), dtype=torch.float32)
    quantity_masks = torch.empty((sample_count, quantity_size), dtype=torch.float32)
    sell_ratios = torch.empty((sample_count, sell_size), dtype=torch.float32)
    sell_masks = torch.empty((sample_count, sell_size), dtype=torch.float32)
    episodes = torch.empty(sample_count, dtype=torch.long)

    episode_map = {}

    for index in range(sample_count):
        sample = replay_dataset[index]
        state = encode_state(sample["observation"])
        target = encode_target(sample["action"], sample["observation"])

        occurrence = torch.tensor(target["occurrence"], dtype=torch.float32)

        states[index] = torch.tensor(state, dtype=torch.float32)
        hires[index] = target["hire"]
        occurrences[index] = occurrence
        quantities[index] = torch.tensor(target["quantity"], dtype=torch.float32)
        quantity_masks[index] = occurrence[QUANTITY_OCCURRENCE_INDICES]
        sell_ratios[index] = torch.tensor(target["sell_ratio"], dtype=torch.float32)
        sell_masks[index] = occurrence[SELL_OCCURRENCE_INDICES]

        episode = sample.get("episode")

        if episode is None:
            raise ValueError(f"Sample {index} has no episode id")

        if episode not in episode_map:
            episode_map[episode] = len(episode_map)

        episodes[index] = episode_map[episode]

        if args.progress > 0 and ((index + 1) % args.progress == 0 or index + 1 == sample_count):
            print(f"{index + 1}/{sample_count} ({100 * (index + 1) / sample_count:.1f}%)")

    data = {
        "state": states,
        "hire": hires,
        "occurrence": occurrences,
        "quantity": quantities,
        "quantity_mask": quantity_masks,
        "sell_ratio": sell_ratios,
        "sell_mask": sell_masks,
        "episode": episodes,
        "feature_names": feature_names(),
        "occurrence_names": occurrence_names(),
        "quantity_names": quantity_names(),
        "sell_names": sell_names(),
        "sample_count": sample_count,
        "episode_count": len(episode_map),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, args.output)

    size_mb = args.output.stat().st_size / 1024 / 1024

    print()
    print("Done")
    print(f"Samples: {sample_count}")
    print(f"Episodes: {len(episode_map)}")
    print(f"Output: {args.output}")
    print(f"Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()