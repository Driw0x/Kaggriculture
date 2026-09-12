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
Deterministic executor
       |
       v
Legal Kaggriculture actions
```

The learning policy is responsible for strategy. The deterministic executor remains responsible for executing these decisions safely and efficiently.

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

The replay dataset can be expanded without changing the training pipeline. Dataset statistics should be regenerated with:

```bash
python scripts/analyze_replays.py
```

## 4. Replay Dataset

`src/learning/replay_dataset.py` reads the raw replay files.

Kaggle replays store the action associated with the previous observation. The correct training alignment is therefore:

```text
observation[t]
      |
      v
action[t + 1]
```

This temporal shift is required for the model to learn the action selected from the corresponding observation.

The expert player is identified using `metadata.json` and the replay team names instead of assuming that the player with the highest final reward is the expert.

Replay files are read recursively from the expert replay directory.

The episode ID is preserved for each sample so training and validation can be separated by complete episodes.

Replay loading is streaming. Replays are processed one at a time instead of storing all decoded observations and actions in memory. This makes preprocessing scalable to substantially larger replay collections.

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

Tile positions are not currently encoded individually. Production is aggregated by crop and animal type because low-level spatial execution remains the responsibility of the deterministic executor.

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

These actions remain the responsibility of the deterministic executor.

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

Strategic actions occur frequently enough at individual ticks to retain the original temporal resolution.

The selected representation is therefore tick-level:

```text
observation at tick t
        |
        v
strategic decisions selected from tick t
```

Multiple strategic decisions may occur during the same tick.

Ticks without strategic decisions are preserved because they teach the policy when not to initiate a new strategic action.

## 8. Learning Targets

`src/learning/target_encoder.py` converts extracted strategic decisions into targets suitable for Behavioral Cloning.

Five target groups are currently used.

### Hire

Hiring is represented as a regression target:

```text
log1p(number_of_hires)
```

The prediction is converted back to an integer number of hires during inference.

This avoids treating neighboring hire counts as completely unrelated classes.

### Purchase Bundle

Purchase decisions are represented jointly instead of with independent binary outputs.

The purchase actions are:

```text
BUY_LAND
BUY_SEED_WHEAT
BUY_SEED_CARROT
BUY_SEED_TOMATO
BUY_SEED_STRAWBERRY
BUY_SEED_MELON
BUY_ANIMAL_GOOSE
BUY_ANIMAL_COW
BUY_ANIMAL_SHEEP
BUY_PRODUCT_WHEAT
BUY_PRODUCT_FERTILIZER
```

The 11 purchase flags are encoded as a bitmask:

```text
2^11 = 2048 possible purchase bundles
```

A categorical purchase bundle prevents the policy from independently combining incompatible purchase modes that never occurred together in expert trajectories.

### Occurrence

Non-purchase strategic decisions are represented with independent binary occurrence targets.

Examples:

```text
plant_WHEAT
place_COW
fertilize
build_pasture
sell_WHEAT
```

Several occurrence decisions may be active during the same tick.

### Quantity

Actions with quantities use:

```text
log1p(quantity)
```

Quantity loss is evaluated only when the corresponding action is active.

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

## 9. Behavioral Cloning Dataset

`src/learning/bc_dataset.py` combines state and target encoding.

Each training sample contains:

```text
state
hire
purchase_bundle
occurrence
quantity
quantity_mask
sell_ratio
sell_mask
episode
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

For larger replay collections, `scripts/preencode_bc.py` builds a pre-encoded tensor dataset:

```text
data/processed/bc_dataset.pt
```

The preprocessing pipeline performs two streaming passes:

```text
pass 1 -> count valid samples
pass 2 -> encode samples directly into preallocated tensors
```

This keeps JSON replay memory usage bounded while preserving the final tensor format used for training.

## 10. Behavioral Cloning Model

`src/learning/model.py` implements the strategic policy.

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
        +-----------+------------------+------------------+------------------+------------------+
        |           |                  |                  |                  |
        v           v                  v                  v                  v
      Hire      Purchase bundle     Occurrence         Quantity          Sell ratio
   regression     2048 classes      multi-label       regression         regression
