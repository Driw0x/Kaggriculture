import argparse
import random
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import DataLoader, Subset

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.learning.model import BCModel
from src.learning.preencoded_dataset import (
    PreencodedBCDataset,
    split_preencoded_by_episode,
)
from src.learning.state_encoder import feature_names
from src.learning.target_encoder import (
    occurrence_names,
    quantity_names,
    sell_names,
)

OCCURRENCE_NAMES = occurrence_names()
QUANTITY_NAMES = quantity_names()
SELL_NAMES = sell_names()


def set_seed(seed):
    random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def compute_hire_weights(dataset):
    counts = torch.zeros(11, dtype=torch.float32)

    for sample in dataset:
        counts[int(sample["hire"])] += 1

    total = counts.sum()
    weights = torch.ones(11, dtype=torch.float32)
    active = counts > 0

    weights[active] = total / (11 * counts[active])

    return weights.clamp(max=20.0)


def compute_occurrence_pos_weight(dataset):
    positives = torch.zeros(
        len(OCCURRENCE_NAMES),
        dtype=torch.float32,
    )

    total = 0

    for sample in dataset:
        positives += sample["occurrence"]
        total += 1

    negatives = total - positives
    weights = torch.ones_like(positives)

    active = positives > 0
    weights[active] = negatives[active] / positives[active]

    return weights.clamp(min=1.0, max=20.0)


def masked_smooth_l1(prediction, target, mask):
    active = mask > 0

    if not active.any():
        return prediction.sum() * 0.0

    return F.smooth_l1_loss(
        prediction[active],
        target[active],
    )


def compute_losses(
    output,
    batch,
    hire_weights,
    occurrence_pos_weight,
):
    hire = F.cross_entropy(
        output["hire"],
        batch["hire"],
        weight=hire_weights,
    )

    occurrence = F.binary_cross_entropy_with_logits(
        output["occurrence"],
        batch["occurrence"],
        pos_weight=occurrence_pos_weight,
    )

    quantity = masked_smooth_l1(
        output["quantity"],
        batch["quantity"],
        batch["quantity_mask"],
    )

    sell = masked_smooth_l1(
        output["sell_ratio"],
        batch["sell_ratio"],
        batch["sell_mask"],
    )

    total = hire + occurrence + quantity + sell

    return {
        "total": total,
        "hire": hire,
        "occurrence": occurrence,
        "quantity": quantity,
        "sell": sell,
    }


def create_stats():
    return {
        "samples": 0,
        "loss": {
            "total": 0.0,
            "hire": 0.0,
            "occurrence": 0.0,
            "quantity": 0.0,
            "sell": 0.0,
        },
        "hire_correct": 0,
        "tp": torch.zeros(len(OCCURRENCE_NAMES)),
        "fp": torch.zeros(len(OCCURRENCE_NAMES)),
        "fn": torch.zeros(len(OCCURRENCE_NAMES)),
    }


def update_metrics(stats, output, batch):
    batch_size = len(batch["hire"])
    stats["samples"] += batch_size

    hire_prediction = output["hire"].argmax(dim=1)

    stats["hire_correct"] += int(
        (hire_prediction == batch["hire"]).sum()
    )

    prediction = torch.sigmoid(
        output["occurrence"]
    ) >= 0.5

    target = batch["occurrence"] > 0.5

    stats["tp"] += (
        prediction & target
    ).sum(dim=0).cpu()

    stats["fp"] += (
        prediction & ~target
    ).sum(dim=0).cpu()

    stats["fn"] += (
        ~prediction & target
    ).sum(dim=0).cpu()


def finalize_metrics(stats):
    samples = stats["samples"]

    tp = stats["tp"]
    fp = stats["fp"]
    fn = stats["fn"]

    micro_tp = tp.sum().item()
    micro_fp = fp.sum().item()
    micro_fn = fn.sum().item()

    micro_precision = micro_tp / max(
        1,
        micro_tp + micro_fp,
    )

    micro_recall = micro_tp / max(
        1,
        micro_tp + micro_fn,
    )

    micro_f1 = (
        2 * micro_precision * micro_recall
        / max(1e-12, micro_precision + micro_recall)
    )

    precision = tp / (tp + fp).clamp(min=1)
    recall = tp / (tp + fn).clamp(min=1)

    f1 = (
        2 * precision * recall
        / (precision + recall).clamp(min=1e-12)
    )

    return {
        "total": stats["loss"]["total"] / samples,
        "hire": stats["loss"]["hire"] / samples,
        "occurrence": (
            stats["loss"]["occurrence"] / samples
        ),
        "quantity": (
            stats["loss"]["quantity"] / samples
        ),
        "sell": stats["loss"]["sell"] / samples,
        "hire_acc": (
            stats["hire_correct"] / samples
        ),
        "occ_micro_f1": micro_f1,
        "occ_macro_f1": f1.mean().item(),
    }


