from experiments.shadow_bc import ShadowAgent, compare_decisions, sparse, summarize


class DummyPolicy:
    def predict(self, obs):
        return {"hire": 0}, {"hire": 0.0}


def test_shadow_agent_one_argument():
    def base_agent(obs):
        return {"farmer": ["PASS"], "hands": [], "market": []}

    shadow = ShadowAgent(base_agent, DummyPolicy())

    obs = {
        "step": 0,
        "day": 0,
        "hour": 0,
        "player": 0,
        "farms": [],
    }

    action = shadow(obs, {})

    assert action == {"farmer": ["PASS"], "hands": [], "market": []}
    assert len(shadow.records) == 1


def test_shadow_agent_two_arguments():
    def base_agent(obs, configuration):
        return {"farmer": ["PASS"], "hands": [], "market": []}

    shadow = ShadowAgent(base_agent, DummyPolicy())

    obs = {
        "step": 0,
        "day": 0,
        "hour": 0,
        "player": 0,
        "farms": [],
    }

    action = shadow(obs, {"episodeSteps": 720})

    assert action == {"farmer": ["PASS"], "hands": [], "market": []}
    assert len(shadow.records) == 1