```

The model remains intentionally compact.

The output heads are:

- `hire`: scalar regression output;
- `purchase_bundle`: 2048 categorical logits;
- `occurrence`: one logit per remaining strategic decision;
- `quantity`: one regression value per quantity target;
- `sell_ratio`: one regression value per sell target.

## 11. Behavioral Cloning Training

`scripts/train_bc.py` trains the strategic policy from the pre-encoded dataset.

The base configuration uses:

```text
Train / validation split: 80% / 20% by episode
Batch size: 512
Hidden size: 256
Learning rate: 1e-3
```

The number of epochs is configurable:

```bash
python scripts/train_bc.py --epochs 50
```

The current losses are:

```text
hire            -> SmoothL1Loss
purchase bundle -> CrossEntropyLoss
occurrence      -> BCEWithLogitsLoss
quantity        -> masked SmoothL1Loss
sell ratio      -> masked SmoothL1Loss
```

The current training does not use inverse-frequency class weighting. Earlier weighted losses caused rare strategic actions to be over-predicted.

Gradient clipping is applied during training.

The best validation checkpoint is stored as:

```text
models/bc_best.pt
```

A smoke mode is also available:

```bash
python scripts/train_bc.py --smoke
```

## 12. Evaluation Metrics

`scripts/evaluate_bc.py` evaluates the best Behavioral Cloning checkpoint.

The evaluation reports:

- hire log MAE;
- hire count MAE;
- exact hire accuracy;
- global purchase bundle accuracy;
- purchase bundle accuracy per class;
- precision, recall and F1 per occurrence decision;
- occurrence micro F1;
- occurrence macro F1;
- quantity MAE;
- sell ratio MAE;
- optimized occurrence thresholds.

The latest 50-epoch model reached:

```text
Hire count MAE: 0.0736
Hire exact accuracy: 0.950
Purchase bundle accuracy: 0.904
Occurrence micro F1 @ 0.5: 0.554
Occurrence macro F1 @ 0.5: 0.549
Occurrence macro F1 with calibrated thresholds: 0.611
```

The optimized occurrence thresholds are stored in:

```text
models/bc_thresholds.json
```

These thresholds must remain paired with the checkpoint used to generate them.

## 13. Autonomous Hybrid Agent

`src/agents/bc_agent.py` integrates the learned strategic policy with deterministic execution.

The autonomous pipeline is:

```text
Observation
     |
     v
State encoder
     |
     v
BC policy
     |
     +---------------------------+
     |                           |
     v                           v
Market / workforce          Production intent
     |                           |
     +-------------+-------------+
                   |
                   v
        Deterministic executor
                   |
                   v
      Worker allocation / pathing
                   |
                   v
          Kaggriculture action
```

The learned model decides strategic intent. The executor handles mechanics that should remain deterministic, including movement, pickup and drop operations, watering, feeding, care, harvesting, fertilizer collection, worker-task assignment and legal action constraints.

The executor also protects the learned policy from invalid or physically impossible actions.

The autonomous agent is evaluated separately from offline validation because small prediction errors can move the policy into states that are not well represented in expert trajectories.

## 14. Closed-Loop Evaluation

Offline Behavioral Cloning metrics are necessary but are not sufficient to measure autonomous performance.

During autonomous play:

```text
prediction error
      |
      v
different next state
      |
      v
state distribution shift
      |
      v
new prediction error
```

This compounding-error problem explains why a model with strong validation metrics can still perform poorly in complete Kaggriculture games.

The autonomous agent must therefore be benchmarked over repeated games using:

- minimum reward;
- maximum reward;
- mean reward;
- reward distribution;
- total hires;
- plant and harvest counts;
- worker idle actions;
- final shed inventory;
- final worker inventory;
- remaining crops and animals;
- weeds and other failure cases.

The deterministic heuristic agent remains the reference baseline.

## 15. Reinforcement Learning

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
Autonomous BC agent
      |
      v
Reinforcement Learning
      |
      v
Optimized learning agent
```

Pure Reinforcement Learning from scratch can later be used as a comparison baseline.

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
- recursive replay discovery;
- streaming replay preprocessing;
- corrected temporal alignment `observation[t] -> action[t + 1]`;
- state encoder with 107 features;
- strategic decision extractor;
- replay and state analysis;
- tick-level learning representation;
- hire regression target;
- joint purchase bundle target;
- multi-label non-purchase occurrence targets;
- quantity targets;
- normalized sell targets;
- episode-level train / validation split;
- pre-encoded Behavioral Cloning dataset;
- multi-head Behavioral Cloning model;
- unweighted and masked training losses;
- checkpoint saving;
- per-decision evaluation;
- occurrence threshold calibration;
- autonomous BC policy integration;
- deterministic execution layer;
- unit and shadow tests for the learning pipeline.

Latest offline model:

```text
Training: 50 epochs
Validation samples: 145957
Hire count MAE: 0.0736
Hire exact accuracy: 95.0%
Purchase bundle accuracy: 90.4%
Occurrence micro F1: 0.554
Occurrence macro F1: 0.549
Calibrated occurrence macro F1: 0.611
```

Final decision:

The learning-based autonomous agent is not retained for further development. Despite encouraging offline validation metrics, autonomous results are less stable and lower than those of the deterministic heuristic agent.

The learning implementation and results are kept as an experimental track, while development continues with the heuristic agent.
