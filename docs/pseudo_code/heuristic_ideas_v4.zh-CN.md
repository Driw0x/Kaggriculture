[English](heuristic_ideas_v4.md) | [Français](heuristic_ideas_v4.fr.md) | [简体中文](heuristic_ideas_v4.zh-CN.md)

[项目 README](../../README.zh-CN.md)

<a id="heuristic-ideas-v4--market-aware-tactical-strategy"></a>
# 启发式理念 v4 — 市场感知战术策略

[← 上一版本](heuristic_ideas_v3.zh-CN.md) · [最终整合版本 →](heuristic_ideas_final.zh-CN.md)

> **系列规范**
>
> `v4` 是 `v3` 的一个**严格增量版本**。它完整继承了 `v3`，并仅在此处明确添加、替换或修正规则。更早的行为通过 `v3` 递归继承；`v4` 不将 `v1` 或 `v2` 视为并列父版本。

<a id="identity"></a>
## 身份

|字段|值|
| --- | --- |
|版本| `v4` |
|来源|Kaggriculture 策略表 + 额外战术说明|
|关联代理|无 — 仅用于设计|
|角色|严格增量版本 [`v3`](heuristic_ideas_v3.zh-CN.md)|
|改进| [`v3`](heuristic_ideas_v3.zh-CN.md) |
|整合由| [`final`](heuristic_ideas_final.zh-CN.md) |
|主要关注点|市场时机、对手建模、边际经济学、库存政策、战术土地使用以及硬性运营约束|
|实施状态|未作为专用 CHI 代理实现|

<a id="inheritance-rule"></a>
## 继承规则

`v4` 完整继承 [`v3`](heuristic_ideas_v3.zh-CN.md)。由于 `v3` 已经继承了 `v2`（进而继承了 `v1`），所有更早的行为都通过递归继承保留。仅在下方列出的规则会修改 `v3` 的设计。

本文件有意**不重复**`v3` 中已存在的理念，包括 `v3` 本身通过递归继承而获得的行为。每日任务规划器、生存优先级、路线/物流、计划中的 `BUY_LAND`、共享预测、局部重规划、验证过的市场日历以及通用终局可行性因此仍从 `v3` 继承。

以下规则是来自后期 Kaggriculture 说明中新增信息或使先前原则更具体化的理念。

---

<a id="main-idea"></a>
## 核心理念

在统一规划器之上增加第二层战略层级：

`shop demand -> own/opponent supply -> future inventory -> future price -> marginal value -> what to produce / hold / sell`

规划器不应再仅询问生产计划是否可行，还应询问**下一个单位**、**下一个地块**、**下一个工人**、**下一次土地购置**或**下一次销售**是否在考虑市场影响、持有价值、劳动力机会成本和对手时机后，能提升预期利润。

---

<a id="1-hard-labor-ceiling--marginal-hiring"></a>
## 1. 硬性劳动上限 + 边际雇佣

<a id="hard-constraint"></a>
### 硬性约束

```text
worker_count <= 14
```

规划器绝不能生成需要超过 14 名工人的计划。

<a id="economic-stopping-rule"></a>
### 经济停止规则

不要仅仅因为存在更多工作就雇佣工人。需将新增一名工人的增量价值与下一次雇佣成本进行比较。

```text
Va = Profit(A + 1 workers) - Profit(A workers)
```

当边际工人不再自我盈利时，停止雇佣。

如果增加一名工人不值得其成本，应将现有劳动力重新分配至价值最高的土地/生产环节，而非扩大劳动力规模。

原始笔记还描述了劳动力机会成本为：

```text
LaborOpportunityCost_i = Va * required_actions_i
```

这比 v3 规则中 `HIRE` 仅需使工作可行的要求更为具体。

---

<a id="2-spatial-layout-constraints"></a>
## 2. 空间布局约束

除继承自 `v3` 的布局逻辑外，还需使用明确的放置区域。

<a id="animal-zone"></a>
### 动物区

动物应集中在一个大约`5 x 5`格子、靠近农场中心/棚屋入口区域的三角形区域内。

目的：

- 减少重复的`FEED`、`CARE`、`HARVEST`以及肥料收集的行程；
- 将高频生产保持在中心区域；
- 避免将动物管理分散到扩大后的土地上。

<a id="central-2-x-2-reserve"></a>
### 中心`2 x 2`预留区