def run_epoch(
    model,
    loader,
    device,
    hire_weights,
    occurrence_pos_weight,
    optimizer=None,
):
    training = optimizer is not None
    model.train(training)

    stats = create_stats()

    for batch in loader:
        batch = {
            key: value.to(device)
            for key, value in batch.items()
        }

        if training:
            optimizer.zero_grad()

        output = model(batch["state"])

        losses = compute_losses(
            output,
            batch,
            hire_weights,
            occurrence_pos_weight,
        )

        if training:
            losses["total"].backward()

            nn.utils.clip_grad_norm_(
                model.parameters(),
                1.0,
            )

            optimizer.step()

        batch_size = len(batch["hire"])

        for name, loss in losses.items():
            stats["loss"][name] += (
                loss.item() * batch_size
            )

        update_metrics(
            stats,
            {
                key: value.detach()
                for key, value in output.items()
            },
            batch,
        )

    return finalize_metrics(stats)


def print_metrics(name, metrics):
    print(
        f"{name:<5} "
        f"loss={metrics['total']:.4f} "
        f"hire={metrics['hire']:.4f} "
        f"occ={metrics['occurrence']:.4f} "
        f"qty={metrics['quantity']:.4f} "
        f"sell={metrics['sell']:.4f} "
        f"hire_acc={100 * metrics['hire_acc']:.2f}% "
        f"occ_micro_f1={metrics['occ_micro_f1']:.3f} "
        f"occ_macro_f1={metrics['occ_macro_f1']:.3f}"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/processed/bc_dataset.pt"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/bc_best.pt"),
    )

    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-size", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
    )

    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--smoke", action="store_true")

    args = parser.parse_args()

    set_seed(args.seed)

    dataset = PreencodedBCDataset(args.dataset)

    train_indices, val_indices = (
        split_preencoded_by_episode(
            dataset,
            args.val_ratio,
            args.seed,
        )
    )

    if args.smoke:
        train_indices = train_indices[:4096]
        val_indices = val_indices[:1024]
        args.epochs = 1

    train_dataset = Subset(
        dataset,
        train_indices,
    )

    val_dataset = Subset(
        dataset,
        val_indices,
    )

    if args.device == "auto":
        device = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )
    else:
        device = torch.device(args.device)

    print(f"Dataset samples: {len(dataset)}")
    print(f"Train samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Device: {device}")

    hire_weights = compute_hire_weights(
        train_dataset
    ).to(device)

    occurrence_pos_weight = (
        compute_occurrence_pos_weight(
            train_dataset
        ).to(device)
    )

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

    model = BCModel(
        hidden_size=args.hidden_size,
        dropout=args.dropout,
    ).to(device)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.lr,
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        print()
        print(f"Epoch {epoch}/{args.epochs}")

        train_metrics = run_epoch(
            model,
            train_loader,
            device,
            hire_weights,
            occurrence_pos_weight,
            optimizer,
        )

        val_metrics = run_epoch(
            model,
            val_loader,
            device,
            hire_weights,
            occurrence_pos_weight,
        )

        print_metrics("train", train_metrics)
        print_metrics("val", val_metrics)

        if val_metrics["total"] < best_val_loss:
            best_val_loss = val_metrics["total"]

            torch.save({
                "epoch": epoch,
                "model_state_dict": (
                    model.state_dict()
                ),
                "optimizer_state_dict": (
                    optimizer.state_dict()
                ),
                "val_loss": best_val_loss,
                "hidden_size": args.hidden_size,
                "dropout": args.dropout,
                "feature_names": feature_names(),
                "occurrence_names": OCCURRENCE_NAMES,
                "quantity_names": QUANTITY_NAMES,
                "sell_names": SELL_NAMES,
                "hire_weights": (
                    hire_weights.cpu()
                ),
                "occurrence_pos_weight": (
                    occurrence_pos_weight.cpu()
                ),
            }, args.output)

            print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()