import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.replay_dataset import ReplayDataset
from src.learning.target_encoder import encode_target, occurrence_names

OCCURRENCE_NAMES = occurrence_names()


def diagnose_hour(dataset, hour):
    samples = [
        sample for sample in dataset.samples
        if sample["observation"]["day"] == 0 and sample["observation"]["hour"] == hour
    ]

    print()
    print(f"=== DAY 0 HOUR {hour} ===")
    print(f"Samples: {len(samples)}")

    if not samples:
        return

    hire_counts = Counter()
    occurrence_counts = Counter()
    active_counts = Counter()

    for sample in samples:
        target = encode_target(sample["action"], sample["observation"])
        hire_counts[target["hire"]] += 1

        active = False

        if target["hire"] > 0:
            active = True

        for name, value in zip(OCCURRENCE_NAMES, target["occurrence"]):
            if value > 0:
                occurrence_counts[name] += 1
                active = True

        active_counts["active" if active else "noop"] += 1

    print("Hire:")
    for hire, count in sorted(hire_counts.items()):
        print(f"  {hire}: {count}/{len(samples)} ({100 * count / len(samples):.1f}%)")

    print("Occurrences:")
    for name in OCCURRENCE_NAMES:
        count = occurrence_counts[name]
        if count > 0:
            print(f"  {name:<25} {count:>3}/{len(samples)} ({100 * count / len(samples):5.1f}%)")

    active = active_counts["active"]
    noop = active_counts["noop"]

    print("Activity:")
    print(f"  active: {active}/{len(samples)} ({100 * active / len(samples):.1f}%)")
    print(f"  noop:   {noop}/{len(samples)} ({100 * noop / len(samples):.1f}%)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--hours", type=int, default=6)
    args = parser.parse_args()

    dataset = ReplayDataset(args.replays)

    print(f"Expert samples: {len(dataset)}")

    for hour in range(args.hours):
        diagnose_hour(dataset, hour)


if __name__ == "__main__":
    main()