避免在中心`2 x 2`区域种植长期回报的作物。

原始笔记还特别指出，此限制在相关最新回本截止点之后即失效。因此，这是一个**时间依赖的布局限制**，而非永久禁令。

<a id="effective-land-usage"></a>
### 有效土地利用率

为了经济比较，笔记中使用了如下内容：

```text
plant effective land = 1 tile
poultry effective land = 5 / 3 tiles
```

该有效占用率可用于比较单位土地时间内的边际价值。

---

<a id="3-three-strategic-game-phases"></a>
## 3. 三个战略游戏阶段

笔记将游戏分为三个主要阶段：

```text
Phase 1: T0  -> T3
Phase 2: T4  -> T20
Phase 3: T20 -> T30
```

具体决策仍取决于状态，但预期角色是：

- **T0–T3：** 建立初始生产基础和生存/饲料能力；
- **T4–T20：** 扩展生产、响应已揭示的商店需求，并最大化生产用地的利用；
- **T20–T30：** 减少长期回本承诺，积极管理库存，并为清算做准备。

此阶段模型是一种额外的战术倾向；来自`v3`的末期可行性仍会覆盖任何不再盈利的固定时间表。

---

<a id="4-historical-opening-templates"></a>
## 4. 历史开局模板

笔记中包含多个开局思路。它们应被保留为**基准测试的替代性开局方案**，而不是因为写于不同阶段而合并为一个强制性开局。

<a id="opening-candidate-a--fixed-initial-farm-package"></a>
### 开局方案A — 固定初始农场包

|项目|数量|记录成本|
| --- | ---: | ---: |
|小麦作物（`W`）| 10 | 100 |
|胡萝卜（`C`）| 6 | 120 |
|番茄（`T`）| 1 | 50 |
|草莓（`S`）| 2 | 200 |
|西瓜（`M`）| 2 | 160 |
|鹅| 1 | 300 |
|牛| 2 | 800 |
|羊| 1 | 500 |
|小麦库存| 16 | 450 |
|雇佣| 4 | 7 |

笔记中记录的总数：

```text
total cost = 2687
remaining cash = 313
```

重要开局意图：

- 立即播种并浇水初始作物；
- 保持足够的小麦以支持动物饲养；
- 在首次收获后，根据已出现的商店重新分配释放出的土地；
- 在必要时利用早期小麦收获来喂养动物；
- 计算当前小麦库存能维持多久，以及何时需要开始新的小麦生产。

<a id="opening-candidate-b--product-by-product-day-1-quantities"></a>
### 开局候选方案 B — 第 1 天各商品的数量

另一份策略表记录了以下初始数量：

|产品|第1天候选数量|
| --- | ---: |
|西瓜| 2 |
|胡萝卜| 6 |
|蛋产量| 1 |
|羊毛产量| 1 |
|牛奶产量| 2 |
|草莓| 2 |
|小麦| 2 |
|番茄| 2 |

这些值作为历史候选先验保留，应根据当前店铺需求、土地、劳动力和市场预测重新评估，而不是盲目硬编码。

---

<a id="5-tactical-land-expansion-schedules"></a>
## 5. 战术性土地扩张计划

继承自`v3`的盈利性和可行性检查仍然必须执行。`v4`增加了**优先时间与布局分支**，当这些检查通过后，可以测试这些分支。

<a id="branch-a--first-two-shops-do-not-create-meaningful-animal-demand"></a>
### 分支A — 前两个店铺不会产生有意义的动物需求

```text
T4: prefer buying NE as first expansion
T9: prefer buying SW as second expansion
```

在NE购入之后：

- 如果出现动物需求，优先安排动物及小麦支持；
- 如果动物需求仍然不存在，则保留大约一只鹅，其余用于满足店铺需求的作物；
- 逐步填充新土地，而不是强制立即完全利用。

对于SW扩张，候选填充模式包括：

- `4 x 4`三角形；
- `4 x 4`方形；
- 根据需求和劳动力情况的条件性部分填充。

<a id="branch-b--first-two-shops-contain-animal-demand"></a>
### 分支B — 前两个店铺包含动物需求

采用更早的扩张方案：

```text
T4 : NE first expansion
T7 : SW second expansion
T12: SE third expansion
```

备注中还指出，当前两个店铺存在动物需求时，应考虑第四块土地。

