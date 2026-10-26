# -*- coding: utf-8 -*-
"""可视化：matplotlib 静态图（中文标注）与 pyvis 交互式网络图。"""
from __future__ import annotations

import os
from pathlib import Path

# 将 matplotlib 配置/字体缓存重定向到项目内，避免系统目录写权限问题
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parent.parent / ".mplcache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib import font_manager

from . import config

# ---------------------------------------------------------------- 中文字体
def setup_font() -> str:
    """探测 Windows 常见中文字体并写入 rcParams，返回实际字体名。"""
    candidates = [
        ("Microsoft YaHei", "msyh.ttc"),
        ("Microsoft YaHei", "msyh.ttf"),
        ("SimHei", "simhei.ttf"),
        ("SimSun", "simsun.ttc"),
        ("Noto Sans CJK SC", "NotoSansCJK-Regular.ttc"),
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for name, fname in candidates:
        if name in available:
            chosen = name
            break
        try:
            p = Path(font_manager.findfont(fname, fallback_to_default=False))
            if p.exists():
                font_manager.fontManager.addfont(str(p))
                chosen = name
                break
        except Exception:
            continue
    if chosen is None:
        chosen = "DejaVu Sans"
    plt.rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


def _label(g, nid):
    return g.nodes[nid].get("Label", nid).strip("《》")


def _component_layout(active: nx.DiGraph) -> dict:
    """按弱连通分量分别弹簧布局后拼合：主分量居中，小分量排到右上角。"""
    und = active.to_undirected()
    comps = sorted(nx.connected_components(und), key=len, reverse=True)
    layout_g = active.copy()
    for _, _, d in layout_g.edges(data=True):
        d["lw"] = 0.4 + 0.6 * float(d.get("Weight", 1.0))

    main = layout_g.subgraph(comps[0]).copy()
    try:  # 主分量连通，KK 布局对这种小网络最均匀美观
        pos = nx.kamada_kawai_layout(main, weight="lw", scale=1.0)
    except Exception:
        pos = nx.spring_layout(main, weight="lw", k=0.72,
                               seed=config.RANDOM_SEED, iterations=600, scale=1.0)
    # 小分量依次排在右下方
    offsets = [(1.55, -1.25), (1.55, -0.45)]
    for i, comp in enumerate(comps[1:]):
        sub = layout_g.subgraph(comp).copy()
        p = nx.spring_layout(sub, weight="lw", k=1.1,
                             seed=config.RANDOM_SEED + i, iterations=300, scale=0.28)
        ox, oy = offsets[min(i, len(offsets) - 1)]
        for nid, (x, y) in p.items():
            pos[nid] = (x + ox, y + oy)
    return pos


def fig_network_overview(g, cen: pd.DataFrame, path) -> None:
    """全网络结构图：节点按成书时代着色、按加权入度定大小，边按关系大类着色。"""
    fig, ax = plt.subplots(figsize=(15, 11), dpi=150)
    active = g.subgraph({n for n in g if g.degree(n) > 0}).copy()
    pos = _component_layout(active)

    node_colors = [config.ERA_COLORS.get(config.NODE_ERA.get(n, ""), "#999999")
                   for n in active]
    win = cen.set_index("节点ID")["加权入度"]
    sizes = [120 + 320 * (win.get(n, 0) / max(win.max(), 1)) for n in active]

    for cat, color in config.RELATION_COLORS.items():
        edges = [(s, t) for s, t, d in active.edges(data=True)
                 if d.get("关系大类") == cat]
        weights = [0.5 + 2.2 * float(d["Weight"])
                   for s, t, d in active.edges(data=True)
                   if d.get("关系大类") == cat]
        nx.draw_networkx_edges(active, pos, edgelist=edges, edge_color=color,
                               width=weights, alpha=0.55, arrows=True,
                               arrowsize=10, ax=ax, node_size=sizes,
                               connectionstyle="arc3,rad=0.06")
    nx.draw_networkx_nodes(active, pos, node_color=node_colors,
                           node_size=sizes, edgecolors="white",
                           linewidths=1.2, alpha=0.95, ax=ax)
    nx.draw_networkx_labels(
        active, pos,
        labels={n: _label(active, n) for n in active},
        font_size=7.5, font_family=plt.rcParams["font.sans-serif"][0], ax=ax,
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.78))

    node_handles = [plt.Line2D([0], [0], marker="o", linestyle="", color=c,
                               markersize=9, label=e)
                    for e, c in config.ERA_COLORS.items()]
    edge_handles = [plt.Line2D([0], [0], color=c, lw=2, label=e)
                    for e, c in config.RELATION_COLORS.items()]
    ax.legend(handles=node_handles + edge_handles, loc="upper left",
              ncol=2, fontsize=9, framealpha=0.9, title="成书时代 / 关系层")
    ax.set_title("乾嘉学派学术传承文献网络（N=%d, M=%d，箭头：后世→原典）"
                 % (g.number_of_nodes(), g.number_of_edges()), fontsize=14)
    ax.set_aspect("equal")
    ax.margins(0.12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_centrality(cen: pd.DataFrame, path) -> None:
    """入度 / 介数 / PageRank 三榜对照条形图。"""
    fig, axes = plt.subplots(1, 3, figsize=(17, 6.5), dpi=150)
    specs = [
        ("加权入度", "被承继权威度（加权入度）", "#C44E52"),
        ("介数(原始)", "范式中介枢纽（介数）", "#4C72B0"),
        ("PageRank", "网络声望（PageRank）", "#55A868"),
    ]
    for ax, (col, title, color) in zip(axes, specs):
        top = cen.sort_values(col, ascending=False).head(10).iloc[::-1]
        ax.barh(top["文献"].str.strip("《》"), top[col], color=color, alpha=0.85)
        ax.set_title(title, fontsize=12)
        ax.tick_params(labelsize=9)
        for i, v in enumerate(top[col]):
            ax.text(v, i, f" {v:g}", va="center", fontsize=8)
        ax.margins(x=0.15)
    fig.suptitle("文献节点中心性 Top 10（三维度对照）", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_communities(g, assign: pd.DataFrame, path) -> None:
    """Louvain 社区着色网络图，节点大小=k 核层。"""
    active = g.subgraph({n for n in g if g.degree(n) > 0}).copy()
    pos = _component_layout(active)
    cmap = ["#4C72B0", "#DD8452", "#55A868", "#8172B3", "#937860",
            "#DA8BC3", "#8C8C8C", "#CCB974"]
    cid_of = assign.set_index("节点ID")["Louvain社区"].to_dict()
    k_of = assign.set_index("节点ID")["k核层"].to_dict()
    colors = [cmap[(cid_of.get(n, 1) - 1) % len(cmap)] for n in active]
    sizes = [160 + 150 * k_of.get(n, 1) for n in active]

    fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
    nx.draw_networkx_edges(active, pos, edge_color="#BBBBBB", width=0.8,
                           alpha=0.6, arrows=False, ax=ax)
    nx.draw_networkx_nodes(active, pos, node_color=colors, node_size=sizes,
                           edgecolors="white", linewidths=1.2, ax=ax)
    nx.draw_networkx_labels(active, pos,
                            labels={n: _label(active, n) for n in active},
                            font_size=7.5,
                            font_family=plt.rcParams["font.sans-serif"][0], ax=ax,
                            bbox=dict(boxstyle="round,pad=0.12", fc="white",
                                      ec="none", alpha=0.78))
    n_comm = assign["Louvain社区"].max()
    handles = [plt.Line2D([0], [0], marker="o", linestyle="",
                          color=cmap[(c - 1) % len(cmap)], markersize=9,
                          label=f"社区 C{c}") for c in range(1, n_comm + 1)]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    ax.set_title("Louvain 社区发现结果（颜色=社区，节点大小=k 核层）", fontsize=14)
    ax.set_aspect("equal")
    ax.margins(0.12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_robustness(curves: pd.DataFrame, rand_stats: dict, path) -> None:
    """鲁棒性衰减曲线。"""
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=150)
    colors = {"度优先攻击": "#C44E52", "介数优先攻击": "#8172B3",
              "加权度优先攻击": "#DD8452", "特征向量优先攻击": "#937860",
              "随机失效(均值)": "#4C72B0"}
    styles = {"度优先攻击": "-", "介数优先攻击": "--",
              "加权度优先攻击": "-.", "特征向量优先攻击": ":",
              "随机失效(均值)": "-"}
    for name, sub in curves.groupby("策略"):
        sub = sub.sort_values("移除比例")
        ax.plot(sub["移除比例"], sub["LCC占比"], label=name,
                color=colors.get(name, "gray"),
                linestyle=styles.get(name, "-"), lw=2)
        if name == "随机失效(均值)":
            x = np.linspace(0, 1, len(rand_stats["random_mean"]))
            ax.fill_between(x,
                            rand_stats["random_mean"] - rand_stats["random_std"],
                            rand_stats["random_mean"] + rand_stats["random_std"],
                            color="#4C72B0", alpha=0.15)
    ax.axhline(0.5, color="gray", ls="--", lw=1)
    ax.set_xlabel("节点移除比例")
    ax.set_ylabel("最大连通分量节点占比")
    ax.set_title("网络鲁棒性：蓄意攻击与随机失效下的主分量衰减", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_era_flow(mat: pd.DataFrame, path) -> None:
    """跨时代传承流向热图。"""
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=150)
    short = {e: e.split("(")[0] for e in config.ERA_ORDER}
    m = mat.copy()
    m.index = [short[e] for e in m.index]
    m.columns = [short[e] for e in m.columns]
    data = m.values
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(m.columns)), m.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(m.index)), m.index)
    ax.set_xlabel("被承继方（原典/师法对象）成书时代")
    ax.set_ylabel("承继方（后世文献）成书时代")
    ax.set_title("跨时代学术传承流向矩阵（边数）", fontsize=13)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] > 0:
                ax.text(j, i, data[i, j], ha="center", va="center",
                        color="black" if data[i, j] < data.max() * 0.6 else "white",
                        fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_layers(layer_df: pd.DataFrame, path) -> None:
    """五层关系网络边数与平均权重。"""
    fig, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
    x = np.arange(len(layer_df))
    cats = [c.replace("类", "") for c in layer_df["关系层"]]
    bars = ax1.bar(x - 0.2, layer_df["边数"], width=0.4, color="#4C72B0",
                   label="边数", alpha=0.85)
    ax1.set_ylabel("边数", color="#4C72B0")
    ax1.tick_params(axis="y", labelcolor="#4C72B0")
    ax1.set_xticks(x, cats, fontsize=10)
    for b in bars:
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                 int(b.get_height()), ha="center", fontsize=9)
    ax2 = ax1.twinx()
    ax2.bar(x + 0.2, layer_df["平均权重"], width=0.4, color="#C44E52",
            label="平均权重", alpha=0.85)
    ax2.set_ylabel("平均关系权重", color="#C44E52")
    ax2.tick_params(axis="y", labelcolor="#C44E52")
    ax2.set_ylim(0, 1)
    ax1.set_title("五类关系层：关系数量与平均证据强度", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- pyvis 交互图
def interactive_network(g, path) -> None:
    """生成 pyvis 交互式有向网络图（边按关系层着色，悬停查看著录与证据信息）。"""
    from pyvis.network import Network

    net = Network(directed=True, height="860px", width="100%",
                  bgcolor="#1e1e24", font_color="#f0f0f0",
                  cdn_resources="in_line", notebook=False)
    # 仅展示有连接的活跃节点，避免孤立原典无意义漂移
    active_ids = {n for n in g if g.degree(n) > 0}

    in_deg = dict(g.in_degree())
    max_in = max((in_deg[n] for n in active_ids), default=1)
    for nid, data in g.nodes(data=True):
        if nid not in active_ids:
            continue
        era = config.NODE_ERA.get(nid, "")
        title = (
            f"<b>{data.get('Label','')}</b><br>责任者：{data.get('责任者','')}<br>"
            f"版本：{data.get('版本','')}（{data.get('出版地','')}·"
            f"{data.get('出版者','')}，{data.get('出版年','')}）<br>"
            f"成书时代编码：{era}<br>节点层级：{data.get('节点层级','')}<br>"
            f"入度 {in_deg.get(nid,0)} / 出度 {g.out_degree(nid)}<br>"
            f"备注：{data.get('备注','')}"
        )
        net.add_node(
            nid, label=str(data.get("Label", nid)).strip("《》"),
            title=title,
            color=config.ERA_COLORS.get(era, "#999999"),
            size=14 + 22 * in_deg.get(nid, 0) / max(max_in, 1) + 8,
            borderWidth=2,
        )
    for s, t, d in g.edges(data=True):
        if s not in active_ids or t not in active_ids:
            continue
        cat = d.get("关系大类", "")
        net.add_edge(
            s, t, color=config.RELATION_COLORS.get(cat, "#888888"),
            value=float(d.get("Weight", 1.0)),
            width=0.5 + 3 * float(d.get("Weight", 1.0)),
            title=(f"{d.get('关系细分','')}（权重 {d.get('Weight','')}）<br>"
                   f"证据：{d.get('证据类型','')}｜{d.get('证据位置','')}<br>"
                   f"{d.get('备注','')}"),
            arrows="to",
        )
    net.set_options("""{
      "nodes": {"font": {"size": 16, "face": "Microsoft YaHei", "color": "#f2f2f8",
                         "strokeWidth": 3, "strokeColor": "#1e1e24"}},
      "edges": {"smooth": {"type": "continuous", "roundness": 0.08},
                "scaling": {"min": 1, "max": 6}},
      "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {"gravitationalConstant": -75, "centralGravity": 0.012,
          "springLength": 130, "springConstant": 0.09, "damping": 0.72,
          "avoidOverlap": 0.8},
        "stabilization": {"enabled": true, "iterations": 300, "updateInterval": 25,
          "fit": true}
      },
      "interaction": {"hover": true, "tooltipDelay": 60, "navigationButtons": true}
    }""")
    net.save_graph(str(path))
    # 移除 pyvis 模板中非必要的 Bootstrap CDN 引用，保证离线自包含
    import re
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"\s*<link[^>]+bootstrap[^>]*>", "", html, flags=re.I)
    html = re.sub(r"\s*<script[^>]+bootstrap[^>]*></script>", "", html,
                  flags=re.I)
    path.write_text(html, encoding="utf-8")
