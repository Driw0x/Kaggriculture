import argparse
import csv
import io
import json
import os
import subprocess
from pathlib import Path

COMPETITION = "kaggriculture"
OUTPUT_DIR = Path("data/expert_replays")


def run_command(*args):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    result = subprocess.run(["kaggle", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def run_kaggle_csv(*args):
    output = run_command(*args, "-v")
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if "," in line:
            return list(csv.DictReader(io.StringIO("\n".join(lines[i:]))))
    return []


def get_top_teams(limit):
    return run_kaggle_csv("competitions", "leaderboard", COMPETITION, "-s")[:limit]


def get_best_submission(team_id):
    rows = run_kaggle_csv("competitions", "team-submissions", str(team_id))
    if not rows:
        return None
    return max(rows, key=lambda row: float(row.get("publicScore") or row.get("score") or "-inf"))


def get_episode_ids(submission_id, limit):
    rows = run_kaggle_csv("competitions", "episodes", str(submission_id))
    rows.sort(key=lambda row: row.get("createTime", ""), reverse=True)

    episode_ids = []
    for row in rows:
        episode_id = row.get("id") or row.get("episodeId")
        if episode_id is not None:
            episode_ids.append(int(episode_id))
        if len(episode_ids) >= limit:
            break

    return episode_ids


def download_replay(episode_id, output_dir):
    path = output_dir / f"{episode_id}.json"

    if path.exists():
        print(f"SKIP {episode_id}")
        return

    run_command("competitions", "replay", str(episode_id), "-p", str(output_dir), "-q")

    downloaded_path = output_dir / f"episode-{episode_id}-replay.json"
    if not downloaded_path.exists():
        raise RuntimeError(f"Replay file not found for episode {episode_id}")

    downloaded_path.replace(path)
    print(f"OK   {episode_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--episodes", type=int, default=40)
    args = parser.parse_args()

    if args.top <= 0:
        raise ValueError("--top must be > 0")
    if args.episodes <= 0:
        raise ValueError("--episodes must be > 0")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    teams = get_top_teams(args.top)
    if not teams:
        raise RuntimeError("No leaderboard teams found")

    metadata = {}

    for rank, team in enumerate(teams, 1):
        team_id = int(team["teamId"])
        team_name = team["teamName"]

        print(f"\n#{rank} {team_name}")

        submission = get_best_submission(team_id)
        if submission is None:
            print("No submission")
            continue

        submission_id = submission.get("id") or submission.get("submissionId")
        if submission_id is None:
            print(f"Unknown submission format: {list(submission.keys())}")
            continue

        submission_id = int(submission_id)

        print(f"Submission: {submission_id}")

        episode_ids = get_episode_ids(submission_id, args.episodes)
        print(f"Episodes: {len(episode_ids)}")

        team_dir = OUTPUT_DIR / f"team_{team_id}"
        team_dir.mkdir(parents=True, exist_ok=True)

        metadata[team_dir.name] = {
            "rank": rank,
            "team_id": team_id,
            "team_name": team_name,
            "submission_id": submission_id,
        }

        for episode_id in episode_ids:
            try:
                download_replay(episode_id, team_dir)
            except Exception as e:
                print(f"ERR  {episode_id}: {e}")

    with (OUTPUT_DIR / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()