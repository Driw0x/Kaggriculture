import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.decision_extractor import extract_decision


PHASES = {
    "early": (0, 5),
    "mid": (6, 19),
    "late": (20, 29),
}

# Décisions particulièrement utiles pour comparer des stratégies Kaggriculture.
KEY_DECISIONS = [
    "hire",
    "buy_land",
    "fertilize",
    "buy_product_WHEAT",
    "buy_product_FERTILIZER",
    "buy_seed_WHEAT",
    "buy_seed_CARROT",
    "buy_seed_STRAWBERRY",
    "buy_seed_TOMATO",
    "buy_seed_MELON",
    "plant_WHEAT",
    "plant_CARROT",
    "plant_STRAWBERRY",
    "plant_TOMATO",
    "plant_MELON",
    "sell_WHEAT",
    "sell_CARROT",
    "sell_STRAWBERRY",
    "sell_TOMATO",
    "sell_MELON",
    "sell_FERTILIZER",
    "sell_MILK",
    "sell_WOOL",
    "sell_EGG",
    "build_pasture",
    "build_coop",
    "buy_animal_COW",
    "buy_animal_SHEEP",
    "buy_animal_GOOSE",
]


def load_replays(replay_dir):
    for path in sorted(replay_dir.rglob("*.json")):
        if path.name in {"metadata.json", "analysis_summary.json"}:
            continue

        try:
            with path.open(encoding="utf-8") as f:
                yield path, json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"INVALID {path}: {e}")


def load_metadata(replay_dir):
    path = replay_dir / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")

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


def safe_mean(values):
    return statistics.fmean(values) if values else 0.0


def phase_for_day(day):
    for phase, (start, end) in PHASES.items():
        if start <= day <= end:
            return phase
    return "other"


def time_index(day, hour):
    if not isinstance(day, int) or not isinstance(hour, int) or day < 0 or hour < 0:
        return None
    return day * 24 + hour


def format_time(index):
    if index is None:
        return "-"
    index = int(round(index))
    return f"D{index // 24:02d} H{index % 24:02d}"


def new_team_stats(rank=None):
    return {
        "rank": rank,
        "replays": 0,
        "samples": 0,
        "zero_decisions": 0,
        "decisions": Counter(),
        "decision_samples": Counter(),
        "phase_decisions": defaultdict(Counter),
        "first_occurrences": defaultdict(list),
    }


