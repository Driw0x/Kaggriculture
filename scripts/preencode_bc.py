import argparse
import gc
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.replay_dataset import ReplayDataset
from src.learning.state_encoder import encode_state, feature_names
from src.learning.target_encoder import PURCHASE_NAMES, encode_target, occurrence_names, quantity_names, sell_names


def count_samples(replay_dataset, progress):
    sample_count = 0

    for replay_index, path in enumerate(replay_dataset.paths, start=1):
        for _ in replay_dataset.iter_replay_samples(path):
            sample_count += 1

        if progress > 0 and (replay_index % 100 == 0 or replay_index == len(replay_dataset.paths)):
            print(f"Counting replays: {replay_index}/{len(replay_dataset.paths)} | samples={sample_count}")

        gc.collect()

    return sample_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/bc_dataset.pt"))
    parser.add_argument("--progress", type=int, default=10000)
    args = parser.parse_args()

    print("Indexing replays...")
    replay_dataset = ReplayDataset(args.replays)

    print(f"Replay files: {len(replay_dataset.paths)}")
    print("Counting valid samples...")
    sample_count = count_samples(replay_dataset, args.progress)

    state_size = len(feature_names())
    occurrence_size = len(occurrence_names())
    quantity_size = len(quantity_names())
    sell_size = len(sell_names())

    print(f"Samples: {sample_count}")
    print(f"State features: {state_size}")
    print(f"Purchase actions: {len(PURCHASE_NAMES)}")
    print("Encoding...")

    states = torch.empty((sample_count, state_size), dtype=torch.float32)
    hires = torch.empty(sample_count, dtype=torch.float32)
    purchase_bundles = torch.empty(sample_count, dtype=torch.long)
    occurrences = torch.empty((sample_count, occurrence_size), dtype=torch.float32)
    quantities = torch.empty((sample_count, quantity_size), dtype=torch.float32)
    quantity_masks = torch.empty((sample_count, quantity_size), dtype=torch.float32)
    sell_ratios = torch.empty((sample_count, sell_size), dtype=torch.float32)
    sell_masks = torch.empty((sample_count, sell_size), dtype=torch.float32)
    episodes = torch.empty(sample_count, dtype=torch.long)

    episode_map = {}
    index = 0

    for replay_index, path in enumerate(replay_dataset.paths, start=1):
        for sample in replay_dataset.iter_replay_samples(path):
            state = encode_state(sample["observation"])
            target = encode_target(sample["action"], sample["observation"])

            states[index] = torch.tensor(state, dtype=torch.float32)
            hires[index] = target["hire"]
            purchase_bundles[index] = target["purchase_bundle"]
            occurrences[index] = torch.tensor(target["occurrence"], dtype=torch.float32)
            quantities[index] = torch.tensor(target["quantity"], dtype=torch.float32)
            quantity_masks[index] = torch.tensor(target["quantity_mask"], dtype=torch.float32)
            sell_ratios[index] = torch.tensor(target["sell_ratio"], dtype=torch.float32)
            sell_masks[index] = torch.tensor(target["sell_mask"], dtype=torch.float32)

            episode = sample.get("episode")
            if episode is None:
                raise ValueError(f"Sample {index} has no episode id")

            if episode not in episode_map:
                episode_map[episode] = len(episode_map)

            episodes[index] = episode_map[episode]
            index += 1

            if args.progress > 0 and (index % args.progress == 0 or index == sample_count):
                print(f"{index}/{sample_count} ({100 * index / sample_count:.1f}%)")

        gc.collect()

    if index != sample_count:
        raise RuntimeError(f"Expected {sample_count} samples, encoded {index}")

    data = {
        "state": states,
        "hire": hires,
        "purchase_bundle": purchase_bundles,
        "occurrence": occurrences,
        "quantity": quantities,
        "quantity_mask": quantity_masks,
        "sell_ratio": sell_ratios,
        "sell_mask": sell_masks,
        "episode": episodes,
        "feature_names": feature_names(),
        "purchase_names": PURCHASE_NAMES,
        "occurrence_names": occurrence_names(),
        "quantity_names": quantity_names(),
        "sell_names": sell_names(),
        "sample_count": sample_count,
        "episode_count": len(episode_map),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(data, args.output)

    print()
    print("Done")
    print(f"Samples: {sample_count}")
    print(f"Episodes: {len(episode_map)}")
    print(f"Output: {args.output}")
    print(f"Size: {args.output.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
