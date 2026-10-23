[English](heuristic_agents.md) | [Français](heuristic_agents.fr.md) | [简体中文](heuristic_agents.zh-CN.md)

[项目 README](../README.zh-CN.md)

<a id="heuristic-agents"></a>
# 启发式代理

本文件补充了 [chi_agents.md](chi_agents.zh-CN.md)。

`chi_agents.md` 描述了从初始固定开局到 CHI10 的 CHI 历史谱系。本文件隔离了从 CHI3 的生产模型重新构建的后期 **启发式规划分支**，并以一系列严格顺序的启发式理念为依据进行记录：

```text
IMPLEMENTED AGENT LINEAGE

CHI3
  |
  v
heuristic_ideas_v1 -> CHI12
  |
  v
heuristic_ideas_v2 -> CHI13
  |
  v
heuristic_ideas_v3 -> CHI14

DESIGN-ONLY CONTINUATION

heuristic_ideas_v3
  |
  v
heuristic_ideas_v4
  |
  v
heuristic_ideas_final
```

设计文档：[ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md) → [ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md) → [ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md) → [ideas_v4](ideas/heuristic_ideas_v4.zh-CN.md) → [ideas_final](ideas/heuristic_ideas_final.zh-CN.md)

设计链是严格的：`v1` 是基准，`v2`、`v3` 和 `v4` 仅改进其直接前驱，而 `final` 是在完整谱系解决后形成的独立完整策略。已实现的代理谱系在 `CHI14` 处停止。该项目现已关闭：`v4` 和 `final` 仅作为设计保留，后续的实现尝试，包括 `CHI16` / `chi_final`，未产生经过验证的后继者，因此未作为源代理保留。

上述谱系是 **设计谱系**。在适用的情况下，代码复用可以更直接：设计继承和 Python 导入结构无需完全一致。

---

<a id="1-objective"></a>
## 1. 目标

该分支的目的不同于 CHI1 至 CHI10 的增量历史。

该分支从 CHI3 开始，因为 CHI3 已经提供了通用规划器所需的可复用生产描述：

- 作物与动物状态描述；
- 收获计划；
- 坐标/路径辅助工具；
- 多日生产语义。

目标是逐步用越来越明确的规划流程替代固定或局部贪婪的行为：

```text
observation
    |
    v
production state / forecast
    |
    v
economic choices
    |
    v
placements and land decisions
    |
    v
task groups with priorities and deadlines
    |
    v
routing + capacity + HIRE
    |
    v
market orders and storage constraints
    |
    v
execution
    |
    v
local replanning from observations
```

四个版本的构思文档逐步使该流程更加具体，最终文档将这些理念整合为一个完整的独立策略。在项目关闭时的快照中，已实现的代理谱系在 `CHI14` 处停止；`v4` 和 `final` 仍为设计阶段。

---

<a id="2-source-mapping"></a>
## 2. 源映射

|代理|设计源|主要角色|
| --- | --- | --- |
| `chi3.py` |CHI 历史分支|生产/状态基础|
| `chi12.py` |[ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md)|每日规划与执行模型|
| `chi13.py` |[ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md)|CHI12 中的规划土地扩展|
| `chi14.py` |[ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md)|统一的预测、路由、市场日历和终局感知规划|

无关联代理的设计阶段：

|设计|状态|主要角色|
| --- | --- | --- |
|[ideas_v4](ideas/heuristic_ideas_v4.zh-CN.md)|仅设计|在 `v3` 上构建的市场感知战术与边际经济层|
|[ideas_final](ideas/heuristic_ideas_final.zh-CN.md)|仅设计|完整的整合策略与实施合同|

---

<a id="3-base--chi3-production-model"></a>
## 3. 基础 — CHI3 生产模型

CHI3 是启发式分支的共同起点。

CHI12 明确从 CHI3 导入：

```python
ANIMAL_STATE
CROP_PRODUCTION
CROP_STATE
coordinates_to_path
distance
```

CHI12 的验证也确认在重写过程中 CHI3 保持只读状态。

该分支因此保留了CHI3的生产词汇，同时对其规划和执行进行了替换。

<a id="retained-concepts"></a>
### 保留的概念

保留的基础包括：

