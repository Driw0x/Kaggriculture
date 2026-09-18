import torch

from scripts.train_bc import compute_losses, masked_smooth_l1


def test_masked_smooth_l1():
    prediction = torch.tensor([[1.0, 5.0], [3.0, 4.0]], requires_grad=True)
    target = torch.tensor([[1.5, 0.0], [0.0, 5.0]])
    mask = torch.tensor([[1.0, 0.0], [0.0, 1.0]])

    loss = masked_smooth_l1(prediction, target, mask)

    assert loss.item() > 0

    loss.backward()

    assert prediction.grad is not None


def test_masked_smooth_l1_empty():
    prediction = torch.randn(2, 3, requires_grad=True)
    target = torch.zeros(2, 3)
    mask = torch.zeros(2, 3)

    loss = masked_smooth_l1(prediction, target, mask)

    assert loss.item() == 0.0

    loss.backward()

    assert prediction.grad is not None


def test_compute_losses():
    output = {
        "hire": torch.randn(2, requires_grad=True),
        "purchase_bundle": torch.randn(2, 4, requires_grad=True),
        "occurrence": torch.randn(2, 3, requires_grad=True),
        "quantity": torch.randn(2, 2, requires_grad=True),
        "sell_ratio": torch.sigmoid(torch.randn(2, 1, requires_grad=True)),
    }

    batch = {
        "hire": torch.tensor([0.0, 2.0]),
        "purchase_bundle": torch.tensor([1, 2]),
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

    losses = compute_losses(output, batch)

    assert set(losses) == {
        "total",
        "hire",
        "purchase_bundle",
        "occurrence",
        "quantity",
        "sell",
    }

    assert losses["total"].item() > 0

    losses["total"].backward()
