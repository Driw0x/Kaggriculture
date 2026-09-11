import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.state_encoder import encode_state, feature_names


def load_metadata(replay_dir):
    path = replay_dir / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_replays(replay_dir):
    for path in sorted(replay_dir.rglob("*.json")):
        if path.name == "metadata.json":
            continue

        try:
            with path.open(encoding="utf-8") as f:
                yield path, json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"INVALID {path}: {e}")


def add_values(counter, value):
    if isinstance(value, dict):
        for key in value:
            counter[str(key)] += 1
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            counter[str(item)] += 1
    elif value is not None:
        counter[str(value)] += 1


def analyze(replay_dir):
    metadata = load_metadata(replay_dir)
    names = feature_names()
    feature_min = [float("inf")] * len(names)
    feature_max = [float("-inf")] * len(names)
    feature_nonzero = [0] * len(names)

    replay_count = 0
    observation_count = 0
    encoding_errors = 0
    size_errors = 0
    nonfinite_states = 0
    metadata_mismatches = 0

    quadrant_types = Counter()
    quadrant_values = Counter()
    shop_types = Counter()
    shop_values = Counter()
    tile_container_types = Counter()
    tile_row_types = Counter()
    tile_types = Counter()
    tile_keys = Counter()
    crop_values = Counter()
    animal_values = Counter()
    inventory_types = Counter()
    inventory_entry_types = Counter()
    farm_keys = Counter()
    private_keys = Counter()
    market_keys = Counter()
    town_keys = Counter()

    error_examples = []

    for path, replay in load_replays(replay_dir):
        expert = metadata.get(path.parent.name)
        if expert is None:
            metadata_mismatches += 1
            continue

        team_names = replay.get("info", {}).get("TeamNames", [])
        team_name = expert["team_name"]

        if team_name not in team_names:
            metadata_mismatches += 1
            continue

        player = team_names.index(team_name)
        replay_count += 1

        for step in replay.get("steps", []):
            if player >= len(step):
                continue

            observation = step[player].get("observation")
            if observation is None or observation.get("player") != player:
                continue

            observation_count += 1

            farms = observation.get("farms", [])
            if not isinstance(farms, list) or player >= len(farms):
                if len(error_examples) < 5:
                    error_examples.append((path.name, "invalid farms structure"))
                encoding_errors += 1
                continue

            farm = farms[player]
            private = observation.get("private", {})
            market = observation.get("market", {})
            town = observation.get("town", {})

            if isinstance(farm, dict):
                farm_keys.update(farm.keys())

            if isinstance(private, dict):
                private_keys.update(private.keys())

            if isinstance(market, dict):
                market_keys.update(market.keys())

            if isinstance(town, dict):
                town_keys.update(town.keys())

            quadrants = farm.get("unlocked_quadrants", [])
            quadrant_types[type(quadrants).__name__] += 1
            add_values(quadrant_values, quadrants)

            shops = town.get("unlocked_shops", [])
            shop_types[type(shops).__name__] += 1
            add_values(shop_values, shops)

            inventories = private.get("inventories", [])
            inventory_types[type(inventories).__name__] += 1

            if isinstance(inventories, (list, tuple)):
                for inventory in inventories:
                    inventory_entry_types[type(inventory).__name__] += 1

            tiles = farm.get("tiles", [])
            tile_container_types[type(tiles).__name__] += 1

            if isinstance(tiles, list):
                for row in tiles:
                    tile_row_types[type(row).__name__] += 1

                    if not isinstance(row, list):
                        continue

                    for tile in row:
                        tile_types[type(tile).__name__] += 1

                        if not isinstance(tile, dict):
                            continue

                        tile_keys.update(tile.keys())

                        crop = tile.get("crop")
                        animal = tile.get("animal")

                        if crop is not None:
                            crop_values[str(crop)] += 1

                        if animal is not None:
                            animal_values[str(animal)] += 1

            try:
                state = encode_state(observation)
            except Exception as e:
                encoding_errors += 1
                if len(error_examples) < 5:
                    error_examples.append((path.name, f"{type(e).__name__}: {e}"))
                continue

            if len(state) != len(names):
                size_errors += 1
                continue

            if not all(math.isfinite(value) for value in state):
                nonfinite_states += 1
                continue

            for i, value in enumerate(state):
                feature_min[i] = min(feature_min[i], value)
                feature_max[i] = max(feature_max[i], value)

                if value != 0:
                    feature_nonzero[i] += 1

    print("\n=== DATASET ===")
    print(f"Replays: {replay_count}")
    print(f"Observations: {observation_count}")
    print(f"Metadata mismatches: {metadata_mismatches}")
    print(f"Encoding errors: {encoding_errors}")
    print(f"Size errors: {size_errors}")
    print(f"Non-finite states: {nonfinite_states}")
    print(f"Feature count: {len(names)}")

    print("\n=== UNLOCKED QUADRANTS ===")
    print(f"Types: {dict(quadrant_types)}")
    print(f"Values: {dict(quadrant_values)}")

    print("\n=== UNLOCKED SHOPS ===")
    print(f"Types: {dict(shop_types)}")
    print(f"Values: {dict(shop_values)}")

    print("\n=== TILES ===")
    print(f"Container types: {dict(tile_container_types)}")
    print(f"Row types: {dict(tile_row_types)}")
    print(f"Tile types: {dict(tile_types)}")
    print(f"Tile keys: {dict(tile_keys)}")
    print(f"Crops: {dict(crop_values)}")
    print(f"Animals: {dict(animal_values)}")

    print("\n=== PRIVATE INVENTORIES ===")
    print(f"Container types: {dict(inventory_types)}")
    print(f"Entry types: {dict(inventory_entry_types)}")

    print("\n=== OBSERVATION KEYS ===")
    print(f"Farm: {dict(farm_keys)}")
    print(f"Private: {dict(private_keys)}")
    print(f"Market: {dict(market_keys)}")
    print(f"Town: {dict(town_keys)}")

    zero_features = [names[i] for i, count in enumerate(feature_nonzero) if count == 0]

    print("\n=== ZERO FEATURES ===")
    if zero_features:
        for name in zero_features:
            print(name)
    else:
        print("None")

    print("\n=== FEATURE RANGES ===")
    for i, name in enumerate(names):
        if feature_min[i] == float("inf"):
            print(f"{name:<35} no valid values")
        else:
            print(
                f"{name:<35} min={feature_min[i]:<12.4f} "
                f"max={feature_max[i]:<12.4f} "
                f"nonzero={feature_nonzero[i]:<8} "
                f"rate={feature_nonzero[i] / observation_count:.2%}"
            )

    if error_examples:
        print("\n=== ERROR EXAMPLES ===")
        for filename, error in error_examples:
            print(f"{filename}: {error}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    args = parser.parse_args()

    if not args.replays.exists():
        raise FileNotFoundError(args.replays)

    analyze(args.replays)


if __name__ == "__main__":
    main()