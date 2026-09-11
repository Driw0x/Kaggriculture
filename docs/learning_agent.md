# Learning Agent

## 1. Objective

The learning agent is an experimental alternative to the deterministic heuristic agent.

The objective is to learn strategic decisions from high-performing Kaggriculture agents while keeping deterministic execution for low-level farm actions and pathing.

The architecture is hybrid:

```text
Game observation
       |
       v
Learning policy
       |
       v
Strategic decisions
       |
       v
Deterministic planner
       |
       v
Legal Kaggriculture actions
```

The learning policy is responsible for strategy. The deterministic planner remains responsible for executing these decisions safely and efficiently.

## 2. Approach

The learning pipeline is divided into two main stages:

1. Imitation Learning
2. Reinforcement Learning

Behavioral Cloning is used first to learn from strong existing agents. Reinforcement Learning can then fine-tune the learned policy through interaction with the Kaggriculture environment.

Pure Reinforcement Learning from scratch can later be evaluated as a baseline, but it is not the primary approach.

## 3. Expert Replays

Expert demonstrations are collected from high-ranking Kaggriculture leaderboard submissions.

The downloader follows the Kaggle simulation competition hierarchy:

```text
Leaderboard
    |
    v
Top N teams
    |
    v
Best submission
    |
    v
Episodes
    |
    v
Replay JSON
```

Replays are stored by stable Kaggle team ID instead of leaderboard rank:

```text
data/
└── expert_replays/
    ├── metadata.json
    ├── team_<team_id>/
    │   ├── <episode_id>.json
    │   └── ...
    └── ...
```

This avoids associating old replay folders with the wrong team when leaderboard rankings change.

Example:

```bash
python scripts/download_replays.py --top 10 --episodes 40
```

Existing replay files are skipped so interrupted downloads can be resumed.

The current dataset contains:

```text
Replays: 399
Samples: 287280
Metadata mismatches: 0
Invalid samples: 0
```

## 4. Replay Dataset

`src/learning/replay_dataset.py` loads the raw replay files.

Each usable sample preserves:

```text
observation_t
      |
      v
action_t
```

The expert player is identified using `metadata.json` and the replay team names instead of assuming that the player with the highest final reward is the expert.

Replay files are read recursively from the expert replay directory.

The episode ID is preserved for each sample so training and validation can later be separated by complete episodes.

## 5. State Encoding

`src/learning/state_encoder.py` converts a raw Kaggriculture observation into a fixed numerical feature vector.

The current state contains 107 features covering:

- day and hour;
- money;
- hired workers;
- unlocked land;
- shed contents;
- available seeds;
- carried products;
- market inventory;
- market prices;
- unlocked shops;
- crop production state;
- animal production state;
- watering state;
- feeding state;
- care state;
- fertilizer state.

Large non-negative quantity features use `log1p` scaling to reduce differences in magnitude between small and large inventories or production counts.

Day and hour are normalized. Market inventories are represented relative to their baseline inventory and market prices relative to their base prices.

Tile positions are not currently encoded individually. Production is aggregated by crop and animal type because low-level spatial execution remains the responsibility of the deterministic planner.

The encoder has been validated on the complete expert dataset:

```text
Observations: 287280
Feature count: 107
Encoding errors: 0
Size errors: 0
Non-finite states: 0
Zero features: none
```

The first learning model deliberately excludes opponent state. Opponent modeling is reserved for a later variant after the base learning agent has been optimized.

## 6. Decision Extraction

`src/learning/decision_extractor.py` converts raw expert actions into strategic decisions.

The current strategic decisions include:

```text
HIRE
BUY_LAND
BUY_SEED
BUY_ANIMAL
BUY_PRODUCT
SELL
PLANT
PLACE
FERTILIZE
BUILD_COOP
BUILD_PASTURE
```

Low-level execution actions are deliberately excluded:

```text
NORTH
SOUTH
EAST
WEST
PASS
PICKUP
DROP
WATER
FEED
CARE
HARVEST
COLLECT_FERTILIZER
```

These actions remain the responsibility of the deterministic planner.

Market quantities and worker action counts are preserved. Invalid oversized `SELL` requests found in some replay actions are limited to the amount actually available in the shed.

