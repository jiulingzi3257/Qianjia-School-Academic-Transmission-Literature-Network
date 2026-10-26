# -*- coding: utf-8 -*-
"""网络鲁棒性仿真：蓄意攻击 vs 随机失效。"""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd

from . import config


def _lcc_fraction(graph: nx.Graph, original_size: int) -> float:
    if graph.number_of_nodes() == 0:
        return 0.0
    return len(max(nx.connected_components(graph), key=len)) / original_size


def simulate(u: nx.Graph, n_random: int = 100) -> tuple[pd.DataFrame, pd.DataFrame]:
    """按节点重要性顺序移除节点，观测最大连通分量（LCC）衰减。

    攻击策略：度优先、介数优先、特征向量优先；对照为随机失效均值。
    返回（衰减曲线长表, 半衰阈值表）。
    """
    original_size = u.number_of_nodes()
    between = nx.betweenness_centrality(u)
    try:
        eigen = nx.eigenvector_centrality_numpy(u, weight="weight")
    except Exception:
        eigen = nx.eigenvector_centrality(u, weight="weight", max_iter=1000)
    strategies = {
        "度优先攻击": sorted(u.nodes, key=lambda x: u.degree(x), reverse=True),
        "介数优先攻击": sorted(u.nodes, key=lambda x: between[x], reverse=True),
        "加权度优先攻击": sorted(u.nodes, key=lambda x: u.degree(x, weight="weight"),
                              reverse=True),
        "特征向量优先攻击": sorted(u.nodes, key=lambda x: eigen[x], reverse=True),
    }

    rng = np.random.default_rng(config.RANDOM_SEED)
    random_curves = []
    for _ in range(n_random):
        order = rng.permutation(u.number_of_nodes())
        nodes = list(u.nodes)
        curve = _attack_curve(u, [nodes[i] for i in order], original_size)
        random_curves.append(curve)
    random_arr = np.array(random_curves)
    random_mean = random_arr.mean(axis=0)
    random_std = random_arr.std(axis=0)

    records = []
    half_table = []
    for name, order in strategies.items():
        curve = _attack_curve(u, order, original_size)
        for i, val in enumerate(curve):
            records.append({
                "移除比例": i / original_size,
                "LCC占比": val,
                "策略": name,
            })
        half = next((i / original_size for i, v in enumerate(curve)
                     if v <= 0.5), 1.0)
        half_table.append({"策略": name, "LCC首次降至一半以下时的移除比例": round(half, 3)})
    for i, (m, s) in enumerate(zip(random_mean, random_std)):
        records.append({"移除比例": i / original_size, "LCC占比": m, "策略": "随机失效(均值)"})
    half = next((i / original_size for i, v in enumerate(random_mean) if v <= 0.5), 1.0)
    half_table.append({"策略": "随机失效(均值)",
                       "LCC首次降至一半以下时的移除比例": round(half, 3)})
    return (pd.DataFrame(records),
            pd.DataFrame(half_table),
            {"random_mean": random_mean, "random_std": random_std,
             "n": original_size})


def _attack_curve(base: nx.Graph, order: list, original_size: int) -> list[float]:
    h = base.copy()
    curve = [1.0]
    for nid in order:
        if nid in h:
            h.remove_node(nid)
        curve.append(_lcc_fraction(h, original_size))
    return curve
