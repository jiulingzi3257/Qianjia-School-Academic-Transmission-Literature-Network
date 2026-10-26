# -*- coding: utf-8 -*-
"""成书时代维度：跨代传承流向矩阵与原典影响力分析。

注意：节点表「出版年」是当代整理本年份，不能代表成书时代；
本模块使用 config.NODE_ERA 的学术史编码，并在报告中明示该口径。
"""
from __future__ import annotations

import pandas as pd

from . import config


def era_flow_matrix(g) -> pd.DataFrame:
    """边的「源时代（承继方）→ 目标时代（被承继方）」计数矩阵。"""
    mat = pd.DataFrame(0, index=config.ERA_ORDER, columns=config.ERA_ORDER)
    for s, t, _ in g.edges(data=True):
        es, et = config.NODE_ERA.get(s), config.NODE_ERA.get(t)
        if es in mat.index and et in mat.columns:
            mat.loc[es, et] += 1
    return mat


def era_summary(g, mat: pd.DataFrame) -> pd.DataFrame:
    """每个时代的外向援引（溯源行为）画像。"""
    rows = []
    for i, era in enumerate(config.ERA_ORDER):
        total = int(mat.loc[era].sum())
        to_classics = int(mat.loc[era, "先秦两汉"])
        earlier = [e for e in config.ERA_ORDER[:i]]
        later = [e for e in config.ERA_ORDER[i + 1:]]
        backward = int(mat.loc[era, earlier].sum()) if earlier else 0
        forward = int(mat.loc[era, later].sum()) if later else 0
        within = int(mat.loc[era, era])
        rows.append({
            "成书时代": era,
            "外向关系总数": total,
            "指向先秦两汉原典": to_classics,
            "指向更早时代合计": backward,
            "同时代内部": within,
            "指向更晚时代": forward,
            "原典指向占比": f"{to_classics / total:.0%}" if total else "—",
        })
    return pd.DataFrame(rows)


def classics_reception(g) -> pd.DataFrame:
    """先秦两汉原典的被承继次数（入度）与其后来源时代构成。"""
    label = {n: g.nodes[n].get("Label", n) for n in g}
    rows = []
    for nid in g:
        if config.NODE_ERA.get(nid) != "先秦两汉":
            continue
        sources = [config.NODE_ERA.get(s) for s in g.predecessors(nid)]
        rows.append({
            "原典": label[nid],
            "责任者": g.nodes[nid].get("责任者", ""),
            "被援引次数(入度)": g.in_degree(nid),
            "援引来源时代": "；".join(
                f"{e.replace('(17世纪)', '').replace('(18世纪)', '').replace('(20世纪)', '')}×{c}"
                for e, c in pd.Series(sources).value_counts().items()) or "—",
        })
    return pd.DataFrame(rows).sort_values("被援引次数(入度)", ascending=False).reset_index(drop=True)