- 规划者使用的五个作物家族；
- 鹅、牛和羊的生产；
- 作物收获时间；
- 动物生产时间；
- 可重用的曼哈顿路径构建；
- 可观察到的作物/动物状态。

<a id="what-the-branch-changes"></a>
### 该分支的变更

新分支并不简单地延续CHI3的路线分配器。

它逐步引入了：

- 显式的任务优先级；
- 行动截止时间；
- 资源感知的路线编排；
- 计划的PICKUP和DROP；
- T+1时的市场供应情况；
- 存储保护；
- 全局工人分配；
- 土地扩展评估；
- 带时间戳的生产批次；
- 动态市场价格预测；
- 完整的可执行经济部署。

---

<a id="4-chi12--ideas_v1"></a>
# 4. CHI12 — [ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md)

`src/agents/chi12.py` 与 [ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md) 描述的基准规划器相关联。

源文件直接说明了这种关系：

```text
CHI12: CHI3 production with the daily planner described by `heuristic_ideas_v1`.
```

CHI3被视为只读的生产参考。

<a id="41-planner-structure"></a>
## 4.1 规划结构

[ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md) 将每一天组织为以下序列：

```text
read current state
    -> economic strategy
    -> generate daily tasks
    -> choose placements
    -> prioritize tasks
    -> build task groups
    -> add logistics
    -> build candidate routes
    -> calculate capacity / HIRE
    -> finalize routes
    -> execute and replan
```

这成为该分支的第一个显式每日规划器。

<a id="42-task-generation"></a>
## 4.2 任务生成

CHI12将观察到的农场转换为有序的本地格子任务包。

示例包括：

```text
crop:
    FERTILIZE
    WATER
    HARVEST
    DIG
    PLANT
    WATER

animal:
    HARVEST
    COLLECT_FERTILIZER
    FEED
    CARE
```

每个任务携带：

- 一个优先级；
- 一个截止时间；
- 一个格子位置；
- 一个估计价值；
- 在该格子上必须执行的有序操作。

实现的优先级类别为：

```text
CRITIQUE
PRODUCTION
RENDEMENT
PREPARATION
SECONDAIRE
```

这确保了生存关键和截止时间敏感的工作优先于可选的产量或清理工作。

<a id="43-placement"></a>
## 4.3 布置

`choose_placements` 保留了已有的生产内容，并在可用格子上重构CHI3的投资组合。

布置成本考虑：

- 预期的访问次数；
- 到最近畜舍的访问距离；
- 与相似生产的邻近程度；
- 结构兼容性。

在此阶段，规划器不进行扩展推测：CHI3的投资组合完全适合初始的西北象限。

<a id="44-explicit-logistics"></a>
## 4.4 显式物流

`v1` 的设计将库存移动作为计划的一部分，而非事后考虑。

CHI12计算：

- 用于饲料的所需小麦；
- 用于施肥的所需肥料；
- 在放置前需PICKUP的动物数量；
- 由计划中的PLANT操作所需的种子数量；
- T+1时的采购可用性；
- 返回畜舍的路径；
- 最终的DROP操作。

`compile_route` 在行动或最终返回错过可操作截止时间时拒绝该路线。

<a id="45-storage-protection"></a>
## 4.5 存储保护

`protect_storage` 按时间顺序模拟：

```text
PICKUP
DROP
SELL
BUY_PRODUCT
BUY_ANIMAL
```

在接受路线之前。

如果仓库无法接收其货物，返回可能会被延迟，但规划器不会仅仅为了将产出保留在仓库之外而推迟收获。

<a id="46-hire-and-routing"></a>
## 4.6 HIRE 与路线规划

首个实现版本采用贪婪式路线插入。

对于每个工人，规划器：

1. 选择一个候选任务；
2. 重新编译完整路线；
3. 验证截止时间；
4. 验证物流；
5. 验证存储；
6. 仅当完整路线仍可执行时才接受插入。

如果现有劳动力无法覆盖所需工作，规划器将使用斐波那契 HIRE 成本和 T+1 工人可用性规则评估额外的农场工人。

<a id="47-observation-checked-execution"></a>
## 4.7 观察验证执行

执行在一天内是持久的。

