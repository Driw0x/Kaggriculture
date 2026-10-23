[English](learning_agent.md) | [Français](learning_agent.fr.md) | [简体中文](learning_agent.zh-CN.md)

[项目 README](../README.zh-CN.md)

<a id="learning-agent"></a>
# 学习代理

<a id="1-objective"></a>
## 1. 目标

学习代理是确定性启发式代理的一种实验性替代方案。

目标是从表现优异的Kaggriculture代理中学习战略决策，同时在低层级农场操作和路径规划方面保持确定性执行。

架构是混合型的：

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

学习策略负责策略决策，确定性执行器则负责安全且高效地执行这些决策。

<a id="2-approach"></a>
## 2. 方法

学习管道分为两个主要阶段：

1. 模仿学习
2. 强化学习

首先使用行为克隆从现有强代理中学习。随后通过与Kaggriculture环境的交互，使用强化学习对已学习的策略进行微调。

从零开始的纯强化学习可以作为基线进行评估，但并非主要方法。


<a id="3-expert-replays"></a>
## 3. 专家回放

专家演示来自高排名Kaggriculture排行榜提交。

下载器遵循Kaggle模拟竞赛的层级结构：

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

回放文件按稳定的Kaggle团队ID存储，而非排行榜排名：

```text
data/
└── expert_replays/
    ├── metadata.json
    ├── team_<team_id>/
    │   ├── <episode_id>.json
    │   └── ...
    └── ...
```

这可以避免当排行榜排名发生变化时，将旧的回放文件夹错误地关联到错误的团队。

示例：

```bash
python scripts/download_replays.py --top 10 --episodes 40
```

跳过已存在的回放文件，以便中断下载可以继续进行。

回放数据集可以在不改变训练管道的情况下扩展。数据集统计信息应使用以下命令重新生成：

```bash
python scripts/analyze_replays.py
```

<a id="4-replay-dataset"></a>
## 4. 回放数据集

`src/learning/replay_dataset.py`读取原始回放文件。

Kaggle回放文件存储与前一个观察相关的动作。因此，正确的训练对齐是：

```text
observation[t]
      |
      v
action[t + 1]
```

这种时间偏移是模型学习从对应观察中选择的动作所必需的。

专家玩家通过`metadata.json`和回放团队名称来识别，而不是假设最终奖励最高的玩家是专家。

回放文件从专家回放目录中递归读取。

每个样本都保留了剧集ID，以便训练和验证可以按完整剧集进行分离。

回放加载是流式处理的。回放文件一次处理一个，而不是将所有解码后的观察和动作存储在内存中。这使得预处理可扩展到显著更大的回放集合。

<a id="5-state-encoding"></a>
## 5. 状态编码

`src/learning/state_encoder.py`将原始Kaggriculture观察结果转换为固定数值特征向量。

当前状态包含107个特征，涵盖：

- 日期和小时；
- 金钱；
- 雇佣的工人数量；
- 已解锁的土地；
- 棚屋内容；
- 可用的种子；
- 携带的产品；
- 市场库存；
- 市场价格；
- 已解锁的商店；
- 作物生产状态；
- 动物生产状态；
- 浇水状态；
- 喂养状态；
- 状态信息;
- 肥料状态。

大非负数量特征使用`log1p`缩放，以减少小规模与大规模库存或产量计数之间的量级差异。

日与小时被归一化。市场库存以基线库存为基准表示，市场价格以基价为基准表示。

当前未单独编码瓷砖位置。生产按作物和动物类型进行聚合，因为低层级空间执行仍由确定性执行器负责。

首个学习模型故意排除对手状态。对手建模被保留至基础学习代理优化之后的后续变体中。

<a id="6-decision-extraction"></a>
## 6. 决策提取

`src/learning/decision_extractor.py`将原始专家动作转换为战略决策。

当前的战略决策包括：

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

低层级执行动作被刻意排除：

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

这些动作仍由确定性执行器负责。

市场数量和工人动作数量被保留。在部分回放动作中发现的无效超量`SELL`请求被限制为实际存在于仓库中的数量。

<a id="7-replay-analysis"></a>
## 7. 回放分析

`scripts/analyze_replays.py`在训练前分析专家数据集。

它报告：

- 回放数量;
- 可用样本数量;
- 无效样本数量;
- 代表的专家团队数量;
- 每种战略决策的频率;
- 数量分布;
- 按日的战略决策;
- 按小时的战略决策;
- 无战略决策的观测记录。

