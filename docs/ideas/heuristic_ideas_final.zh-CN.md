[English](heuristic_ideas_final.md) | [Français](heuristic_ideas_final.fr.md) | [简体中文](heuristic_ideas_final.zh-CN.md)

[项目 README](../../README.zh-CN.md)

<a id="heuristic-ideas--final-consolidated-strategy"></a>
# 启发式想法 — 最终整合策略

[← 上一设计变更](heuristic_ideas_v4.zh-CN.md) · 最终整合版本

> **系列约定**
>
> `heuristic_ideas_final.md` 并非另一个变更。它是应用 `v1 -> v2 -> v3 -> v4` 并解决剩余矛盾后获得的完整独立战略快照。它是启发式分支的权威独立设计参考。

<a id="identity"></a>
## 身份

|字段|值|
| --- | --- |
|版本| `final` |
|关联代理|无 — 仅设计用途|
|角色|完整独立策略快照|
|基于|[`v4`](heuristic_ideas_v4.zh-CN.md)，且已完全解析 `v1 -> v4` 的继承关系|
|权威状态|**完整独立策略参考**|
|实施状态|仅设计用途 — 项目关闭，未验证专用代理|

<a id="status"></a>
## 状态

本文件整合了 `heuristic_ideas_v1` 至 `v4` 的内容，消除了重复想法，解决了矛盾，并将已验证的机制、活跃的战略规则、经济规则以及仅用于基准的历史启发式方法区分开来。

它是已解决的启发式策略的**单一完整战略设计参考**。该项目未验证该完整设计的实施，因此未作为实际行为呈现，而是保留用于可追溯性。下文定义的固定开局、工人上限、土地购买计划、土地订单、三角布局以及中央 `2 x 2` 限制属于设计基准，而非仅用于基准的先验假设。

明确分类为仅用于基准的历史公式和带日期的微观计划，默认状态下保持禁用。

---

<a id="0-rule-precedence"></a>
## 0. 规则优先级

当两个规则发生冲突时，按以下顺序应用：

1. **游戏机制约束** — 必须永远不得违反。
2. **可行性 / 安全约束** — 资源、生存、截止日期、路径、存储、市场槽位、可执行现金以及土地购买的现金下限。
3. **活跃战略规则** — 固定开局、战略工人上限、计划中的土地购买、固定扩张顺序、三角布局几何结构以及中央 `2 x 2` 限制。
4. **已接受计划的保留** — 保护仍具价值的资产或行动。
5. **边际经济价值** — 选择最佳的增量非强制性行动。
6. **路径 / 空间效率** — 减少工人使用和移动。
7. **仅用于基准的历史启发式** — 除非在孤立实验中明确启用，否则默认禁用。

活跃战略规则是刻意的承诺。它们不会被通用边际价值模型降级为可选先验。它们仍需符合机制和可行性要求。

---

<a id="1-verified-mechanical-baseline"></a>
# 1. 已验证的机制基准

规划者必须明确建模以下事实。

<a id="11-survival-and-production"></a>
## 1.1 生存与生产

- 植物在连续两天未浇水后会变成杂草。
- 新种植的作物必须在种植当天浇水。
- 一只动物在连续两天没有小麦后逃脱。
- 新放置的动物可能存活其第一天不进食，但正常的规划仍应考虑下一个生存截止时间。
- 存储在方格上的动物产品上限为`max_held`。
- 每只存活的动物每天可提供一份肥料；未收集的肥料不会累积。
- `CARE`行为在当前参考测试中存在已观察到的异常，因此仅基于理论`pending_care_bonus`模型进行的激进护理跳过在行为完全解释前是不安全的。

<a id="12-storage"></a>
## 1.2 存储

```text
SHED_CAPACITY = 100 non-seed items
```

种子不会消耗释放容量。

计划下落的精确溢出条件是：

```text
ProjectedShedAfterDrop > 100
```

可选地使用一个一格的安全缓冲区：

```text
SafetyTarget = 99
```

但`99`是政策目标，而非实际容量。

<a id="13-market-actions"></a>
## 1.3 市场行为

- 每个模拟周期最多可提交10条市场订单。
- 超出限制的订单将被环境静默丢弃。
- `BUY`、`SELL`、`HIRE`和`BUY_LAND`因此共享一个经过验证的市场日历。
- 市场订单的执行顺序很重要。
- 玩家订单在执行过程中会与对手订单及价格曲线相互作用。

<a id="14-land"></a>
## 1.4 土地

扩张成本是：

```text
1st expansion = 1000
2nd expansion = 2000
3rd expansion = 4000
```

扩张订单由游戏固定，策略不得对其进行优化或重新排列：

```text
1st expansion -> NE
2nd expansion -> SW
3rd expansion -> SE
```

购买的区域在购买被观察确认后才会提供实际方格。

---

<a id="15-workers"></a>
## 1.5 工人

农工是为当前日雇佣的，雇佣成本根据每日斐波那契序列递增。雇佣成本序列在新一天开始时重置。

游戏引擎的工人上限与策略的工人上限是两个独立的概念。

基础策略使用以下**主动硬性战略上限**：

```text
MAX_WORKERS = 14
```

规划器绝不能接受任何会导致受控劳动力超过14的`HIRE`，即使第15名工人预计边际价值为正。这是策略规则，而非关于引擎最大可能工人数量的声明。

---

<a id="16-shop-demand"></a>
## 1.6 商店需求

商店构成会改变需求，应明确表示。多个实例会叠加其需求。

每个商店实例对普通需求商品的需求约为每天 6 单位；×2 商店对其加倍需求商品的需求约为每天 12 单位。

---

<a id="2-planner-architecture"></a>
# 2. 规划架构

使用一个一致的规划状态，而非多个独立的近似值。

```text
OBSERVE REAL STATE
    -> UPDATE SHARED FORECAST
    -> UPDATE MARKET / OPPONENT SCENARIOS
    -> GENERATE ECONOMIC CANDIDATES
    -> GENERATE DEPENDENCY-AWARE TASK GROUPS
    -> ASSIGN ROUTES + LOGISTICS + OPTIONAL HIRES
    -> VALIDATE CASH / STOCK / MARKET CALENDAR
    -> EXECUTE
    -> LOCAL REPAIR WHEN MATERIAL STATE CHANGES
```

每个子系统读取相同的预测和预订信息。

---

<a id="3-shared-forecast"></a>
# 3. 共享预测

维护一个从当前周期开始到游戏结束的导出物理/经济预测。

至少跟踪：

- 作物年龄、水分状态、肥料状态、下一次生产与衰减；
- 动物饲料、护理、产品持有、下一次生产与饱和风险；
- 当前及预留的种子/产品/动物/肥料；
- 工人位置、可用性、路线后缀及携带库存；
- 抛售库存并处理按时间索引的流入下降；
- 地块占用与未来释放情况；
- 现金及已承诺支出；
- 商店需求；
- 预期自身市场订单；
- 预期对手市场行为；
- 市场库存及预期价格路径；
- 游戏结束时现金结算的可行性。

在发生变更后，仅当可能时，更新受影响的预测组件。

---

