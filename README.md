# 乾嘉学派学术传承文献网络 / Qianjia School Academic Transmission Literature Network

> 构建乾嘉学派学术传承文献网络，锚定近现代中文学术诚信标准，为 AI 时代的古籍整理提供可计算的规则底座。
> Building a scholarly transmission network of the Qianjia (Qianlong-Jiaqing) School of Qing philology to anchor modern Chinese academic integrity standards, and to provide a computable rule-base for classical text processing in the AI era.

[![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](http://creativecommons.org/publicdomain/zero/1.0/)
[![Standard: GB/T 7714-2025](https://img.shields.io/badge/Standard-GB%2FT%207714--2025-blue.svg)](https://openstd.samr.gov.cn/)

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
- [使用方法 / Usage](#使用方法--usage)
- [引用 / Citation](#引用--citation)
- [许可证 / License](#许可证--license)
- [联系方式 / Contact](#联系方式--contact)

---

## 项目概述 / Overview

**中文**：本项目构建了清代乾嘉学派学术传承的文献网络，包含 **40 个文献节点** 与 **41 条关系边**，覆盖从先秦原典（《说文解字》《尔雅》《广韵》）到近现代语文规范化著作（黎锦熙《新著国语文法》《国语辞典》）的学术传承脉络。节点著录严格遵循 GB/T 7714-2025《信息与文献 参考文献著录规则》（武汉大学牵头编制，2026 年 7 月 1 日实施），边表关系设计参考新国标对"图书中的析出文献"的灵活化规定。

**English**: This project constructs a scholarly transmission network of the Qianjia School of Qing-dynasty philology, containing **40 literature nodes** and **41 relational edges**, spanning from pre-Qin classics (*Shuowen Jiezi*, *Erya*, *Guangyun*) to modern Chinese language standardization works (Li Jinxi's *New Grammar of the National Language*, *Mandarin Dictionary*). Node cataloging strictly follows **GB/T 7714-2025** *Information and Documentation — Bibliographic References* (led by Wuhan University, effective July 1, 2026). The edge-table design references the new standard's flexible provisions for analytic entries in monographs (图书中的析出文献).

---

## 核心创新点 / Key Innovations

1. **双轨脉络 / Dual-track lineage**：黎锦熙代表的「国语运动与语文规范化」路径，与袁吉六等地方教育家代表的「教育传承」路径，共同构成乾嘉学术诚信精神向现代转化的双轨脉络。The path of "National Language Movement & Language Standardization" represented by Li Jinxi, together with the path of "Educational Transmission" represented by local educators such as Yuan Jiliu, jointly form the dual-track lineage of the Qianjia spirit of academic integrity transforming into modernity.
2. **国标驱动 / GB/T 7714-2025-driven**：节点著录严格遵循 GB/T 7714-2025，边表设计利用新国标对析出文献标识符的灵活化处理（不再强制 [A]，可归入 [M]）。Node cataloging strictly follows GB/T 7714-2025; the edge design exploits the new standard's flexible treatment of analytic-entry identifiers (no longer mandatorily [A], may fall under [M]).
3. **AI 规则底座 / Computable rule-base for AI**：以文献网络锚定学术诚信规则，以研学补充语料，减少 AI 幻觉，使乾嘉"无征不信"传统转化为可计算的 AI 训练约束。Anchoring academic-integrity rules via the literature network and supplementing corpus via study-tours (研学), this project reduces AI hallucination by turning the Qianjia "no evidence, no belief" (无征不信) tradition into computable constraints for AI training.

---

## 数据规模 / Data Scale

| 指标 / Metric | 数值 / Value |
| --- | --- |
| 节点数 / Nodes | 40（NODE-001 ~ NODE-040） |
| 边数 / Edges | 41（E-001 ~ E-041） |
| 节点层级 / Node Levels | 一级（完整著作）· 二级（单篇析出）· 三级（残卷） / Level 1 (monograph) · Level 2 (analytic entry) · Level 3 (fragment) |
| 关系大类 / Relation Categories | 版本源流 · 注疏阐释 · 学术传承 · 方法支撑 · 引文参考 / Version Lineage · Commentary & Exegesis · Scholarly Transmission · Methodological Support · Citation Reference |

---

## 文件结构 / File Structure

| 文件 / File | 说明 / Description |
| --- | --- |
| `乾嘉学派学术传承网络_已核对.xlsx` | 主数据文件（节点表 + 边表）/ Main data file (node sheet + edge sheet) |
| `gephi_nodes.csv` | Gephi 节点导入文件 / Gephi node import file |
| `gephi_edges.csv` | Gephi 边导入文件 / Gephi edge import file |
| `LICENSE` | CC0-1.0 协议全文 / Full text of CC0-1.0 |
| `README.md` | 本说明文件 / This README |

---

## 节点表字段 / Node Table Fields

| 字段 / Field | 说明 / Description | GB/T 7714-2025 |
| --- | --- | --- |
| ID | 节点唯一编号（NODE-XXX）/ Unique node ID | — |
| label | 文献题名 / Title of the work | 7.2 题名 / Title |
| 责任者 / Creator | 文献责任者 / Responsible creator | 7.1 责任者 |
| 责任方式 / Responsibility | 撰/注/编/主编等 / Author, annotator, compiler, editor-in-chief | 7.1 责任者 |
| 标识 / Type ID | 文献类型标识 [M] / Document type identifier | 7.3 文献类型标识 |
| 版本 / Edition | 版本说明 / Edition statement | 7.4 版本 |
| 出版地 / Place | 出版者所在地 / Place of publication | 7.5.2 出版地 |
| 出版者 / Publisher | 出版机构 / Publisher | 7.5.3 出版者 |
| 出版年 / Year | 公元纪年 / Publication year (CE) | 7.5.4 出版日期 |
| 细粒度定位 / Location | 卷次/篇名等 / Volume, chapter, etc. | 7.7 页码 |
| 永久标识符 / Persistent ID | ISBN / Persistent identifier | 7.9 永久标识符 |
| 获取路径 / Access Path | 数字化获取渠道 / Digital access channel | 7.8 获取和访问路径 |
| 访问日期 / Access Date | 电子资源访问日期 / Access date for electronic resources | 7.6 引用日期 |
| 备注 / Notes | 补充说明 / Supplementary notes | — |
| 节点层级 / Node Level | 一级/二级/三级 / Level 1/2/3 | — |

---

## 边表字段 / Edge Table Fields

| 字段 / Field | 说明 / Description |
| --- | --- |
| 边ID / Edge ID | 边唯一编号（E-XXX）/ Unique edge ID |
| 源节点ID / Source Node | 关系起点 / Source node of the relation |
| 目标节点ID / Target Node | 关系终点 / Target node of the relation |
| 关系大类 / Category | 五大类之一 / One of five categories |
| 关系细分 / Subtype | 师承授受/同派同源/方法继承/学术同源等 / Master-student, same school, method inheritance, academic affinity, etc. |
| 权重值 / Weight | 双因子计算结果 / Dual-factor calculated value |
| 析出层级 / Analytic Level | 一级（版本层）/二级（阐释传承层）/三级（引用层）/ Level 1 (version), Level 2 (exegesis/transmission), Level 3 (citation) |
| 证据位置 / Evidence Location | 卷次/序/全书等 / Volume, preface, whole book |
| 证据类型 / Evidence Type | 文本内证/学术史定论/目录著录/后人推断 / Internal textual evidence, scholarly consensus, catalog record, later inference |
| 备注 / Notes | 补充说明 / Supplementary notes |

---

## 权重计算方法 / Weight Calculation

**公式 / Formula**: 权重 = 关系类型基准值 + 证据类型修正值，限定在该关系类型上下限内。
Weight = relation-type baseline + evidence-type correction, bounded within the range of the relation type.

| 关系大类 / Category | 权重区间 / Weight Range | 典型关系 / Typical Relations |
| --- | --- | --- |
| 版本源流 / Version Lineage | 0.85 ~ 0.95 | 底本源流、增订衍生 / Textual base lineage, expanded derivation |
| 注疏阐释 / Commentary & Exegesis | 0.85 ~ 0.92 | 注疏解经 / Commentary on classics |
| 学术传承 / Scholarly Transmission | 0.65 ~ 0.88 | 师承授受、同派同源、方法继承、学术同源 |
| 方法支撑 / Methodological Support | 0.75 ~ 0.88 | 密码本支撑 / Codebook support |
| 引文参考 / Citation Reference | 0.30 ~ 0.72 | 直接引用、暗用化用 / Direct quotation, implicit adaptation |

---

## 网络统计 / Network Statistics

由 Gephi 计算 / Computed via Gephi:

- 平均度 / Average Degree: **1.025**
- 网络直径 / Network Diameter: **5**
- 模块化系数 / Modularity: **0.521**（5 个社区 / 5 communities）
- 平均路径长度 / Average Path Length: **2.05**
- 社区分布 / Communities: 乾嘉核心派（绿）· 训诂辞书派（紫）· 古音学派（蓝）· 十三经原典（灰）· 近现代派（橙） / Qianjia Core (green) · Exegetical-Dictionary (purple) · Historical Phonology (blue) · Thirteen Classics (grey) · Modern (orange)

---

## 使用方法 / Usage

### 网络可视化 / Network Visualization

1. 安装 Gephi（https://gephi.org）/ Install Gephi.
2. 导入 `gephi_nodes.csv`（节点表）/ Import `gephi_nodes.csv` (nodes).
3. 导入 `gephi_edges.csv`（边表）/ Import `gephi_edges.csv` (edges).
4. 运行统计指标（平均度、模块化、路径长度等）/ Run statistics (degree, modularity, path length, etc.).
5. 节点着色：按 Modularity Class / Color nodes by Modularity Class.
6. 节点大小：按度中心性（Degree）/ Size nodes by Degree centrality.
7. 布局：ForceAtlas2（先"防止重叠"，再"近似斥力"）/ Layout: ForceAtlas2 (first "Prevent Overlap", then "Approximate Repulsion").
8. 导出：文件 → 导出 → 图片 → PNG（4x 分辨率）/ Export: File → Export → Image → PNG (4x).

### 数据复用 / Data Reuse

- 节点表与边表可直接用于 NetworkX、igraph、Cytoscape 等网络分析工具 / Node & edge sheets work with NetworkX, igraph, Cytoscape, etc.
- 节点著录信息可作为古籍引用的规范模板 / Node catalog entries serve as a normative template for classical-text citation.
- 权重计算方法可迁移至其他学术传承网络构建 / The weight method is transferable to other scholarly-transmission network projects.

---

## 引用 / Citation

**中文 / Chinese**：

> 林俊森. 乾嘉学派学术传承文献网络数据集[DS/OL]. 2026. https://doi.org/10.5281/zenodo.XXXXXXX

**English**：

> Lin, J. (2026). *Qianjia School Academic Transmission Literature Network* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

> **注**：DOI 为预留位，正式发布后请替换。The DOI is a placeholder; replace it after formal publication.

---

## 许可证 / License

本项目以 **CC0-1.0**（公共领域贡献）协议发布，可自由使用、修改和分发，无需署名（学术惯例仍建议引用）。
This project is released under **CC0-1.0** (Public Domain Dedication). You may freely use, modify, and redistribute it without attribution (though scholarly convention recommends citation).

---

## 联系方式 / Contact

- 作者 / Author: 林俊森 / Lin Junsen
- 问题与建议 / Issues & suggestions: 通过 GitHub Issues 提交 / Please submit via GitHub Issues.

---

*最后更新 / Last updated: 2026-10-26*