运行：

```bash
python scripts/analyze_replays.py
```

战略动作在单个时间步长内频繁发生，足以保留原始的时间分辨率。

因此所选表示为时间步长级别：

```text
observation at tick t
        |
        v
strategic decisions selected from tick t
```

同一时间步长内可能产生多个战略决策。

无战略决策的时间步长被保留，因为它们教会策略在何种情况下不应启动新的战略动作。

<a id="8-learning-targets"></a>
## 8. 学习目标

`src/learning/target_encoder.py`将提取的战略决策转换为适用于行为克隆的学习目标。

目前使用五个目标组。

<a id="hire"></a>
### 招聘

招聘以回归目标表示：

```text
log1p(number_of_hires)
```

在推理阶段，预测结果会被转换为实际的招聘人数整数。

这避免了将相邻招聘数量视为完全无关的类别。

<a id="purchase-bundle"></a>
### 购买组合

购买决策以联合方式表示，而非独立的二元输出。

购买动作包括：

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

11个购买标志以位掩码形式编码：

```text
2^11 = 2048 possible purchase bundles
```

类别型购买组合防止策略独立组合在专家轨迹中从未同时出现的不兼容购买模式。

<a id="occurrence"></a>
### 发生频率

非购买战略决策以独立的二元发生目标表示。

示例：

```text
plant_WHEAT
place_COW
fertilize
build_pasture
sell_WHEAT
```

同一时间步内可能有多个决策处于激活状态。

<a id="quantity"></a>
### 数量

涉及数量的操作使用：

```text
log1p(quantity)
```

数量损失仅在对应操作激活时进行评估。

<a id="sell-ratio"></a>
### 卖出比例

卖出数量相对于可售库存表示：

```text
sell_ratio = sold_quantity / available_quantity
```

这使得策略能够在不依赖绝对库存大小的情况下区分部分销售与完全清仓。

该比例被限制为：

```text
0 <= sell_ratio <= 1
```

<a id="9-behavioral-cloning-dataset"></a>
## 9. 行为克隆数据集

`src/learning/bc_dataset.py`结合了状态和目标编码。

每个训练样本包含：

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

数量和卖出损失被屏蔽，使得未激活的决策不会对其回归损失产生贡献。

训练和验证是按完整回合划分，而非随机时间步：

```text
episode A -> train
episode B -> train
episode C -> validation
```

因此，同一回放中的时间步不会同时出现在训练和验证中。

这防止了高度相关邻近观测之间的时序泄露。

对于较大的回放集合，`scripts/preencode_bc.py`构建预编码张量数据集：

```text
data/processed/bc_dataset.pt
```

预处理流水线执行两次流式遍历：

```text
pass 1 -> count valid samples
pass 2 -> encode samples directly into preallocated tensors
```

这在保持用于训练的最终张量格式的同时，将JSON回放的内存使用量限制在有界范围内。

<a id="10-behavioral-cloning-model"></a>
## 10. 行为克隆模型

`src/learning/model.py`实现了策略模型。

该模型使用共享的MLP：

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

该模型保持有意的紧凑性。

输出头包括：

- `hire`：标量回归输出；
- `purchase_bundle`：2048个分类logits；
- `occurrence`：每个剩余战略决策一个logit；
- `quantity`：每个数量目标一个回归值；
- `sell_ratio`：每个卖出目标一个回归值。

<a id="11-behavioral-cloning-training"></a>
## 11. 行为克隆训练

`scripts/train_bc.py`从预编码数据集中训练策略模型。

基础配置使用：

```text
Train / validation split: 80% / 20% by episode
Batch size: 512
Hidden size: 256
Learning rate: 1e-3
```

训练轮数可配置：

```bash
python scripts/train_bc.py --epochs 50
```

当前损失包括：

```text
hire            -> SmoothL1Loss
purchase bundle -> CrossEntropyLoss
occurrence      -> BCEWithLogitsLoss
quantity        -> masked SmoothL1Loss
sell ratio      -> masked SmoothL1Loss
```

当前训练不使用逆频率类别加权。早期加权损失导致罕见战略动作被过度预测。

训练过程中应用梯度裁剪。

最佳验证检查点存储为：

```text
models/bc_best.pt
```