<a id="4-separate-farm-production-from-market-inventory"></a>
# 4. 将农场生产与市场库存分开

这是被综合经济模型保留的关键修正。

作物变为可收获，并**不会**直接增加全球市场库存。生产首先变为农场/工人/棚屋库存。全球市场库存仅在单位实际进入或离开市场或被消耗时才会发生变化。

使用两个独立的预测。

<a id="41-farm-side-supply-forecast"></a>
## 4.1 农场侧供应预测

```text
FarmOutput(t) = expected harvest / animal production available to us at t
```

这决定了我们之后可能持有的、消耗的或出售的量。

<a id="42-market-inventory-forecast"></a>
## 4.2 市场库存预测

```text
MarketInventory(t + 1) =
    MarketInventory(t)
    + ExpectedOurSales(t)
    + ExpectedOpponentSales(t)
    - ExpectedOurPurchases(t)
    - ExpectedOpponentPurchases(t)
    - ShopConsumption(t)
```

除非当前环境/规则明确表示，否则不包含其他任何消费来源。

然后：

```text
ExpectedPrice(t) = PriceFunction(ExpectedMarketInventory(t))
```

这防止了规划器将未售出的农产品价格定为已涌入市场的假象。

---

<a id="5-opponent-model-scenarios-not-false-precision"></a>
# 5. 对手模型：情景分析，而非虚假精确度

跟踪可见对手能力：

- 已种植作物类型/数量/年龄；
- 动物类型/数量；
- 预期成熟与生产日期；
- 可见的收获事件；
- 与对手买卖行为一致的观察到的市场库存变化。

维持三个有界情景，而不自行发明概率权重：

```text
LOW opponent supply
BASE opponent supply
HIGH opponent supply
```

基准情景：

- 使用 `BASE` 作为预期值排序的中心情景；
- 使用 `LOW` 和 `HIGH` 来暴露敏感性与市场崩盘风险；
- 除非后续配置并基准化了明确的情景权重，否则不得计算任意加权平均值；
- 不得自行发明一个数值为 `RiskPenalty` 的系数。

当两个选择具有相同的 `BASE` 值时，在应用全局平局规则前，优先选择在 `LOW/HIGH` 情景下仍可行且更稳健的那个。

已确认的观察结果获得完整置信度。尚未揭示的未来商店或对手行为必须保持情景化，而非被转化为虚假精确度。

---

<a id="6-economic-acceptance-rule"></a>
# 6. 经济可接受规则

一个非强制性的经济候选方案仅在其**完整的增量现金流出链**可行且有价值时才被接受。本文件中定义的主动战略承诺由其各自的门控机制处理。

对于候选方案 `i`：

```text
IncrementalValue_i =
    IncrementalExpectedSalesRevenue
    - IncrementalDirectCashCost
    - IncrementalFeedOpportunityCost
    - IncrementalHireCost
    - IncrementalHolding / StorageCost
    - IncrementalRoutingOpportunityCost
```

仅当其代表真实的未来选项时，才可添加可选战略条款：

```text
+ LayoutOptionValue
+ DemandHedgeValue
+ ResourceSecurityValue
```

接受门控：

```text
IncrementalValue_i > 0
AND all feasibility constraints pass
AND cash-out can occur before the game ends
```

如果候选方案的绝对值为负，仅因其比率得分高而接受是不成立的。

---

<a id="7-land-scarcity-and-land-time-value"></a>
# 7. 土地稀缺性与土地时间价值

土地时间效率仅在土地实际上稀缺时才有用。

对于在土地压力下筛选可行的正价值候选者：

```text
LandEfficiency_i =
    IncrementalValue_i
    / EffectiveOccupiedLandTime_i
```

不要将此比率作为普遍目标。当土地不构成约束时，绝对增量价值更为重要。

区分：

```text
PhysicalOccupancy = real map tiles reserved over time
EconomicEffectiveLand = optional comparison metric
```

例如，历史`5/3`禽类等效土地价值可能仍是一种实验性的经济权重，但它绝不能替代实际地块的预留。

---

<a id="8-labor-economics"></a>
# 8. 劳动经济学

<a id="81-feasibility-first"></a>
## 8.1 可行性优先

现有员工首先被分配。只有当无法以经济方式完成其他被接受的工作时，才会考虑新员工的聘用。

<a id="82-correct-marginal-hire-test"></a>
## 8.2 正确的边际雇佣测试

设：

```text
ProfitWithoutHire = best feasible plan with A workers
ProfitWithHire    = best feasible plan with A + 1 workers
MarginalWorkerValue = ProfitWithHire - ProfitWithoutHire
```

仅在满足以下条件时才聘用：

```text
MarginalWorkerValue > NextHireCost
```

并且该新员工实际上使相关工作变得可行。

<a id="83-labor-shadow-cost"></a>
## 8.3 劳动影子成本

不要使用：

```text
Va * required_actions
```

当`Va`已经是另一个完整员工的总价值时；这会混合单位并可能导致严重重复计算劳动成本。

相反，应从稀缺劳动力容量出发估算每tick/每动作的机会成本：

```text
LaborShadowCostPerTick ~=
    value of the best displaced task per scarce worker tick
```

或使用包含候选方案的最佳调度与不包含候选方案的最佳调度之间的精确差值。

当差值足够小且可计算时，优先采用精确调度差值。

<a id="84-active-worker-cap"></a>
## 8.4 活跃员工上限

```text
MAX_WORKERS = 14
```

此上限默认开启，并属于基础策略的一部分。

招聘仍需具备正的边际价值和实际调度可行性，但即使是一项盈利性招聘，如果会导致员工数量达到15以上，也将被拒绝。

---

<a id="9-asset-preservation-is-conditional-not-absolute"></a>
# 9. 资产保全具有条件性，而非绝对性

生存优先级仅适用于被接受计划仍打算保留的资产。

定义：

```text
KeepAsset(asset) = remaining expected value of preserving asset > abandonment alternative
```

然后：

- 生存用途的 `WATER` 仅在植物值得保留时才属于 `CRITICAL` 优先级；
- 生存用途的 `FEED` 仅在动物值得保留时才属于 `CRITICAL` 优先级；
- 延迟肥料/护理/喂养且无可兑现未来效果的应被移除；
- 一个现有的沉没成本资产如果其剩余运营价值为负，则可以被放弃。

这解决了早期游戏生存优先级与后期游戏清算之间的矛盾。

---

<a id="10-taskgroup-model"></a>
# 10. 任务组模型

直接生成稳定的、具有依赖感知的 `TaskGroup` 对象。

```text
TaskGroup:
    id
    position
    ordered_actions[]
    priority
    deadline
    required_resources
    expected_incremental_value
    dependencies
    assigned_worker_or_none
```

稳定的ID必须在生成运行两次且材料状态未改变时，防止重复规划。

先决条件继承其依赖任务的紧迫性。

---

<a id="11-action-priority"></a>
# 11. 行动优先级

使用条件优先级层级。

<a id="critical"></a>
## CRITICAL

只有当基础资产/行动仍属于已接受的计划时：

