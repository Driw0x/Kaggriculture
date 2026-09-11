import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.model import BCModel
from src.learning.preencoded_dataset import PreencodedBCDataset, split_preencoded_by_episode
from src.learning.target_encoder import occurrence_names, quantity_names, sell_names

OCCURRENCE_NAMES = occurrence_names()
QUANTITY_NAMES = quantity_names()
SELL_NAMES = sell_names()


def safe_div(a, b):
    return a / b if b else 0.0


def evaluate_occurrences(logits, targets, threshold):
    predicted = torch.sigmoid(logits) >= threshold
    target = targets > 0.5
    tp = (predicted & target).sum(dim=0)
    fp = (predicted & ~target).sum(dim=0)
    fn = (~predicted & target).sum(dim=0)
    tn = (~predicted & ~target).sum(dim=0)
    return tp, fp, fn, tn


def compute_f1(tp, fp, fn):
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    return precision, recall, safe_div(2 * precision * recall, precision + recall)


def search_best_threshold(probabilities, targets, thresholds=None):
    thresholds = thresholds or [i / 100 for i in range(5, 96, 5)]
    best_threshold = 0.5
    best_f1 = -1.0
    for threshold in thresholds:
        predicted = probabilities >= threshold
        target = targets > 0.5
        tp = int((predicted & target).sum())
        fp = int((predicted & ~target).sum())
        fn = int((~predicted & target).sum())
        _, _, f1 = compute_f1(tp, fp, fn)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    return best_threshold, best_f1


def save_thresholds(path, thresholds):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2, sort_keys=True)
        f.write("\n")


def print_hire_confusion(matrix):
    print("\n=== HIRE CONFUSION MATRIX ===")
    print("true\\pred " + " ".join(f"{i:>6}" for i in range(11)))
    for true_class in range(11):
        row = " ".join(f"{int(matrix[true_class, pred]):>6}" for pred in range(11))
        print(f"{true_class:>9} {row}")


