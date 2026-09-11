import torch
from torch import nn

from scripts.train_bc import compute_losses, masked_smooth_l1


def test_masked_smooth_l1():
    prediction = torch.tensor([[1.0, 10.0]])
    target = torch.tensor([[2.0, 0.0]])
    mask = torch.tensor([[1.0, 0.0]])

    loss = masked_smooth_l1(prediction, target, mask)

    assert loss.item() == 0.5


def test_masked_smooth_l1_empty():
    prediction = torch.tensor([[1.0, 2.0]], requires_grad=True)
    target = torch.zeros_like(prediction)
    mask = torch.zeros_like(prediction)

    loss = masked_smooth_l1(prediction, target, mask)

    assert loss.item() == 0.0

    loss.backward()

    assert prediction.grad is not None


def test_compute_losses():
    output = {
        "hire": torch.randn(2, 11, requires_grad=True),
        "occurrence": torch.randn(2, 3, requires_grad=True),
        "quantity": torch.randn(2, 2, requires_grad=True),
        "sell_ratio": torch.sigmoid(torch.randn(2, 1, requires_grad=True)),
    }

    batch = {
        "hire": torch.tensor([0, 2]),
        "occurrence": torch.tensor([
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 0.0],
        ]),
        "quantity": torch.tensor([
            [1.0, 0.0],
            [0.0, 2.0],
        ]),
        "quantity_mask": torch.tensor([
            [1.0, 0.0],
            [0.0, 1.0],
        ]),
        "sell_ratio": torch.tensor([
            [1.0],
            [0.0],
        ]),
        "sell_mask": torch.tensor([
            [1.0],
            [0.0],
        ]),
    }

    hire_loss_fn = nn.CrossEntropyLoss()
    occurrence_loss_fn = nn.BCEWithLogitsLoss()

    losses = compute_losses(
        output,
        batch,
        hire_loss_fn,
        occurrence_loss_fn,
    )

    assert set(losses) == {
        "total",
        "hire",
        "occurrence",
        "quantity",
        "sell",
    }

    assert all(torch.isfinite(loss) for loss in losses.values())

    losses["total"].backward()