- 生存浇水；
- 生存喂养；
- 在衰败/饱和/不可逆损失之前收获；
- 必须在种植日进行浇水；
- 在必须的流入下降之前必须释放存储；
- 在硬截止日期之前必须依赖市场；

<a id="production"></a>
## 生产

- 有盈利计划的收获；
- 必需的植物/建造/放置；
- 必需的生产性饲料；
- 必需的资源拾取/购买。

<a id="yield"></a>
## 产量

- 盈利的肥料；
- 盈利的养护；
- 增产的水。

<a id="preparation"></a>
## 准备阶段

- 挖掘阻隔以接受生产；
- 安装用于未来接受的生产。

<a id="secondary"></a>
## 次要任务

- 非紧急的肥料收集；
- 可选的杂草清除；
- 可选的本地路线作业。

---

<a id="12-action-ordering-use-dependencies-not-one-universal-sequence"></a>
# 12. 行动排序：使用依赖关系，而非单一通用序列

避免使用如以下的通用动物序列：

```text
FEED -> HARVEST -> CARE -> COLLECT
```

每次访问时。

相反，仅强制执行当前状态下真正重要的依赖关系。

示例：

- `FEED -> CARE` 当养护需要当天喂养动物时；
- `HARVEST` 在下一个生产事件之前，当 `max_held` 饱和会导致产量损失时；
- `HARVEST` 在游戏末期返售/销售截止日期之前；
- `COLLECT_FERTILIZER` 仅当其价值超过行动/旅行的机会成本时；
- 对于作物，`FERTILIZE -> WATER` 当肥料必须在该浇水事件前已激活，才能提升产量时；
- `WATER -> HARVEST` 仅当当天浇水改变可收获的产量时。

这避免了单纯为了遵守历史固定顺序而消耗行动。

---

<a id="13-animal-care-policy"></a>
# 13. 动物养护政策

由于当前参考测试报告了一个尚未解决的养护异常，采用保守的养护逻辑。

养护允许的情况是：

```text
expected additional saleable yield
    * expected marginal sale value
>
CARE action/travel opportunity cost
```

但不要仅仅因为简化版 `pending_care_bonus` 计算预测无收益，就激进地跳过养护。

候选养护计划如 `skip T5` 或 `skip T5-T7` 在生产异常得到解释并可靠重现之前，仅作为基准保留。

---

<a id="14-animal-harvest-policy"></a>
# 14. 动物收获政策

当至少满足一个条件时，立即收获动物产出：

```text
1. saturation risk before the next opportunity to harvest
2. planned near-term sale requires the output
3. an existing route passes close enough that marginal labor/travel cost is low
4. endgame requires collection now to allow return + DROP + SELL in time
```

否则推迟收获以节省劳力。

末期规则：

- 如果最终可用的动物产出必须在最后可玩日出售，则提前安排收获——可能提前到前一天——以确保返程、下落和销售。

---

<a id="15-placement-policy"></a>
# 15. 安置政策

安置首先遵循硬性几何规则，然后使用经济/路径优先级进行折中。不要发明加权安置系数。

<a id="151-mandatory-center-facing-5-x-5-triangular-animal-layout"></a>
## 15.1 必须朝中心的 `5 x 5` 三角形动物布局

以下行从北到南书写，列从西到东书写。

`1` = 三角形布局允许的动物安置单元。   `*` = 不是动物安置单元。

对于西北象限，使用精确：

```text
NW
* * * * 1
* * * 1 1
* * 1 1 1
* 1 1 1 1
1 1 1 1 1
```

对其他象限应用精确对称性：

```text
NE
1 * * * *
1 1 * * *
1 1 1 * *
1 1 1 1 *
1 1 1 1 1
```

```text
SW
1 1 1 1 1
* 1 1 1 1
* * 1 1 1
* * * 1 1
* * * * 1
```

```text
SE
1 1 1 1 1
1 1 1 1 *
1 1 1 * *
1 1 * * *
1 * * * *
```

动物必须安置在对应朝中心三角形的 `1` 单元内。当存在多个符合条件的单元时，使用全局优先级顺序进行填充或选择，而不是任意加权评分。

<a id="152-central-2-x-2-long-term-crop-exclusion"></a>
## 15.2 中心 `2 x 2` 长期作物排除

中心 `2 x 2` 高连接区域对长期作物存在**绝对基础禁止**：

```text
if tile in CENTRAL_2X2 and crop is LONG_TERM_CROP:
    placement is forbidden
```

这是一个活跃的战略布局约束，而不是机会成本偏好。短期生产及非农作物用途仍由其自身的可行性规则所支配。实施过程必须使用项目明确设定的长期农作物分类，不得在不声明的情况下擅自设定持续时间阈值。

<a id="153-placement-tie-break-without-arbitrary-weights"></a>
## 15.3 无任意权重的布局优先级排序

在满足硬性几何结构和可行性条件后，按以下顺序进行比较：

```text
1. higher expected economic value
2. smaller deadline slack
3. fewer worker/labor ticks required
4. less travel
```

若仍存在并列，则采用一个稳定的确定性坐标顺序，以确保重复规划产生相同结果。

---

<a id="16-land-purchase"></a>
# 16. 土地购买

土地购买有两种模式：**计划性战略扩张**和**非计划性经济扩张**。

<a id="161-scheduled-strategic-expansion"></a>
## 16.1 计划性战略扩张

基准时间表是活跃的，并采用游戏定义的顺序`NE -> SW -> SE`。此处`Tn`表示**第n天**；应在该天最早合法的市场时间点提交购买请求。

```text
T4:
    BUY NE

AT T7, once the first two shops are known:

    IF the first two shops contain animal demand:
        T7  -> BUY SW
        T12 -> BUY SE

    ELSE:
        T9 -> BUY SW
        no mandatory T12 SE purchase
```

因此，首个`NE`的购买行为与前两个商店分支无关。该分支仅改变`SW`的时间点，以及`SE`在`T12`时是否为强制性要求。

每一次计划性购买的执行必须满足以下全部条件：

```text
purchase is legal and executable
AND required market slot is available
AND cash-floor / operating-reserve constraint passes
```

使用明确的现金底线：

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

当存在更精确的运营储备计算时，可额外验证：

```text
CashAfterPurchase >=
    ImmediateDeploymentCost
    + RequiredOperatingSpendUntilNextReliableIncome
```

计划性购买是一项活跃的战略承诺；它**不会仅仅因为通用的无土地边际价值比较认为无需扩张而被取消**。机制和现金/可行性条件仍会优先于该承诺。

若由于现金底线或硬性机制依赖失败，导致计划性购买无法在目标时间点执行，则将其保留待定，并在最早合法时间点重新评估；不得在不通知的情况下默默删除该承诺。

<a id="162-unscheduled--additional-expansion"></a>
## 16.2 非计划性/额外扩张

所有未被上述时间表要求的土地购买均使用经济土地门限：

1. 计算不购买的最优方案；
2. 在复制状态上模拟下一次合法扩张；
3. 预留新地块的未来具体用途；
4. 包含部署、维护、工人容量、路径规划、库存及销售；
5. 验证市场日历和现金储备；
6. 要求增量可实现最终现金为正。

