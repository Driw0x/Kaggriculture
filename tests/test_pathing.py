import math
import random

from src.agents.agent import distance, get_best_paths, optimize_path_direction


PLANT_ACTIONS = [
    "HARVEST",
    "PLANT",
    "WATER",
]

ANIMAL_ACTIONS = [
    "FEED",
    "CARE",
    "HARVEST",
    "COLLECT_FERTILIZER",
]


def build_test_tasks(width, height, ticks_available=24, start=(0, 0)):
    tasks = []

    for y in range(height):
        for x in range(width):
            position = (x, y)
            movement = distance(start, position)

            if movement >= ticks_available:
                continue

            task_type = random.choice(["PLANT", "ANIMAL"])
            possible_actions = PLANT_ACTIONS if task_type == "PLANT" else ANIMAL_ACTIONS
            max_actions = min(len(possible_actions), ticks_available - movement)
            action_count = random.randint(1, max_actions)
            selected = random.sample(possible_actions, action_count)

            if task_type == "PLANT":
                actions = [action for action in PLANT_ACTIONS if action in selected]
            else:
                actions = [action for action in ANIMAL_ACTIONS if action in selected]

            tasks.append({
                "position": position,
                "type": task_type,
                "actions": actions,
            })

    return tasks


def evaluate_plan(tasks, unit_count, start_positions, ticks_available):
    paths = get_best_paths(tasks, unit_count, start_positions, ticks_available)
    results = []

    for unit_index in range(unit_count):
        start = start_positions[unit_index]
        path = optimize_path_direction(paths[unit_index], start)
        action_ticks = sum(len(task["actions"]) for task in path)
        movement_ticks = 0
        position = start

        for task in path:
            movement_ticks += distance(position, task["position"])
            position = task["position"]

        results.append({
            "unit": unit_index,
            "tiles": len(path),
            "actions": action_ticks,
            "movement": movement_ticks,
            "total": action_ticks + movement_ticks,
            "path": path,
        })

    return results


def print_task_map(tasks, start, ticks_available):
    print("=== GENERATED TASKS ===")

    for task in tasks:
        position = task["position"]
        movement = distance(start, position)
        actions = len(task["actions"])
        total = movement + actions
        print(f"{position}: movement={movement} actions={actions} minimum_total={total}/{ticks_available} {task['actions']}")


def print_plan_report(results, ticks_available, task_count):
    total_actions = sum(result["actions"] for result in results)
    total_movement = sum(result["movement"] for result in results)
    total_ticks = sum(result["total"] for result in results)
    total_idle = sum(max(0, ticks_available - result["total"]) for result in results)
    max_ticks = max(result["total"] for result in results)
    min_ticks = min(result["total"] for result in results)
    imbalance = max_ticks - min_ticks
    movement_overhead = total_movement / total_actions if total_actions else 0
    theoretical_units = math.ceil(total_actions / ticks_available)
    assigned = sum(result["tiles"] for result in results)
    planner_units = len(results)
    previous_capacity = max(0, planner_units - 1) * ticks_available
    max_movement_previous = previous_capacity - total_actions
    movement_reduction_needed = max(0, total_movement - max_movement_previous)

    print()
    print("=== PATHING REPORT ===")

    for result in results:
        idle_ticks = max(0, ticks_available - result["total"])
        utilization = min(1.0, result["total"] / ticks_available)
        print(f"Unit {result['unit']}: tiles={result['tiles']} actions={result['actions']} movement={result['movement']} total={result['total']}/{ticks_available} idle={idle_ticks} utilization={utilization:.2%}")

    print()
    print(f"Assigned tasks: {assigned}/{task_count}")
    print(f"Total action ticks: {total_actions}")
    print(f"Total movement ticks: {total_movement}")
    print(f"Total ticks consumed: {total_ticks}")
    print(f"Total idle ticks: {total_idle}")
    print(f"Movement overhead: {movement_overhead:.2%}")
    print(f"Theoretical action-only minimum units: {theoretical_units}")
    print(f"Planner units: {planner_units}")
    print(f"Gap from action-only lower bound: +{planner_units - theoretical_units}")
    print(f"Longest path: {max_ticks}/{ticks_available}")
    print(f"Shortest path: {min_ticks}/{ticks_available}")
    print(f"Load imbalance: {imbalance}")
    print(f"Movement needed for {planner_units - 1} units: <= {max_movement_previous}")
    print(f"Current movement: {total_movement}")
    print(f"Movement reduction needed: {movement_reduction_needed}")
    print(f"Fits in day: {assigned == task_count and max_ticks <= ticks_available}")


def compare_unit_counts(tasks, max_units, ticks_available, start=(0, 0)):
    print()
    print("=== UNIT COUNT COMPARISON ===")

    for unit_count in range(1, max_units + 1):
        start_positions = [start] * unit_count
        results = evaluate_plan(tasks, unit_count, start_positions, ticks_available)
        assigned = sum(result["tiles"] for result in results)
        max_ticks = max(result["total"] for result in results)
        total_movement = sum(result["movement"] for result in results)
        total_idle = sum(max(0, ticks_available - result["total"]) for result in results)
        fits = assigned == len(tasks) and max_ticks <= ticks_available
        print(f"{unit_count} units: assigned={assigned}/{len(tasks)} completion={max_ticks}/{ticks_available} movement={total_movement} idle={total_idle} fits={fits}")


def find_minimum_units(tasks, ticks_available, start=(0, 0)):
    for task in tasks:
        minimum_cost = distance(start, task["position"]) + len(task["actions"])

        if minimum_cost > ticks_available:
            return None, None

    total_actions = sum(len(task["actions"]) for task in tasks)
    minimum_units = max(1, math.ceil(total_actions / ticks_available))

    for unit_count in range(minimum_units, len(tasks) + 1):
        start_positions = [start] * unit_count
        results = evaluate_plan(tasks, unit_count, start_positions, ticks_available)
        assigned = sum(result["tiles"] for result in results)

        if assigned != len(tasks):
            continue

        if max(result["total"] for result in results) <= ticks_available:
            return unit_count, results

    return None, None


def main():
    width = 5
    height = 5
    ticks_available = 24
    start = (0, 0)

    tasks = build_test_tasks(width, height, ticks_available, start)
    print_task_map(tasks, start, ticks_available)

    total_actions = sum(len(task["actions"]) for task in tasks)
    theoretical_units = math.ceil(total_actions / ticks_available)

    print()
    print(f"Theoretical action-only minimum units: {theoretical_units}")

    unit_count, results = find_minimum_units(tasks, ticks_available, start)

    if unit_count is None:
        print()
        print("No valid plan.")
    else:
        print()
        print(f"Minimum required units: {unit_count}")
        print_plan_report(results, ticks_available, len(tasks))

    compare_unit_counts(tasks, max_units=min(25, len(tasks)), ticks_available=ticks_available, start=start)


if __name__ == "__main__":
    main()