# -*- coding: utf-8 -*-
"""学术传承谱系与关键师承路径分析。"""
from __future__ import annotations

import networkx as nx
import pandas as pd

from . import config

LINEAGE_CATEGORIES = ("学术传承类", "注疏阐释类")


def lineage_subgraph(g: nx.DiGraph) -> nx.DiGraph:
    """传承谱系子图 = 学术传承类 ∪ 注疏阐释类。"""
    keep = [(s, t) for s, t, d in g.edges(data=True)
            if d.get("关系大类") in LINEAGE_CATEGORIES]
    return g.edge_subgraph(keep).copy()


def _longest_chains(g: nx.DiGraph) -> dict:
    """在（假设无环的）有向图中求每个节点出发的最长链。

    边方向为「后世 → 原典」，故最长外向链即最深的学术溯源链。
    """
    topo = list(nx.topological_sort(g))
    dist = {n: 0 for n in g}
    nxt = {n: None for n in g}
    for u in reversed(topo):
        for v in g.successors(u):
            if dist[v] + 1 > dist[u]:
                dist[u] = dist[v] + 1
                nxt[u] = v
    return dist, nxt


def _trace(start: str, nxt: dict) -> list:
    chain, cur = [], start
    while cur is not None:
        chain.append(cur)
        cur = nxt[cur]
    return chain


def analyze_lineage(g: nx.DiGraph) -> dict:
    """返回师承表、关键传承链与 DAG 结构信息。"""
    lg = lineage_subgraph(g)
    is_dag = nx.is_directed_acyclic_graph(lg)

    # 师承授受明线
    master_rows = []
    for s, t, d in sorted(lg.edges(data=True), key=lambda x: x[2]["Id"]):
        if d.get("关系细分") == "师承授受":
            master_rows.append({
                "后学": f"{g.nodes[s]['Label']}（{g.nodes[s].get('责任者', '')}）",
                "宗师": f"{g.nodes[t]['Label']}（{g.nodes[t].get('责任者', '')}）",
                "权重": d.get("Weight", ""),
                "证据": d.get("证据类型", ""),
                "证据位置": d.get("证据位置", ""),
                "史源说明": d.get("备注", ""),
            })
    master_df = pd.DataFrame(master_rows)

    # 最长溯源链
    chains: list[tuple] = []
    if is_dag:
        dist, nxt = _longest_chains(lg)
        starts = [n for n in lg if config.NODE_ERA.get(n) in
                  ("近现代(20世纪)", "乾嘉鼎盛(18世纪)", "清初(17世纪)")]
        seen = set()
        for s in sorted(starts, key=lambda x: -dist[x]):
            if dist[s] < 2:
                continue
            chain = tuple(_trace(s, nxt))
            if any(set(chain) < set(c) or chain == c for c in seen):
                continue  # 去掉被更长链包含的子链与重复链
            seen.add(chain)
            chains.append(chain)
        chains.sort(key=lambda c: (-len(c), c))

    chain_rows = []
    for chain in chains[:15]:
        labels = [g.nodes[n]["Label"] for n in chain]
        eras = [config.NODE_ERA.get(n, "").split("(")[0] for n in chain]
        edge_types = [lg[chain[i]][chain[i + 1]].get("关系细分", "")
                      for i in range(len(chain) - 1)]
        chain_rows.append({
            "链长(边)": len(chain) - 1,
            "溯源链（后世→原典）": " → ".join(labels),
            "时代序列": " → ".join(eras),
            "关系序列": " → ".join(edge_types),
        })
    chains_df = pd.DataFrame(chain_rows)

    # 全图（含引文/方法支撑）口径下的最大可达深度
    full_dag = nx.is_directed_acyclic_graph(g)
    depth_rows = []
    if full_dag:
        dist_all, nxt_all = _longest_chains(g)
        labels = nodes_label(g)
        for nid, dval in sorted(dist_all.items(), key=lambda x: -x[1])[:10]:
            depth_rows.append({
                "文献": labels[nid],
                "责任者": g.nodes[nid].get("责任者", ""),
                "成书时代": config.NODE_ERA.get(nid, ""),
                "全网络溯源深度(边)": dval,
            })
    depth_df = pd.DataFrame(depth_rows)

    return {
        "subgraph": lg,
        "is_dag": is_dag,
        "edges": lg.number_of_edges(),
        "nodes": lg.number_of_nodes(),
        "master_df": master_df,
        "chains_df": chains_df,
        "depth_df": depth_df,
        "full_dag": full_dag,
    }


def nodes_label(g: nx.DiGraph) -> dict:
    return {n: g.nodes[n].get("Label", n) for n in g}
