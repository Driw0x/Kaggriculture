import importlib

from kaggle_environments import make

import src.agents.chi9 as agent1_module
import submissions.agent as agent2_module

AGENT1_NAME = "chi9"
AGENT2_NAME = "chi9_exp0_clean"
MATCHES = 10

agent1_wins = 0
agent2_wins = 0
draws = 0

agent1_rewards = []
agent2_rewards = []

for match in range(MATCHES):
    agent1_module = importlib.reload(agent1_module)
    agent2_module = importlib.reload(agent2_module)

    agent1 = agent1_module.agent
    agent2 = agent2_module.agent

    env = make(
        "kaggriculture",
        configuration={"episodeSteps": 720},
        debug=False,
    )

    if match % 2 == 0:
        env.run([agent1, agent2])
        final = env.steps[-1]
        reward1 = final[0].reward
        reward2 = final[1].reward
    else:
        env.run([agent2, agent1])
        final = env.steps[-1]
        reward1 = final[1].reward
        reward2 = final[0].reward

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

    print(
        f"Match {match + 1:03d}: "
        f"{AGENT1_NAME}={reward1:.0f} | "
        f"{AGENT2_NAME}={reward2:.0f} | "
        f"winner={winner}"
    )

print()
print(
    f"Result: {AGENT1_NAME} {agent1_wins} - "
    f"{agent2_wins} {AGENT2_NAME} "
    f"({draws} draws)"
)
print(
    f"Average reward: "
    f"{AGENT1_NAME}={sum(agent1_rewards) / MATCHES:.1f} | "
    f"{AGENT2_NAME}={sum(agent2_rewards) / MATCHES:.1f}"
)