候选SE利用方案包括：

- `4 x 4`三角形；
- `4 x 4`中心附近子集；
- 根据需求和可用劳动力情况的条件性填充。

<a id="historical-timing-ceiling"></a>
### 历史时间上限

另一条备注也记录了：

```text
first land  < T7
second land < T12
third land  < T12
```

将其作为实验性时间先验保留，而不是替代继承自`v3`的经济验证。

<a id="land-cash-floor"></a>
### 土地现金下限

除了继承自`v3`的现金储备逻辑外，还需明确设定下限：

```text
cash
- land_cost
- days_until_next_income * average_labor_price
> 300
```

笔记中还提出另一种表述是：

```text
current_cash >=
    land_cost
    + immediate_deployment_cost_after_expansion
    + operating_reserve_until_first_harvest
```

两者表达了相同的战略意图：如果购买土地会使农场无法在下一次可实现收入前运营，则不应购买土地。

---

<a id="6-explicit-market-demand-and-opponent-forecast"></a>
## 6. 明确的市场需求与对手预测

<a id="market-gap"></a>
### 市场缺口

对每种产品，估算未来短缺情况为：

```text
MarketGap =
    shop_demand
    + town_center_demand
    - own_expected_supply
    - opponent_expected_supply
```

**不要**假设完全填补这一缺口总是最有利可图。由于额外供应可能压低价格，经济最优数量可能更小。

<a id="opponent-supply-model"></a>
### 对手供应模型

跟踪对手可见的生产情况：

- 种植的作物类型和数量；
- 动物类型和数量；
- 预期产量/成熟时间；
- 预期产量金额；
- 可能的市场释放时间。

近似不确定对手供应为：

```text
OpponentExpectedSupply = VisibleCapacity * ExpectedExecutionRate
```

源笔记明确建议，在对手执行不确定时，应设定低/中/高概率水平。

当市场库存发生变化时，应将其作为证据更新对对手库存状态的估计。

<a id="demand-certainty"></a>
### 需求确定性

```text
ConfirmedDemandWeight = 1
FutureExpectedDemandWeight < 1
```

因此，已确认的店铺需求应比不确定的未来需求对生产决策产生更强影响。

---

<a id="7-future-inventory---future-price"></a>
## 7. 未来库存 -> 未来价格

使用市场价格曲线代替将当前价格视为永久不变

<a id="short-term-inventory-forecast"></a>
### 短期库存预测

```text
FutureInventory =
    CurrentMarketInventory
    + FutureOwnSupply
    + FutureOpponentSupply
    - FutureShopConsumption
    - FutureTownConsumption
```

然后：

```text
ExpectedFuturePrice = PriceFunction(FutureInventory)
```

<a id="long-term-approximation"></a>
### 长期近似

笔记中还提出：

```text
FutureInventory(h) =
    CurrentMarketInventory
    + h * (
        OwnAverageDailySupply
        + OpponentAverageDailySupply
        - ShopAverageDailyConsumption
      )
```

当逐事件精确投影的成本不值得付出时，这很有用

<a id="supply-timing"></a>
### 供应时机

区分：

- 同步供应；
- 分批供应；
- 平滑供应。

即使总产量相同，两个计划的价值也可能不同，如果其中一个避免了在与对手相同的低价谷期进行销售。

---

<a id="8-marginal-production-economics"></a>
## 8. 边际生产经济学

产能选择应比较**下一增量单位的产能**，而不仅仅是整个项目的总利润

<a id="expected-revenue"></a>
### 预期收入

对于一次性作物：

```text
ER_i = ExpectedFuturePrice_at_harvest * ExpectedYield
```

对于重复生产，应将每个未来产出按其自身生产日期的预期价格求和：

```text
ER_i = sum_t(ExpectedPrice_t * ExpectedYield_t)
```

<a id="plant-direct-cost"></a>
### 直接种植成本

```text
PlantCost = SeedCost * Quantity + LaborCost
```

<a id="animal-direct-cost"></a>
### 直接动物成本

笔记将动物成本建模为：

```text
AnimalCost =
    PurchaseCost
    + FeedOpportunityCost
    + LaborCost
```

包括可出售小麦的饲料机会成本在内。

<a id="marginal-value"></a>
### 边际价值

```text
MV_i = DeltaER_i - DeltaC_i - DeltaFeed_i - DeltaLabor_i
```

