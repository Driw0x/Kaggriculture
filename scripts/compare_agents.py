import importlib
import statistics

from kaggle_environments import make

import src.agents.jet3 as agent1_module
import src.agents.jet5 as agent2_module


AGENT1_NAME = "jet3"
AGENT2_NAME = "jet5"
SEEDS = tuple(range(100))
CONFIGURATION = {"episodeSteps": 720}


def telemetry_errors(module):
    telemetry = getattr(module, "_YE1_TELEMETRY", {})
    return {
        "outer_errors": int(telemetry.get("outer_errors", 0)),
        "fallbacks": int(telemetry.get("fallbacks", 0)),
        "policy_errors": sum(
            int(value) for value in telemetry.get("policy_errors", {}).values()
        ),
    }


agent1_wins = 0
agent2_wins = 0
draws = 0
agent1_rewards = []
agent2_rewards = []
errors = {
    AGENT1_NAME: {"outer_errors": 0, "fallbacks": 0, "policy_errors": 0},
    AGENT2_NAME: {"outer_errors": 0, "fallbacks": 0, "policy_errors": 0},
}
fertilizer_telemetry = {
    "buys_examined": 0,
    "buys_modified": 0,
    "buys_removed": 0,
    "units_avoided": 0,
}

match = 0
for seed in SEEDS:
    for agent1_seat in (0, 1):
        match += 1
        agent1_module = importlib.reload(agent1_module)
        agent2_module = importlib.reload(agent2_module)
        agents = [agent2_module.agent, agent1_module.agent]
        agents[agent1_seat] = agent1_module.agent
        agents[1 - agent1_seat] = agent2_module.agent

        configuration = dict(CONFIGURATION, seed=seed)
        env = make("kaggriculture", configuration=configuration, debug=False)
        env.run(agents)
        final = env.steps[-1]
        reward1 = final[agent1_seat].reward
        reward2 = final[1 - agent1_seat].reward
        agent1_rewards.append(reward1)
        agent2_rewards.append(reward2)

        if reward1 > reward2:
            winner = AGENT1_NAME
            agent1_wins += 1
        elif reward2 > reward1:
            winner = AGENT2_NAME
            agent2_wins += 1
        else:
            winner = "draw"
            draws += 1

        for name, module in (
            (AGENT1_NAME, agent1_module),
            (AGENT2_NAME, agent2_module),
        ):
            current = telemetry_errors(module)
            for key, value in current.items():
                errors[name][key] += value
        for key, value in agent2_module._JET5_FERTILIZER_TELEMETRY.items():
            fertilizer_telemetry[key] += int(value)

        print(
            f"Match {match:03d} seed={seed} {AGENT1_NAME}_seat={agent1_seat}: "
            f"{AGENT1_NAME}={reward1:.2f} | "
            f"{AGENT2_NAME}={reward2:.2f} | winner={winner}"
        )

differences = [
    reward2 - reward1
    for reward1, reward2 in zip(agent1_rewards, agent2_rewards)
]
print()
print(
    f"Result: {AGENT1_NAME} {agent1_wins} - "
    f"{agent2_wins} {AGENT2_NAME} ({draws} draws)"
)
print(
    f"{AGENT1_NAME}: mean={statistics.mean(agent1_rewards):.2f} "
    f"median={statistics.median(agent1_rewards):.2f} "
    f"min={min(agent1_rewards):.2f} max={max(agent1_rewards):.2f}"
)
print(
    f"{AGENT2_NAME}: mean={statistics.mean(agent2_rewards):.2f} "
    f"median={statistics.median(agent2_rewards):.2f} "
    f"min={min(agent2_rewards):.2f} max={max(agent2_rewards):.2f}"
)
print(
    f"Paired difference ({AGENT2_NAME}-{AGENT1_NAME}): "
    f"mean={statistics.mean(differences):+.2f} "
    f"min={min(differences):+.2f} max={max(differences):+.2f}"
)
print(f"Errors: {errors}")
print(f"Fertilizer telemetry: {fertilizer_telemetry}")
