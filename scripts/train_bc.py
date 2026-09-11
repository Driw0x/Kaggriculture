import argparse
import random
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.bc_dataset import BCDataset, split_by_episode
from src.learning.model import BCModel
from src.learning.replay_dataset import ReplayDataset
from src.learning.state_encoder import feature_names
from src.learning.target_encoder import encode_target, occurrence_names, quantity_names, sell_names

OCCURRENCE_NAMES = occurrence_names()
QUANTITY_NAMES = quantity_names()
SELL_NAMES = sell_names()


def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)


def compute_hire_weights(replay_dataset, indices, max_weight=20.0):
    counts = torch.zeros(11, dtype=torch.float32)

    for index in indices:
        sample = replay_dataset[index]
        target = encode_target(sample["action"], sample["observation"])
        counts[target["hire"]] += 1

    total = counts.sum()
    weights = torch.ones(11, dtype=torch.float32)

    for i, count in enumerate(counts):
        if count > 0:
            weights[i] = min(max_weight, (total / (len(counts) * count)).item())

    return weights


def compute_occurrence_pos_weight(replay_dataset, indices, max_weight=20.0):
    positives = torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.float32)

    for index in indices:
        sample = replay_dataset[index]
        target = encode_target(sample["action"], sample["observation"])
        positives += torch.tensor(target["occurrence"], dtype=torch.float32)

    total = float(len(indices))
    negatives = total - positives
    weights = torch.ones_like(positives)

    mask = positives > 0
    weights[mask] = negatives[mask] / positives[mask]

    return torch.clamp(weights, min=1.0, max=max_weight)


def masked_smooth_l1(prediction, target, mask):
    active = mask > 0

    if not active.any():
        return prediction.sum() * 0.0

    return F.smooth_l1_loss(prediction[active], target[active])


def compute_losses(output, batch, hire_loss_fn, occurrence_loss_fn):
    hire_loss = hire_loss_fn(output["hire"], batch["hire"])
    occurrence_loss = occurrence_loss_fn(output["occurrence"], batch["occurrence"])
    quantity_loss = masked_smooth_l1(output["quantity"], batch["quantity"], batch["quantity_mask"])
    sell_loss = masked_smooth_l1(output["sell_ratio"], batch["sell_ratio"], batch["sell_mask"])

    total = hire_loss + occurrence_loss + quantity_loss + sell_loss

    return {
        "total": total,
        "hire": hire_loss,
        "occurrence": occurrence_loss,
        "quantity": quantity_loss,
        "sell": sell_loss,
    }


def update_metrics(stats, output, batch):
    batch_size = batch["hire"].shape[0]

    hire_prediction = output["hire"].argmax(dim=1)
    stats["hire_correct"] += (hire_prediction == batch["hire"]).sum().item()
    stats["samples"] += batch_size

    predicted = torch.sigmoid(output["occurrence"]) >= 0.5
    target = batch["occurrence"] > 0.5

    stats["tp"] += (predicted & target).sum(dim=0).cpu()
    stats["fp"] += (predicted & ~target).sum(dim=0).cpu()
    stats["fn"] += (~predicted & target).sum(dim=0).cpu()


def finalize_metrics(stats):
    tp = stats["tp"].float()
    fp = stats["fp"].float()
    fn = stats["fn"].float()

    precision = tp / (tp + fp).clamp_min(1)
    recall = tp / (tp + fn).clamp_min(1)
    f1 = 2 * precision * recall / (precision + recall).clamp_min(1e-8)

    micro_tp = tp.sum()
    micro_fp = fp.sum()
    micro_fn = fn.sum()

    micro_precision = micro_tp / (micro_tp + micro_fp).clamp_min(1)
    micro_recall = micro_tp / (micro_tp + micro_fn).clamp_min(1)
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall).clamp_min(1e-8)

    return {
        "hire_acc": stats["hire_correct"] / max(1, stats["samples"]),
        "occ_micro_f1": micro_f1.item(),
        "occ_macro_f1": f1.mean().item(),
    }


