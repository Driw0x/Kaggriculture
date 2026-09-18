import torch

from src.learning.model import BCModel
from src.learning.state_encoder import feature_names
from src.learning.target_encoder import PURCHASE_BUNDLE_COUNT, occurrence_names, quantity_names, sell_names


def test_model():
    model = BCModel()
    batch_size = 4
    state = torch.randn(batch_size, len(feature_names()))

    output = model(state)

    assert output["hire"].shape == (batch_size,)
    assert output["purchase_bundle"].shape == (batch_size, PURCHASE_BUNDLE_COUNT)
    assert output["occurrence"].shape == (batch_size, len(occurrence_names()))
    assert output["quantity"].shape == (batch_size, len(quantity_names()))
    assert output["sell_ratio"].shape == (batch_size, len(sell_names()))

    assert torch.isfinite(output["hire"]).all()
    assert torch.isfinite(output["purchase_bundle"]).all()
    assert torch.isfinite(output["occurrence"]).all()
    assert torch.isfinite(output["quantity"]).all()
    assert torch.isfinite(output["sell_ratio"]).all()

    assert (output["sell_ratio"] >= 0).all()
    assert (output["sell_ratio"] <= 1).all()
