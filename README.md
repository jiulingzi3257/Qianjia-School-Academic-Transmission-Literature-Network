# 乾嘉学派学术传承文献网络 / Qianjia School Academic Transmission Literature Network

> 构建乾嘉学派学术传承文献网络，锚定近现代中文学术诚信标准，为 AI 时代的古籍整理提供可计算的规则底座。
> Building a scholarly transmission network of the Qianjia (Qianlong-Jiaqing) School of Qing philology to anchor modern Chinese academic integrity standards, and to provide a computable rule-base for classical text processing in the AI era.

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Standard: GB/T 7714-2025](https://img.shields.io/badge/Standard-GB%2FT%207714--2025-blue.svg)](https://openstd.samr.gov.cn/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

---

## 目录 / Table of Contents

- [项目概述 / Overview](#项目概述--overview)
- [核心创新点 / Key Innovations](#核心创新点--key-innovations)
- [数据规模 / Data Scale](#数据规模--data-scale)
- [文件结构 / File Structure](#文件结构--file-structure)
- [节点表字段 / Node Table Fields](#节点表字段--node-table-fields)
- [边表字段 / Edge Table Fields](#边表字段--edge-table-fields)
- [权重计算方法 / Weight Calculation](#权重计算方法--weight-calculation)
- [网络统计 / Network Statistics](#网络统计--network-statistics)
- [快速开始 / Quick Start](#快速开始--quick-start)
- [分析代码模块 / Analysis Modules](#分析代码模块--analysis-modules)
- [使用方法 / Usage](#使用方法--usage)
- [引用 / Citation](#引用--citation)
- [许可证 / License](#许可证--license)
- [联系方式 / Contact](#联系方式--contact)

---

## 项目概述 / Overview

**中文**：本项目构建了清代乾嘉学派学术传承的文献网络，包含 **40 个文献节点** 与 **41 条关系边**，覆盖从先秦原典（《说文解字》《尔雅》《广韵》）到近现代语文规范化著作（黎锦熙《新著国语文法》《国语辞典》）的学术传承脉络。节点著录严格遵循 GB/T 7714-2025《信息与文献 参考文献著录规则》（武汉大学牵头编制，2026 年 7 月 1 日实施），边表关系设计参考新国标对"图书中的析出文献"的灵活化规定。仓库同时提供完整的 Python 社会网络分析（SNA）管线，可复现所有指标与可视化报告。

**English**: This project constructs a scholarly transmission network of the Qianjia School of Qing-dynasty philology, containing **40 literature nodes** and **41 relational edges**, spanning from pre-Qin classics (*Shuowen Jiezi*, *Erya*, *Guangyun*) to modern Chinese language standardization works (Li Jinxi's *New Grammar of the National Language*, *Mandarin Dictionary*). Node cataloging strictly follows **GB/T 7714-2025** *Information and Documentation — Bibliographic References* (led by Wuhan University, effective July 1, 2026). The repository also ships a complete Python social-network-analysis (SNA) pipeline reproducing all metrics and visualizations.

---

## 核心创新点 / Key Innovations

1. **双轨脉络 / Dual-track lineage**：黎锦熙代表的「国语运动与语文规范化」路径，与袁吉六等地方教育家代表的「教育传承」路径，共同构成乾嘉学术诚信精神向现代转化的双轨脉络。
2. **国标驱动 / GB/T 7714-2025-driven**：节点著录严格遵循 GB/T 7714-2025；边表设计利用新国标对析出文献标识符的灵活化处理（不再强制 [A]，可归入 [M]）。
3. **AI 规则底座 / Computable rule-base for AI**：以文献网络锚定学术诚信规则，减少 AI 幻觉，使乾嘉"无征不信"传统转化为可计算的 AI 训练约束。
4. **可复现分析管线 / Reproducible analysis pipeline**：从 xlsx 源数据到 17 份分析 CSV、交互式 HTML 报告，全部由 `run_analysis.py` 一键复现。/ From xlsx source to 17 result CSVs and interactive HTML reports, all reproducible via `run_analysis.py`.

---

## 数据规模 / Data Scale

| 指标 / Metric | 数值 / Value |
| --- | --- |
| 节点数 / Nodes | 40（NODE-001 ~ NODE-040） |
| 边数 / Edges | 41（E-001 ~ E-041） |
| 节点层级 / Node Levels | 一级（完整著作）· 二级（单篇析出）· 三级（残卷） |
| 关系大类 / Relation Categories | 版本源流 · 注疏阐释 · 学术传承 · 方法支撑 · 引文参考 |
| 分析产物 / Analysis outputs | 17 份 CSV + 交互式 HTML 报告 |

---

## 文件结构 / File Structure

```
.
├── 乾嘉学派学术传承网络（GB_T_7714-2025）.xlsx   # 主数据：节点表 + 边表
├── gephi_nodes.csv                             # Gephi 节点导入（40 行）
├── gephi_edges.csv                             # Gephi 边导入（41 行）
├── 乾嘉学派学术传承网络节点表1.csv              # 节点表 CSV 导出
├── 乾嘉学派学术传承网络边表1.csv                # 边表 CSV 导出
├── run_analysis.py                             # SNA 分析入口
├── config.py / data_loader.py                  # 配置与数据加载
├── topology.py / centrality.py                  # 拓扑与中心性
├── communities.py / lineage.py                 # 社区检测与师承溯源
├── multilayer.py / temporal.py                 # 多层网络与时代流向
├── robustness.py / visualization.py / report.py # 鲁棒性、可视化、报告
├── 00_数据质量核查.csv ~ 16_原典被承继谱.csv     # 17 份分析结果
├── network_interactive.html                    # 交互式网络图（pyvis）
├── report_standalone.html                      # 自包含分析报告（~2 MB）
├── 乾嘉学派...学术诚信标准的影响.pdf            # AI 文献综述
├── requirements.txt                            # Python 依赖
├── README.md / CITATION.cff / LICENSE / .gitignore
```

---

## 节点表字段 / Node Table Fields

| 字段 / Field | 说明 / Description | GB/T 7714-2025 |
| --- | --- | --- |
| ID | 节点唯一编号（NODE-XXX） | — |
| label | 文献题名 | 7.2 题名 |
| 责任者 / Creator | 文献责任者 | 7.1 责任者 |
| 责任方式 / Responsibility | 撰/注/编/主编等 | 7.1 责任者 |
| 版本 / Edition | 版本说明 | 7.4 版本 |
| 出版者 / Publisher | 出版机构 | 7.5.3 出版者 |
| 出版年 / Year | 公元纪年 | 7.5.4 出版日期 |
| 永久标识符 / Persistent ID | ISBN | 7.9 永久标识符 |
| 节点层级 / Node Level | 一级/二级/三级 | — |

---

## 边表字段 / Edge Table Fields

| 字段 / Field | 说明 / Description |
| --- | --- |
| 边ID / Edge ID | E-XXX |
| Source / Target | 源/目标节点编号 |
| Type | Directed（有向） |
| Weight | 双因子权重 |
| 关系大类 / Category | 五大类之一 |
| 关系细分 / Subtype | 师承授受/同派同源/方法继承/学术同源/直接引用/暗用化用/注疏解经/密码本支撑等 |
| 析出层级 / Analytic Level | 一级（版本层）/二级（阐释传承层）/三级（引用层） |
| 证据位置 / Evidence Location | 卷次/序/全书 |
| 证据类型 / Evidence Type | 文本内证/学术史定论/目录著录/后人推断 |

---

## 权重计算方法 / Weight Calculation

**公式**: 权重 = 关系类型基准值 + 证据类型修正值，限定在该关系类型上下限内。

| 关系大类 / Category | 权重区间 | 典型关系 |
| --- | --- | --- |
| 版本源流 / Version Lineage | 0.85 ~ 0.95 | 底本源流、增订衍生 |
| 注疏阐释 / Commentary & Exegesis | 0.85 ~ 0.92 | 注疏解经 |
| 学术传承 / Scholarly Transmission | 0.65 ~ 0.88 | 师承授受、同派同源、方法继承、学术同源 |
| 方法支撑 / Methodological Support | 0.75 ~ 0.88 | 密码本支撑 |
| 引文参考 / Citation Reference | 0.30 ~ 0.72 | 直接引用、暗用化用 |

---

## 网络统计 / Network Statistics

由 Gephi 与 Python（NetworkX）双重计算：

- 平均度 / Average Degree: **1.025**
- 网络直径 / Network Diameter: **5**
- 模块化系数 / Modularity: **0.521**（5 个社区）
- 平均路径长度 / Average Path Length: **2.05**
- 社区分布: 乾嘉核心派（绿）· 训诂辞书派（紫）· 古音学派（蓝）· 十三经原典（灰）· 近现代派（橙）

---

## 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.10+

### 一键复现 / Reproduce

```bash
# 1. 克隆仓库
# Clone the repository
git clone https://github.com/jiulingzi3257/Qianjia-School-Academic-Transmission-Literature-Network.git
cd Qianjia-School-Academic-Transmission-Literature-Network

# 2. 安装依赖
# Install dependencies
pip install -r requirements.txt

# 3. 运行完整分析管线
# Run the full analysis pipeline
python run_analysis.py
```

运行后会在当前目录生成 / 更新 `00_*.csv` ~ `16_*.csv` 分析结果、`network_interactive.html` 和 `report_standalone.html`。

---

## 分析代码模块 / Analysis Modules

| 模块 | 职责 |
| --- | --- |
| `data_loader.py` | 从 xlsx 读取节点表与边表，构建 NetworkX DiGraph |
| `topology.py` | 整体拓扑：节点数、边数、密度、直径、平均路径、度分布 |
| `centrality.py` | 度/接近/中介/特征向量中心性排行 |
| `communities.py` | Louvain 社区检测、社区画像、模块化系数 |
| `lineage.py` | 师承授受明线、最长溯源链、溯源深度排行 |
| `multilayer.py` | 析出层级交叉、跨层参与度、关系层对比 |
| `temporal.py` | 时代流向矩阵、时代援引画像、原典被承继谱 |
| `robustness.py` | 蓄意攻击/随机故障下的鲁棒性衰减曲线与半衰阈值 |
| `visualization.py` | pyvis 交互式网络图、matplotlib 静态图 |
| `report.py` | 汇总生成自包含 HTML 报告 |

---

## 使用方法 / Usage

### Gephi 可视化 / Gephi Visualization

1. 安装 Gephi（https://gephi.org）
2. 导入 `gephi_nodes.csv`（节点表）和 `gephi_edges.csv`（边表）
3. 运行 Statistics（平均度、模块化、路径长度）
4. 节点着色按 Modularity Class，大小按 Degree
5. 布局：ForceAtlas2（先勾选 "Prevent Overlap"，再调 "Approximate Repulsion"）

### 数据复用 / Data Reuse

- 节点表与边表可直接用于 NetworkX、igraph、Cytoscape 等工具
- 节点著录信息可作为古籍引用的 GB/T 7714-2025 规范模板
- 权重计算方法可迁移至其他学术传承网络构建

---

## 引用 / Citation

**中文**：

> 林俊森. 乾嘉学派学术传承文献网络数据集[DS/OL]. 2026. https://doi.org/10.5281/zenodo.XXXXXXX

**English**：

> Lin, J. (2026). *Qianjia School Academic Transmission Literature Network* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

> **注**：DOI 为预留位，正式发布后请替换。详见 `CITATION.cff`。

---

## 许可证 / License

本项目以 **CC0-1.0**（公共领域贡献）协议发布，可自由使用、修改和分发。
This project is released under **CC0-1.0** (Public Domain Dedication).

---

## 联系方式 / Contact

- 作者 / Author: 林俊森 / Lin Junsen
- 问题与建议 / Issues: https://github.com/jiulingzi3257/Qianjia-School-Academic-Transmission-Literature-Network/issues

---

*最后更新 / Last updated: 2026-10-26*
