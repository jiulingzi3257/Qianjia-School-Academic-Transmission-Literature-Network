# -*- coding: utf-8 -*-
"""节点中心性指标，并与节点表内 Gephi 预算指标做信度交叉校验。"""
from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

from . import config


def compute_centrality(g: nx.DiGraph, nodes_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """返回（节点中心性宽表, 与 Gephi 指标的一致性校验表）。

    方向约定：边由后世文献指向原典 / 师法对象，因此
    入度 / 加权入度刻画「被承继、被援引」的权威度，
    出度刻画「博采、溯源」的用功广度。
    """
    und = g.to_undirected()
    n = g.number_of_nodes()

    in_deg = dict(g.in_degree())
    out_deg = dict(g.out_degree())
    win_str = {nid: sum(d["Weight"] for _, _, d in g.in_edges(nid, data=True))
               for nid in g}
    wout_str = {nid: sum(d["Weight"] for _, _, d in g.out_edges(nid, data=True))
                for nid in g}

    # 介数：Gephi 默认按无权最短路径；另给出以 1/权重 为距离的加权口径
    bet_raw = nx.betweenness_centrality(g, normalized=False)
    bet_norm = nx.betweenness_centrality(g, normalized=True)
    g_dist = g.copy()
    for _, _, d in g_dist.edges(data=True):
        d["distance"] = 1.0 / max(float(d["Weight"]), 1e-6)
    bet_weighted = nx.betweenness_centrality(g_dist, weight="distance", normalized=True)

    close_in = nx.closeness_centrality(g.reverse(copy=True))  # 入接近：被他人到达
    close_und = nx.closeness_centrality(und)                  # 无向口径（与 Gephi 对照）
    harm_out = nx.harmonic_centrality(g)                  # 溯源可达
    harm_in = nx.harmonic_centrality(g.reverse(copy=True))
    harm_out = {k: v / (n - 1) for k, v in harm_out.items()}
    harm_in = {k: v / (n - 1) for k, v in harm_in.items()}
    harm_und = {k: v / (n - 1) for k, v in
                nx.harmonic_centrality(und).items()}

    pagerank = nx.pagerank(g, weight="Weight", alpha=0.85)
    try:
        eig = nx.eigenvector_centrality_numpy(und, weight="Weight")
    except Exception:  # 极端情况下回退到幂迭代
        eig = nx.eigenvector_centrality(und, weight="Weight", max_iter=1000)
    clustering = nx.clustering(und)

    meta = nodes_df.set_index("Id")
    rows = []
    for nid in g:
        rows.append({
            "节点ID": nid,
            "文献": g.nodes[nid].get("Label", ""),
            "责任者": g.nodes[nid].get("责任者", ""),
            "成书时代": config.NODE_ERA.get(nid, ""),
            "入度": in_deg[nid],
            "出度": out_deg[nid],
            "总度": in_deg[nid] + out_deg[nid],
            "加权入度": round(win_str[nid], 3),
            "加权出度": round(wout_str[nid], 3),
            "加权总度": round(win_str[nid] + wout_str[nid], 3),
            "介数(原始)": round(bet_raw[nid], 3),
            "介数中心性": round(bet_norm[nid], 4),
            "介数(加权距离)": round(bet_weighted[nid], 4),
            "入接近中心性": round(close_in[nid], 4),
            "接近中心性(无向)": round(close_und[nid], 4),
            "入调和接近": round(harm_in[nid], 4),
            "调和接近(无向)": round(harm_und[nid], 4),
            "PageRank": round(pagerank[nid], 5),
            "特征向量中心性": round(eig[nid], 4),
            "聚类系数": round(clustering[nid], 4),
        })
    cen = pd.DataFrame(rows).sort_values("介数(原始)", ascending=False).reset_index(drop=True)

    validation = _validate_against_gephi(nodes_df, cen, in_deg, out_deg,
                                         win_str, bet_raw, close_in, close_und,
                                         harm_in, harm_und, clustering)
    return cen, validation


def _spearman(a: pd.Series, b: pd.Series) -> tuple[float, float, int]:
    mask = a.notna() & b.notna()
    if mask.sum() < 3 or a[mask].nunique() < 2 or b[mask].nunique() < 2:
        return float("nan"), float("nan"), int(mask.sum())  # 常量列无法定义秩相关
    rho, p = stats.spearmanr(a[mask], b[mask])
    return float(rho), float(p), int(mask.sum())


def _validate_against_gephi(nodes_df, cen, in_deg, out_deg, win_str,
                            bet_raw, close_in, close_und,
                            harm_in, harm_und, clustering) -> pd.DataFrame:
    """与节点表中 Gephi 0.10 预算指标做秩相关校验。"""
    gephi = nodes_df.set_index("Id")
    cur = cen.set_index("节点ID")
    n = len(cen)

    pairs = [
        ("入度", gephi["indegree"], pd.Series(in_deg), "精确计数", "spearman"),
        ("出度", gephi["outdegree"], pd.Series(out_deg), "精确计数", "spearman"),
        ("总度", gephi["degree"], cur["总度"], "精确计数", "spearman"),
        ("加权入度", gephi["weighted indegree"], pd.Series(win_str).round(3),
         "入边权重之和", "spearman"),
        ("介数", gephi["betweenesscentrality"], pd.Series(bet_raw),
         "均为无权最短路径口径，仅尺度归一化不同", "spearman"),
        ("接近中心性(有向·入)", gephi["closnesscentrality"], pd.Series(close_in),
         "Gephi 对有向图的接近中心性口径", "spearman"),
        ("接近中心性(无向)", gephi["closnesscentrality"], pd.Series(close_und),
         "无向投影口径，便于对照", "spearman"),
        ("调和接近(有向·入)", gephi["harmonicclosnesscentrality"], pd.Series(harm_in),
         "调和平均对不连通图更稳健", "spearman"),
        ("调和接近(无向)", gephi["harmonicclosnesscentrality"], pd.Series(harm_und),
         "无向投影口径，便于对照", "spearman"),
        ("聚类系数", gephi["clustering"], pd.Series(clustering),
         "无向投影局部聚类", "spearman"),
    ]
    rows = []
    for name, gv, cv, note, _ in pairs:
        gv, cv = gv.align(cv, join="inner")
        rho, p, k = _spearman(gv, cv)
        if np.isnan(rho):
            verdict = "无法比较（常量/样本不足）"
        else:
            verdict = "高度一致" if rho >= 0.9 else "基本一致" if rho >= 0.7 else "存在口径差异"
        rows.append({
            "指标": name,
            "Spearman秩相关ρ": round(rho, 4) if not np.isnan(rho) else "—",
            "显著性p": f"{p:.2e}" if not np.isnan(p) else "—",
            "样本n": k,
            "判定": verdict,
            "口径说明": note,
        })
    _ = n
    return pd.DataFrame(rows)
