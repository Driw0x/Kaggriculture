[English](heuristic_ideas_v1.md) | [Français](heuristic_ideas_v1.fr.md) | [简体中文](heuristic_ideas_v1.zh-CN.md)

[项目 README](../../README.zh-CN.md)

<a id="heuristic-ideas-v1--corrected-daily-planner"></a>
# 启发式想法 v1 — 修正版每日计划

[上一版本：无](#) · [下一版本 →](heuristic_ideas_v2.zh-CN.md)

> **系列规范**
>
> - `v1` 是启发式想法系列的完整基准版本。
> - `v2`、`v3` 和 `v4` 是对前一版本的**严格增量更新**。
> - 除非明确添加、替换或修正某条规则，否则增量版本会完整继承其直接前代版本。
> - 继承具有传递性：后续版本不会将更早的版本作为并行设计的父版本使用。
> - [`heuristic_ideas_final.md`](heuristic_ideas_final.zh-CN.md) 是整个链路之后的完整独立快照，且不关联任何代理。

<a id="identity"></a>
## 身份

|字段|值|
| --- | --- |
|版本| `v1` |
|原始来源| `detail_corrige` |
|关联代理| `chi12.py` |
|角色|启发式计划的完整基准|
|改进点| [`v2`](heuristic_ideas_v2.zh-CN.md) |

<a id="main-idea"></a>
## 核心理念

每日构建从当前游戏状态出发，将需求转化为优先级任务，将相关行动归类，添加所需后勤，分配路线与工人，然后执行，并在观察到状态变化时进行本地计划修复。

<a id="core-ideas"></a>
## 核心理念

<a id="1-plan-every-day-from-the-real-state"></a>
### 1. 每日计划基于真实状态

每天开始时，读取当前状态，并从实际存在的要素中重建可用工作：植物、动物、杂草、库存、工人、棚屋容量、市场需求以及可能的生产活动。

每日流程在概念上为：

`economy -> tasks -> placement -> priorities -> bundles -> logistics -> routes -> capacity/HIRE -> execution/replanning`

<a id="2-survival-work-comes-before-optimization"></a>
### 2. 生存工作优先于优化

必须保障的维护工作不能为了可选的利润而被牺牲：

- 当错过一天会导致生存问题时，必须浇水植物；
- 当错过一天会导致动物逃脱时，必须喂养动物；
- 在产出丢失或动物达到存储饱和前必须收获；
- 必须保护种植日的必要浇水。

这些行动被视为 `CRITICAL`。

<a id="3-separate-survival-production-yield-preparation-and-secondary-work"></a>
### 3. 将生存、生产、产量、准备和次要工作分开

并非所有任务都等同。计划器区分了以下几类任务：

- `CRITICAL`：防止损失或失败；
- `PRODUCTION`：必需的收获、种植、建造、放置或生产性喂养；
- `YIELD`：施肥、照料以及有益的额外浇水；
- `PREPARATION`：为未来生产所需挖掘或安装；
- `SECONDARY`：非紧急的肥料收集或杂草清除。

截止日期和经济价值会细化这些类别内的排序。

<a id="4-place-production-to-reduce-future-maintenance-cost"></a>
### 4. 将生产安排在降低未来维护成本的位置

选址不仅基于找到空地，候选地块会根据以下因素评分：

- 到棚屋的距离；
- 未来的维护访问频率；
- 与类似生产的邻近程度；
- 路线阻塞情况；
- 空间占用情况。

高维护成本的生产应靠近高效路线和棚屋入口。因此，动物对选址的敏感度高于简单的临时作物。

<a id="5-keep-dependent-actions-together"></a>
### 5. 保持依赖动作在一起

涉及同一地块的动作应尽可能形成一组。

典型组包括：

- `DIG -> PLANT -> WATER`;
- `BUILD -> PLACE -> FEED -> CARE` 用于新增动物；
- `HARVEST -> optional DIG -> PLANT -> optional FERTILIZE -> WATER` 用于重新种植。

规划器必须保留顺序约束，尤其是在相关情况下保留 `FERTILIZE before WATER` 和 `WATER before HARVEST`。

<a id="6-treat-logistics-as-part-of-the-plan"></a>
### 6. 将物流视为计划的一部分

只有当工人具备执行路线所需资源时，路线才是可行的。

因此，规划器应：

- 预留种子、肥料、动物和饲料；
- 当库存不足时创建采购依赖关系；
- 计算精确的取货数量；
- 在工人离开棚屋区域前加载路线资源；
- 跟踪收获后的未来工人库存；
- 在需要时安排返回和 `DROP` 动作。

<a id="7-protect-shed-capacity-before-a-required-drop"></a>
### 7. 在需要 DROP 之前保护棚屋容量

存储压力必须在它阻碍必要生产之前得到解决。

如果计划中的 `DROP` 会导致棚屋溢出，规划器应提前释放容量，例如通过出售库存、插入更早的 DROP 或重新分配路线。

不应仅仅为了避免棚屋压力而推迟必要的收获。

<a id="8-build-routes-around-urgency-and-locality"></a>
### 8. 根据紧迫性和地域性构建路线

路线从最紧迫的任务组开始，并添加附近兼容的工作，同时保持截止日期。

插入平衡：

- 行驶距离；
- 操作成本；
- 截止日期风险；
- 同一区域的机会；
- 同一类型的机会。

目标不是全局最优路线，而是能够按时完成重要工作的实用路线。

<a id="9-hire-exists-to-make-planned-work-feasible"></a>
### 9. HIRE 存在是为了使计划工作可行

容量规划确定现有工人是否能够执行所有重要路线。如果不能，规划器可以安排 `HIRE` 动作，并在工人可用的时钟周期后分配新工人。

只有在检查以下内容后，路线才被视为最终确定：

- 工人生成和可用性；
- 取货；
- 行驶和操作时间；
- 返回棚屋；
- 截止日期；
- 市场依赖关系；
- 棚屋容量。

<a id="10-replan-locally-when-reality-differs-from-the-plan"></a>
### 10. 当现实与计划不符时，局部重新规划

执行过程会持续检查假设是否仍然成立。

重要变化包括：

- 新商店或显著价格变动；
- 对手行为；
- 意外杂草；
- 收获/生产结果不同；
- `BUY` 或 `HIRE` 失败；
- 工人落后于进度；
- 库存或棚屋饱和。

当发生变更时，应尽可能保留已完成的工作、已支付的雇佣和有效路线，并仅重新构建受影响的未来工作。

<a id="11-respect-the-market-order-limit"></a>
### 11. 尊重市场订单限制

`SELL`、`BUY` 和 `HIRE` 动作共享每时钟周期最多 10 条订单的市场限制。

当法律允许时，可以合并相同的订单。如果超出限制，必须在保留关键依赖订单和截止日期订单的前提下，再处理较低优先级的经济订单。

<a id="12-end-of-game-liquidation-is-explicit"></a>
### 12. 游戏结束时的清算操作是明确的

最后一天不被视为普通的一天。

在`episodeSteps = 720`下，清算以及最终的`DROP`必须在第29天第22小时之前完成。规划者应确保没有重要的收获被遗漏，也没有工人库存被遗留在棚屋之外。

<a id="key-invariants"></a>
## 关键不变量

- 绝不允许新种植的作物缺少其必需的浇水操作。
- 绝不允许生存相关的`WATER`或`FEED`因可选工作而失败。
- 绝不允许在未配备完成所需资源的情况下安排路线。
- 绝不允许关键的`DROP`超出棚屋的容量。
- 绝不允许仅仅因为存储规划不佳就推迟必要的收获。
- 单个时间步长内绝不执行超过10个市场订单。
- 在重新规划过程中，必须保留已完成或仍然有效的作业。
- 必须在最后可玩的最后一天时间步长内完成最终清算。

<a id="what-v1-establishes"></a>
## v1版本确立的内容

`v1`是完整的参考规划器。它的唯一直接后继者是[`v2`](heuristic_ideas_v2.zh-CN.md)。所有后续行为都通过版本链进行继承，而不是将`v1`视为并行的父版本。


---

<a id="navigation"></a>
## 导航

上一版本：无 · [下一版本 →](heuristic_ideas_v2.zh-CN.md)