在任何购买确认后，其成本即被消耗。此后该地块上的所有生产将仅从剩余成本与价值重新评估。

---

<a id="17-shop-dependent-expansion-branch"></a>
# 17. 依赖商店的扩张分支

前两个商店仅在`T7`时分支变得可观察时才被使用。它们**不会**对强制性的`T4 -> NE`购买产生回溯性影响。

将`animal demand`精确定义为：前两个商店中至少有一个消耗了`EGG`、`MILK`或`WOOL`。

决策摘要：

```text
T4 -> NE always

At T7:
    first two shops contain animal demand
        -> SW at T7
        -> SE at T12

    first two shops contain no animal demand
        -> SW at T9
        -> no mandatory SE at T12
```

扩张方向本身并非选择：引擎的顺序是`NE -> SW -> SE`。策略仅决定是否以及何时根据上述规则触发计划性购买。

---

<a id="18-event-driven-phases-instead-of-hard-phase-boundaries"></a>
# 18. 以事件驱动阶段替代硬性阶段边界

历史阶段：

```text
T0-T3
T4-T20
T20-T30
```

虽有助于描述性先验，但不应作为硬性策略切换。

优先采用事件驱动的制度变更：

```text
OPENING:
    little shop information, establish resilient production

EXPANSION / ADAPTATION:
    new shop information materially changes marginal values

CAPACITY-LIMITED MIDGAME:
    land/labor/storage become binding constraints

LIQUIDATION HORIZON:
    new investments fail full cash-out feasibility
```

精确的过渡时间点源自预测结果，而非固定日期。

---

<a id="19-inventory-reservations"></a>
# 19. 库存预留

为每种产品维护：

```text
AvailableStock
ReservedForOperations
ReservedForConfirmedDemand
ReservedForPlannedProduction
UncommittedStock
```

当存在带日期的预测时，不要使用产品特定的固定预留数量，应由预测直接计算需求。

历史预留作为后备先验：

- 小麦：饲料加应急预留；
- 鸡蛋：配合烘焙/早餐需求的小量预留；
- 胡萝卜：配合宠物咖啡馆/农场市场需求的短期预留；
- 草莓/牛奶：当确认近期短缺时，设置较大预留；
- 羊毛：当毛线需求活跃或高度可能时，设置预留；
- 瓜类/肥料：在需求疲软时，通常避免长期持有。

---

<a id="20-shed-overflow"></a>
# 20. 舍屋溢出

使用时间索引的投影。

对于每一个未来的下跌事件 `d`：

```text
ProjectedShed(d) =
    current shed
    + all prior planned drops
    - all prior planned sells / uses / purchases from shed
```

所需应急清仓量：

```text
RequiredNeedSell = max(0, ProjectedShed(d) - 100)
```

可选的一格安全版本：

```text
SafetyNeedSell = max(0, ProjectedShed(d) - 99)
```

不要盲目加上所有工人的携带库存：只计算预计在相关容量事件前抵达舍屋的库存量。

---

<a id="21-selling-exact-marginal-simulation"></a>
# 21. 销售：精确边际模拟

保留使用 `P1/P3/P4/P5` 的历史分售方程仅作为直觉参考。基础销售引擎会枚举所有可实现的销售数量。

对于每种当前可售的 `stock` 产品单位：

```text
for q in 0 .. stock:
    simulate selling exactly q units
    compute the exact marginal revenue sequence
    propagate market inventory / price effects
    propagate enabled cash-dependent BUY / HIRE actions
    evaluate retained stock value

choose q with the highest resulting expected final value
```

此处的 `stock` 指的是 **在运营、生产及已确认需求预留之后，尚未承诺的可售库存**，而非原始舍屋库存。

当对手行为重要时，需将相同的销售数量通过 `LOW / BASE / HIGH` 对手情景进行运行。基础排序使用 `BASE`；`LOW/HIGH` 为稳健性检验，不引入人为概率权重。

收入必须基于实际的边际价格路径计算，而非 `q * initial_price`。所有候选销售均需符合每tick最多10个订单及流动性要求。

---

<a id="22-sell-versus-hold"></a>
# 22. 销售与持有

对于每一个下一个单位：

```text
MarginalSellValue(unit) = simulated cash received if this unit is sold now
```

对比：

```text
RetentionValue(unit) = max(
    FutureExpectedResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

在以下情况销售：

```text
MarginalSellValue > RetentionValue
```

然而，当现在销售能解锁更盈利的受限行动时，需明确包含该流动性价值。

---

<a id="23-liquidity-value-instead-of-arbitrary-financial-discounting"></a>
# 23. 采用流动性价值而非任意财务折现

不要依赖实验性公式：

```text
FuturePrice / (1 + r)^h
```

除非经实证验证，否则不使用推断出的 `r`。

Kaggriculture 有较短的有限时间范围。延迟现金支付的主要成本是 **在等待期间无法融资的最佳行动**。

优先：

```text
LiquidityOpportunityCost =
    Profit(best feasible plan with cash now)
    - Profit(best feasible plan without that cash until t+h)
```

然后：

```text
FutureResaleValueAdjusted =
    ExpectedFutureSaleRevenue
    - LiquidityOpportunityCost
    - HoldingRisk
```

如果精确比较成本过高，可采用一个更简单的有界近似。

---

<a id="24-cash-urgency"></a>
# 24. 现金紧迫性

避免使用无界或负的紧迫性系数。

```text
NearTermShortfall = max(
    0,
    RequiredCommittedSpendBeforeNextReliableIncome
    - LiquidCashAvailable
)

CashUrgency =
    NearTermShortfall
    / max(1, RequiredCommittedSpendBeforeNextReliableIncome)
```

因此：

```text
0 <= CashUrgency <= 1
```

将其作为销售评估中的流动性加分项，而非独立理由去以极差价格大批量出售。

---

<a id="25-price-impact-and-opponent-timing"></a>
# 25. 价格影响与对手时机

不要自动填补整个市场短缺估计值。

评估下一个销售单位的边际价格。

当预计对手供应即将到来时：

- 在对手成熟/发布之前，考虑出售盈利单位；
- 仅在预期的恢复/需求值得延迟时保留单位；
- 避免对敏感于过剩供应的产品进行同步抛售；
- 根据观察到的对手行为立即更新情景。

精确的市场模拟器应在足够信息可用时，取代诸如‘在对手成熟前必须清空’这类固定规则。

---

<a id="26-production-quantity"></a>
# 26. 生产数量

对于每一个候选产品，逐步增加生产量——**每次仅增加一个单位**。

```text
k = current_quantity + 1

while k is physically and operationally feasible:
    MV = marginal value of adding unit/tile/animal k

    if MV <= 0:
        stop

    accept k
    k += 1
```

一旦出现以下任一情况，立即停止：

- `MV <= 0`；或
- 存在约束条件阻止下一个单位的生产：土地/地块时间、工人上限/容量、现金、饲料、存储、截止时间、市场时段，或最终阶段现金结算可行性。

不要直接跳到需求缺口数量，除非另有明确规则规定固定的生产上限，否则不得自行设定生产上限。

---

<a id="27-wheat-as-an-operating-resource"></a>
# 27. 小麦作为运营资源

小麦具有销售价值和饲料价值。

计算一个带时间戳的饲料需求：

```text
RequiredWheat(t0..t1) =
    feed actions required by accepted animal plan
    + safety reserve for survival risk