本地重新规划可能由以下情况触发：

- 工人位置的意外变化；
- 被拒绝的采购；
- 未找到雇佣的工人；
- 意外出现的杂草；
- 生产格子的变更；
- 产量不匹配；
- 新开的商店；
- 价格发生足够大的变化。

在可能的情况下，保留有效路线，而不是重建整个计划。

---

<a id="5-chi12-validation"></a>
## 5. CHI12 验证

为 CHI12 提供了专门的 Codex 验证报告。

<a id="engine-behavior-verified"></a>
### 引擎行为已验证

验证确认了规划器使用的多个引擎约束条件：

- 工人行动在市场订单之前执行；
- 在 T 时刻发出的采购和 HIRE 在 T+1 时刻变得可用；
- 同一时间步的 DROP 可以被出售；
- 同一时间步的销售不会在该 DROP 之前释放仓库空间；
- 在默认的 720 步游戏中，最后一个可执行步骤是第 718 步；
- 因此，最终的明确返回和清算必须在游戏结束前完成。

<a id="tests"></a>
### 测试

CHI12 特定测试套件包含 **28 个测试**。

验证时完整的测试套件包含 **68 个通过的测试**。

这些案例涵盖以下内容：

- PLANT 后接必须的 WATER；
- 动物 FEED 资源需求；
- 多个 FERTILIZE 行动；
- 所有三种动物物种的放置；
- FERTILIZE/WATER/HARVEST 的执行顺序；
- 番茄和草莓的替换；
- 返回和 DROP 的成本；
- 杂草；
- HIRE 和 BUY 在 T+1 时刻的可用性；
- 市场订单限制；
- 满仓和同时返回的情况；
- 最终清算；
- 重新规划期间路线的保留；
- 被拒绝的采购/HIRE；
- 生产变化的意外情况。

<a id="chi3-comparison"></a>
### CHI3 对比

保留的基准使用座位0到19，每个代理进行40场比赛。

|代理|游戏|最小值|最大值|平均值|中位数|无效|
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|CHI3| 40 | 0 | 0 | 0 | 0 | 0 |
|CHI12| 40 | 55,033 | 62,953 | 59,597.25 | 60,306 | 0 |

该比较有一个重要局限性：测试代码中CHI3不会发出卖出订单。因此，结果验证了CHI12的完整可玩/经济循环，但**并未**单独验证新路由算法的价值。

---

<a id="6-chi13--ideas_v2"></a>
# 6. CHI13 — [ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md)

`src/agents/chi13.py`是与[ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md)中严格`v2`增量相关的CHI12的演进版本。

其源代码将目标总结为：

```text
CHI13: targeted CHI12 evolution with global routing and planned land use.
```

实现复用了CHI12已测试的面向引擎的原语。

<a id="61-main-design-change"></a>
## 6.1 主要设计变更

[ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md)在正常每日任务流水线之前增加了一个缺失的顶层经济决策：

```text
DECIDER_ACHAT_TERRAIN()
```

土地不再仅仅因为农场已满而被购买。

扩张必须对应一个真实的额外生产需求，该需求无法在已解锁的土地上及时满足。

<a id="62-land-order-model"></a>
## 6.2 土地订单模型

实现遵循了法律扩张顺序：

```text
NW -> NE -> SW -> SE
```

成本为：

```text
1000
2000
4000
```

规划器不会发明在任意象限之间的选择。它决定是否购买下一个合法象限以及如何利用它。

<a id="63-concrete-expansion-plan"></a>
## 6.3 具体扩张计划

在接受一个BUY_LAND之前，CHI13会估算：

- 剩余盈利的生产量；
- 新象限中的方格位置；
- 土地成本；
- 额外的雇佣成本；
- 当前已承诺的市场成本；
- 路线容量；
- 安装是否仍能在截止前完成。

因此，一个候选扩张必须同时满足：

```text
affordable
and
routable
and
profitable
```

新象限的布局仅在土地购买确认后才被保留。

<a id="64-global-worker-assignment"></a>
## 6.4 全局工人分配

CHI12是按工人逐个构建路线的。

CHI13改变了分配器，使得一个任务首先在所有现有工人之间进行测试。所选插入方式在可行工人中最小化增量路线成本。

