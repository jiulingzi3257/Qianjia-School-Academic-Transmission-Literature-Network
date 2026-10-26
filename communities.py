# -*- coding: utf-8 -*-
"""社区发现（Louvain）、k-核分解与核心-边缘结构识别。"""
from __future__ import annotations

import math
from collections import Counter

import networkx as nx
import pandas as pd

from . import config


def to_weighted_undirected(g: nx.DiGraph, active_only: bool = True) -> nx.Graph:
    """有向图 → 无向加权图；双向边权重取较大值并记录并边次数。

    Louvain / k-核等方法要求无向输入，权重保留关系强度。
    """
    if active_only:
        keep = {n for n in g if g.degree(n) > 0}
        g = g.subgraph(keep).copy()
    u = nx.Graph()
    u.add_nodes_from(g.nodes(data=True))
    for s, t, d in g.edges(data=True):
        w = float(d.get("Weight", 1.0))
        if u.has_edge(s, t):
            u[s][t]["weight"] = max(u[s][t]["weight"], w)
            u[s][t]["merged_edges"] = u[s][t].get("merged_edges", 1) + 1
        else:
            u.add_edge(s, t, weight=w, merged_edges=1)
    return u


def _nmi(a: dict, b: dict) -> float:
    """两划分之间的标准化互信息（NMI，几何平均归一化）。"""
    keys = sorted(set(a) & set(b))
    la = {v: i for i, v in enumerate(sorted({a[k] for k in keys}))}
    lb = {v: i for i, v in enumerate(sorted({b[k] for k in keys}))}
    n = len(keys)
    ca = Counter(a[k] for k in keys)
    cb = Counter(b[k] for k in keys)
    joint = Counter((a[k], b[k]) for k in keys)
    mi = sum(c / n * math.log(c * n / (ca[x] * cb[y]))
             for (x, y), c in joint.items())
    ha = -sum(c / n * math.log(c / n) for c in ca.values())
    hb = -sum(c / n * math.log(c / n) for c in cb.values())
    return mi / math.sqrt(ha * hb) if ha and hb else 0.0


def detect_communities(g: nx.DiGraph, nodes_df: pd.DataFrame):
    """Louvain 社区 + k-核分解。

    返回
    ----
    assign  : DataFrame 节点→社区/核层/核心边缘
    summary : DataFrame 社区画像
    stats   : dict 模块度、NMI、核层数等
    u_active: 活跃节点无向加权图
    """
    u = to_weighted_undirected(g, active_only=True)

    # ---- Louvain（加权、固定种子、多次扫描取最佳）
    best_parts, best_mod = None, -1.0
    for seed in range(config.RANDOM_SEED, config.RANDOM_SEED + 10):
        parts = nx.community.louvain_communities(u, weight="weight", seed=seed)
        mod = nx.community.modularity(u, parts, weight="weight")
        if mod > best_mod:
            best_parts, best_mod = parts, mod
    parts_sorted = sorted(best_parts, key=len, reverse=True)
    community_of = {}
    for cid, members in enumerate(parts_sorted, start=1):
        for nid in members:
            community_of[nid] = cid

    # 与 Gephi modularity_class 的一致性
    gephi_map = nodes_df.set_index("Id")["modularity_class"].dropna().to_dict()
    gephi_map = {k: int(v) for k, v in gephi_map.items() if k in community_of}
    nmi = _nmi(community_of, gephi_map) if gephi_map else float("nan")
    gephi_mod = float("nan")
    if gephi_map:
        sets: dict[int, set] = {}
        for nid, c in gephi_map.items():
            sets.setdefault(c, set()).add(nid)
        try:  # 若 Gephi 划分未覆盖 u 的全部节点会报错
            gephi_mod = nx.community.modularity(
                u, [s for s in sets.values() if s], weight="weight")
        except Exception:
            gephi_mod = float("nan")

    # ---- k-核分解（无权度口径）与核心-边缘判定
    core_num = nx.core_number(u)
    max_k = max(core_num.values())
    # 核心层：最高 k-核；桥梁层：2-核以上但非核心；边缘层：1-核
    def tier(k):
        if k == max_k:
            return "核心层"
        if k >= 2:
            return "桥梁层"
        return "边缘层"

    labels = nodes_df.set_index("Id")
    rows = []
    for nid in g.nodes:
        active = g.degree(nid) > 0
        rows.append({
            "节点ID": nid,
            "文献": labels.loc[nid, "Label"] if nid in labels.index else nid,
            "成书时代": config.NODE_ERA.get(nid, ""),
            "是否活跃": active,
            "Louvain社区": community_of.get(nid, 0),
            "Gephi社区": int(gephi_map[nid]) if nid in gephi_map else None,
            "k核层": core_num.get(nid, 0),
            "核心边缘": tier(core_num.get(nid, 0)) if active else "孤立层",
        })
    assign = pd.DataFrame(rows).sort_values(
        ["Louvain社区", "k核层", "节点ID"], ascending=[True, False, True]
    ).reset_index(drop=True)

    # ---- 社区画像
    cen = g.in_degree()
    sum_rows = []
    for cid, members in enumerate(parts_sorted, start=1):
        mem_ids = list(members)
        eras = Counter(config.NODE_ERA.get(x, "未编码") for x in mem_ids)
        top_auth = max(mem_ids, key=lambda x: cen[x])
        sum_rows.append({
            "社区": f"C{cid}",
            "规模(节点)": len(mem_ids),
            "内部边数": u.subgraph(mem_ids).number_of_edges(),
            "主要成书时代": "、".join(f"{e}{c}" for e, c in eras.most_common(2)),
            "入度最高节点": f"{labels.loc[top_auth, 'Label']}（{labels.loc[top_auth, '责任者']}，入度{cen[top_auth]}）",
            "成员": "、".join(labels.loc[x, "Label"] for x in
                             sorted(mem_ids, key=lambda z: (-cen[z], z))),
        })
    summary = pd.DataFrame(sum_rows)

    shell_dist = Counter(core_num.values())
    stats = {
        "louvain模块度Q": round(best_mod, 4),
        "社区数": len(parts_sorted),
        "与Gephi划分NMI": round(nmi, 4) if nmi == nmi else float("nan"),
        "Gephi划分模块度Q": round(gephi_mod, 4) if gephi_mod == gephi_mod else float("nan"),
        "最大k核层数": max_k,
        "核心层节点数": sum(1 for v in core_num.values() if v == max_k),
        "k壳分布": dict(sorted(shell_dist.items())),
    }
    return assign, summary, stats, u
