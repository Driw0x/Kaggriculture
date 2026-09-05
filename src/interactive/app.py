from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from kaggle_environments import make

from src.interactive.recorder import GameRecorder

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
recorder = GameRecorder(BASE_DIR / "sessions")


def new_environment():
    environment = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
    environment.reset()
    return environment


env = new_environment()


def to_plain(value):
    if isinstance(value, dict):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_plain(item) for item in value]
    if hasattr(value, "items"):
        return {str(key): to_plain(item) for key, item in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def player_observation(player=0):
    return to_plain(env.steps[-1][player].observation)


def player_summary(player=0):
    state = env.steps[-1][player]
    observation = player_observation(player)
    farm = observation["farms"][player]
    return {
        "step": observation.get("step", len(env.steps) - 1),
        "day": observation.get("day", 0),
        "hour": observation.get("hour", 0),
        "money": farm.get("money", 0),
        "hands": len(farm.get("hands", [])),
        "reward": state.reward,
        "status": str(state.status),
        "done": env.done,
        "session": recorder.path.name,
    }


def pass_action(player):
    observation = player_observation(player)
    hand_count = len(observation["farms"][player].get("hands", []))
    return {
        "farmer": ["PASS"],
        "hands": [["PASS"] for _ in range(hand_count)],
        "market": [],
    }


def normalize_action(action):
    observation = player_observation(0)
    hand_count = len(observation["farms"][0].get("hands", []))

    farmer = action.get("farmer", ["PASS"])
    hands = action.get("hands", [])
    market = action.get("market", [])

    if not isinstance(farmer, list) or not farmer:
        farmer = ["PASS"]

    normalized_hands = []
    for index in range(hand_count):
        if index < len(hands) and isinstance(hands[index], list) and hands[index]:
            normalized_hands.append(hands[index])
        else:
            normalized_hands.append(["PASS"])

    if not isinstance(market, list):
        market = []

    return {
        "farmer": farmer,
        "hands": normalized_hands,
        "market": market[:10],
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/state")
def state():
    return jsonify(player_summary())


@app.route("/render")
def render_game():
    html = env.render(mode="html", width=1200, height=800)
    return Response(html, mimetype="text/html")


@app.route("/step", methods=["POST"])
def step():
    if env.done:
        return jsonify({"error": "La partie est terminée."}), 400

    payload = request.get_json(silent=True) or {}
    human_action = normalize_action(payload)
    opponent_action = pass_action(1)
    step_number = player_observation(0).get("step", len(env.steps) - 1)
    observation_before = player_observation(0)

    try:
        env.step([human_action, opponent_action])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    observation_after = player_observation(0)
    recorder.record(step_number, observation_before, human_action, observation_after)
    return jsonify(player_summary())


@app.route("/reset", methods=["POST"])
def reset():
    global env
    env = new_environment()
    session = recorder.new_session()
    result = player_summary()
    result["session"] = session
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