预期的顺序变为：

```text
existing workers first
    -> fit as many required groups as possible
    -> only then consider HIRE
```

这直接实现了[ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md)的目标，即在已有工人能够吸收工作时避免雇佣。

<a id="65-centralized-market-scheduling"></a>
## 6.5 集中式市场调度

CHI13增加了一个最终的市场订单整合步骤。

订单被：

- 合并；
- 去重；
- 限制为每tick配置的市场订单数量；
- 在需要时延至后续tick。

这使得市场槽位约束由单一所有者持有，而不是让独立的规划模块相互竞争相同的槽位。

<a id="66-execution-relationship"></a>
## 6.6 执行关系

CHI13保持了CHI12的执行模型：

- 持久路线；
- 来自观察的确认；
- BUY/HIRE失败的检测；
- 选择性路径无效化；
- 局部重新规划；
- 存储保护。

因此主要变化并非引入新的动作执行器，而是在测试的CHI12原语之上增加了一个更强的规划器。

---

<a id="7-chi14--ideas_v3"></a>
# 7. CHI14 — [ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md)

`src/agents/chi14.py` 与 [ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md) 中的严格 `v3` 偏差相关联。

其源描述版本为：

```text
CHI14: CHI13 routing with dated marginal crop economics.
```

因此CHI14保留了CHI13的路由/执行层，并专注于生产与扩张的经济价值。

<a id="71-single-forecast-oriented-architecture"></a>
## 7.1 单一预测导向架构

[ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md) 将早期的长规划简化为六个紧密连接的模块：

```text
forecast
    -> economy / placement / expansion
    -> task groups and dependencies
    -> routing / capacity / HIRE
    -> stock and market calendar
    -> execution / local replanning / endgame
```

目标是让规划器在整个过程中使用同一时间点的状态，而不是让路由、经济和市场代码各自维持独立的近似值。

<a id="72-exact-market-price-projection"></a>
## 7.2 精确市场价格预测

CHI14 使用 Kaggriculture 引擎的定价函数来预测交易价格。

`project_market` 模拟了：

- 逐单位的 SELL 定价；
- BUY_PRODUCT 定价；
- 当前市场库存；
- 已开启商店的消费；
- 城镇中心消费；
- 按模拟步长（tick）排序的交易。

规划器首先验证本地定价函数能否复现当前观察到的报价，才信任其预测结果。

<a id="73-dated-production-lots"></a>
## 7.3 时序生产批次

不再将作物视为单一静态数值，CHI14 创建了具有时间戳的可售批次。

对于每项生产，它追踪足够信息以估算：

```text
harvest day
    -> earliest feasible return
    -> DROP
    -> SELL tick
```

现有种植设施与计划中的种植设施分开处理，以避免生产被重复计算。

在最终结束前无法出售的产出不产生任何预测收入。

<a id="74-marginal-contribution"></a>
## 7.4 边际贡献

核心决策变为两个完整投资组合之间的比较：

```text
reference layout
versus
reference layout + one candidate production
```

对于候选方案，CHI14 重新计算：

- 预测收入；
- 种子成本；
- 雇佣成本；
- 路线可行性；
- 适用情况下的土地成本。

最终结果是一个边际贡献，而非固定作物评分。

<a id="75-prudent-scenario"></a>
## 7.5 谨慎情景

CHI14 评估两种情况：

- 一个中心预测；
- 一个更保守的预测，包含可见对手作物供应。

因此，规划器可使用：

```text
contribution_prudent
```

以此判断候选方案是否仍值得采用。

这里仍只使用可见的对手产出，不会虚构对手的隐藏库存。

<a id="76-marginal-land-expansion"></a>
## 7.6 边际土地扩张

土地评估现在增量式地扩展所提议的新布局。

对于每个候选地块：

1. 测试每种作物；
2. 计算边际贡献；
3. 重建 CHI13 路线计划；
4. 验证该地块是否实际被分配；
5. 使用新路线重新计算贡献；
6. 仅在谨慎情景下的边际贡献仍为正时，才保留该新增地块。

完整的土地成本随后一次性收取，计入候选扩展前缀。


---

