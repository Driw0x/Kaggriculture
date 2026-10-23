[English](getting_started.md) | [Français](getting_started.fr.md) | [简体中文](getting_started.zh-CN.md)

[项目 README](../README.zh-CN.md)

<a id="kaggriculture-getting-started"></a>
# Kaggriculture：入门指南

本指南将带您一步步完成构建代理、本地测试以及将其提交至Kaggle上的Kaggriculture竞赛的过程。

有关游戏规则、作物/动物/商店表格、价格函数以及回合处理顺序的完整说明，请参见[game_rules.md](game_rules.zh-CN.md)。

<a id="game-overview"></a>
## 游戏概览

Kaggriculture是一款两人参与的农场模拟游戏。每位玩家管理一座农场，通过购买种子和牲畜、种植、浇水、收获、饲养动物、雇佣助手以及在动态市场中交易等方式，力争在固定季节内赚取最多的金币。

- **农场** — 每位玩家拥有一个 `boardSize` × `boardSize` 的网格（默认为 10 × 10），被划分为四个 5 × 5 的区域。游戏开始时仅解锁西北（NW）区域；其余三个区域（`NE`、`SW`、`SE`）可通过 `BUY_LAND` 购买，价格分别为 $1k / $2k 和 $4k。
- **初始资金** — `startingMoney` 默认为 3000 美元
- **农民与农工** — 每位玩家拥有一个主农民，每日最多可雇佣 N 名农工。雇佣成本为 `farmHandCostMult * fib(n)`，其中 `n` 为当日已雇佣的农工数量；默认值为 `farmHandCostMult = 1` 时，成本为 `1, 1, 2, 3, 5, 8, 13, 21, ...`，每日开始时重置。每个单位独立在每回合行动
- **作物** — 小麦、胡萝卜、番茄（持续性）、草莓（持续性）、西瓜。每种作物均有独立的种子成本、生长周期、产量曲线和基础售价（详见 [game_rules.md](game_rules.zh-CN.md) 中的物体类型表）
- **浇水加成** — 对一次性作物，在加成窗口期间（从 `ceil(max_yield_day / 2)` 开始）浇水，可每日增加 1 单位可收获产量。`FERTILIZE` 会在接下来的 3 天内将该加成翻倍。对于持续性作物，按计划生产默认产量为 1，若当日同时施肥和浇水，则产量翻倍至 2
- **动物** — 鹅（产蛋，需有鸡舍）、牛（产奶，需有牧场）、羊（产毛，需有牧场）。每日必须喂食小麦；`CARE` 每日喂养并照料后增加 +1，该值在下次计划生产时全额结算；`COLLECT_FERTILIZER` 每日为每头动物收集 1 单位肥料。与作物不同，只要持续喂养，动物将无限产生成果——`max_held` 对未收获的产品数量进行上限限制，而非总产量
- **浇水与喂食** — 植物必须每日浇水，动物必须每日喂食。连续两天未完成每日结束时的刷新操作，会导致植物变为杂草且动物逃脱（无法恢复）。种植日即视为首次未浇水日
- **衰减** — 一旦植物超过其最大寿命（一次性作物为 `max_yield_day` 之后的第二天，持续性作物为累计产量上限之后的第二天），`yield_units` 每隔两回合减少 1，直至归零，此时该格子变为杂草
- **杂草** — 每个空闲且解锁的格子在每日结束时以 `weedSpawnChance`（默认值为 0.005）的概率生成一株杂草；可通过 `DIG` 清除
- **棚舍** — 非种子类物品库存上限为 100 项。每日结束时超出上限的物品将被丢弃。种子存放在独立槽位（无上限，不会被 `PICKUP` 收集——`PLANT` 会直接消耗它们）
- **市场** — 种子、动物以及`BUY_PRODUCT`订单的固定价格；收获产品的销售价格会根据市场库存动态变化。在共享初始库存`I0`时，价格为`base`，随着库存减少而上涨，随着库存增加而下跌，使用每种资源的形状函数（`linear`、`sq`、`sqrt`或`log`），该函数可在`I0`两侧不同——因此过剩会严重冲击高端商品（草莓、西瓜、牛奶、羊毛），将其价格压至1美元，而基础商品则更温和地吸收过剩（参见[game_rules.md](game_rules.zh-CN.md)中的价格函数表）。只有小麦和化肥可以通过`BUY_PRODUCT`买回；所有产品都可以通过`SELL`出售。每回合，每个玩家最多处理`maxMarketOrdersPerTurn`（默认值为10）个订单；超出部分将被静默丢弃
- **城镇** — 城镇中心始终产生需求：每 `townCenterSellInterval` 回合（默认 24，即每天一次），消耗每种非肥料商品各 1 单位，整个季节保持不变。每 `townShopUnlockInterval` 天解锁额外商店（默认 3；均匀随机且**有放回**抽取，因此允许重复，最多 8 个实例）。每个已解锁商店实例每 `townShopSellInterval` 回合（默认 4），消耗其需求的每种商品各 1 单位；单商品商店消耗量为 2 倍。参见 [game_rules.md](game_rules.zh-CN.md) 的城镇建筑表。
- **季节时长** — 默认为每天24回合×30天=720回合
- **胜利条件** — 季节结束时银行中金币数量最多；可能出现平局

