from torch import nn

from src.learning.state_encoder import feature_names
from src.learning.target_encoder import PURCHASE_BUNDLE_COUNT, occurrence_names, quantity_names, sell_names


class BCModel(nn.Module):
    def __init__(self, hidden_size=256, dropout=0.1):
        super().__init__()
        input_size = len(feature_names())

        self.encoder = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size),
        )

        self.hire_head = nn.Linear(hidden_size, 1)
        self.purchase_bundle_head = nn.Linear(hidden_size, PURCHASE_BUNDLE_COUNT)
        self.occurrence_head = nn.Linear(hidden_size, len(occurrence_names()))
        self.quantity_head = nn.Linear(hidden_size, len(quantity_names()))
        self.sell_head = nn.Linear(hidden_size, len(sell_names()))

    def forward(self, state):
        hidden = self.encoder(state)
        return {
            "hire": self.hire_head(hidden).squeeze(-1),
            "purchase_bundle": self.purchase_bundle_head(hidden),
            "occurrence": self.occurrence_head(hidden),
            "quantity": self.quantity_head(hidden),
            "sell_ratio": self.sell_head(hidden).sigmoid(),
        }