还提供一种烟雾模式：

```bash
python scripts/train_bc.py --smoke
```

<a id="12-evaluation-metrics"></a>
## 12. 评估指标

`scripts/evaluate_bc.py`评估最佳的行为克隆检查点。

评估报告包括：

- 招聘日志MAE；
- 招聘数量MAE；
- 精确招聘准确率；
- 全局采购捆绑准确率；
- 各类别采购捆绑准确率；
- 每个决策发生的精确率、召回率和F1值；
- 决策微F1；
- 决策宏F1；
- 数量MAE；
- 卖出比例MAE；
- 优化后的决策阈值。

最新50轮模型达到了：

```text
Hire count MAE: 0.0736
Hire exact accuracy: 0.950
Purchase bundle accuracy: 0.904
Occurrence micro F1 @ 0.5: 0.554
Occurrence macro F1 @ 0.5: 0.549
Occurrence macro F1 with calibrated thresholds: 0.611
```

优化后的决策阈值存储在：

```text
models/bc_thresholds.json
```

这些阈值必须与生成它们的检查点保持配对。

<a id="13-autonomous-hybrid-agent"></a>
## 13. 自主混合代理

`src/agents/bc_agent.py` 将学习到的战略策略与确定性执行相结合。

自主流程为：

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

学习模型决定战略意图。执行器处理应保持确定性的操作机制，包括移动、拾取和放置操作、浇水、喂养、照料、收获、肥料收集、工人任务分配以及法律行动约束。

执行器还保护学习策略免受无效或物理上不可能的操作影响。

自主代理的评估必须与离线验证分开进行，因为小的预测误差可能导致策略进入在专家轨迹中未良好表示的状态。

<a id="14-closed-loop-evaluation"></a>
## 14. 闭环评估

离线行为克隆指标是必要的，但不足以衡量自主性能。

在自主对战过程中：

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

这种累积误差问题解释了为何即使模型在验证指标上表现强劲，其在完整 Kaggriculture 游戏中的实际表现仍可能不佳。

因此，自主代理必须通过以下指标在多次游戏中进行基准测试：

- 最小奖励；
- 最大奖励；
- 平均奖励；
- 奖励分布；
- 总雇佣人数；
- 植物和收获数量；
- 工人空闲操作次数；
- 最终棚屋库存；
- 最终工人库存；
- 剩余作物和动物；
- 杂草及其他失败案例。

确定性启发式代理仍作为参考基准。

<a id="15-reinforcement-learning"></a>
## 15. 强化学习

在行为克隆之后，可以使用强化学习对学习策略进行微调。

主要目标仍然是 Kaggriculture 奖励：

```text
final money
```

计划序列是：

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

从零开始的纯强化学习之后可以作为对比基准使用。

<a id="16-opponent-modeling"></a>
## 16. 对手建模

对手建模被有意排除在初始学习代理之外。

首要目标是最大化基础策略的性能，而不依赖对手信息。

一旦优化版本稳定，可以维持两种变体：

```text
Base optimized agent
Base optimized agent + opponent modeling
```

这使得对手建模的效果可以独立于核心策略进行测量。

<a id="17-current-status"></a>
## 17. 当前状态

已实现并验证：

- 专家回放下载；
- 稳定团队回放存储；
- 专家身份元数据；
- 递归回放发现；
- 流式回放预处理；
- 时间对齐修正 `observation[t] -> action[t + 1]`；
- 具有107个特征的状态编码器；
- 战略决策提取器；
- 回放与状态分析；
- 逐tick学习表示；
- 雇佣回归目标；
- 联合采购捆绑目标；
- 多标签非采购发生目标；
- 数量目标；
- 归一化卖出目标；
- 集锦级训练/验证划分；
- 预编码的行为克隆数据集；
- 多头行为克隆模型；
- 未加权且掩码的训练损失；
- 检查点保存；
- 每决策评估；
- 发生频率阈值校准；
- 自主行为克隆策略集成；
- 确定性执行层；
- 学习流程的单元测试和影子测试。

最新离线模型：

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

最终决策：

基于学习的自主代理未被保留用于进一步开发。尽管离线验证指标表现良好，但自主结果的稳定性和性能均低于确定性启发式代理。

学习实现与结果被保留为实验性内容。该项目现已关闭；本文件不暗示将进行任何学习代理或启发式代理的进一步开发。
