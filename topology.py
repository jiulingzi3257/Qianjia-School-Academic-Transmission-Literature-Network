# -*- coding: utf-8 -*-
"""整体网络拓扑指标。"""
from __future__ import annotations

import networkx as nx
import pandas as pd


def overall_metrics(g: nx.DiGraph) -> tuple[pd.DataFrame, nx.DiGraph]:
    """计算整体拓扑指标，返回（指标表, 最大弱连通分量子图）。"""
    n, m = g.number_of_nodes(), g.number_of_edges()
    isolates = list(nx.isolates(g))
    und = g.to_undirected()

    wccs = sorted(nx.weakly_connected_components(g), key=len, reverse=True)
    sccs_all = list(nx.strongly_connected_components(g))
    scc_nontriv = [c for c in sccs_all if len(c) > 1]
    lcc = g.subgraph(wccs[0]).copy()
    lcc_und = lcc.to_undirected()

    try:
        diameter = nx.diameter(lcc_und)
        avg_path = nx.average_shortest_path_length(lcc_und)
    except nx.NetworkXError:
        diameter = avg_path = float("nan")

    data = [
        ("节点数 N", n, "网络中的全部文献节点（含孤立节点）"),
        ("边数 M", m, "有向学术关系总数"),
        ("孤立节点数", len(isolates), "无任何关系连接的节点"),
        ("活跃节点数", n - len(isolates), "至少参与一条边的节点"),
        ("网络密度", nx.density(g), "实际边数 / 可能边数 N(N-1)"),
        ("平均度", 2 * m / n, "有向图总度均值（入度+出度）"),
        ("平均出/入度", m / n, "每个节点平均引述/被引述次数"),
        ("弱连通分量数", len(wccs), "忽略方向后互不连通的子图数量（含孤立点）"),
        ("最大弱连通分量规模", len(wccs[0]), f"占总节点 {len(wccs[0]) / n:.1%}"),
        ("最大分量内边数", lcc.number_of_edges(), "主分量承载的关系数量"),
        ("强连通分量数（非平凡）", len(scc_nontriv),
         "存在相互可达环路的分量数；0 表示网络呈无环的源流结构"),
        ("互惠性", nx.reciprocity(g), "双向边占比"),
        ("传递性（全局聚类）", nx.transitivity(g), "闭合三元组占比（有向口径）"),
        ("平均聚类系数", nx.average_clustering(und), "无向投影下节点局部聚类均值"),
        ("最大分量直径（无向）", diameter, "主分量内最远两点距离"),
        ("最大分量平均路径（无向）", avg_path, "主分量任意两点平均最短距离"),
        ("度同配系数", nx.degree_assortativity_coefficient(und),
         "大度节点是否倾向彼此相连；负值为异配（枢纽—边缘结构）"),
    ]
    df = pd.DataFrame(data, columns=["指标", "数值", "口径说明"])
    return df, lcc