一个更完整的战略评分也允许：

```text
MV_i += DeltaStrategic_i - DeltaRisk_i
```

<a id="value-per-land-time"></a>
### 单位土地时间价值

通过每单位有效占用土地和锁定时长所生产的增量价值来比较产品：

```text
MarginalScore_i =
    MV_i
    / (AddedEffectiveLand_i * LandLockTime_i)
```

笔记中也表达了同样的观点：

```text
Expected lifecycle profit per tile =
    (future sales revenue
     - seed/direct cost
     - labor cost
     - inventory/holding cost)
    / occupied land-days
```

<a id="additional-strategic-terms"></a>
### 额外战略术语

候选排序可能还包括：

- 市场风险系数；
- 价格崩盘系数；
- 战略价值；
- 保留/改善未来布局的期权价值；
- 施肥优化；
- 小麦应是自产还是外部采购。

---

<a id="9-historical-product-score-formulas"></a>
## 9. 历史产品评分公式

早期的一份策略表使用了特定产品评分的近似公式。其符号表示在此保留，因为它们是有效的实验先验，但原始资料中并未完全定义其括号结构。

|产品|记录的评分理念|
| --- | --- |
|甜瓜| `sum(q * dynamic_price) - 80 - fertilizer - labor / land_occupation` |
|胡萝卜| `sum(q * dynamic_price) - 20 - labor / land_occupation` |
|鸡蛋| `sum(q * dynamic_price) - 300 - labor * 1.6 / land_occupation` |
|羊毛| `sum(q * dynamic_price) - 500 - labor * 1.6 / land_occupation` |
|牛奶| `sum(q * dynamic_price) - 400 - labor * 1.6 / land_occupation` |
|草莓| `sum(q * dynamic_price) - 100 - labor / land_occupation` |
|小麦| `sum(q * dynamic_price) - 10 - labor / land_occupation` |
|番茄| `sum(q * dynamic_price) - 50 - labor / land_occupation` |

这些公式早于上述更一般的边际价值模型。因此，它们应被视为候选校准规则，而非第二个独立的经济引擎。

---

<a id="10-historical-demand-formulas"></a>
## 10. 历史需求公式

笔记中还包含特定产品的需求估算。其缩写（`Dm`, `Npc`, `Nfm`, `Nb`, `Nbs`, `Ny`, `Np`, `Ni`, `Ns`, `Nic`, `q`）在原始资料中未完全定义，因此公式被保留而非重新解释。

|产品|记录的`Dtotal`公式|
| --- | --- |
|甜瓜| `Dtotal = 1/day` |
|胡萝卜| `Dtotal = Dm + 12 * Npc * q + 6 * Nfm * q` |
|鸡蛋| `Dtotal = Dm + 6 * Nb * q + 6 * Nbs * q` |
|羊毛| `Dtotal = Dm + 12 * Ny * q` |
|牛奶| `Dtotal = Dm + 6 * Np * q + 6 * Ni * q + 6 * Ns * q` |
|草莓| `Dtotal = Dm + 6 * Nb * q + 6 * Nic * q + 6 * Ns * q + 6 * Nfm * q + 6 * Ns * q` |
|小麦| `Dtotal = Dm + 6 * Ni * q + 6 * Nb * q + 6 * Ns * q + 6 * Nfm * q + 6 * Nb * q` |
|番茄| `Dtotal = Dm + 6 * Np * q + 6 * Nfm * q` |

重复项完全保持原样，不进行静默修正。

---

<a id="11-production-quantity-should-react-to-opponent-supply"></a>
## 11. 生产数量应响应对手的供应情况

对于对手未生产的商品，当足够土地资源可用时，仅比较一次商品评分。

如果对手已经生产，则：

```text
AdjustedGap = MarketGap - OpponentSupply
```

并重新评估额外生产仍具价值的程度。

在确定自身生产与销售时间之前，需跟踪对手的下一次收获日期和数量。

笔记中还定义了一个竞争利润概念：

```text
MarginMax = OurProfit - OpponentProfit
```

该概念可作为次要战略信号，但不应替代绝对盈利能力。

---

<a id="12-sell-decision--current-marginal-value-vs-retention-value"></a>
## 12. 销售决策 = 当前边际价值 vs 保留价值

不要仅仅因为库存存在就进行销售。

