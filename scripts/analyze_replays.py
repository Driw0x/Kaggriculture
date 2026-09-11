import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.decision_extractor import extract_decision


def load_replays(replay_dir):
    for path in sorted(replay_dir.rglob("*.json")):
        if path.name == "metadata.json":
            continue

        try:
            with path.open(encoding="utf-8") as f:
                yield path, json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"INVALID {path}: {e}")


def load_metadata(replay_dir):
    path = replay_dir / "metadata.json"
    if not path.exists():
        raise FileNotFoundError("Missing data/expert_replays/metadata.json")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def percentile(values, percentile_value):
    if not values:
        return 0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percentile_value
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower

    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def analyze(replay_dir):
    metadata = load_metadata(replay_dir)
    replay_count = 0
    sample_count = 0
    invalid_samples = 0
    zero_decisions = 0

    teams = Counter()
    decisions = Counter()
    decision_samples = Counter()
    decision_quantities = defaultdict(list)
    decisions_by_day = defaultdict(Counter)
    decisions_by_hour = defaultdict(Counter)

    for path, replay in load_replays(replay_dir):
        expert = metadata.get(path.parent.name)
        if expert is None:
            continue

        team_name = expert["team_name"]
        team_names = replay.get("info", {}).get("TeamNames", [])

        if team_name not in team_names:
            continue

        player = team_names.index(team_name)
        replay_count += 1
        teams[team_name] += 1

        for step in replay.get("steps", []):
            if player >= len(step):
                invalid_samples += 1
                continue

            record = step[player]
            observation = record.get("observation")
            action = record.get("action")

            if observation is None or action is None:
                invalid_samples += 1
                continue

            if observation.get("player") != player:
                invalid_samples += 1
                continue

            sample_count += 1

            day = observation.get("day", -1)
            hour = observation.get("hour", -1)
            decision = extract_decision(action, observation)
            active = False

            for name, quantity in decision.items():
                if quantity <= 0:
                    continue

                active = True
                decisions[name] += quantity
                decision_samples[name] += 1
                decision_quantities[name].append(quantity)
                decisions_by_day[day][name] += quantity
                decisions_by_hour[hour][name] += quantity

            if not active:
                zero_decisions += 1

    print("\n=== DATASET ===")
    print(f"Replays: {replay_count}")
    print(f"Samples: {sample_count}")
    print(f"Invalid samples: {invalid_samples}")

    if sample_count:
        print(f"Zero strategic decisions: {zero_decisions} ({zero_decisions / sample_count:.2%})")

    print("\n=== TEAMS ===")
    for team, count in teams.most_common():
        print(f"{team}: {count}")

    print("\n=== DECISIONS ===")
    for name, quantity in decisions.most_common():
        samples = decision_samples[name]
        print(f"{name:<25} quantity={quantity:<8} samples={samples:<8} rate={samples / sample_count:.2%}")

    print("\n=== QUANTITY STATISTICS ===")
    for name in sorted(decision_quantities):
        values = decision_quantities[name]

        minimum = min(values)
        maximum = max(values)
        mean = statistics.fmean(values)
        median = statistics.median(values)
        p90 = percentile(values, 0.90)
        p95 = percentile(values, 0.95)
        p99 = percentile(values, 0.99)

        print(
            f"{name:<25} "
            f"min={minimum:<7.2f} "
            f"mean={mean:<8.2f} "
            f"median={median:<7.2f} "
            f"p90={p90:<7.2f} "
            f"p95={p95:<7.2f} "
            f"p99={p99:<7.2f} "
            f"max={maximum:<7.2f}"
        )

    print("\n=== DECISIONS BY DAY ===")
    for day in sorted(decisions_by_day):
        total = sum(decisions_by_day[day].values())

        if total == 0:
            continue

        top = decisions_by_day[day].most_common(5)
        formatted = ", ".join(f"{name}={quantity}" for name, quantity in top)

        print(f"day {day:02d}: {total:<6} {formatted}")

    print("\n=== DECISIONS BY HOUR ===")
    for hour in sorted(decisions_by_hour):
        total = sum(decisions_by_hour[hour].values())

        if total == 0:
            continue

        top = decisions_by_hour[hour].most_common(5)
        formatted = ", ".join(f"{name}={quantity}" for name, quantity in top)

        print(f"hour {hour:02d}: {total:<6} {formatted}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    args = parser.parse_args()

    if not args.replays.exists():
        raise FileNotFoundError(args.replays)

    analyze(args.replays)


if __name__ == "__main__":
    main()