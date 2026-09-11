import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.decision_extractor import extract_decision


def load_replays(replay_dir):
    for path in sorted(replay_dir.rglob("*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                yield path, json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"INVALID {path}: {e}")


def get_expert_player(replay):
    rewards = replay.get("rewards", [])

    if not rewards:
        return None

    valid = [
        (i, reward)
        for i, reward in enumerate(rewards)
        if isinstance(reward, (int, float))
    ]

    if not valid:
        return None

    return max(valid, key=lambda x: x[1])[0]


def analyze(replay_dir):
    replay_count = 0
    sample_count = 0
    invalid_samples = 0
    zero_decisions = 0

    teams = Counter()
    decisions = Counter()
    decision_samples = Counter()
    decisions_by_day = defaultdict(Counter)
    decisions_by_hour = defaultdict(Counter)

    for path, replay in load_replays(replay_dir):
        player = get_expert_player(replay)

        if player is None:
            continue

        replay_count += 1

        team_names = replay.get("info", {}).get("TeamNames", [])

        if player < len(team_names):
            teams[team_names[player]] += 1
        else:
            teams["UNKNOWN"] += 1

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

            decision = extract_decision(action)

            active = False

            for name, quantity in decision.items():
                if quantity <= 0:
                    continue

                active = True
                decisions[name] += quantity
                decision_samples[name] += 1
                decisions_by_day[day][name] += quantity
                decisions_by_hour[hour][name] += quantity

            if not active:
                zero_decisions += 1

    print("\n=== DATASET ===")
    print(f"Replays: {replay_count}")
    print(f"Samples: {sample_count}")
    print(f"Invalid samples: {invalid_samples}")

    if sample_count:
        print(
            f"Zero strategic decisions: "
            f"{zero_decisions} "
            f"({zero_decisions / sample_count:.2%})"
        )

    print("\n=== TEAMS ===")

    for team, count in teams.most_common():
        print(f"{team}: {count}")

    print("\n=== DECISIONS ===")

    for name, quantity in decisions.most_common():
        samples = decision_samples[name]

        print(
            f"{name:<25} "
            f"quantity={quantity:<8} "
            f"samples={samples:<8} "
            f"rate={samples / sample_count:.2%}"
        )

    print("\n=== DECISIONS BY DAY ===")

    for day in sorted(decisions_by_day):
        total = sum(
            decisions_by_day[day].values()
        )

        if total == 0:
            continue

        top = decisions_by_day[day].most_common(5)

        formatted = ", ".join(
            f"{name}={quantity}"
            for name, quantity in top
        )

        print(
            f"day {day:02d}: "
            f"{total:<6} "
            f"{formatted}"
        )

    print("\n=== DECISIONS BY HOUR ===")

    for hour in sorted(decisions_by_hour):
        total = sum(
            decisions_by_hour[hour].values()
        )

        if total == 0:
            continue

        top = decisions_by_hour[hour].most_common(5)

        formatted = ", ".join(
            f"{name}={quantity}"
            for name, quantity in top
        )

        print(
            f"hour {hour:02d}: "
            f"{total:<6} "
            f"{formatted}"
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--replays",
        type=Path,
        default=Path("data/expert_replays"),
    )

    args = parser.parse_args()

    if not args.replays.exists():
        raise FileNotFoundError(
            args.replays
        )

    analyze(args.replays)


if __name__ == "__main__":
    main()