对于每一个待考虑的额外单位：

```text
CurrentMarginalSalePrice =
    P(CurrentMarketInventory + considered_unit_index - 1)
```

将其与保留该单位的价值进行比较：

```text
RetentionValue = max(
    FutureResaleValue,
    ProductionUseValue,
    SafetyStockValue
)
```

在以下情况下销售：

```text
CurrentMarginalSaleValue > RetentionValue
```

并当边际销售价值低于下个单位持有边际价值时停止。

---

<a id="13-time-discounted-future-resale-value"></a>
## 13. 时间折现的未来转售价值

未来的销售应进行折现，因为后期收到的现金比现在可用的现金价值更低。

笔记提出：

```text
FutureResaleValue(h) = E[P(t + h)] / (1 + r)^h
```

并采用一个实验性的机会成本估算值：

```text
r = ((CapitalPrepared + ExtraNetBenefit) / CapitalPrepared)^(1 / h) - 1
```

原文提到需评估多个`h`时间范围，包括下一个及最近的相关销售机会；其具体的平均方法并未完全说明。

---

<a id="14-cash-urgency-changes-the-sell-threshold"></a>
## 14. 现金紧迫性会改变销售阈值

定义来自必要支出的短期现金压力：

```text
CashUrgency =
    (NearTermRequiredSpend - CurrentCash)
    / NearTermRequiredSpend
```

然后随着现金紧迫性增加，降低正常的持有/销售阈值：

```text
AdjustedSellThreshold =
    BaseSellThreshold - CashUrgencyAdjustment
```

较早的笔记中还提到一个`lambda`系数作为现金需求因子。

这使得规划者在现金战略价值高于等待理论最佳市场价格时，能够提前销售。

---

<a id="15-control-price-impact-and-sale-quantity"></a>
## 15. 控制价格影响和销售数量

估算一次销售造成的价格损害：

```text
PriceImpactRate =
    (PriceBeforeSale - PriceAfterSale)
    / PriceBeforeSale
```

不要一次性销售超过短期市场可承受的量：

```text
SaleQuantity <= ShortTermAbsorbableDemand
```

选择最大销售数量，使得边际销售价值仍高于边际持有价值，**而不必要地导致价格崩溃**。

这明确回应了笔记中‘填满整个市场缺口’并不总是利润最大化行为的观点。

---

<a id="16-sell-before-expected-opponent-supply-when-profitable"></a>
## 16. 在对手供应预期到来前盈利时进行销售

对手成熟日期会形成销售窗口。

通用策略：

- 估算对手下一次收获/生产日期；
- 考虑在该供应到达前部分销售我们的库存；
- 避免等待进入由对手驱动的可预测价格下跌；
- 如果双方同时生产，应考虑迅速匹配或响应对手的发布，而不是盲目等待。

产品手册中的历史规则：

```text
if combined supply < shop consumption:
    sell n units before opponent's next maturity,
    subject to value constraints

if combined supply > shop consumption:
    prefer selling around maturity rather than accumulating excess stock
```

瓜类商品有特别激进的历史规则：在对手成熟前清空库存，若双方同时种植，则一旦对手销售即立即响应。

---

<a id="17-explicit-split-sale-comparison"></a>
## 17. 明确的分批销售比较

后期笔记定义了关于现在出售还是分割出售的具体测试标准。

定义：

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

当满足以下条件时，优先选择分割出售路径：

```text
(n + m) * P1 - x * P5
<
n * P1 + m * P4 - x * P3
```

解释：将当前立即抛售`n + m`与分别现在出售`n`、之后出售`m`的策略进行战略价值比较，同时考虑对手价格的相互作用。

---

<a id="18-inventory-overflow-formula"></a>
## 18. 库存溢出公式

在存储空间未满之前，明确估算所需的库存清仓数量：

```text
NeedSell = Shed + Carry + Incoming - 99
```

如果`NeedSell > 0`，至少必须出售或移除该数量的库存，以防止新到货的库存达到储藏空间上限。

这通过直接清仓数量，对来自`v3`继承的存储可行性逻辑进行了细化。

---

<a id="19-product-specific-inventory-policy"></a>
## 19. 产品特定库存政策

<a id="fertilizer"></a>
### 肥料

- 当不需要用于短期盈利性施肥时，优先立即出售；
- 避免长期储存，因为肥料是持续生产的，且外部需求较弱。