def print_hire_metrics(matrix):
    print("\n=== HIRE PER CLASS ===")
    for cls in range(11):
        tp = int(matrix[cls, cls])
        fp = int(matrix[:, cls].sum()) - tp
        fn = int(matrix[cls, :].sum()) - tp
        precision, recall, f1 = compute_f1(tp, fp, fn)
        support = int(matrix[cls, :].sum())
        print(f"hire={cls:<2} support={support:<6} precision={precision:.3f} recall={recall:.3f} f1={f1:.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/bc_dataset.pt"))
    parser.add_argument("--checkpoint", type=Path, default=Path("models/bc_best.pt"))
    parser.add_argument("--threshold-output", type=Path, default=Path("models/bc_thresholds.json"))
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()

    if not args.checkpoint.exists():
        raise FileNotFoundError(args.checkpoint)

    dataset = PreencodedBCDataset(args.dataset)
    _, val_indices = split_preencoded_by_episode(dataset, args.val_ratio, args.seed)
    val_dataset = Subset(dataset, val_indices)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model = BCModel(hidden_size=checkpoint["hidden_size"], dropout=checkpoint["dropout"]).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    print(f"Checkpoint epoch: {checkpoint['epoch']}")
    print(f"Checkpoint val loss: {checkpoint['val_loss']:.4f}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Device: {device}")

    hire_confusion = torch.zeros((11, 11), dtype=torch.long)
    occurrence_tp = torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long)
    occurrence_fp = torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long)
    occurrence_fn = torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long)
    occurrence_tn = torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long)
    occurrence_probabilities = defaultdict(list)
    occurrence_targets = defaultdict(list)
    quantity_abs_error = torch.zeros(len(QUANTITY_NAMES), dtype=torch.float64)
    quantity_count = torch.zeros(len(QUANTITY_NAMES), dtype=torch.long)
    sell_abs_error = torch.zeros(len(SELL_NAMES), dtype=torch.float64)
    sell_count = torch.zeros(len(SELL_NAMES), dtype=torch.long)

    with torch.no_grad():
        for batch in loader:
            batch = {key: value.to(device) for key, value in batch.items()}
            output = model(batch["state"])
            hire_prediction = output["hire"].argmax(dim=1)

            for true_value, predicted_value in zip(batch["hire"].cpu(), hire_prediction.cpu()):
                hire_confusion[int(true_value), int(predicted_value)] += 1

            tp, fp, fn, tn = evaluate_occurrences(output["occurrence"], batch["occurrence"], args.threshold)
            occurrence_tp += tp.cpu()
            occurrence_fp += fp.cpu()
            occurrence_fn += fn.cpu()
            occurrence_tn += tn.cpu()

            probabilities = torch.sigmoid(output["occurrence"]).cpu()
            targets = batch["occurrence"].cpu()

            for index, name in enumerate(OCCURRENCE_NAMES):
                occurrence_probabilities[name].append(probabilities[:, index])
                occurrence_targets[name].append(targets[:, index])

            quantity_error = torch.abs(output["quantity"] - batch["quantity"])
            quantity_mask = batch["quantity_mask"] > 0

            for index in range(len(QUANTITY_NAMES)):
                active = quantity_mask[:, index]
                if active.any():
                    quantity_abs_error[index] += quantity_error[active, index].sum().item()
                    quantity_count[index] += active.sum().item()

            sell_error = torch.abs(output["sell_ratio"] - batch["sell_ratio"])
            sell_mask = batch["sell_mask"] > 0

            for index in range(len(SELL_NAMES)):
                active = sell_mask[:, index]
                if active.any():
                    sell_abs_error[index] += sell_error[active, index].sum().item()
                    sell_count[index] += active.sum().item()

    print_hire_confusion(hire_confusion)
    print_hire_metrics(hire_confusion)

    hire_correct = int(hire_confusion.diag().sum())
    hire_total = int(hire_confusion.sum())

    print("\n=== HIRE GLOBAL ===")
    print(f"accuracy={safe_div(hire_correct, hire_total):.3f}")

    print("\n=== OCCURRENCE PER DECISION ===")
    f1_values = []

    for index, name in enumerate(OCCURRENCE_NAMES):
        tp = int(occurrence_tp[index])
        fp = int(occurrence_fp[index])
        fn = int(occurrence_fn[index])
        tn = int(occurrence_tn[index])
        precision, recall, f1 = compute_f1(tp, fp, fn)
        support = tp + fn
        predicted = tp + fp
        f1_values.append(f1)
        print(f"{name:<25} support={support:<6} pred={predicted:<6} precision={precision:.3f} recall={recall:.3f} f1={f1:.3f} tn={tn}")

    micro_tp = int(occurrence_tp.sum())
    micro_fp = int(occurrence_fp.sum())
    micro_fn = int(occurrence_fn.sum())
    micro_precision, micro_recall, micro_f1 = compute_f1(micro_tp, micro_fp, micro_fn)

    print("\n=== OCCURRENCE GLOBAL ===")
    print(f"micro_precision={micro_precision:.3f}")
    print(f"micro_recall={micro_recall:.3f}")
    print(f"micro_f1={micro_f1:.3f}")
    print(f"macro_f1={sum(f1_values) / len(f1_values):.3f}")

    print("\n=== QUANTITY MAE ===")
    for index, name in enumerate(QUANTITY_NAMES):
        count = int(quantity_count[index])
        mae_log = safe_div(quantity_abs_error[index].item(), count)
        print(f"{name:<25} samples={count:<6} mae_log={mae_log:.4f}")

    print("\n=== SELL RATIO MAE ===")
    for index, name in enumerate(SELL_NAMES):
        count = int(sell_count[index])
        mae = safe_div(sell_abs_error[index].item(), count)
        print(f"{name:<25} samples={count:<6} mae={mae:.4f}")

    print("\n=== BEST OCCURRENCE THRESHOLDS ===")
    optimized_thresholds = {}
    threshold_f1_values = []

    for name in OCCURRENCE_NAMES:
        probabilities = torch.cat(occurrence_probabilities[name])
        targets = torch.cat(occurrence_targets[name])
        threshold, f1 = search_best_threshold(probabilities, targets)
        optimized_thresholds[name] = threshold
        threshold_f1_values.append(f1)
        print(f"{name:<25} threshold={threshold:.2f} f1={f1:.3f}")

    print("\n=== OPTIMIZED THRESHOLD SUMMARY ===")
    print(f"macro_f1={sum(threshold_f1_values) / len(threshold_f1_values):.3f}")

    save_thresholds(args.threshold_output, optimized_thresholds)
    print(f"Thresholds saved to: {args.threshold_output}")


if __name__ == "__main__":
    main()