def run_epoch(model, loader, device, hire_loss_fn, occurrence_loss_fn, optimizer=None):
    training = optimizer is not None
    model.train(training)

    totals = {
        "total": 0.0,
        "hire": 0.0,
        "occurrence": 0.0,
        "quantity": 0.0,
        "sell": 0.0,
    }

    stats = {
        "samples": 0,
        "hire_correct": 0,
        "tp": torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long),
        "fp": torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long),
        "fn": torch.zeros(len(OCCURRENCE_NAMES), dtype=torch.long),
    }

    for batch in loader:
        batch = {key: value.to(device) for key, value in batch.items()}

        if training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(training):
            output = model(batch["state"])
            losses = compute_losses(output, batch, hire_loss_fn, occurrence_loss_fn)

            if training:
                losses["total"].backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

        batch_size = batch["state"].shape[0]

        for name in totals:
            totals[name] += losses[name].item() * batch_size

        update_metrics(stats, {key: value.detach() for key, value in output.items()}, batch)

    sample_count = max(1, stats["samples"])

    results = {name: value / sample_count for name, value in totals.items()}
    results.update(finalize_metrics(stats))

    return results


def print_metrics(prefix, metrics):
    print(
        f"{prefix} "
        f"loss={metrics['total']:.4f} "
        f"hire={metrics['hire']:.4f} "
        f"occ={metrics['occurrence']:.4f} "
        f"qty={metrics['quantity']:.4f} "
        f"sell={metrics['sell']:.4f} "
        f"hire_acc={metrics['hire_acc']:.2%} "
        f"occ_micro_f1={metrics['occ_micro_f1']:.3f} "
        f"occ_macro_f1={metrics['occ_macro_f1']:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replays", type=Path, default=Path("data/expert_replays"))
    parser.add_argument("--output", type=Path, default=Path("models/bc_best.pt"))
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-size", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    if args.epochs <= 0:
        raise ValueError("--epochs must be > 0")

    if args.batch_size <= 0:
        raise ValueError("--batch-size must be > 0")

    set_seed(args.seed)

    replay_dataset = ReplayDataset(args.replays)
    train_indices, val_indices = split_by_episode(replay_dataset, args.val_ratio, args.seed)

    if args.smoke:
        train_indices = train_indices[:4096]
        val_indices = val_indices[:1024]
        args.epochs = 1

    train_dataset = BCDataset(replay_dataset, train_indices)
    val_dataset = BCDataset(replay_dataset, val_indices)

    print(f"Replays samples: {len(replay_dataset)}")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")

    hire_weights = compute_hire_weights(replay_dataset, train_indices)
    occurrence_pos_weight = compute_occurrence_pos_weight(replay_dataset, train_indices)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    print(f"Device: {device}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    model = BCModel(hidden_size=args.hidden_size, dropout=args.dropout).to(device)

    hire_loss_fn = nn.CrossEntropyLoss(weight=hire_weights.to(device))
    occurrence_loss_fn = nn.BCEWithLogitsLoss(pos_weight=occurrence_pos_weight.to(device))

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        train_metrics = run_epoch(
            model,
            train_loader,
            device,
            hire_loss_fn,
            occurrence_loss_fn,
            optimizer,
        )

        with torch.no_grad():
            val_metrics = run_epoch(
                model,
                val_loader,
                device,
                hire_loss_fn,
                occurrence_loss_fn,
            )

        print(f"\nEpoch {epoch}/{args.epochs}")
        print_metrics("train", train_metrics)
        print_metrics("val  ", val_metrics)

        if val_metrics["total"] < best_val_loss:
            best_val_loss = val_metrics["total"]

            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_loss": best_val_loss,
                    "hidden_size": args.hidden_size,
                    "dropout": args.dropout,
                    "feature_names": feature_names(),
                    "occurrence_names": OCCURRENCE_NAMES,
                    "quantity_names": QUANTITY_NAMES,
                    "sell_names": SELL_NAMES,
                    "hire_weights": hire_weights,
                    "occurrence_pos_weight": occurrence_pos_weight,
                },
                args.output,
            )

            print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()