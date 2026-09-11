import torch

from scripts.evaluate_bc import compute_f1, evaluate_occurrences, search_best_threshold


def test_compute_f1():
    precision, recall, f1 = compute_f1(8, 2, 4)

    assert precision == 0.8
    assert recall == 8 / 12
    assert 0 < f1 < 1


def test_compute_f1_empty():
    precision, recall, f1 = compute_f1(0, 0, 0)

    assert precision == 0.0
    assert recall == 0.0
    assert f1 == 0.0


def test_evaluate_occurrences():
    logits = torch.tensor([
        [10.0, -10.0],
        [-10.0, 10.0],
        [10.0, 10.0],
    ])

    targets = torch.tensor([
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0],
    ])

    tp, fp, fn, tn = evaluate_occurrences(logits, targets, threshold=0.5)

    assert tp.tolist() == [1, 2]
    assert fp.tolist() == [1, 0]
    assert fn.tolist() == [0, 0]
    assert tn.tolist() == [1, 1]


def test_search_best_threshold():
    probabilities = torch.tensor([0.1, 0.2, 0.4, 0.8, 0.9])
    targets = torch.tensor([0.0, 0.0, 1.0, 1.0, 1.0])

    threshold, f1 = search_best_threshold(
        probabilities,
        targets,
        thresholds=[0.3, 0.5, 0.7],
    )

    assert threshold == 0.3
    assert f1 == 1.0