<a id="melon"></a>
### 甜瓜

- 避免长期储存；
- 立即出售或与对手进行时机对冲；
- 历史笔记中将甜瓜总产量限制在`120`附近；
- 历史甜瓜策略中允许甚至鼓励施肥。

<a id="wheat"></a>
### 小麦

主要储备用于饲料和应急操作：

```text
WheatReserve =
    5 * animal_q
    - WheatExpectedToMatureInNext5Days
```

应出售多余的小麦，而不是长期占用大量储藏空间。

同时比较自产小麦与市场购买小麦的优劣。

<a id="egg"></a>
### 鸡蛋

- 如果没有相关店铺，不应保留不必要的鸡蛋库存；
- 在面包店/早餐店有需求时，保留大约一天的需求量；
- 历史动物政策每日使用`CARE`作为基准。

<a id="carrot"></a>
### 胡萝卜

- 没有宠物咖啡馆需求时，应出售而非持有；
- 当有宠物咖啡馆/农场市场的需求时，保留大约两天的需求量；
- 避免大量长期库存；
- 将其视为周转期短的产品；
- 历史规则：不进行施肥。

<a id="tomato"></a>
### 番茄

- 如果成熟番茄植株已经确保了后续补给，可以更激进地出售库存；
- 历史计划建议：在`T8`左右施肥，收获时间在`T9`和`T11`左右。

<a id="strawberry"></a>
### 草莓

- 当有相关店铺时，保留大约两天的**净**需求量；
- 优先选择小批量出售，以避免不必要的价格损失；
- 历史时间安排建议：在`T10`左右施肥，收获时间在`T12`，施肥时间在`T14`，收获时间在`T16`。

<a id="milk"></a>
### 牛奶

- 当有相关需求时，保留大约两天的净需求量；
- 如果没有相关店铺，且一头奶牛即将产奶量增加时，应提高当前牛奶的销售优先级；
- 优先选择小批量出售；
- 历史规则：以高价出售；
- 历史护理计划在`CARE`附近跳过`T5–T7`。

<a id="wool"></a>
### 羊毛

- 在等待毛线需求时，应保留羊毛；
- 如果没有毛线需求，可考虑出售。
- 历史护理计划每日使用，除`T5`之外的时段外。

---

<a id="20-inventory-priority-classes"></a>
## 20. 库存优先级类别

笔记还将库存分为五个大类。

<a id="class-1--operating-inventory-only"></a>
### 类别1 — 仅限运营库存

`Wheat`

保留饲料和应急储备，但不要让多余的麦子在棚内长期滞留。

<a id="class-2--fast-turnover"></a>
### 类别2 — 快速周转

`Carrot`

默认采用短期持有周期；只有在商店需求强劲时，才增加短期库存。

<a id="class-3--balanced"></a>
### 类别3 — 平衡类

`Tomato`, `Egg`

可以储存，但通常不会获得棚内最高优先级。保留主要取决于下一个需求窗口。

<a id="class-4--high-value-timing-inventory"></a>
### 类别4 — 高价值时机库存

`Strawberry`, `Milk`, `Wool`

当需求确认且未来短缺可预测时，应给予这些产品更高的存储优先级，并避免低价大批量清仓。

<a id="class-5--avoid-long-holding"></a>
### 类别5 — 避免长期持有

`Melon`, `Fertilizer`

优先周转，因为甜瓜缺乏稳定的商店需求，而肥料是持续再生的。

---

<a id="21-seed--animal-deployment-capacity-constraint"></a>
## 21. 种子/动物部署能力约束

不要购买超过当前可部署容量所能吸收的立即可部署生产量。

历史约束：

```text
sum(seed_units_to_deploy) + number_of_animals_to_place
<= available_free_tiles
```

从种子单位/结构到占用格子的精确转换，仍然取决于生产类型以及从`v3`继承的部署模型。

---

<a id="22-animal-action-ordering"></a>
## 22. 动物行动排序

当动物即将进行生产访问时，笔记更倾向于：

```text
FEED
-> HARVEST
-> CARE
-> COLLECT_FERTILIZER
```

这比从`v3`继承的依赖感知动物任务分组更为具体。

后期维护应在动物不再有盈利生产时停止。一个具体的历史标准是：

