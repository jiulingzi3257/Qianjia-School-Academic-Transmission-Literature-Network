# -*- coding: utf-8 -*-
"""按关系大类拆解的多层（multiplex）网络对比分析。"""
from __future__ import annotations

from collections import Counter

import networkx as nx
import pandas as pd

from . import config


def layer_metrics(g: nx.DiGraph) -> tuple[pd.DataFrame, dict]:
    """逐层统计规模、密度、枢纽节点、证据结构。"""
    n_total = g.number_of_nodes()
    label = {n: g.nodes[n].get("Label", n) for n in g}
    layers: dict[str, nx.DiGraph] = {}
    rows = []
    for cat in config.RELATION_CATEGORIES:
        edges = [(s, t, d) for s, t, d in g.edges(data=True)
                 if d.get("关系大类") == cat]
        sub = g.edge_subgraph([(s, t) for s, t, _ in edges]).copy()
        layers[cat] = sub
        active_n = sub.number_of_nodes()
        indeg = dict(sub.in_degree())
        tops = sorted(indeg.items(), key=lambda x: (-x[1], x[0]))[:3]
        top_txt = "；".join(f"{label[n]}({d})" for n, d in tops if d > 0)
        sub_types = Counter(d.get("关系细分", "") for _, _, d in edges)
        evidence = Counter(d.get("证据类型", "") for _, _, d in edges)
        weights = [float(d.get("Weight", 1.0)) for _, _, d in edges]
        rows.append({
            "关系层": cat,
            "含义": config.RELATION_DESC[cat],
            "边数": len(edges),
            "涉及节点": active_n,
            "层密度(全节点口径)": round(len(edges) / (n_total * (n_total - 1)), 5),
            "平均权重": round(sum(weights) / len(weights), 3) if weights else 0,
            "被援引最多节点(层内入度)": top_txt,
            "关系细分": "；".join(f"{k}{v}" for k, v in sub_types.most_common()),
            "证据构成": "；".join(f"{k}{v}" for k, v in evidence.most_common()),
        })
    df = pd.DataFrame(rows)
    return df, layers


def participation(g: nx.DiGraph) -> pd.DataFrame:
    """节点跨层参与度：一个文献在多少类关系中出现。"""
    layers_of: dict[str, set] = {n: set() for n in g}
    for s, t, d in g.edges(data=True):
        cat = d.get("关系大类")
        layers_of[s].add(cat)
        layers_of[t].add(cat)
    rows = []
    for nid, cats in layers_of.items():
        if not cats:
            continue
        rows.append({
            "文献": g.nodes[nid].get("Label", nid),
            "责任者": g.nodes[nid].get("责任者", ""),
            "成书时代": config.NODE_ERA.get(nid, ""),
            "参与关系层数": len(cats),
            "关系层": "、".join(c.replace("类", "") for c in config.RELATION_CATEGORIES
                              if c in cats),
        })
    return pd.DataFrame(rows).sort_values(
        ["参与关系层数", "文献"], ascending=[False, True]).reset_index(drop=True)


def edge_level_table(g: nx.DiGraph) -> pd.DataFrame:
    """按「析出层级」统计边的分布（版本层 / 阐释传承层 / 引用层）。"""
    cnt = Counter(d.get("析出层级", "未标注") for _, _, d in g.edges(data=True))
    cat_cross = Counter((d.get("析出层级", "未标注"), d.get("关系大类", ""))
                        for _, _, d in g.edges(data=True))
    rows = [{"析出层级": k, "边数": v} for k, v in
            sorted(cnt.items(), key=lambda x: x[0])]
    df = pd.DataFrame(rows)
    detail = pd.DataFrame(
        [{"析出层级": k[0], "关系大类": k[1], "边数": v}
         for k, v in sorted(cat_cross.items())]
    )
    return df, detail
