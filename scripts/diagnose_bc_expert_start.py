import argparse
import sys
from collections import Counter
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.model import BCModel
from src.learning.replay_dataset import ReplayDataset
from src.learning.state_encoder import encode_state
from src.learning.target_encoder import encode_target, occurrence_names

OCCURRENCE_NAMES = occurrence_names()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--checkpoint", type=Path, default=Path("models/bc_best.pt"))
    parser.add_argument("--hour", type=int, default=1)
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()

    dataset = ReplayDataset(args.replays)
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)

    model = BCModel(
        hidden_size=checkpoint["hidden_size"],
        dropout=checkpoint["dropout"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    samples = [
        sample for sample in dataset.samples
        if sample["observation"]["day"] == 0
        and sample["observation"]["hour"] == args.hour
    ]

    print(f"Samples: {len(samples)}")

    truth_hire = Counter()
    pred_hire = Counter()
    truth_occurrence = Counter()
    probability_sum = torch.zeros(len(OCCURRENCE_NAMES))
    predicted_occurrence = Counter()

    with torch.no_grad():
        for sample in samples:
            state = torch.tensor(
                encode_state(sample["observation"]),
                dtype=torch.float32,
            ).unsqueeze(0)

            output = model(state)
            target = encode_target(sample["action"], sample["observation"])

            true_hire = target["hire"]
            predicted_hire = int(output["hire"][0].argmax().item())

            truth_hire[true_hire] += 1
            pred_hire[predicted_hire] += 1

            probabilities = torch.sigmoid(output["occurrence"][0])
            probability_sum += probabilities.cpu()

            for index, name in enumerate(OCCURRENCE_NAMES):
                if target["occurrence"][index] > 0:
                    truth_occurrence[name] += 1

                if probabilities[index].item() >= args.threshold:
                    predicted_occurrence[name] += 1

    print()
    print("=== HIRE ===")

    print("Truth:")
    for value, count in sorted(truth_hire.items()):
        print(f"  {value}: {count}/{len(samples)} ({100 * count / len(samples):.1f}%)")

    print("Prediction:")
    for value, count in sorted(pred_hire.items()):
        print(f"  {value}: {count}/{len(samples)} ({100 * count / len(samples):.1f}%)")

    print()
    print("=== OCCURRENCES ===")

    mean_probabilities = probability_sum / len(samples)

    for index, name in enumerate(OCCURRENCE_NAMES):
        truth = truth_occurrence[name]
        predicted = predicted_occurrence[name]
        mean_probability = float(mean_probabilities[index].item())

        if truth > 0 or predicted > 0 or mean_probability >= 0.05:
            print(
                f"{name:<25} "
                f"truth={100 * truth / len(samples):6.1f}% "
                f"pred@{args.threshold:.2f}={100 * predicted / len(samples):6.1f}% "
                f"mean_p={mean_probability:.3f}"
            )


if __name__ == "__main__":
    main()