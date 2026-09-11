import argparse
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.replay_dataset import ReplayDataset
from src.learning.target_encoder import encode_target, occurrence_names, quantity_names, sell_names


def percentile(values, percentile_value):
    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return float(ordered[0])

    position = (len(ordered) - 1) * percentile_value
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower

    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def analyze(replay_dir):
    dataset = ReplayDataset(replay_dir)

    occurrences = Counter()
    quantities = defaultdict(list)
    sell_ratios = defaultdict(list)
    hires = Counter()
    errors = 0
    error_examples = []

    occurrence_keys = occurrence_names()
    quantity_keys = quantity_names()
    sell_keys = sell_names()

    for sample in dataset.samples:
        try:
            target = encode_target(sample["action"], sample["observation"])
        except Exception as e:
            errors += 1
            if len(error_examples) < 5:
                error_examples.append(
                    (
                        sample.get("team"),
                        sample.get("episode"),
                        sample["observation"].get("day"),
                        sample["observation"].get("hour"),
                        f"{type(e).__name__}: {e}",
                    )
                )
            continue

        hires[target["hire"]] += 1

        for name, value in zip(occurrence_keys, target["occurrence"]):
            if value > 0:
                occurrences[name] += 1

        for name, value in zip(quantity_keys, target["quantity"]):
            if value > 0:
                quantities[name].append(math.expm1(value))

        for name, value in zip(sell_keys, target["sell_ratio"]):
            if value > 0:
                sell_ratios[name].append(value)

    valid_samples = len(dataset) - errors

    print("\n=== DATASET ===")
    print(f"Samples: {len(dataset)}")
    print(f"Valid targets: {valid_samples}")
    print(f"Errors: {errors}")

    print("\n=== HIRE CLASSES ===")
    for hire in range(11):
        count = hires[hire]
        rate = count / valid_samples if valid_samples else 0.0
        print(f"hire={hire:<2} samples={count:<8} rate={rate:.2%}")

    print("\n=== OCCURRENCES ===")
    for name in occurrence_keys:
        count = occurrences[name]
        rate = count / valid_samples if valid_samples else 0.0
        print(f"{name:<25} samples={count:<8} rate={rate:.2%}")

    print("\n=== QUANTITIES ===")
    for name in quantity_keys:
        values = quantities[name]

        if not values:
            print(f"{name:<25} no active samples")
            continue

        print(
            f"{name:<25} "
            f"min={min(values):<7.2f} "
            f"mean={statistics.fmean(values):<8.2f} "
            f"median={statistics.median(values):<7.2f} "
            f"p90={percentile(values, 0.90):<7.2f} "
            f"p95={percentile(values, 0.95):<7.2f} "
            f"p99={percentile(values, 0.99):<7.2f} "
            f"max={max(values):<7.2f}"
        )

    print("\n=== SELL RATIOS ===")
    for name in sell_keys:
        values = sell_ratios[name]

        if not values:
            print(f"{name:<25} no active samples")
            continue

        full_sales = sum(value >= 0.999 for value in values)

        print(
            f"{name:<25} "
            f"samples={len(values):<7} "
            f"mean={statistics.fmean(values):<7.3f} "
            f"median={statistics.median(values):<7.3f} "
            f"p90={percentile(values, 0.90):<7.3f} "
            f"p95={percentile(values, 0.95):<7.3f} "
            f"p99={percentile(values, 0.99):<7.3f} "
            f"full={full_sales / len(values):.2%}"
        )

    if error_examples:
        print("\n=== ERROR EXAMPLES ===")
        for team, episode, day, hour, error in error_examples:
            print(f"team={team} episode={episode} day={day} hour={hour}: {error}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    args = parser.parse_args()

    if not args.replays.exists():
        raise FileNotFoundError(args.replays)

    analyze(args.replays)


if __name__ == "__main__":
    main()