<a id="your-agent"></a>
## 您的代理

您的代理是一个函数，接收一个观察结果并返回一个动作字典。

**观察字段：**
- `player` — 您的玩家索引（0或1）
- `step` — 当前回合（从0开始索引；由kaggle-environments框架提供）
- `day` — 当前游戏日（从0开始索引）
- `hour` — 一天内的当前回合（从0开始索引，范围为0到`turnsPerDay`-1）
- `farms` — 包含每个玩家一条记录的列表（公开；两个农场均可见）。每条记录包含：
  - `money` — 当前银行余额
  - `tiles` — 一个二维数组，按 `tiles[y][x]` 索引。每个方格是 `None`（空且解锁），`"LOCKED"`（锁定象限），一个植物字典（`kind="PLANT"`，`crop`，`planted_day`，`watered_today`，`consecutive_unwatered`，`yield_units`，`max_lifespan_step`，`fertilized_until_day`），一个杂草字典（`kind="WEED"`），或一个动物-建筑字典（`kind="COOP"` 或 `"PASTURE"`，可选地包含 `animal`，`placed_day`，`yield_units`，`fed_today`，`consecutive_unfed`，`cared_today`，`fertilizer_available`，`pending_care_bonus`）
  - `farmer` — `[x, y]` 主农夫的位置（x = 列，y = 行）
  - `hands` — 今日所有雇佣农工的`[x, y]`位置列表
  - `unlocked_quadrants` — `["NW", "NE", "SW", "SE"]`的子集
  - `hires_today` — 到目前为止已雇佣的手数（驱动下一个HIRE成本）
- `private` — 仅属于你的玩家；对手的私有状态是隐藏的：
  - `shed` — `{item: count}` 用于储存的收获品、动物和肥料
  - `seeds` — `{crop: count}`；种子存放在自己的槽位中，并直接被`PLANT`消耗
  - `inventories` — `[main_farmer_inv, hand1_inv, ...]`；田间携带的单位库存
- `market` — 共享：
  - `inventory` — `{product: int}` 当前市场供应量
  - `prices` — `{product: int}` 当前单位售价（四舍五入，向下取整为1）
- `town` — 共享：`unlocked_shops` — 当前活跃店铺名称列表；名称可能重复（店铺是带放回抽样的），每个条目独立消耗

**操作格式：**

```py
{
  "farmer": [op, ...args],          # one main-farmer op this turn
  "hands":  [[op, ...args], ...],   # one op per hired hand, in hands order
  "market": [[op, ...args], ...],   # ordered list of market orders, capped at maxMarketOrdersPerTurn
}
```