```

减去当前持有的小麦以及在每个饲料截止日期前将成熟的麦子。

只有超出部分的小麦才可自由出售。

使用相同的边际价值框架，将自产与市场采购进行比较：

```text
cost of Wheat land + labor + delayed cash-out
vs
expected market purchase cost at feed date
```

这在获得更精确的时间预测时，取代了固定的`5 * animal_q - next5day_maturity`储备。

---

<a id="28-fertilizer"></a>
# 28. 肥料

由于动物粪肥不会积累，因此收集它并不自动具有价值。

仅在以下至少一项成立时才进行收集：

- 存在一项盈利的施肥任务需要它；
- 预期销售价值超过收集与出行的机会成本；
- 收集可以几乎免费地融入现有路线；
- 若现在不收集，将永久丧失无法后续恢复的价值。

仅当增量未来的可变现收益/时间优势超过肥料、人工、出行及替代用途成本时才进行施肥。

---

<a id="29-product-specific-behavior-is-a-fallback-not-the-economy-engine"></a>
# 29. 产品特定行为是后备机制，而非经济引擎

保持广泛的产品特征作为先验假设：

- 小麦：先作为运营储备和饲料储备；
- 胡萝卜：快速周转且对稀缺性敏感；
- 番茄：持续产出且对稀缺性敏感；
- 草莓：价格高但对过剩供应极为敏感；
- 西瓜：单位价值高但对过剩供应极为敏感；
- 鸡蛋：频繁产出且相对抗过剩供应；
- 牛奶：价值高且对过剩供应敏感；
- 羊毛：价值高且对过剩供应极为敏感；
- 肥料：在收集具有价值时选择使用或出售。

历史产品特定的固定时间表和评分公式不得覆盖共享的边际模型。

---

<a id="30-routing-logistics-and-hires"></a>
# 30. 路线、物流与雇佣

对于每一个未分配的`TaskGroup`，测试将其插入现有路线的可行性。

插入成本包括：

```text
travel
+ actions
+ pickup / resource acquisition
+ waiting
+ return / DROP
+ deadline risk
+ inventory effect
+ market dependency effect
```

选择最可行的插入方案。

如果重要的已接受任务未被分配，则使用精确的边际雇佣逻辑测试新的工人。

在获得可行路线后，仅使用小范围的局部移动/交换。除非基准证据明确证明需要，否则不要引入复杂的全局VRP求解器。

---

<a id="31-resource-reservations"></a>
# 31. 资源预留

每一个已接受的任务都会在相关时间点预留其所需的所有资源。

示例：

- 种子；
- 小麦饲料；
- 肥料；
- 购买的动物；
- 棚舍容量；
- 市场订单时段；
- 工人时间；
- 物理方格时间。

如果购买、雇佣、土地购买或销售延迟或失败，则会无效化相关依赖的预留并触发局部修复。

---

<a id="32-deployment-capacity-use-time-indexed-tile-reservations"></a>
# 32. 部署能力：使用时间索引的格子预留

不要使用静态历史约束：

```text
sum(seed_units) + animals <= currently_free_tiles
```

作为最终规则。

而是验证随时间变化的物理占用情况：

```text
for each placement interval [start, release):
    reserve exact tile
    reject overlapping incompatible reservations