<a id="8-design-v4--ideas_v4"></a>
# 8. 设计 v4 — [ideas_v4](ideas/heuristic_ideas_v4.zh-CN.md)

`v4` 没有关联的代理。它严格遵循 CHI14 / `v3` 实现的设计所形成的增量设计。

`v4` 并未从零开始重新定义规划器。它继承了完整的 `v3` 设计，并在其统一的预测、路由、市场日历、本地维修和终局模型之上，增加了一个具有市场感知的战术层。

<a id="81-main-design-change"></a>
## 8.1 主要设计变更

核心新增链为：

```text
shop demand
    -> own + opponent supply
    -> future market inventory
    -> future price
    -> marginal value
    -> production / hold / sell decisions
```

因此，该设计不仅评估工作是否可行，还评估下一个单位、方块、工人、土地购买或出售是否仍能提升预期价值。

<a id="82-labor-and-spatial-constraints"></a>
## 8.2 劳动力与空间约束

`v4` 设计增加了：

- 战略工人上限 `MAX_WORKERS = 14`；
- 在另一次雇佣前进行边际价值测试；
- 中心附近动物放置；
- 一个中央 `2 x 2` 预留，用于长期作物；
- 具有时间感知的土地-经济比较。

这些规则位于从 `v3` 继承的路由与可行性机制之上。

<a id="83-market-and-opponent-aware-economics"></a>
## 8.3 市场与对手感知的经济体系

`v4` 增加了关于以下内容的明确推理：

- 对手可见的生产情况与时间安排；
- 未来市场库存与价格；
- 边际生产价值；
- 出售与持有价值对比；
- 售价影响；
- 现金流紧迫性；
- 产品级库存行为。

`v4` 中的历史公式和固定日程在最终整合设计未明确推广前仍属于实验性内容。

<a id="84-tactical-land-policy"></a>
## 8.4 战术土地政策

`v4` 增加了优先土地时间分支和明确的运营现金流底线，同时保留了继承的可行性与盈利能力门控机制。

这些战术规则的精确活跃解释在 [ideas_final](ideas/heuristic_ideas_final.zh-CN.md) 中得到明确。

---

<a id="9-final-consolidated-design--ideas_final"></a>
# 9. 最终整合设计 — [ideas_final](ideas/heuristic_ideas_final.zh-CN.md)

`final` 也没有关联的代理。它是一个文档/设计快照，而非已实现的 CHI 版本。该项目在未验证 `CHI16` / `chi_final` 后继版本的情况下关闭。

与 `v2`、`v3` 和 `v4` 不同，最终文档**并非增量变更**。它是完整设计链应用完毕、矛盾已解决后获得的独立快照。

<a id="91-canonical-final-design"></a>
## 9.1 标准最终设计

最终策略在一处明确定义了：

- 已验证的机械约束；
- 一个共享的物理/经济预测；
- 农场侧供应与全球市场库存的分离；
- `LOW / BASE / HIGH` 对手情景；
- 条件性资产保留与放弃；
- 具有依赖感知的 `TaskGroup` 规划；
- 精确的资源、方块时间、现金、存储、工人时间以及市场时段预留；
- `MAX_WORKERS = 14`;
- 活跃放置几何结构和固定开局规则；
- 主动计划的土地扩张加上经济上的非计划扩张；
- 边际产量与精确销售数量的搜索；
- 局部维修而非整体重新规划；
- 逆向终局现金结算规划；
- 一份验证与实施合同。

<a id="92-historical-ideas-remain-traceable"></a>
## 9.2 历史思想仍可追溯

曾被考虑但现已不活跃的思想被保留在最终文档中作为基准性历史记录。版本化文件有助于理解每个变更如何进入设计脉络，而`final`是任何未来实施的完整解决快照。

---

<a id="10-evolution-of-the-heuristic-branch"></a>
# 10. 启发式分支的演进

这一演进是一条严格的设计算法链：每个版本仅回答一个额外的规划问题，且不以旧版本作为并行父版本使用。

<a id="chi12--v1--can-the-work-actually-be-executed"></a>
## CHI12 / v1 — 工作是否真的可以执行？

[ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md) 建立了完整的每日基准：

