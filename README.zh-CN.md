[English](README.md) | [Français](README.fr.md) | [简体中文](README.zh-CN.md)

<a id="kaggriculture"></a>
# Kaggriculture

为Kaggriculture竞赛在Kaggle上开发的AI智能体。

<a id="competition"></a>
## 竞赛

Kaggriculture是一个回合制策略竞赛，参与者开发自主智能体来管理农场、资源、生产以及市场互动。

本仓库的目标是开发、评估并迭代改进该竞赛中的智能体。

<a id="project-status"></a>
## 项目状态

本仓库现已作为**已结束项目的快照**保留。保留的成果如下：

- **启发式规划器：** `chi14.py`是重构启发式分支的最后一个经过验证的实现。`heuristic_ideas_v4`和`heuristic_ideas_final`仅作为设计参考保留；后续的实现尝试，包括`CHI16` / `chi_final`，未被保留为经过验证的后继版本。
- **学习型智能体：** 行为克隆和混合执行器被保留为实验性赛道，但学习型智能体未被保留用于自主竞赛使用。
- **公开衍生分支：** `jet6.py`（公开智能体10）是该分支最终保留的本地基准版本。

最终仓库状态中不包含`CHI16`或`chi_final`源智能体。

<a id="repository-map"></a>
## 仓库地图

|路径|用途|
| --- | --- |
| `src/agents/` |智能体实现|
| `src/learning/` |行为克隆模型、数据集、编码器和策略|
| `scripts/` |训练、评估和工具脚本|
| `experiments/` |实验结果与策略对比|
| `submissions/` |提交至Kaggle的智能体|
| `data/` |回放数据和处理后的学习数据集|
| `models/` |训练模型检查点和推理配置|
| `tests/` |自动化测试|
| `docs/` |游戏规则与智能体开发文档|
| `requirements.txt` |Python依赖项|
| `LICENSE` |Apache 2.0许可证|

<a id="setup"></a>
## 设置

克隆仓库：

```bash
git clone https://github.com/Driw0x/kaggriculture.git
cd kaggriculture
```

创建虚拟环境：

```bash
python -m venv .venv
```

在Windows上激活它：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖项：

```bash
pip install -r requirements.txt
```

<a id="documentation"></a>
## 文档

* [`docs/game_rules.md`](docs/game_rules.zh-CN.md) --- 完整的游戏规则和机制

* [`docs/getting_started.md`](docs/getting_started.zh-CN.md) --- 智能体开发、本地测试和Kaggle提交指南

* [`docs/game_mechanics_reference.md`](docs/game_mechanics_reference.zh-CN.md) --- 核心游戏机制、生产、动物、农场基础设施、工人、镇上商店及市场行为的参考说明。

* [`docs/chi_agents.md`](docs/chi_agents.zh-CN.md) --- 原始 CHI 启发式规划器谱系（截至 CHI10）及计时实验。

* [`docs/heuristic_agents.md`](docs/heuristic_agents.zh-CN.md) --- 从CHI12重构的启发式规划器分支，直至最终保留的CHI14实现，以及归档的v4/最终设计仅延续版本。

* [`docs/learning_agent.md`](docs/learning_agent.zh-CN.md) --- 基于学习的实验赛道、离线结果、自主评估，以及决定不将其保留用于进一步开发。

* [`docs/public_agent.md`](docs/public_agent.zh-CN.md) --- 公开衍生/参考智能体家族、来源、本地基准、被拒绝的实验，以及最终保留的公开智能体10基准。

* [`docs/agent_ideas.md`](docs/agent_ideas.zh-CN.md) --- 智能体想法的历史清单及其实施状态。


<a id="license"></a>
## 许可证

本项目遵循 Apache License 2.0 协议。

详情请参见 [`LICENSE`](LICENSE)。

<!-- multilingual-documentation -->

## 更多文档

- [docs/pseudo_code/heuristic_ideas_final.md](docs/pseudo_code/heuristic_ideas_final.zh-CN.md)
- [docs/pseudo_code/heuristic_ideas_v1.md](docs/pseudo_code/heuristic_ideas_v1.zh-CN.md)
- [docs/pseudo_code/heuristic_ideas_v2.md](docs/pseudo_code/heuristic_ideas_v2.zh-CN.md)
- [docs/pseudo_code/heuristic_ideas_v3.md](docs/pseudo_code/heuristic_ideas_v3.zh-CN.md)
- [docs/pseudo_code/heuristic_ideas_v4.md](docs/pseudo_code/heuristic_ideas_v4.zh-CN.md)