## 7. Replay Analysis

`scripts/analyze_replays.py` analyzes the expert dataset before training.

It reports:

- number of replays;
- number of usable samples;
- invalid samples;
- represented expert teams;
- frequency of each strategic decision;
- quantity distributions;
- strategic decisions by day;
- strategic decisions by hour;
- observations without strategic decisions.

Run:

```bash
python scripts/analyze_replays.py
```

The current dataset contains:

```text
Replays: 399
Samples: 287280
Invalid samples: 0
Zero strategic decisions: 42.88%
```

Strategic actions occur frequently enough at individual ticks to retain the original temporal resolution.

The selected representation is therefore tick-level:

```text
observation at tick t
        |
        v
strategic decisions at tick t
```

Multiple strategic decisions may occur during the same tick, so the problem is multi-label rather than single-class classification.

Ticks without strategic decisions are preserved because they teach the policy when not to initiate a new strategic action.

## 8. Learning Targets

`src/learning/target_encoder.py` converts extracted strategic decisions into targets suitable for Behavioral Cloning.

Four target groups are used.

### Hire

Hiring is represented as an 11-class classification problem:

```text
0, 1, 2, ..., 10 hires
```

The dataset is strongly imbalanced, with most ticks containing no hire action.

### Occurrence

Strategic decisions are represented with independent binary occurrence targets.

Examples:

```text
buy_seed_WHEAT
buy_animal_COW
sell_WHEAT
plant_CARROT
fertilize
build_pasture
```

This allows several decisions to be active during the same tick.

### Quantity

Actions with quantities use:

```text
log1p(quantity)
```

Quantity loss is evaluated only when the corresponding occurrence target is active.

### Sell Ratio

Sell quantities are represented relative to the available shed inventory:

```text
sell_ratio = sold_quantity / available_quantity
```

This allows the policy to distinguish partial sales from complete liquidation without depending on an absolute inventory size.

The ratio is bounded to:

```text
0 <= sell_ratio <= 1
```

The replay analysis confirms that both partial and complete sales are common.

## 9. Behavioral Cloning Dataset

`src/learning/bc_dataset.py` combines state and target encoding.

Each training sample contains:

```text
state
hire
occurrence
quantity
quantity_mask
sell_ratio
sell_mask
```

Quantity and sell losses are masked so inactive decisions do not contribute to their regression losses.

Training and validation are split by complete episode rather than random ticks:

```text
episode A -> train
episode B -> train
episode C -> validation
```

Ticks from the same replay therefore cannot appear in both training and validation.

This prevents temporal leakage between highly correlated neighboring observations.

## 10. Behavioral Cloning Model

`src/learning/model.py` implements the first strategic policy.

The model uses a shared MLP:

```text
107 state features
        |
        v
Linear(107, 256)
ReLU
LayerNorm
Dropout
        |
        v
Linear(256, 256)
ReLU
LayerNorm
        |
        +------------------+------------------+------------------+
        |                  |                  |                  |
        v                  v                  v                  v
      Hire             Occurrence          Quantity          Sell ratio
   11 classes          multi-label         regression         regression
```

The model is intentionally small for the first Behavioral Cloning baseline.

The output heads are:

- `hire`: 11 logits;
- `occurrence`: one logit per strategic decision;
- `quantity`: one regression value per quantity target;
- `sell_ratio`: one value in `[0, 1]` per sell target.

## 11. Behavioral Cloning Training

`scripts/train_bc.py` trains the strategic policy.

The default configuration is:

```text
Train / validation split: 80% / 20% by episode
Batch size: 512
Epochs: 20
Hidden size: 256
Learning rate: 1e-3
```

The losses are:

```text
hire        -> weighted CrossEntropyLoss
occurrence  -> weighted BCEWithLogitsLoss
quantity    -> masked SmoothL1Loss
sell ratio  -> masked SmoothL1Loss
```

Class weights are calculated only from the training split.

Weights are capped to limit instability caused by extremely rare decisions.

Gradient clipping is applied during training.

The best validation checkpoint is stored as:

```text
models/bc_best.pt
```

A smoke mode is available:

```bash
python scripts/train_bc.py --smoke
```

It uses:

