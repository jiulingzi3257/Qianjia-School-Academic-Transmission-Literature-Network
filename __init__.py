# -*- coding: utf-8 -*-
"""乾嘉学派学术传承文献网络建模分析工具包。

模块划分
--------
- config        路径、关系类型、成书时代分组等全局配置
- data_loader   CSV 读取、数据质检、有向加权图构建
- topology      整体网络拓扑指标
- centrality    节点中心性及与 Gephi 预算指标的一致性校验
- communities   Louvain 社区、k-核分解与核心-边缘识别
- lineage       学术传承谱系与关键师承路径
- multilayer    五大关系类多层子网络对比
- robustness    蓄意攻击 / 随机失效鲁棒性仿真
- temporal      成书时代维度的跨代传承分析
- visualization matplotlib 静态图与 pyvis 交互网络图
- report        中文 HTML 分析报告组装
"""

__version__ = "1.0.0"