农民/手动操作：
- 移动：`"NORTH"`, `"SOUTH"`, `"EAST"`, `"WEST"`, `"PASS"`。锁定区域是可通行的——单位可以穿越未购买的区域，但不能在该区域执行操作
- 棚屋/库存：`"PICKUP" <item> [n]`（从棚屋获取），`"PLACE" <item> [n]`（当站在匹配结构上时将动物放置于该结构，或当相邻时将物品丢入棚屋），`"DROP"`（当与棚屋相邻时，将全部库存倾倒至棚屋；超出`shedCapacity`的部分被丢弃）。"与棚屋相邻"指站在四个中心格子之一：`(4,4)`, `(5,4)`, `(4,5)`, `(5,5)`。棚屋本身不在`tiles`中。
- 植物：`"PLANT" <crop>`, `"WATER"`, `"HARVEST"`, `"FERTILIZE"`
- 动物：`"BUILD_COOP"`, `"BUILD_PASTURE"`, `"FEED"`, `"COLLECT_FERTILIZER"`, `"CARE"`
- 地形：`"DIG"`（移除当前格子中的植物、杂草或*空*的鸡舍/牧场；若结构上已有动物，则无法挖掘）

市场操作：`["BUY_SEED", crop, n]`, `["BUY_PRODUCT", item, n]`, `["BUY_ANIMAL", animal, n]`, `["SELL", item, n]`, `["HIRE"]`, `["BUY_LAND"]`。无效操作将静默执行无操作。

**示例 — 小麦循环：**

对于小麦（`first_yield_day = 2`, `max_yield_day = 4`），浇水奖励窗口为第2至第4天。我们播种，在窗口期间浇水，并在第2天或之后收获。

```python
def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    market = []
    if private["seeds"].get("WHEAT", 0) == 0 and me["money"] >= 10:
        market.append(["BUY_SEED", "WHEAT", 1])
    # Sell any wheat sitting in the shed.
    wheat_in_shed = private["shed"].get("WHEAT", 0)
    if wheat_in_shed > 0:
        market.append(["SELL", "WHEAT", wheat_in_shed])

    if tile is None and private["seeds"].get("WHEAT", 0) > 0:
        return {"farmer": ["PLANT", "WHEAT"], "hands": [], "market": market}
    if isinstance(tile, dict) and tile.get("kind") == "PLANT":
        crop_age = obs["day"] - tile["planted_day"]
        if crop_age >= 2:  # WHEAT first_yield_day = 2; harvest as soon as possible
            return {"farmer": ["HARVEST"], "hands": [], "market": market}
        if not tile["watered_today"]:
            return {"farmer": ["WATER"], "hands": [], "market": market}

    return {"farmer": ["PASS"], "hands": [], "market": market}
```

对于更完整的示例（以及胡萝卜、番茄、草莓和蜜瓜每种作物的产量和成本详情），请参阅[game_rules.md](game_rules.zh-CN.md)中的‘对象类型’和‘快速入门’部分。

<a id="test-locally"></a>
## 本地测试

从PyPI安装环境（任何包含Kaggriculture的较新版本）：

```bash
pip install -U kaggle-environments
```

从Python或笔记本中运行游戏——你可以直接传递代理函数，或传递`.py`文件的路径：

```python
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent, "random"])  # or env.run(["main.py", "random"]) to load from a file

# View result
final = env.steps[-1]
for i, s in enumerate(final):
    print(f"Player {i}: reward={s.reward}, status={s.status}")

# Render in a notebook
env.render(mode="ipython", width=1200, height=800)

# Or dump a replay JSON for the visualizer / offline analysis
import json
with open("replay.json", "w") as f:
    json.dump(env.toJSON(), f)
```

有三个内置代理可通过名称访问：`"pass"`, `"random"`, 和 `"starter"`（一个确定性基线）。

<a id="set-up-the-kaggle-cli"></a>
## 设置Kaggle CLI

安装CLI：

```bash
pip install kaggle
```