```

这使得生产可以使用在部署前就会被释放的格子，并防止经济 `effective land` 指标被误认为是物理占用情况。

---

<a id="33-local-replanning"></a>
# 33. 本地重新规划

仅当变更影响可行性、预期值符号或所选经济行动时才重新规划。

相关变更包括：

- 新开设商店；
- 具有实际意义的市场价格/库存变动；
- 对手种植、收获、购买或销售行为；
- 意外出现的杂草/逃逸动物；
- 实际生产与预测不符；
- 市场行动失败或延迟；
- 路线延迟；
- 股票/现金冲突；
- 土地确认；
- 终局地平线穿越。

保留：

- 已确认的事实；
- 已完成的动作；
- 已支付的工人；
- 仍然有效的路线前缀；
- 仍然有效的预订。

仅释放受影响的未来预订和路线后缀。

---

<a id="34-endgame"></a>
# 34. 终局

终局在每个新决策中都被评估，而不仅在清理阶段。

如果新增作物、动物、土地购买、肥料使用或雇佣行为，其完整链条：

```text
install
-> maintain
-> produce
-> harvest
-> return
-> DROP
-> SELL
```

无法在最后一次可执行销售前创造正向可实现的最终现金。

从最后一次销售倒推计划：

```text
last SELL
<- required DROP
<- required return travel
<- required HARVEST
<- required maintenance / production
```

如果配置环境使用已知的`episodeSteps = 720`时间表，则必须保留一个明确的回归测试，确保最终清算在最后一个实际可执行的时刻（当前项目惯例：第29天，22小时）完成。

绝不依赖自动游戏结束后的存款。

---

<a id="35-fixed-opening-strategy"></a>
# 35. 固定开局策略

基础策略使用以下固定开局包。它**默认启用**，并非仅仅是一个基准种子。

目标开局数量：

|项目|数量|
| --- | ---: |
|小麦作物| 10 |
|胡萝卜| 6 |
|番茄| 1 |
|草莓| 2 |
|西瓜| 2 |
|鹅| 1 |
|牛| 2 |
|羊| 1 |
|小麦库存| 16 |
|初始雇用农工| 4 |

初始规则：

- 在机制和行动能力允许的范围内，尽早创建/放置/种植目标包；
- 新种植作物的当日强制浇水仍不可协商；
- 动物必须遵守强制性的朝中心方向的三角放置掩码；
- 长期作物不得占据中央`2 x 2`；
- 获取并储备足够的小麦以支持固定的动物包；
- 在初始构建阶段，不得用边际搜索量替代固定的数量；
- 一旦初始包建立，正常的共享预测和边际规划将接管额外生产；

执行过程中使用实际观测到的价格/成本和游戏状态。记录的历史总成本不被视为机制常量；

---

<a id="36-objective"></a>
# 36. 目标

游戏目标是最终银行资金。

因此，核心规划目标应保持为：

```text
maximize expected final realizable cash
```

对手建模是有用的，因为对手会改变价格，胜利取决于相对最终结果，但不要用历史启发式替代绝对值：

```text
MarginMax = OurProfit - OpponentProfit
```

除非明确进行了独立的竞争策略基准测试。

主要的生产与运营决策不应仅仅为了减少对对手的估计利润，而损害我们自身的预期现金流。

---

<a id="37-historical-ideas-retained-only-for-benchmark"></a>
# 37. 历史想法仅保留用于基准测试

以下内容默认处于**禁用状态**，除非有独立的基准测试明确启用，否则不得影响基础代理的行为：

- 固定的CARE跳过天数，例如`T5`或`T5-T7`；
- 固定的肥料/收获日期，例如`T8`、`T10`、`T12`、`T14`、`T16`；
- 历史产品评分公式中括号含义模糊;
- 历史 `Dtotal` 公式中缩写未定义或重复;
- `Va * required_actions` 作为劳动力成本;
- 推导出的财务折现率 `r`;
- 原始农场产量直接加到全球市场库存中;
- `P1/P3/P4/P5` 分销销售不等式作为最终销售引擎;
- `NeedSell = Shed + Carry + Incoming - 99` 作为精确存储方程;
- 静态 `seeds + animals <= free tiles` 作为部署容量;
- 刚性 `T0-T3 / T4-T20 / T20-T30` 策略模式切换;

以下内容**不再仅作为基准**，而是作为有效基线规则:

- 工人上限 `14`;
- 固定初始包;
- 按计划进行的土地购买 `T4/T7/T9/T12`，其店铺分支在§16-17中定义;
- 固定扩展订单 `NE -> SW -> SE`;
- 强制对称 `5 x 5` 三角动物布局;
- 长期作物的绝对中心 `2 x 2` 禁令;


<a id="371-historical-alternative-opening"></a>
### 37.1 历史替代初始方案

以下日-1数量被记录为替代初始方案候选，并仅保留用于孤立基准对比:

|产品|历史日-1候选数量|
| --- | ---: |
|甜瓜| 2 |
|胡萝卜| 6 |
|蛋产量| 1 |
|毛产量| 1 |
|奶产量| 2 |
|草莓| 2 |
|小麦| 2 |
|番茄| 2 |

它们不覆盖第35条中的活动固定开启点。

<a id="372-historical-phase-boundaries"></a>
### 37.2 历史阶段边界

固定的描述性阶段被保留为历史先验：

```text
T0-T3   -> opening
T4-T20  -> expansion / adaptation
T20-T30 -> liquidation-oriented play
```

活动规划器使用第18条中的事件驱动制度，而不是将这些边界视为硬切换。

<a id="373-historical-expansion-timing-and-fill-patterns"></a>
### 37.3 历史扩展时间与填充模式

较早的记录记载了时间上限：

```text
first land  < T7
second land < T12
third land  < T12
```

他们还提出了候选新土地填充模式：

- SW：`4 x 4` 三角形，`4 x 4` 正方形，或条件部分填充；
- SE：`4 x 4` 三角形，中心附近 `4 x 4` 子集，或条件部分填充。

这些仅作为基准保留。活动扩展计划和几何结构在第15-17条中定义。

<a id="374-historical-effective-land-weight"></a>
### 37.4 历史有效土地权重

旧经济比较使用了：

```text
plant effective land   = 1 tile
poultry effective land = 5 / 3 tiles
```

这可以作为经济比较权重进行基准测试，但它绝不能替代第32条中的精确物理格子时间预留。

<a id="375-historical-opponent-and-demand-approximations"></a>
### 37.5 历史对手与需求近似

旧对手模型提出：

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

和需求置信度：

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

最终基准保留了`LOW / BASE / HIGH`对手情景，而不引入概率权重。这些公式仅作为可能的实验性近似保留。

<a id="376-historical-long-horizon-market-approximation"></a>
### 37.6 历史长期市场近似

当事件级投影被认为过于昂贵时，记录提出：

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

该近似仅作为基准保留。活动模型保持农场侧产出与全球市场库存分离，并偏好第4条中的过时库存路径。

<a id="377-historical-product-score-formulas"></a>
### 37.7 历史产品评分公式

以下评分想法被精确保留为策略笔记。其原始括号化未完全指定，因此不得被静默地变为基准公式。

|产品|历史评分想法|
| --- | --- |
|西瓜| `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
|胡萝卜| `sum(q * dynamic_price) - 20 - labor / land_occupation` |
|蛋| `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
|毛| `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
|奶| `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
|草莓| `sum(q * dynamic_price) - 100 - labor / land_occupation` |
|小麦| `sum(q * dynamic_price) - 10 - labor / land_occupation` |
|番茄| `sum(q * dynamic_price) - 50 - labor / land_occupation` |

<a id="378-historical-demand-formulas"></a>
### 37.8 历史需求公式

原始缩写未完全定义。重复术语有意保留，而非静默修正。

|产品|历史`Dtotal`公式|
| --- | --- |
|西瓜| `Dtotal = 1/day` |
|胡萝卜| `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
|蛋| `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
|毛| `Dtotal = Dm + 12 * Ny * q` |
|奶| `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
|草莓| `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
|小麦| `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
|番茄| `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

<a id="379-historical-competitive-margin-signal"></a>
### 37.9 历史竞争利润率信号

记录提出：

```text
MarginMax = OurProfit - OpponentProfit
```

它可能被作为次要信号进行基准测试，但第36条将预期最终可实现现金作为基准目标。

<a id="3710-historical-financial-discounting"></a>
### 37.10 历史财务贴现

旧的卖出/持有模型提出：

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h

r =
    ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h)
    - 1
```

精确的边界聚合并未完全指定。因此，最终基线在第23节使用流动性-机会成本模型，除非明确启用了折现率实验。

<a id="3711-historical-split-sale-comparison"></a>
### 37.11 历史分售对比

较早的战术笔记将立即出售`n + m`与分售进行了对比：

```text
P  = average price
n  = quantity sold now
P1 = current price
D  = shop consumption
m  = later quantity we may sell before opponent maturity
x  = opponent quantity sold one day before our later sale
P3 = opponent sale price before our later sale
P4 = our resulting price after that opponent sale
P5 = opponent's later price after our n + m sales and before our next maturity
```

历史分售条件：

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

这仍属于直觉/基准材料。第21节中的活跃售出引擎会直接枚举可实现的售出数量。

<a id="3712-historical-overflow-and-deployment-shortcuts"></a>
### 37.12 历史溢出与部署快捷方式

较早的笔记使用了：

```text
NeedSell = Shed + Carry + Incoming - 99
```

和：

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

它们仅作为实验的快捷方式保留。活跃规划器使用真实的舍弃容量`100`、时间索引的入库量以及精确的格子时间预留。

<a id="3713-historical-animal-action-ordering"></a>
### 37.13 历史动物行为顺序

旧的生产访问序列是：

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

最终基线并不普遍强制执行这一点。第12节仅保留对当前状态有影响的依赖关系。

<a id="3714-historical-product-level-inventory-and-timing-heuristics"></a>
### 37.14 历史产品级库存与时间启发式

以下产品规则仍作为基准先验保留，而非基线覆盖：

- 肥料：当不需要用于有利的短期施肥时，优先立即出售。
- 西瓜：避免长期持有；旧笔记将总产量限制在`120`附近。
- 小麦：旧储备估计值`5 * animal_q - WheatExpectedToMatureInNext5Days`。
- 鸡蛋：在面包店/早餐需求下，保持大约一天的需求量；旧政策每日使用`CARE`。
- 胡萝卜：在宠物咖啡馆/农场市场需求下，保持大约两天的需求量；旧规则未进行施肥。
- 番茄：历史施肥/收获想法在`T8`、`T9`和`T11`附近。
- 草莓：历史施肥/收获想法在`T10`、`T12`、`T14`和`T16`附近。
- 牛奶：在相关需求下，保持大约两天的净需求量；旧CARE时间表在`T5-T7`附近跳过。
- 羊毛：在等待毛线需求时保持；旧CARE时间表在`T5`附近跳过。