```text
Train samples: 4096
Validation samples: 1024
Epochs: 1
```

The first smoke training completed successfully:

```text
train loss=3.3477
train hire_acc=36.55%
train occ_micro_f1=0.066
train occ_macro_f1=0.042

val loss=2.7795
val hire_acc=65.82%
val occ_micro_f1=0.224
val occ_macro_f1=0.044
```

The smoke test validates the complete forward, backward, loss, metric and checkpoint pipeline. These values are not considered final model performance because the smoke dataset and training duration are intentionally small.

Full training can be launched with:

```bash
python scripts/train_bc.py
```

## 12. Evaluation Metrics

Accuracy alone is insufficient because strategic decisions are strongly imbalanced.

For example, most ticks contain no hire action and several strategic actions occur in less than 1% of observations.

Training therefore reports:

- total loss;
- hire loss;
- occurrence loss;
- quantity loss;
- sell loss;
- hire accuracy;
- occurrence micro F1;
- occurrence macro F1.

Macro F1 is particularly important because it gives rare strategic decisions more visibility than aggregate accuracy.

Further evaluation will add per-decision metrics and confusion analysis after the first full Behavioral Cloning training.

## 13. Hybrid Agent

The learned model is not intended to directly replace all existing planning logic.

The target architecture remains:

```text
Observation
     |
     v
State encoder
     |
     v
Learned strategic policy
     |
     +-------------------------+
     |                         |
     v                         v
Production targets       Market / workforce
     |                         |
     +------------+------------+
                  |
                  v
        Deterministic planner
                  |
                  v
     Worker allocation / pathing
                  |
                  v
         Kaggriculture action
```

The learning model selects strategic objectives while deterministic logic enforces game mechanics, survival constraints, legal actions and efficient pathing.

## 14. Reinforcement Learning

After Behavioral Cloning, the learned policy can be fine-tuned using Reinforcement Learning.

The main objective remains the Kaggriculture reward:

```text
final money
```

The planned sequence is:

```text
Expert replays
      |
      v
Behavioral Cloning
      |
      v
Pretrained strategic policy
      |
      v
Reinforcement Learning
      |
      v
Optimized hybrid agent
```

Pure Reinforcement Learning from scratch can later be used as a comparison baseline.

## 15. Evaluation

Learning agents will be compared against the deterministic heuristic agent using repeated Kaggriculture simulations.

Planned comparisons include:

```text
Heuristic agent
Behavioral Cloning
Behavioral Cloning + Reinforcement Learning
Reinforcement Learning from scratch
```

Evaluation should use multiple games and report at least:

- minimum reward;
- maximum reward;
- mean reward;
- reward distribution;
- failure cases.

The deterministic heuristic agent remains the reference baseline.

## 16. Opponent Modeling

Opponent modeling is deliberately excluded from the initial learning agent.

The first objective is to maximize the performance of the base policy without depending on opponent information.

Once the optimized version is stable, two variants can be maintained:

```text
Base optimized agent
Base optimized agent + opponent modeling
```

This keeps the effect of opponent modeling measurable independently from the core strategy.

## 17. Current Status

Implemented and validated:

- expert replay downloading;
- stable team-based replay storage;
- expert identity metadata;
- recursive replay loading;
- state encoder with 107 features;
- strategic decision extractor;
- replay and state analysis;
- tick-level learning representation;
- multi-label strategic targets;
- quantity targets;
- normalized sell targets;
- Behavioral Cloning dataset;
- episode-level train/validation split;
- multi-head Behavioral Cloning model;
- weighted and masked training losses;
- training metrics;
- model checkpoint saving;
- Behavioral Cloning smoke training;
- unit tests for the learning pipeline.

Current dataset:

```text
Expert replays: 399
Samples: 287280
Invalid samples: 0
Metadata mismatches: 0
Encoding errors: 0
```

Next:

1. train the Behavioral Cloning model on the complete expert dataset;
2. evaluate global and per-decision validation performance;
3. implement strategic policy inference;
4. integrate the learned policy with the deterministic planner;
5. benchmark against the heuristic agent;
6. analyze failure cases;
7. fine-tune with Reinforcement Learning;
8. evaluate opponent modeling only after the base optimized agent is stable.