```text
What must be done?
When must it be done?
What resources must be carried?
Can a worker complete the route and return?
Can the shed accept the result?
```

<a id="chi13--v2--should-the-farm-expand"></a>
## CHI13 / v2 — 农场是否应扩张？

[ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md) 仅修改自`v1`继承的土地决策：

```text
Is additional profitable production blocked by land?
What is the best no-purchase plan?
Can the new quadrant be exploited in time?
Does the complete expansion plan repay its cost?
```

<a id="chi14--v3--can-every-subsystem-reason-from-the-same-plan"></a>
## CHI14 / v3 — 每个子系统是否都能基于同一计划进行推理？

[ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md) 重新组织了自继承的规划器围绕：

```text
one forecast
-> stable TaskGroups
-> integrated routing / logistics / HIRE
-> one market calendar
-> local repair
-> endgame-aware feasibility
```

<a id="v4--how-should-feasible-work-react-to-the-market-and-opponent"></a>
## v4 — 可行工作应如何响应市场与对手？

[ideas_v4](ideas/heuristic_ideas_v4.zh-CN.md) 增加了：

```text
shop demand
-> own/opponent supply
-> future market inventory
-> expected price
-> marginal production / labor / sell value
```

<a id="final--what-is-the-complete-resolved-strategy"></a>
## 最终 — 完整的解决策略是什么？

[ideas_final](ideas/heuristic_ideas_final.zh-CN.md) 整合了整个链条，解决了历史启发式中的冲突，将活跃规则与仅作基准的思想区分开来，并作为归档的独立设计参考保持存在。在项目关闭前，未保留任何该阶段的已验证实现。

---

<a id="11-architecture-summary"></a>
# 11. 架构概要

|版本|规划|路径规划 / 劳动力|经济|扩张|
| --- | --- | --- | --- | --- |
|CHI3|动态产量维护|动态每日路径规划|最小|无|
|CHI12 / v1|优先级 + 期限 + 资源包|可执行路径 + HIRE|基础经济决策|无隐含的投机性扩张|
|CHI13 / v2|v1 + 显式土地决策|继承的规划器，经扩张验证|无土地对比土地计划|预留、观察并经经济验证的扩张|
|CHI14 / v3|共享预测 + 稳定的`TaskGroup`|集成分配、物流和HIRE|一个经验证的市场日历|扩张消耗共享计划|
|v4（设计阶段仅）|v3 + 战术市场层|工人上限 + 边际劳动力价值|对手/价格/边际售出与生产逻辑|战术时间优先级 + 现金底线|
|最终（设计阶段仅）|完整解决策略|精确预留 + 局部修复|最终现金目标 + 精确边际搜索|活跃计划 + 经济未安排的门|

---

<a id="12-relationship-with-chi_agentsmd"></a>
# 12. 与 `chi_agents.md` 的关系

两份文件故意描述了不同的历史记录。

`chi_agents.md` 仍然是原始 CHI 进展的记录：

```text
chi.py -> CHI1 -> ... -> CHI10
```

本文件记录了独立的启发式规划器设计脉络：

```text
CHI3
  -> heuristic_ideas_v1    -> CHI12
  -> heuristic_ideas_v2    -> CHI13
  -> heuristic_ideas_v3    -> CHI14
  -> heuristic_ideas_v4    -> design only
  -> heuristic_ideas_final -> design only
```

标准设计链：

[ideas_v1](ideas/heuristic_ideas_v1.zh-CN.md) → [ideas_v2](ideas/heuristic_ideas_v2.zh-CN.md) → [ideas_v3](ideas/heuristic_ideas_v3.zh-CN.md) → [ideas_v4](ideas/heuristic_ideas_v4.zh-CN.md) → [ideas_final](ideas/heuristic_ideas_final.zh-CN.md)

因此 CHI3 在两份文件中出现的原因不同：

- 在 `chi_agents.md` 中，它是第三次历史 CHI 迭代；
- 在 `heuristic_agents.md` 中，它是可重用的生产/状态基础，后来的启发式规划器正是基于此重建的。


这种分离保持了仓库历史的可读性，同时不会将 CHI12 之后的版本直接视为 CHI10 的连续历史继承者。