相关的历史库存类别是：

```text
Class 1 — operating inventory only: Wheat
Class 2 — fast turnover: Carrot
Class 3 — balanced: Tomato, Egg
Class 4 — high-value timing inventory: Strawberry, Milk, Wool
Class 5 — avoid long holding: Melon, Fertilizer
```

活跃规划器相反地从历史预测中推导预留，并仅将广义产品特征在第29节作为后备先验使用。

<a id="3715-historical-market-aware-sale-biases"></a>
### 37.15 历史市场感知售出偏见

当完整边际模拟器对孤立基准被禁用时，旧笔记建议：

- 胡萝卜/鸡蛋/小麦/番茄：在现金压力下提前出售；
- 羊毛：在可行时等待毛线需求；
- 牛奶/草莓：优先选择高价时段；
- 西瓜：立即出售或在预期对手供应前出售；
- 在舍弃压力下：优先按利润顺序出售，而非FIFO。

这些规则不得覆盖第21-25节中的基线售出/持有和精确数量逻辑。


---

<a id="38-final-hard--near-hard-invariants"></a>
# 38. 最终硬/近硬不变量

1. 绝不违反实际的游戏机制限制。
2. 绝不超过活跃战略工人数额上限`14`。
3. 绝不让新种植作物缺少当日必需的水分。
4. 永远不要遗漏对计划中打算保留的资产的生存维护工作。
5. 永远不要对最佳剩余计划是放弃的资产进行维护支出。
6. 永远不要在缺少所需资源和依赖项的情况下安排工作。
7. 永远不要允许必需的下降超出真实的棚舍容量 `100`。
8. 永远不要在一个时间步长内提交超过10个市场订单。
9. 永远不要假设待解锁的土地已经解锁。
10. 永远不要将未售出的农场产量计入全球市场库存。
11. 永远不要将动物放置在活动象限中心面向的三角形 `1` 掩码之外。
12. 永远不要将长期作物放置在中央 `2 x 2`。
13. 在开盘构建期间，除非机制使请求的操作暂时不可能，否则必须保持固定的开市数量。
14. 保持预定的土地承诺：`T4 NE`；然后在 `T7`，动物需求分支 -> `T7 SW` + `T12 SE`，否则 `T9 SW` 且无强制性的 `T12 SE`。
15. 预定的土地购买可能会因机制或现金地板失败而延迟，但绝不能被静默地取消。
16. 永远不要仅仅因为存在工作就接受非强制性的雇佣；必须在雇佣前要求正的边际价值和工人数量 `< 14`。
17. 永远不要仅仅因为田地已满就接受未安排的土地购买；必须要求与不购地计划相比的正的增量最终现金。
18. 永远不要接受无法在游戏结束前完成其全部现金流出链的非强制性新投资。
19. 永远不要因为市场槽位压力而静默截断依赖关系。
20. 永远不要在无变更重计划后重复任务组/预留。
21. 仅保留受影响的未来后缀中的有效工作和维修。

---

<a id="39-verification-suite-for-the-final-design"></a>
# 39. 最终设计的验证套件

任何声称遵循最终策略的实现，直到这些情况通过之前都不应被视为忠实。

<a id="mechanics"></a>
## 机制

- 新种植的作物无当日浇水 -> 规划器拒绝路线；
- 在生存截止日期保留的动物 -> 安排饲料；
- 被放弃/不盈利的后期动物 -> 生存饲料可故意省略；
- 棚舍容量为95，有10个进入下降 -> 下降前至少需释放5个容量；
- 针对相同情况的安全缓冲模式 -> 释放6个容量以达到99目标；
- 种子不计入棚舍容量；
- 市场日历永远不会在一个时间步长内发出超过10个订单。

<a id="market-model"></a>
## 市场模型

- 农场收获但未销售 -> 全球市场库存不变；
- 我们销售 -> 全球库存增加，并重新计算下一个边际销售价格；
- 我们购买 -> 全球库存减少；
- 商店消费 -> 全球库存减少；
- 双人同时销售场景 -> 收入使用环境的顺序/交错边际价格，而不是 `quantity * initial_price`；
- LOW/BASE/HIGH 对手情景可以改变销售数量而不破坏可行性。

<a id="labor"></a>
## 劳动力

- 仅执行负价值可选工作的新增工人 -> 不进行雇佣；
- 新工人完成一个盈利且关键的截止任务，并覆盖招聘成本 -> HIRE;
- 第15个工人即使其孤立边际价值为正，也被主动战略上限拒绝。

<a id="land"></a>
## 土地

- 当前全部田地但无新增正价值产出 -> 不 BUY_LAND;
- 盈利产出但维护不可行 -> 不 BUY_LAND;
- 盈利扩张但违反运营现金流储备 -> 不 BUY_LAND;
- 确认的土地对应当前不良预留作物 -> 取消作物，尽管已发生土地沉没成本;
- `T4 -> NE` 的调度独立于店铺需求;
- 在 `T7`，前两个店铺的动物需求立即调度 `SW`，并在 `T12` 调度 `SE`;
- 在 `T7`，无动物需求调度 `SW` 在 `T9`，且不强制调度 `SE` 在 `T12`;
- 一个计划采购若未通过现金底线则被延迟/挂起，而非静默丢弃;
- 扩张方向从未被重新排列远离 `NE -> SW -> SE`。

<a id="opening-and-placement"></a>
## 开设与放置

- 固定的开设目标数量符合 §35;
- 开张规划器在构建固定包之前不会替代边际更优的量;
- NW/NE/SW/SE 三角形掩码是指定 `5 x 5` 模板的精确对称;
- 动物放置在 `1` 单元格之外被拒绝;
- 长期作物放置在 `CENTRAL_2X2` 内部被拒绝。

<a id="inventory"></a>
## 库存

- 仅在目标下落前到达棚屋的库存调度才对容量事件产生贡献;
- 未来饲料截止前所需的麦子不能作为未承诺库存出售;
- 未来店铺需求储备影响出售/持有价值;
- 库存压力即使等待的单位价格更高，也能强制出售。

<a id="endgame"></a>
## 终局阶段

- 投资首次可实现销售在游戏结束之后 -> 被拒绝;
- 必须在最后一天出售的动物收获 -> 早于最后一天收获，以确保返还/下落/出售;
- 最终工人不携带有价值的未售出库存;
- 无规划决策假设游戏结束后自动清算。

<a id="replanning"></a>
## 重规划

- 在状态不变的情况下重复生成 -> 生成相同任务ID，无重复;
- 延迟 HIRE 仅使依赖的未来路线容量失效;
- 失败的 BUY 使依赖的取货/种植任务失效;
- 新店铺重新计算受影响的需求、价格、储备和产量;
- 无关的价格变动不会重建未受影响的路线。

---

<a id="40-benchmark-protocol-for-uncertain-heuristics"></a>
# 40. 不确定启发式算法的基准协议

对于每一个可选的启发式算法，需与相同的最终基准进行对比，使用配对种子和相同对手策略。