def analyze(replay_dir, top_decisions=8, output_json=None):
    metadata = load_metadata(replay_dir)

    replay_count = 0
    sample_count = 0
    invalid_samples = 0
    zero_decisions = 0

    teams = Counter()
    team_stats = {}

    decisions = Counter()
    decision_samples = Counter()
    decision_quantities = defaultdict(list)
    decisions_by_day = defaultdict(Counter)
    decisions_by_hour = defaultdict(Counter)
    decisions_by_phase = defaultdict(Counter)
    first_occurrences = defaultdict(list)

    for path, replay in load_replays(replay_dir):
        expert = metadata.get(path.parent.name)
        if expert is None:
            continue

        team_name = expert["team_name"]
        rank = expert.get("rank")
        team_names = replay.get("info", {}).get("TeamNames", [])

        if team_name not in team_names:
            continue

        player = team_names.index(team_name)
        replay_count += 1
        teams[team_name] += 1

        stats = team_stats.setdefault(team_name, new_team_stats(rank))
        if stats["rank"] is None and rank is not None:
            stats["rank"] = rank
        stats["replays"] += 1

        replay_first = {}

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
            stats["samples"] += 1

            day = observation.get("day", -1)
            hour = observation.get("hour", -1)
            phase = phase_for_day(day)
            current_time = time_index(day, hour)
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
                decisions_by_phase[phase][name] += quantity

                stats["decisions"][name] += quantity
                stats["decision_samples"][name] += 1
                stats["phase_decisions"][phase][name] += quantity

                if current_time is not None and name not in replay_first:
                    replay_first[name] = current_time

            if not active:
                zero_decisions += 1
                stats["zero_decisions"] += 1

        for name, first_time in replay_first.items():
            first_occurrences[name].append(first_time)
            stats["first_occurrences"][name].append(first_time)

    print("\n=== DATASET ===")
    print(f"Replays: {replay_count}")
    print(f"Samples: {sample_count}")
    print(f"Invalid samples: {invalid_samples}")
    if sample_count:
        print(f"Zero strategic decisions: {zero_decisions} ({zero_decisions / sample_count:.2%})")

    print("\n=== TEAMS ===")
    for team, stats in sorted(
        team_stats.items(), key=lambda item: (item[1]["rank"] is None, item[1]["rank"] or 10**9, item[0])
    ):
        rank = stats["rank"] if stats["rank"] is not None else "?"
        zero_rate = stats["zero_decisions"] / stats["samples"] if stats["samples"] else 0
        print(
            f"#{rank:<3} {team:<25} "
            f"replays={stats['replays']:<4} "
            f"samples/game={stats['samples'] / stats['replays'] if stats['replays'] else 0:>7.1f} "
            f"zero={zero_rate:>6.2%}"
        )

    print("\n=== DECISIONS ===")
    for name, quantity in decisions.most_common():
        samples = decision_samples[name]
        print(
            f"{name:<25} quantity={quantity:<8} samples={samples:<8} "
            f"rate={samples / sample_count if sample_count else 0:.2%} "
            f"qty/game={quantity / replay_count if replay_count else 0:.2f}"
        )

    print("\n=== QUANTITY STATISTICS ===")
    for name in sorted(decision_quantities):
        values = decision_quantities[name]
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

    print("\n=== GAME PHASES (NORMALIZED PER REPLAY) ===")
    for phase in ("early", "mid", "late", "other"):
        phase_counter = decisions_by_phase.get(phase)
        if not phase_counter:
            continue
        start_end = PHASES.get(phase)
        label = f"days {start_end[0]}-{start_end[1]}" if start_end else "outside normal range"
        top = phase_counter.most_common(top_decisions)
        formatted = ", ".join(
            f"{name}={quantity / replay_count:.2f}/game" for name, quantity in top
        ) if replay_count else ""
        print(f"{phase:<6} ({label}): {formatted}")

    print("\n=== STRATEGY BY TEAM / RANK (NORMALIZED PER REPLAY) ===")
    ordered_teams = sorted(
        team_stats.items(), key=lambda item: (item[1]["rank"] is None, item[1]["rank"] or 10**9, item[0])
    )
    for team, stats in ordered_teams:
        rank = stats["rank"] if stats["rank"] is not None else "?"
        replays = stats["replays"]
        print(f"\n#{rank} {team} ({replays} replays)")
        for name, quantity in stats["decisions"].most_common(top_decisions):
            sample_rate = stats["decision_samples"][name] / stats["samples"] if stats["samples"] else 0
            print(
                f"  {name:<25} qty/game={quantity / replays:>8.2f} "
                f"sample_rate={sample_rate:>7.2%}"
            )

    present_keys = [name for name in KEY_DECISIONS if name in decisions]
    print("\n=== KEY DECISIONS BY TEAM (QTY / GAME) ===")
    for team, stats in ordered_teams:
        rank = stats["rank"] if stats["rank"] is not None else "?"
        replays = stats["replays"]
        values = [
            f"{name}={stats['decisions'][name] / replays:.2f}"
            for name in present_keys
            if stats["decisions"][name] > 0
        ]
        print(f"#{rank} {team}: " + ", ".join(values))

    print("\n=== FIRST OCCURRENCE TIMING ===")
    # Priorité aux décisions globalement fréquentes afin de garder une sortie lisible.
    for name, _ in decisions.most_common(max(top_decisions * 2, 12)):
        values = first_occurrences.get(name, [])
        if not values:
            continue
        coverage = len(values) / replay_count if replay_count else 0
        print(
            f"{name:<25} "
            f"coverage={coverage:>6.2%} "
            f"mean={format_time(safe_mean(values)):<8} "
            f"median={format_time(statistics.median(values)):<8}"
        )

    print("\n=== FIRST OCCURRENCE BY TEAM (KEY DECISIONS) ===")
    timing_keys = [
        "hire",
        "buy_land",
        "fertilize",
        "buy_seed_MELON",
        "buy_seed_STRAWBERRY",
        "buy_seed_TOMATO",
        "buy_animal_COW",
        "buy_animal_SHEEP",
        "buy_animal_GOOSE",
    ]
    for team, stats in ordered_teams:
        rank = stats["rank"] if stats["rank"] is not None else "?"
        replays = stats["replays"]
        parts = []
        for name in timing_keys:
            values = stats["first_occurrences"].get(name, [])
            if not values:
                continue
            parts.append(
                f"{name}={format_time(statistics.median(values))} "
                f"({len(values) / replays:.0%})"
            )
        print(f"#{rank} {team}: " + (", ".join(parts) if parts else "no key timing data"))

    summary = {
        "dataset": {
            "replays": replay_count,
            "samples": sample_count,
            "invalid_samples": invalid_samples,
            "zero_decisions": zero_decisions,
            "zero_decision_rate": zero_decisions / sample_count if sample_count else 0,
        },
        "global": {
            "decisions": dict(decisions),
            "decision_samples": dict(decision_samples),
            "decisions_per_replay": {
                name: quantity / replay_count if replay_count else 0
                for name, quantity in decisions.items()
            },
            "phases": {
                phase: dict(counter) for phase, counter in decisions_by_phase.items()
            },
            "first_occurrences": {
                name: {
                    "coverage": len(values) / replay_count if replay_count else 0,
                    "mean_time_index": safe_mean(values),
                    "median_time_index": statistics.median(values),
                }
                for name, values in first_occurrences.items()
                if values
            },
        },
        "teams": {},
    }

    for team, stats in ordered_teams:
        replays = stats["replays"]
        summary["teams"][team] = {
            "rank": stats["rank"],
            "replays": replays,
            "samples": stats["samples"],
            "zero_decision_rate": stats["zero_decisions"] / stats["samples"] if stats["samples"] else 0,
            "decisions": dict(stats["decisions"]),
            "decisions_per_replay": {
                name: quantity / replays if replays else 0
                for name, quantity in stats["decisions"].items()
            },
            "phases": {
                phase: dict(counter) for phase, counter in stats["phase_decisions"].items()
            },
            "first_occurrences": {
                name: {
                    "coverage": len(values) / replays if replays else 0,
                    "mean_time_index": safe_mean(values),
                    "median_time_index": statistics.median(values),
                }
                for name, values in stats["first_occurrences"].items()
                if values
            },
        }

    if output_json is not None:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\nJSON summary written to: {output_json}")

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument(
        "--top-decisions",
        type=int,
        default=8,
        help="Number of top decisions shown in compact team/phase summaries.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Optional path for a machine-readable analysis summary.",
    )
    args = parser.parse_args()

    if not args.replays.exists():
        raise FileNotFoundError(args.replays)
    if args.top_decisions <= 0:
        raise ValueError("--top-decisions must be > 0")

    analyze(
        replay_dir=args.replays,
        top_decisions=args.top_decisions,
        output_json=args.output_json,
    )


if __name__ == "__main__":
    main()