```text
if next useful production is beyond the remaining horizon
and fertilizer value < maintenance cost:
    stop FEED / CARE
```

通用v3末期规则仍决定最终可行性。

---

<a id="23-abandonment--liquidation-trigger-from-expected-price"></a>
## 23. 从预期价格出发的放弃/清仓触发条件

不要仅仅因为生产已经存在就维持它。

如果：

```text
ExpectedMarketValue
< MaintenanceCost + HarvestCost + CleanupCost
```

应开始清仓或放弃该生产，而不是继续投入劳动。

历史笔记还建议在倒数第二天开始大规模清仓。v3的最终现金结算可行性仍是更强的硬性约束。

---

<a id="24-recompute-on-new-shops"></a>
## 24. 新商店出现时重新计算

当新商店出现时，应立即重新计算所有受影响产品的市场需求和经济情况。

这包括：

- 目标生产数量；
- 预期短缺；
- 库存储备；
- 销售时机；
- 土地使用；
- 动物与作物的分配。

`v3` 已经在经济相关商店变更时重新规划；`v4` 增加了要求必须重新计算**市场需求和边际价值模型**本身。

---

<a id="25-market-aware-product-specific-sell-behavior"></a>
## 25. 市场感知的特定产品销售行为

历史策略笔记包含以下产品级别的偏好：

- 胡萝卜/鸡蛋/小麦/番茄：在需要现金时提前出售；
- 羊毛：在可行时等待纱线再出售；
- 牛奶/草莓：偏好高价窗口；
- 甜瓜：立即出售或在对手供应前出售；
- 所有产品：当库存容量紧张时，应按利润优先顺序出售，而非按FIFO或任意顺序。

这些是当完整边际出售模型过于昂贵或不确定时的备用启发式方法。

---

<a id="26-core-strategic-chain"></a>
## 26. 核心战略链

v4经济层可以总结为：

```text
shops define demand
-> own + opponent production define future supply
-> future supply and demand define future market inventory
-> market inventory defines expected price
-> expected price defines marginal revenue
-> marginal revenue minus direct/feed/labor/land/risk costs defines marginal value
-> marginal value decides what to produce, how much to produce, what to hold, and what to sell
```

这条链是v4的核心新思想。

---

<a id="key-invariants-added-by-v4"></a>
## v4新增的关键不变量

- 绝不超过`14`工人的数量。
- 不要雇佣其边际经济价值低于边际雇佣成本的工人。
- 在可行的情况下，将高维护成本的动物保留在首选中心附近动物区内部。
- 在该保留规则生效期间，必须保留中央`2 x 2`免受长期作物的影响。
- 不要让首选土地购买日期绕过来自`v3`继承的盈利能力、现金流、路线可行性或终局可行性。
- 如果明确的运营现金流底线将被违反，则不得购买土地。
- 在决定生产与销售时，需预测对手产量和市场时机。
- 不要假设填补整个市场短缺能最大化利润。
- 将出售一个单位的边际价值与持有该单位的边际价值进行比较。
- 当追加单位会导致价格影响过大时，限制销售规模。
- 仅在具有饲料、需求或战略价值时，才保留产品特定的安全库存。
- 使用`NeedSell = Shed + Carry + Incoming - 99`来量化紧急变现。
- 停止维持那些剩余预期市场价值无法覆盖其剩余运营成本的生产活动。

---

<a id="what-v4-changes-relative-to-v3"></a>
## v4相较于v3的变更

`v3`使规划器在内部保持一致性。`v4`在此一致规划器之上增加了更明确的**经济政策**：

1. 严格的工人和空间布局约束；
2. 战术开局与土地扩张的优先级；
3. 明确的对手产量预测；
4. 基于未来库存的价格预测；
5. 每单位土地时间的边际生产价值；
6. 雇佣工人的边际劳动价值；
7. 保留价值与时间折现销售价值；
8. 考虑价格影响的分批销售；
9. 产品特定的库存储备与周转类别；
10. 具体的现金流底线、溢出和变现规则。

历史表中记录的固定时间与数量是**可作为基准的启发式方法**，而来自`v3`继承的可行性与盈利能力规则仍为最终门槛。


---

<a id="navigation"></a>
## 导航

[← 上一版本](heuristic_ideas_v3.zh-CN.md) · [最终整合版本 →](heuristic_ideas_final.zh-CN.md)