记录至少：

```text
mean final money
median final money
minimum final money
win rate / money difference if relevant to the evaluation setup
mean hires per day
land purchase timing
idle worker ticks
missed critical tasks
shed overflow incidents
market-order truncation incidents
unrealized final inventory
runtime
```

仅当：

```text
1. it improves the chosen primary metric,
2. it does not introduce a clear tail-risk regression,
3. the gain survives more than a tiny seed sample,
4. the implementation does not duplicate an existing planner mechanism.
```

---

<a id="41-final-strategy-summary"></a>
# 41. 最终策略总结

最终规划器应表现如下：

```text
1. Execute the fixed opening package.
2. Observe the real game state and maintain one forecast through game end.
3. Keep farm inventory and global market inventory separate.
4. Model opponent supply with LOW / BASE / HIGH scenarios without arbitrary weights.
5. Enforce MAX_WORKERS = 14.
6. Enforce the center-facing 5x5 triangular animal masks and central 2x2 long-crop ban.
7. Follow the active land schedule:
       T4 -> NE
       at T7: animal-demand branch -> SW T7 + SE T12
              no-animal-demand branch -> SW T9, no mandatory SE T12
8. Generate non-mandatory production one unit at a time until MV <= 0 or a constraint binds.
9. Reserve exact tile-time, stock, cash, market slots and worker-time.
10. Protect valuable assets; abandon negative-value sunk assets.
11. Route existing workers first; hire only on positive marginal schedule delta and below cap 14.
12. Enumerate sale quantities q = 0..sellable_stock with the exact market simulator.
13. Use the deterministic tie-break: value -> smallest slack -> less labor -> less travel.
14. Replan locally when observations materially change feasibility or value.
15. Plan final harvest/drop/sale backward so value becomes cash before game end.
```

核心设计原则是：

> **机制定义了可能的内容；主动策略定义了承诺的基准；可行性定义了可以执行的内容；边际最终现金优化了所有剩余的可选内容。**


---

<a id="42-version-to-final-traceability"></a>
# 42. 版本到最终的可追溯性

历史概念文档现已演变为严格链路，而本文件是完整的独立结果：

|设计版本|关联代理|本设计中纳入的主要贡献|
| --- | --- | --- |
| [`v1`](heuristic_ideas_v1.zh-CN.md) | `chi12.py` |每日规划、优先级、物流、路径规划、存储保护、本地重规划、清算|
| [`v2`](heuristic_ideas_v2.zh-CN.md) | `chi13.py` |明确规划的土地扩展、无土地基准、确认与依赖处理|
| [`v3`](heuristic_ideas_v3.zh-CN.md) | `chi14.py` |共享预测、稳定`TaskGroup`、集成路径/HIRE、单一市场日历、本地维修、终局集成|
| [`v4`](heuristic_ideas_v4.zh-CN.md) |—|市场/对手感知的经济模型、边际生产/销售、劳动力/空间约束、战术优先级|
| `final` |—|完整解决的战略、主动策略与基准策略的优先级、修正后的市场模型与实施合同|

最终战略被明确规定，使得仅从本文件即可推导出实现方案；版本化文档仍可用于设计历史记录和变更归属。在封闭项目中，未保留此类经验证的后续版本。


<a id="43-implementation-contract"></a>
# 43. 实施合同

本节移除了可能引发两个代理在行为不同情况下仍声称相同策略的实施自由度。

<a id="431-active-vs-benchmark-only-rules"></a>
## 43.1 主动策略与仅基准策略规则

本文件中所有明确标记为主动的规则默认为开启。

历史/仅基准规则默认关闭，除非实验明确启用，否则不得影响基准。

主动规则至少包括：

```text
MAX_WORKERS = 14
fixed opening package from §35
fixed expansion order = NE -> SW -> SE
active land schedule from §16-17
mandatory 5x5 triangular animal masks
absolute central 2x2 long-term-crop exclusion
```

<a id="432-storage"></a>
## 43.2 存储

```text
SHED_CAPACITY = 100
```

使用`100`进行可行性与溢出检查。

`99`仅作为可选的安全目标，不得视为引擎容量。基准可能暴露一个配置标志以表示该边际，但无规则需以此证明基本可行性。

<a id="433-forecast-horizon"></a>
## 43.3 预测时域

物理/经济预测从当前时间步持续至游戏结束。内部可使用更短的缓存近似值，但必须能证明其在受影响范围内的决策保持不变。

<a id="434-marginal-production-search"></a>
## 43.4 边际生产搜索

对于非强制性生产，每次仅测试一个额外单位/格/动物，并在以下情况停止：

```text
MV <= 0
OR a binding constraint prevents the next unit
```

不得直接跳转到猜测的目标数量。

<a id="435-sale-quantity-search"></a>
## 43.5 销售数量搜索

对于每种产品，在预留之后：

```text
sellable_stock = uncommitted stock
for q in 0 .. sellable_stock:
    simulate q exactly
choose q maximizing expected final value
```

不得使用固定批量大小作为决策基准。

<a id="436-deterministic-tie-break"></a>
## 43.6 确定性并列处理

当两个可行选择在主要目标下相等时，应用：

```text
1. higher value
2. smaller deadline slack
3. fewer labor / worker ticks
4. less travel
5. stable deterministic ID / coordinate order
```

`smaller slack`表示更紧急的可行任务获胜。

<a id="437-no-arbitrary-economic-coefficients"></a>
## 43.7 无任意经济系数

不得为以下内容发明未解释的常数：

- `RiskPenalty`;
- LOW/BASE/HIGH概率；
- 放置权重；
- 流动性折现率；
- 战略价值乘数。

基线约定：

- 使用 `BASE` 对手场景对预期结果进行排序；
- 除非后续明确配置了概率，否则仅将 `LOW/HIGH` 用于稳健性/敏感性检查；
- 使用硬性布局几何结构以及确定性破平规则，而不是加权布局评分；
- 使用直接的调度/现金差值，而不是人为发明的财务折现系数。

如果仍然不可避免地需要数值系数，应将其暴露为一个命名配置值，并标记为 **策略未指定**。它绝不能在基线中静默地成为一部分。

<a id="438-mechanical-execution-contract"></a>
## 43.8 机械执行合同

战略代码必须从游戏规则/环境精确读取执行语义，而不是自行发明。特别在测试中需验证：

- `HIRE` 之后的工人可用性精确值；
- 工人生成位置的实际值；
- 减去已携带库存后，`PICKUP` 数量的精确值；
- 市场订单处理/交错的实际值；
- 商店消费时机；
- 每日生产/刷新时机；
- 最后实际可执行的时钟周期。

这些是机制，而非策略参数。

<a id="439-traceability-requirement"></a>
## 43.9 可追溯性要求

任何声称采用本最终设计的实现中，每一个战略分支都必须可追溯到本文件的某一部分。如果某种行为无法由本文件或经验证的游戏机制加以证明，Codex 必须不得静默添加它。


---

<a id="navigation"></a>
## 导航

[← 上一设计变更](heuristic_ideas_v4.zh-CN.md) · 最终整合设计
