# -*- coding: utf-8 -*-
"""数据加载、质量核查与有向加权图构建。"""
from __future__ import annotations

import networkx as nx
import pandas as pd

from . import config

# 节点表中需要转成数值型的列
_NODE_NUMERIC = [
    "出版年", "indegree", "outdegree", "degree", "modularity_class",
    "Eccentricity", "closnesscentrality", "harmonicclosnesscentrality",
    "betweenesscentrality", "clustering",
    "weighted indegree", "weighted outdegree", "weighted degree",
]

REQUIRED_NODE_COLS = {"Id", "Label", "责任者", "节点层级", "备注"}
REQUIRED_EDGE_COLS = {
    "Source", "Target", "Type", "Id", "Label", "Weight",
    "关系大类", "关系细分", "析出层级", "证据位置", "证据类型", "备注",
}


def read_csv_safely(path) -> pd.DataFrame:
    """按 utf-8-sig / utf-8 / gbk 顺序尝试读取 CSV，空值保留为空字符串。"""
    last_err: Exception | None = None
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str, keep_default_na=False)
            df.columns = [c.strip() for c in df.columns]
            for col in df.select_dtypes(include="object").columns:
                df[col] = df[col].str.strip()
            return df
        except UnicodeDecodeError as exc:  # 换编码重试
            last_err = exc
    raise UnicodeDecodeError("csv", b"", 0, 1, f"无法识别文件编码: {path} ({last_err})")


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    """读取节点表与边表（原始字符串 + 数值列转换）。"""
    nodes = read_csv_safely(config.NODE_CSV)
    edges = read_csv_safely(config.EDGE_CSV)

    for col in _NODE_NUMERIC:
        if col in nodes.columns:
            nodes[col] = pd.to_numeric(nodes[col].replace("", pd.NA), errors="coerce")
    if "Weight" in edges.columns:
        edges["Weight"] = pd.to_numeric(edges["Weight"].replace("", pd.NA), errors="coerce")
    return nodes, edges


def _qc(nodes: pd.DataFrame, edges: pd.DataFrame) -> list[dict]:
    """结构与著录完整性核查，返回 [{级别, 项目, 结果, 明细}]。"""
    rows: list[dict] = []

    def add(level, item, result, detail=""):
        rows.append({"级别": level, "检查项": item, "结果": result, "明细": detail})

    # 列完整性
    miss_n = REQUIRED_NODE_COLS - set(nodes.columns)
    miss_e = REQUIRED_EDGE_COLS - set(edges.columns)
    add("通过" if not miss_n else "错误", "节点表必需字段",
        "齐全" if not miss_n else f"缺失 {sorted(miss_n)}")
    add("通过" if not miss_e else "错误", "边表必需字段",
        "齐全" if not miss_e else f"缺失 {sorted(miss_e)}")

    # ID 唯一性
    dup_nodes = nodes["Id"].duplicated().sum()
    dup_edges = edges["Id"].duplicated().sum()
    add("通过" if dup_nodes == 0 else "错误", "节点 Id 唯一", f"重复 {dup_nodes} 个")
    add("通过" if dup_edges == 0 else "错误", "边 Id 唯一", f"重复 {dup_edges} 个")

    # 悬挂边
    node_ids = set(nodes["Id"])
    bad_src = sorted(set(edges["Source"]) - node_ids)
    bad_tgt = sorted(set(edges["Target"]) - node_ids)
    add("通过" if not bad_src and not bad_tgt else "错误", "边端点均可在节点表中找到",
        "全部匹配" if not bad_src and not bad_tgt else
        f"孤立引用 Source={bad_src} Target={bad_tgt}")

    # 有向性
    types = sorted(edges["Type"].unique())
    add("通过" if types == ["Directed"] else "警告", "边方向类型", "，".join(types))

    # 权重区间
    w = edges["Weight"].dropna()
    out_of_range = ((w <= 0) | (w > 1)).sum()
    add("通过" if out_of_range == 0 else "错误", "权重取值 (0, 1]",
        f"越界 {out_of_range} 条；区间 {w.min():.2f}–{w.max():.2f}，均值 {w.mean():.3f}")

    # 自环 / 重边
    self_loops = (edges["Source"] == edges["Target"]).sum()
    pair_dup = edges.duplicated(subset=["Source", "Target"]).sum()
    add("通过" if self_loops == 0 else "警告", "自环", f"{self_loops} 条")
    add("通过" if pair_dup == 0 else "警告", "同序点对重边", f"{pair_dup} 条")

    # 关系大类取值
    cats = set(edges["关系大类"]) - set(config.RELATION_CATEGORIES)
    add("通过" if not cats else "警告", "关系大类编码",
        "五类齐全" if set(edges["关系大类"]) == set(config.RELATION_CATEGORIES)
        else f"异常取值 {sorted(cats)}")

    # 孤立节点
    linked = set(edges["Source"]) | set(edges["Target"])
    isolated = sorted(node_ids - linked)
    iso_labels = nodes.set_index("Id").loc[isolated, "Label"].tolist()
    add("信息", "孤立节点（无任何边）", f"{len(isolated)} 个",
        "、".join(iso_labels) if iso_labels else "")

    # 著录完整性（GB/T 7714 要素）
    for col in ("责任者", "出版者", "出版年", "永久标识符"):
        series = nodes[col]
        miss = int(series.isna().sum() +
                   (series.astype(str).str.strip().isin(["", "nan", "None"])).sum())
        add("信息", f"著录字段缺失：{col}", f"{miss}/{len(nodes)} 个节点")

    # 证据结构
    ev = edges["证据类型"].value_counts().to_dict()
    add("信息", "证据类型分布", "；".join(f"{k} {v}" for k, v in ev.items()))

    # 时代编码完整性
    era_miss = sorted(node_ids - set(config.NODE_ERA))
    add("通过" if not era_miss else "警告", "成书时代编码完整",
        "40 个节点全部编码" if not era_miss else f"未编码 {era_miss}")
    return rows


def build_graph(nodes: pd.DataFrame, edges: pd.DataFrame) -> nx.DiGraph:
    """构建有向加权图：节点挂载全部著录属性，边挂载关系与证据属性。"""
    g = nx.DiGraph()
    for _, row in nodes.iterrows():
        attrs = {c: row[c] for c in nodes.columns}
        g.add_node(row["Id"], **attrs)

    for _, row in edges.iterrows():
        s, t = row["Source"], row["Target"]
        if s not in g or t not in g:  # 质检已报错，构图时跳过
            continue
        g.add_edge(s, t, **{c: row[c] for c in edges.columns})
    return g


def active_subgraph(g: nx.DiGraph) -> nx.DiGraph:
    """剔除孤立节点后的活跃子图（保留全部边属性）。"""
    return g.subgraph({n for n in g if g.degree(n) > 0}).copy()


def load_dataset():
    """一站式入口：返回 nodes_df, edges_df, graph, qc_rows。"""
    nodes, edges = load_raw()
    qc_rows = _qc(nodes, edges)
    g = build_graph(nodes, edges)
    return nodes, edges, g, qc_rows