你需要一个Kaggle账户——如果没有，请在https://www.kaggle.com注册。然后在"API"部分点击**"生成新令牌"**，下载你的API凭据至https://www.kaggle.com/settings/api。

**推荐：API令牌文件。** 将令牌字符串保存至`~/.kaggle/access_token`：

```bash
mkdir -p ~/.kaggle
# Paste the token from the Kaggle settings UI into this file
nano ~/.kaggle/access_token
chmod 600 ~/.kaggle/access_token
```

其他认证方法：
- **OAuth（浏览器流程）：** `kaggle auth login`
- **环境变量：** `export KAGGLE_API_TOKEN=xxxxxxxxxxxxxx`

验证CLI已正确配置：

```bash
kaggle competitions list -s "kaggriculture"
```

<a id="find-the-competition"></a>
## 找到竞赛

```bash
kaggle competitions list -s "kaggriculture"
kaggle competitions pages kaggriculture
kaggle competitions pages kaggriculture --content
```

<a id="accept-the-competition-rules"></a>
## 接受竞赛规则

在提交前，你**必须**接受Kaggle网站上的规则。导航至`https://www.kaggle.com/competitions/kaggriculture`并点击**"加入竞赛"**。

验证你已加入：

```bash
kaggle competitions list --group entered
```

<a id="download-competition-data"></a>
## 下载竞赛数据

```bash
kaggle competitions download kaggriculture -p kaggriculture-data
```

<a id="submit-your-agent"></a>
## 提交你的代理

你的提交必须在根目录包含一个`main.py`，其中包含一个`agent`函数。

**单文件代理：**

```bash
kaggle competitions submit kaggriculture -f main.py -m "Wheat loop v1"
```

**多文件代理** — 以 `main.py` 为根目录打包成 tar.gz 文件:

```bash
tar -czf submission.tar.gz main.py helper.py model_weights.pkl
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Multi-file agent v1"
```

**笔记本提交：**

```bash
kaggle competitions submit kaggriculture -k YOUR_USERNAME/kaggriculture-agent -f submission.tar.gz -v 1 -m "Notebook agent v1"
```

<a id="monitor-your-submission"></a>
## 监控您的提交

检查提交状态：

```bash
kaggle competitions submissions kaggriculture
```

注意输出中的提交 ID —— 您将在回合中使用它。

<a id="list-episodes"></a>
## 列出回合

一旦您的提交已进行了一些游戏：

```bash
kaggle competitions episodes <SUBMISSION_ID>
```

用于脚本的 CSV 输出：

```bash
kaggle competitions episodes <SUBMISSION_ID> -v
```

<a id="download-replays-and-logs"></a>
## 下载对战回放和日志

下载某回合的回放 JSON 文件（用于可视化或分析）：

```bash
kaggle competitions replay <EPISODE_ID>
kaggle competitions replay <EPISODE_ID> -p ./replays
```

下载代理日志以调试代理行为：

```bash
# Logs for the first agent (index 0)
kaggle competitions logs <EPISODE_ID> 0

# Logs for the second agent (index 1)
kaggle competitions logs <EPISODE_ID> 1 -p ./logs
```

<a id="check-the-leaderboard"></a>
## 查看排行榜

```bash
kaggle competitions leaderboard kaggriculture -s
```

<a id="typical-workflow"></a>
## 典型工作流程

```bash
# Test locally
python -c "
from kaggle_environments import make
env = make('kaggriculture', debug=True)
env.run(['main.py', 'random'])
print([(i, s.reward) for i, s in enumerate(env.steps[-1])])
"

# Submit
kaggle competitions submit kaggriculture -f main.py -m "v1"

# Check status
kaggle competitions submissions kaggriculture

# Review episodes
kaggle competitions episodes <SUBMISSION_ID>

# Download replay and logs
kaggle competitions replay <EPISODE_ID>
kaggle competitions logs <EPISODE_ID> 0

# Check leaderboard
kaggle competitions leaderboard kaggriculture -s
```
