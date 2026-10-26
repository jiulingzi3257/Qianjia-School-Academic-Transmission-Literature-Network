# -*- coding: utf-8 -*-
"""乾嘉学派学术传承文献网络建模分析 —— 一键运行入口。

用法：
    python run_analysis.py

产物（output/）：
    report.html                     中文综合分析报告
    figures/*.png                   6 张静态图
    interactive/network_interactive.html  pyvis 交互式网络图
    tables/*.csv                    全部中间指标表
"""
from __future__ import annotations

import traceback

from qianjia_sna import (
    centrality as cen_mod,
    communities as comm_mod,
    config,
    data_loader,
    lineage as lin_mod,
    multilayer as ml_mod,
    report as report_mod,
    robustness as rob_mod,
    temporal as temp_mod,
    topology as topo_mod,
    visualization as viz,
)


def main() -> None:
    config.ensure_dirs()
    font_used = viz.setup_font()
    print(f"[1/9] 中文字体：{font_used}")

    warnings: list[str] = []

    # ---------- 数据
    print("[2/9] 读取数据并构图 ...")
    nodes_df, edges_df, g, qc_rows = data_loader.load_dataset()
    import pandas as pd
    pd.DataFrame(qc_rows).to_csv(config.TABLE_DIR / "00_数据质量核查.csv",
                                 index=False, encoding="utf-8-sig")
    err = [r for r in qc_rows if r["级别"] == "错误"]
    if err:
        raise SystemExit(f"数据质检发现致命错误：{err}")
    print(f"      节点 {g.number_of_nodes()}，边 {g.number_of_edges()}")

    # ---------- 拓扑
    print("[3/9] 整体拓扑 ...")
    topo_df, lcc = topo_mod.overall_metrics(g)
    topo_df.to_csv(config.TABLE_DIR / "01_整体拓扑指标.csv",
                   index=False, encoding="utf-8-sig")

    # ---------- 中心性
    print("[4/9] 中心性与 Gephi 交叉校验 ...")
    cen_df, valid_df = cen_mod.compute_centrality(g, nodes_df)

    # ---------- 社区
    print("[5/9] Louvain 社区 / k-核 ...")
    assign_df, comm_summary, comm_stats, u_active = comm_mod.detect_communities(g, nodes_df)
    cen_df = cen_df.merge(
        assign_df[["节点ID", "Louvain社区", "核心边缘", "k核层"]],
        left_on="节点ID", right_on="节点ID", how="left")
    cen_df.to_csv(config.TABLE_DIR / "02_节点中心性.csv",
                  index=False, encoding="utf-8-sig")
    valid_df.to_csv(config.TABLE_DIR / "03_Gephi一致性校验.csv",
                    index=False, encoding="utf-8-sig")
    assign_df.to_csv(config.TABLE_DIR / "04_社区与核层归属.csv",
                     index=False, encoding="utf-8-sig")
    comm_summary.to_csv(config.TABLE_DIR / "05_社区画像.csv",
                        index=False, encoding="utf-8-sig")

    # ---------- 谱系
    print("[6/9] 传承谱系与关键路径 ...")
    lineage = lin_mod.analyze_lineage(g)
    lineage["master_df"].to_csv(config.TABLE_DIR / "06_师承授受明线.csv",
                                index=False, encoding="utf-8-sig")
    lineage["chains_df"].to_csv(config.TABLE_DIR / "07_最长溯源链.csv",
                                index=False, encoding="utf-8-sig")
    lineage["depth_df"].to_csv(config.TABLE_DIR / "08_溯源深度排行.csv",
                               index=False, encoding="utf-8-sig")

    # ---------- 多层
    layer_df, layers = ml_mod.layer_metrics(g)
    particip = ml_mod.participation(g)
    level_df, level_detail = ml_mod.edge_level_table(g)
    layer_df.to_csv(config.TABLE_DIR / "09_关系层对比.csv",
                    index=False, encoding="utf-8-sig")
    particip.to_csv(config.TABLE_DIR / "10_跨层参与度.csv",
                    index=False, encoding="utf-8-sig")
    level_detail.to_csv(config.TABLE_DIR / "11_析出层级交叉表.csv",
                        index=False, encoding="utf-8-sig")

    # ---------- 鲁棒性
    print("[7/9] 鲁棒性仿真 ...")
    curves_df, half_df, rand_stats = rob_mod.simulate(u_active, n_random=100)
    curves_df.to_csv(config.TABLE_DIR / "12_鲁棒性衰减曲线.csv",
                     index=False, encoding="utf-8-sig")
    half_df.to_csv(config.TABLE_DIR / "13_鲁棒性半衰阈值.csv",
                   index=False, encoding="utf-8-sig")

    # ---------- 时序
    print("[8/9] 跨代时序 ...")
    era_mat = temp_mod.era_flow_matrix(g)
    era_sum = temp_mod.era_summary(g, era_mat)
    classics = temp_mod.classics_reception(g)
    era_mat.to_csv(config.TABLE_DIR / "14_时代流向矩阵.csv",
                   encoding="utf-8-sig")
    era_sum.to_csv(config.TABLE_DIR / "15_时代援引画像.csv",
                   index=False, encoding="utf-8-sig")
    classics.to_csv(config.TABLE_DIR / "16_原典被承继谱.csv",
                    index=False, encoding="utf-8-sig")

    # ---------- 可视化（逐图容错）
    print("[9/9] 生成图表与交互网络 ...")
    fig_jobs = [
        ("fig_network_overview", lambda: viz.fig_network_overview(
            g, cen_df, config.FIG_DIR / "fig_network.png")),
        ("fig_centrality", lambda: viz.fig_centrality(
            cen_df, config.FIG_DIR / "fig_centrality.png")),
        ("fig_communities", lambda: viz.fig_communities(
            g, assign_df, config.FIG_DIR / "fig_communities.png")),
        ("fig_robustness", lambda: viz.fig_robustness(
            curves_df, rand_stats, config.FIG_DIR / "fig_robustness.png")),
        ("fig_era_flow", lambda: viz.fig_era_flow(
            era_mat, config.FIG_DIR / "fig_era_flow.png")),
        ("fig_layers", lambda: viz.fig_layers(
            layer_df, config.FIG_DIR / "fig_layers.png")),
    ]
    for name, job in fig_jobs:
        try:
            job()
        except Exception as exc:  # 图失败不阻断报告
            warnings.append(f"{name} 生成失败：{exc}")
            traceback.print_exc()

    try:
        viz.interactive_network(
            g, config.INTERACTIVE_DIR / "network_interactive.html")
    except Exception as exc:
        warnings.append(f"交互式网络图生成失败：{exc}")
        traceback.print_exc()

    # ---------- 报告
    results = {
        "qc_rows": qc_rows,
        "topo_df": topo_df, "lcc": lcc,
        "centrality": cen_df, "validation": valid_df,
        "comm_summary": comm_summary, "comm_stats": comm_stats,
        "lineage": lineage,
        "layer_df": layer_df, "participation": particip,
        "half_df": half_df,
        "era_mat": era_mat, "era_sum": era_sum, "classics": classics,
        "warnings": warnings,
    }
    report_path = config.OUTPUT_DIR / "report.html"
    report_mod.build_report(results, report_path)
    standalone_path = config.OUTPUT_DIR / "report_standalone.html"
    report_mod.pack_standalone(
        report_path, standalone_path,
        config.INTERACTIVE_DIR / "network_interactive.html")
    print(f"\n完成 ✅  报告：{report_path}")
    print(f"          单文件版：{standalone_path}")
    if warnings:
        print("运行期提示：")
        for w in warnings:
            print("  -", w)


if __name__ == "__main__":
    main()
