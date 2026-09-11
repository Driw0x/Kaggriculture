import json
import math
from pathlib import Path

import torch

from src.learning.model import BCModel
from src.learning.state_encoder import PRODUCTS, encode_state
from src.learning.target_encoder import occurrence_names, quantity_names, sell_names

OCCURRENCE_NAMES = occurrence_names()
QUANTITY_NAMES = quantity_names()
SELL_NAMES = sell_names()


def load_thresholds(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run: python scripts/evaluate_bc.py")

    with path.open(encoding="utf-8") as f:
        thresholds = json.load(f)

    missing = set(OCCURRENCE_NAMES) - set(thresholds)
    if missing:
        raise ValueError(f"Missing occurrence thresholds: {sorted(missing)}")

    return {name: float(thresholds[name]) for name in OCCURRENCE_NAMES}


def decode_quantity(value):
    return max(1, int(round(math.expm1(max(0.0, float(value))))))


def decode_output(output, observation, thresholds):
    hire_logits = output["hire"][0]
    occurrence_logits = output["occurrence"][0]
    quantity_values = output["quantity"][0]
    sell_ratios = output["sell_ratio"][0]
    occurrence_probabilities = torch.sigmoid(occurrence_logits)

    decision = {"hire": int(hire_logits.argmax().item())}
    scores = {"hire": float(torch.softmax(hire_logits, dim=0).max().item())}

    farm = observation["farms"][observation["player"]]
    hires_today = farm.get("hires_today", 0)
    decision["hire"] = min(decision["hire"], max(0, 10 - hires_today))

    quantity_index = {name: index for index, name in enumerate(QUANTITY_NAMES)}
    sell_index = {name: index for index, name in enumerate(SELL_NAMES)}

    for index, name in enumerate(OCCURRENCE_NAMES):
        probability = float(occurrence_probabilities[index].item())
        scores[name] = probability

        if probability < thresholds[name]:
            decision[name] = 0
            continue

        if name == "buy_land":
            decision[name] = int(len(farm.get("unlocked_quadrants", [])) < 4)
            continue

        if name in quantity_index:
            decision[name] = decode_quantity(quantity_values[quantity_index[name]].item())
            continue

        if name in sell_index:
            item = name.removeprefix("sell_")
            available = max(0, int(observation.get("private", {}).get("shed", {}).get(item, 0)))
            if available == 0:
                decision[name] = 0
                continue

            ratio = float(sell_ratios[sell_index[name]].item())
            decision[name] = min(max(1, int(round(ratio * available))), available)
            continue

        decision[name] = 1

    return decision, scores


class BCPolicy:
    def __init__(self, checkpoint="models/bc_best.pt", thresholds="models/bc_thresholds.json", device="auto"):
        self.checkpoint_path = Path(checkpoint)
        self.threshold_path = Path(thresholds)
        self.thresholds = load_thresholds(self.threshold_path)

        if device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        checkpoint_data = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        self.model = BCModel(hidden_size=checkpoint_data["hidden_size"], dropout=checkpoint_data["dropout"]).to(self.device)
        self.model.load_state_dict(checkpoint_data["model_state_dict"])
        self.model.eval()

        self.epoch = checkpoint_data["epoch"]
        self.val_loss = checkpoint_data["val_loss"]

    def predict(self, observation):
        state = torch.tensor(encode_state(observation), dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            output = self.model(state)
        return decode_output(output, observation, self.thresholds)

    def predict_decision(self, observation):
        decision, _ = self.predict(observation)
        return decision


def market_orders_from_decision(decision, max_orders=10):
    orders = []

    for _ in range(decision.get("hire", 0)):
        orders.append(["HIRE"])

    if decision.get("buy_land", 0):
        orders.append(["BUY_LAND"])

    for crop in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"):
        quantity = decision.get(f"buy_seed_{crop}", 0)
        if quantity > 0:
            orders.append(["BUY_SEED", crop, quantity])

    for animal in ("GOOSE", "COW", "SHEEP"):
        quantity = decision.get(f"buy_animal_{animal}", 0)
        if quantity > 0:
            orders.append(["BUY_ANIMAL", animal, quantity])

    for item in ("WHEAT", "FERTILIZER"):
        quantity = decision.get(f"buy_product_{item}", 0)
        if quantity > 0:
            orders.append(["BUY_PRODUCT", item, quantity])

    for item in PRODUCTS:
        quantity = decision.get(f"sell_{item}", 0)
        if quantity > 0:
            orders.append(["SELL", item, quantity])

    return orders[:max_orders]