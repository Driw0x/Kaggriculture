import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.replay_dataset import ReplayDataset
from src.learning.state_encoder import encode_state, feature_names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/bc_dataset.pt"))
    parser.add_argument("--samples", type=int, default=1000)
    args = parser.parse_args()

    print("Loading replays...")
    replays = ReplayDataset(args.replays)

    print("Loading preencoded dataset...")
    data = torch.load(args.dataset, map_location="cpu", weights_only=False)

    current_names = feature_names()
    stored_names = data.get("feature_names")

    print(f"Replay samples: {len(replays)}")
    print(f"Preencoded samples: {len(data['state'])}")
    print(f"Current features: {len(current_names)}")
    print(f"Stored features: {len(stored_names) if stored_names else 'missing'}")

    if stored_names is None:
        print("ERROR: feature_names missing from dataset")
        return

    if stored_names != current_names:
        print("ERROR: feature_names differ")
        for index, (stored, current) in enumerate(zip(stored_names, current_names)):
            if stored != current:
                print(f"  {index}: stored={stored} current={current}")
        return

    print("Feature names: OK")

    count = min(args.samples, len(replays), len(data["state"]))
    mismatches = 0
    max_difference = 0.0

    for index in range(count):
        current = torch.tensor(encode_state(replays[index]["observation"]), dtype=torch.float32)
        stored = data["state"][index]

        difference = torch.abs(current - stored)
        sample_max = float(difference.max().item())

        if sample_max > 1e-6:
            mismatches += 1
            max_difference = max(max_difference, sample_max)

            if mismatches <= 5:
                print()
                print(f"Mismatch sample {index}: max_diff={sample_max}")

                for feature_index in torch.nonzero(difference > 1e-6).flatten().tolist():
                    print(
                        f"  {feature_index:>3} {current_names[feature_index]:<30} "
                        f"stored={stored[feature_index].item():.6f} "
                        f"current={current[feature_index].item():.6f}"
                    )

    print()
    print("=== RESULT ===")
    print(f"Checked: {count}")
    print(f"Mismatches: {mismatches}")
    print(f"Max difference: {max_difference:.8f}")

    if mismatches == 0:
        print("Encoding: OK")
    else:
        print("Encoding: INVALID")


if __name__ == "__main__":
    main()