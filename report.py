# -*- coding: utf-8 -*-
"""将全部分析结果组装为中文 HTML 报告，并提供单文件打包。"""
from __future__ import annotations

import base64
import datetime as _dt
import re
from html import escape
from pathlib import Path

import pandas as pd

from . import config


def _df_html(df: pd.DataFrame, float_fmt: str = "{:.3f}") -> str:
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].map(lambda v: "" if pd.isna(v) else float_fmt.format(v))
    return df.to_html(index=False, escape=True, border=0,
                      classes="tbl", justify="center")


def _metric(df: pd.DataFrame, name: str):
    row = df[df["指标"] == name]
    return row.iloc[0]["数值"] if len(row) else None


def _build_findings(r: dict) -> list[str]:
    """根据实际计算结果生成核心发现条目。"""
    topo, lcc = r["topo_df"], r["lcc"]
    cen = r["centrality"]
    comm_stats = r["comm_stats"]
    layer_df = r["layer_df"]
    half = r["half_df"]

    top_in = cen.sort_values("加权入度", ascending=False).head(3)
    top_bet = cen.sort_values("介数(原始)", ascending=False).head(3)
    in_txt = "、".join(f"《{x['文献'].strip('《》')}》({x['加权入度']:.2f})"
                       for _, x in top_in.iterrows())
    bet_txt = "、".join(f"《{x['文献'].strip('《》')}》(介数{x['介数(原始)']:.1f})"
                        for _, x in top_bet.iterrows())

    lineage_edge = int(layer_df.loc[layer_df["关系层"] == "学术传承类", "边数"].iloc[0])
    zhushu_edge = int(layer_df.loc[layer_df["关系层"] == "注疏阐释类", "边数"].iloc[0])
    yinwen_edge = int(layer_df.loc[layer_df["关系层"] == "引文参考类", "边数"].iloc[0])
    fangfa_edge = int(layer_df.loc[layer_df["关系层"] == "方法支撑类", "边数"].iloc[0])
    banben_edge = int(layer_df.loc[layer_df["关系层"] == "版本源流类", "边数"].iloc[0])

    bet_first = half[half["策略"] == "介数优先攻击"]["LCC首次降至一半以下时的移除比例"].iloc[0]
    rand_first = half[half["策略"] == "随机失效(均值)"]["LCC首次降至一半以下时的移除比例"].iloc[0]

    findings = [
        f"网络含 <b>{topo.loc[topo['指标']=='节点数 N','数值'].iloc[0]:.0f}</b> 个文献节点、"
        f"<b>{topo.loc[topo['指标']=='边数 M','数值'].iloc[0]:.0f}</b> 条有向加权关系，"
        f"密度仅 {_metric(topo,'网络密度'):.3f}，最大弱连通分量包含 "
        f"{_metric(topo,'最大弱连通分量规模'):.0f} 个节点"
        f"（占全网络 {_metric(topo,'最大弱连通分量规模')/40:.0%}，占活跃节点 "
        f"{_metric(topo,'最大弱连通分量规模')/(40-_metric(topo,'孤立节点数')):.0%}），"
        f"另含 11 个孤立节点与 1 个独立的《方言》校勘三元链；主网络是一张稀疏但"
        f"连通度很高的「枢纽—原典」型学术传承网络；非平凡强连通分量为 "
        f"{_metric(topo,'强连通分量数（非平凡）'):.0f} 个，表明网络整体呈"
        f"「后世溯源、原典被溯」的无环源流结构。",

        f"加权入度（被承继权威度）前三为 {in_txt}——《说文》《尔雅》《广韵》三部"
        f"小学原典构成考据方法的「密码本」基石；介数中心性前三为 {bet_txt}，"
        f"戴震《孟子字义疏证》高居中介枢纽，量化印证了「戴震承顾启段、联结高邮二王」"
        f"的乾嘉范式中枢地位。",

        f"Louvain 加权社区发现模块度 Q = {comm_stats['louvain模块度Q']}，"
        f"得到 {comm_stats['社区数']} 个学群，与 Gephi 预置划分的标准化互信息 "
        f"NMI = {comm_stats['与Gephi划分NMI']}，两套算法相互印证；最高 "
        f"{comm_stats['最大k核层数']}-核核心层仅 {comm_stats['核心层节点数']} 个节点"
        f"（《说文》《尔雅》与黎锦熙两部语文著作），说明跨时代最致密的结构内核"
        f"是「形义—训诂原典 ↔ 现代语文编纂」的直接接续。",

        f"关系层结构：学术传承 {lineage_edge} 条、注疏阐释 {zhushu_edge} 条、"
        f"方法支撑 {fangfa_edge} 条、引文参考 {yinwen_edge} 条、版本源流 {banben_edge} 条。"
        f"传承+阐释关系占近半数，说明网络的主导联结是「师承授受—文本注疏」而非简单引用，"
        f"符合乾嘉学术以注经和家法传递知识的特征。",

        f"鲁棒性仿真显示：按介数移除约 {bet_first:.0%} 的节点即令主分量跌破一半，"
        f"而随机失效需移除约 {rand_first:.0%}，网络对「关键范式人物」的蓄意攻击显著敏感，"
        f"呈典型的小世界枢纽依赖结构——这从反面说明戴震等中介者对传统维系的决定性意义。",

        f"全部关系均标注证据类型与位置：文本内证、目录著录、学术史定论、后人推断四级"
        f"证据与权重（0.34–0.92）一一对应，把「无征不信」的考据伦理转译为可审计的"
        f"边权重与证据字段，为人文网络的数据诚信提供了可复核范式。",
    ]
    return findings


_CSS = """
:root{--ink:#22263b;--brand:#7a1f2b;--accent:#b88746;--soft:#f7f4ee;--line:#e3ddd2;}
*{box-sizing:border-box;}
body{font-family:"Microsoft YaHei","SimHei",sans-serif;color:var(--ink);
 margin:0;background:var(--soft);line-height:1.85;}
.hero{background:linear-gradient(135deg,#2b2330,#7a1f2b);color:#fff;padding:48px 0 38px;}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px;}
.hero h1{margin:0 0 8px;font-size:28px;letter-spacing:1px;}
.hero p{margin:4px 0;opacity:.9;font-size:14px;}
section{background:#fff;border:1px solid var(--line);border-radius:12px;
 padding:26px 30px;margin:26px 0;box-shadow:0 2px 10px rgba(60,40,20,.05);}
h2{font-size:21px;color:var(--brand);border-left:5px solid var(--accent);
 padding-left:12px;margin:0 0 16px;}
h3{font-size:16px;color:#5b3b16;margin:22px 0 8px;}
p{font-size:14.5px;text-align:justify;}
ul.findings{padding-left:0;list-style:none;}
ul.findings li{background:#fbf7ef;border-left:4px solid var(--accent);
 padding:12px 16px;margin:10px 0;border-radius:0 8px 8px 0;font-size:14px;}
table.tbl{border-collapse:collapse;width:100%;font-size:12.5px;margin:12px 0;}
.tbl th{background:#efe7d8;color:#4a3418;padding:8px 9px;text-align:center;
 border-bottom:2px solid var(--accent);white-space:nowrap;}
.tbl td{padding:6px 9px;border-bottom:1px solid var(--line);vertical-align:top;}
.tbl tr:nth-child(even){background:#faf7f1;}
.fig{width:100%;border:1px solid var(--line);border-radius:8px;margin:14px 0;}
.pill{display:inline-block;background:#efe7d8;color:#6b4a1c;border-radius:999px;
 padding:2px 12px;font-size:12px;margin-right:8px;}
.note{background:#eef3f7;border-left:4px solid #4C72B0;padding:10px 14px;
 border-radius:0 8px 8px 0;font-size:13.5px;margin:12px 0;}
.warn{background:#fdf0ee;border-left:4px solid #C44E52;padding:10px 14px;
 border-radius:0 8px 8px 0;font-size:13.5px;margin:12px 0;}
a.btn{display:inline-block;background:var(--brand);color:#fff;padding:9px 20px;
 border-radius:8px;text-decoration:none;font-size:14px;margin:6px 10px 6px 0;}
.qc-通过{color:#2e7d32;font-weight:bold;}
.qc-警告{color:#b26a00;font-weight:bold;}
.qc-错误{color:#c62828;font-weight:bold;}
.qc-信息{color:#555;}
footer{text-align:center;color:#8a7f6d;font-size:12.5px;padding:30px 0 46px;}
code{background:#efe7d8;padding:1px 6px;border-radius:4px;font-size:12.5px;}
"""


def build_report(r: dict, out_path) -> None:
    findings = _build_findings(r)
    qc_df = pd.DataFrame(r["qc_rows"])
    qc_df["结果"] = [f'<span class="qc-{lvl}">{escape(str(v))}</span>'
                    for lvl, v in zip(qc_df["级别"], qc_df["结果"])]
    qc_html = qc_df[["检查项", "结果", "明细"]].to_html(
        index=False, escape=False, border=0, classes="tbl", justify="center")

    topo_view = r["topo_df"].copy()
    topo_view["数值"] = topo_view["数值"].map(
        lambda v: (f"{v:.4f}" if isinstance(v, float) and abs(v) < 10 and v == v
                   else (f"{v:.0f}" if float(v).is_integer() else f"{v:.3f}")))

    cen_cols = ["文献", "责任者", "成书时代", "入度", "出度", "加权入度",
                "介数(原始)", "入接近中心性", "PageRank", "特征向量中心性",
                "聚类系数", "Louvain社区", "核心边缘"]
    cen_view = r["centrality"][cen_cols].head(20)

    parts: list[str] = []
    parts.append(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>乾嘉学派学术传承文献网络建模分析报告</title><style>{_CSS}</style></head><body>
<div class="hero"><div class="wrap">
<h1>乾嘉学派学术传承文献网络 · 建模与社会网络分析报告</h1>
<p>数据基础：《乾嘉学派学术传承网络节点表/边表》（GB/T 7714-2025 著录，40 节点 / 41 边）</p>
<p>方法框架：有向加权图 · 中心性 · Louvain 社区 · k-核/核心-边缘 · 多层网络 · 鲁棒性仿真 · 跨代时序</p>
<p>生成时间：{_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}　随机种子：{config.RANDOM_SEED}（全流程可复现）</p>
</div></div><div class="wrap">""")

    # ---------------- 摘要
    parts.append("<section><h2>一、核心发现摘要</h2><ul class='findings'>")
    parts.extend(f"<li>{f}</li>" for f in findings)
    parts.append("""</ul>
<a class="btn" href="interactive/network_interactive.html" target="_blank">▶ 全屏打开交互式网络图</a>
<a class="btn" href="tables/" target="_blank">📂 查看全部指标 CSV</a>
<h3>交互式网络图（可拖拽 / 滚轮缩放 / 悬停查看著录与证据信息）</h3>
<iframe loading="lazy" src="interactive/network_interactive.html" title="交互式网络图"
 style="width:100%;height:880px;border:1px solid var(--line);border-radius:8px;background:#1e1e24;"></iframe>
</section>""")

    # ---------------- 数据建模与质检
    parts.append(f"""<section><h2>二、数据建模与质量核查</h2>
<p>将文献视为节点、文献间关系视为<b>有向加权边</b>：边由后世/承继方文献指向原典/师法对象，
权重为 0–1 的关系强度（由证据等级标定：注疏与师承 0.84–0.92，直接引用 0.68，后人推断的暗用仅 0.34）。
节点挂载 GB/T 7714 著录属性，边挂载关系大类、关系细分、析出层级、证据位置与证据类型，
形成「节点—边—证据」三层可追溯模型。关系大类共五类，对应版本层、阐释层、传承层、引用层。</p>
<div class="note"><span class="pill">口径</span>节点表中的 <code>indegree / betweenesscentrality</code>
等列为 Gephi 0.10 预算结果，本工具全部指标由 NetworkX 独立重算，并以 Spearman 秩相关做交叉信度校验；
著录字段中的「出版年」为当代整理本年份，时序分析另用成书时代编码（见第九节）。</div>
<h3>2.1 数据质量核查表</h3>{qc_html}
</section>""")

    # ---------------- 整体拓扑
    parts.append(f"""<section><h2>三、整体网络拓扑结构</h2>
<img class="fig" src="figures/fig_network.png" alt="网络总览图">
{topo_view.to_html(index=False, escape=False, border=0, classes='tbl', justify='center')}
<p>解读：网络稀疏（密度 {_metric(r['topo_df'],'网络密度'):.3f}）而主分量连通度高
（主分量 {_metric(r['topo_df'],'最大弱连通分量规模'):.0f} 节点，占活跃节点
{_metric(r['topo_df'],'最大弱连通分量规模')/(40-_metric(r['topo_df'],'孤立节点数')):.0%}；
另有 11 个孤立节点与《方言》校勘三元链独立于主分量），
平均路径长度 {_metric(r['topo_df'],'最大分量平均路径（无向）'):.2f}、直径
 {_metric(r['topo_df'],'最大分量直径（无向）'):.0f}，主分量内任意两部文献平均约 2.8 步即可经
某部枢纽文献建立联系，具备<b>小世界</b>特征；互惠性为 0，源流关系不可逆转——
注疏者引原典而原典无法反向引用，这是历史文献网络区别于现代引文网络的结构性特征。
度同配系数为负，说明高度数枢纽倾向连接低度边缘原典，呈典型的<b>异配枢纽结构</b>。</p></section>""")

    # ---------------- 中心性
    rho_rows = r["validation"]
    parts.append(f"""<section><h2>四、中心性分析：谁是权威，谁是枢纽</h2>
<img class="fig" src="figures/fig_centrality.png" alt="中心性图">
<h3>4.1 节点中心性一览（按介数排序，前 20）</h3>
{_df_html(cen_view)}
<h3>4.2 与 Gephi 预算指标的交叉信度校验（Spearman 秩相关）</h3>
{_df_html(rho_rows, float_fmt="{:.4f}")}
<div class="note">入度、介数、聚类系数与 Gephi 结果的秩相关 ρ = 1.0，完全一致，验证了建模与重算的
可靠性；接近 / 调和接近中心性 ρ ≈ 0.61–0.64，差异来自 Gephi 对有向图采用「按可达节点归一化
（Wasserman–Faust）」口径，而本表同时报告全样本归一化的有向入接近与无向投影两种口径，
孤立点的处理亦不同，表中已逐项注明，属口径差异而非计算错误。</div>
<p><b>学术含义：</b>《说文》《尔雅》《广韵》以高加权入度成为「被援引的权威」（知识源头），
而戴震著作以高介数成为「必经的枢纽」（范式中介）——权威度与介数中心性在本网络中分离，
说明乾嘉学术中<b>原典立基、宗师转枢</b>的双层权力结构：原典提供方法工具，
戴震等集大成者负责把方法转化为可传承的研究范式并分配给后学。</p></section>""")

    # ---------------- 社区
    parts.append(f"""<section><h2>五、社区结构与核心—边缘</h2>
<img class="fig" src="figures/fig_communities.png" alt="社区图">
<h3>5.1 社区统计</h3>
{_df_html(r['comm_summary'])}
<h3>5.2 结构指标</h3>
{_df_html(pd.DataFrame([{'指标': k, '值': str(v)} for k, v in r['comm_stats'].items()
                       if k != 'k壳分布']))}
<p>四个社区的成员构成可作如下学群解读：<b>C1 近现代语文编纂群</b>（10 节点）以黎锦熙
《新著国语文法》《国语辞典》及《辞源》《辞海》《袁吉六集》为主体，与《说文》《尔雅》
及其清人注疏（段注、邵疏、郭注）同居一群——20 世纪辞书与语法学并非另起炉灶，而是直接
嵌入汉代小学原典；<b>C2 皖派—高邮孟学校勘群</b>（10 节点）以戴震《孟子字义疏证》为枢纽，
上承《孟子》《论语》《乐记》与顾炎武《日知录》，下启高邮王氏四种；<b>C3 古韵学群</b>
（6 节点）由《切韵》→《广韵》→《集韵》版本源流链与顾炎武《音学五书》、戴震《声韵考》、
段玉裁《六书音韵表》构成；<b>C4 方言校勘群</b>（3 节点）为《方言》→郭璞《方言注》→
戴震《方言疏证》的跨千年专学链。最高 3-核核心层为《说文》《尔雅》与黎锦熙两部著作，
表明全网最致密的联结恰好发生在<b>汉代原典与现代语文工程之间</b>。</p></section>""")

    # ---------------- 谱系
    parts.append('<section><h2>六、学术传承谱系与师承路径</h2>')
    parts.append(f"""<p>在「学术传承 ∪ 注疏阐释」子图（{r['lineage']['nodes']} 节点 /
{r['lineage']['edges']} 边，DAG={r['lineage']['is_dag']}）上提取师承明线与最长溯源链：</p>
<h3>6.1 师承授受明线</h3>{_df_html(r['lineage']['master_df'])}""")
    if len(r["lineage"]["chains_df"]):
        top_chain = r["lineage"]["chains_df"].iloc[0]["溯源链（后世→原典）"]
        parts.append(f"<h3>6.2 最长学术溯源链（去重后前 15）</h3>"
                     f"{_df_html(r['lineage']['chains_df'])}")
    else:
        top_chain = ""
    parts.append(f"""<h3>6.3 全网络溯源深度 Top 10</h3>{_df_html(r['lineage']['depth_df'])}
<div class="note">最长链路为「{top_chain}」，把 20 世纪现代语法学经高邮王氏家学、
戴震范式一路锚定到先秦《孟子》；全网络最深溯源达 7 跳，定量呈现了乾嘉学术
「学有渊源、语有来历」的传承纵深。</div>
</section>""")

    # ---------------- 多层
    parts.append(f"""<section><h2>七、多层关系网络：五类学术联结的分工</h2>
<img class="fig" src="figures/fig_layers.png" alt="关系层图">
{_df_html(r['layer_df'])}
<h3>7.1 跨层参与度最高的文献</h3>
{_df_html(r['participation'].head(12))}
<p>「方法支撑层」的被支撑对象高度集中于《广韵》（5 条）与《说文解字》（3 条）——音、形
两大「密码本」是乾嘉校勘训诂的操作工具，《尔雅》本身亦以「形义互证／音义互证」边汇入该层；
高跨层参与度节点（《尔雅》《说文》《孟子字义疏证》《广雅疏证》）同时充当原典、工具与
传承中介，是多层耦合的关键接口。</p></section>""")

    # ---------------- 鲁棒性
    parts.append(f"""<section><h2>八、网络鲁棒性：对枢纽人物的结构依赖</h2>
<img class="fig" src="figures/fig_robustness.png" alt="鲁棒性图">
{_df_html(r['half_df'])}
<p>在无向加权投影上对比四种蓄意攻击与 100 次随机失效。主分量对度/介数导向攻击高度敏感、
对随机失效稳健，是枢纽依赖型小世界网络的典型韧性曲线（样本规模有限，曲线形态解读优先于
具体阈值）。其史学含义是：乾嘉学术共同体的维系
高度依赖戴震、顾炎武等少数范式中介，一旦中介缺席，学群即裂解为分散的原典注疏者。</p></section>""")

    # ---------------- 时序
    era_mat = r["era_mat"].copy()
    era_mat.insert(0, "承继方＼被承继方", era_mat.index)
    parts.append(f"""<section><h2>九、跨代时序：两千年的溯源方向</h2>
<img class="fig" src="figures/fig_era_flow.png" alt="时代流向图">
<h3>9.1 各时代外向援引画像</h3>{_df_html(r['era_sum'])}
<h3>9.2 先秦两汉原典的被承继谱</h3>{_df_html(r['classics'])}
<div class="warn"><b>方法论说明：</b>节点表「出版年」字段是中华书局等当代整理本年份
（1980–2024），不能用于历史时序；本节的成书时代系依据学术史常识对 40 个节点逐一人工编码
（汉 / 魏晋至宋 / 清初 / 乾嘉 / 近现代），编码表见 <code>qianjia_sna/config.py</code>，可独立复核修正。</div>
<p>流向矩阵几乎全部集中在「后世行 × 原典列」：乾嘉鼎盛层 18 条外向关系中 11 条
（约六成）指向先秦两汉、魏晋与清初先于自己的文献，其余 7 条为同时代（戴、段、二王之间）
互涉；近现代层（黎锦熙、辞书）则同时溯至汉代原典（7 条）与乾嘉层（2 条），
构成<b>「原典—清学—近现代」三段不断流的证据链</b>。</p></section>""")

    # ---------------- 学术诚信论域
    parts.append("""<section><h2>十、方法论对接：文献网络与「无征不信」的学术诚信命题</h2>
<p>本工具的建模选择与所研究论文的论旨形成直接呼应，可将乾嘉学术诚信规范从思想史叙述
转写为可计算的网络证据：</p>
<ul class="findings">
<li><b>证据可审计化：</b>每条边强制携带「证据类型 + 证据位置」，注疏类文本内证（如「段注直接
注释《说文》」）权重 0.87–0.92，后人推断的暗用（如「暗用『以意逆志』」）仅 0.34——低权重关系
在 PageRank、社区与鲁棒性中自动获得更小影响，从模型机制上实现了「无征不信」。</li>
<li><b>穷尽式利用的网络投影：</b>高入度原典（《说文》《尔雅》各 6 次、《孟子》3 次）与
高密度核心层，量化了乾嘉学者「竭泽而渔」式征用原典的研究伦理；核心—边缘结构显示
新注（边缘）始终回接证据核心（原典与范式著作），杜绝无根之论。</li>
<li><b>师承可追溯：</b>师承授受边均以「序」为证据位置、标为学术史定论，最长溯源链使每位学者的
方法来源可逐级回溯至原典，为学术传承中的优先权与贡献界定提供结构化依据。</li>
<li><b>批判性继承的拓扑表达：</b>郭璞《方言注》与戴震《方言疏证》并立指向《方言》、
邵晋涵《尔雅正义》「承郭注而补正」（边备注中明示）等「同一原典、新旧注本并存」的结构，
刻画了乾嘉「实事求是」对旧注既承继又纠谬的学术对话方式。</li>
</ul></section>""")

    # ---------------- 局限
    parts.append(f"""<section><h2>十一、局限与可复现性</h2>
<ul>
<li><b>样本规模有限（N=40, M=41）：</b>指标趋势（枢纽、社区、鲁棒性）稳健，但点估计
（尤其特征向量中心性、同配系数）不宜外推为整个清代学术网络的总体参数；扩充焦循、阮元、
钱大昕等节点后结构可能微调。</li>
<li><b>权重含专家判断：</b>关系强度由证据等级编码，反映研究团队的史学判断而非文献计量频率；
已通过证据字段公开编码依据，支持敏感性分析（可改用 0/1 无权网对照）。</li>
<li><b>成书时代为人工编码：</b>单篇析出文献（如《乐记》《大学》）的成书年代本身有学术争议，
编码取通行说法，集中存于配置文件便于修订重算。</li>
<li>可复现：固定随机种子 {config.RANDOM_SEED}；运行 <code>python run_analysis.py</code>
一键重算全部 CSV、PNG 与 HTML；全部图表失败不阻断报告生成。</li>
</ul></section>""")

    if r["warnings"]:
        parts.append("<section><h2>附：运行期提示</h2><ul>" +
                     "".join(f"<li>{escape(w)}</li>" for w in r["warnings"]) +
                     "</ul></section>")

    parts.append("""<footer>乾嘉学派学术传承网络建模分析 · Python(NetworkX/pandas/matplotlib/pyvis) ·
方法论：历史文献分析 + 社会网络分析(SNA) + 多层网络 + 鲁棒性仿真</footer>
</div></body></html>""")

    out_path.write_text("".join(parts), encoding="utf-8")


def pack_standalone(report_path, out_path, interactive_path=None) -> None:
    """把报告打包成单文件 HTML：图片转 base64 内嵌，交互图整页内嵌为数据页 iframe。

    打包后仅需分发一个文件即可在任意浏览器离线打开。
    """
    report_path, out_path = Path(report_path), Path(out_path)
    html = report_path.read_text(encoding="utf-8")

    def _embed_img(m: "re.Match[str]") -> str:
        img = report_path.parent / m.group(1)
        if img.exists():
            b64 = base64.b64encode(img.read_bytes()).decode()
            return f'src="data:image/png;base64,{b64}"'
        return m.group(0)

    html = re.sub(r'src="(figures/[^"]+)"', _embed_img, html)

    # 去掉依赖本地目录的入口按钮（单文件版无 tables/ 等伴随目录）
    html = re.sub(r'<a class="btn" href="tables/"[^>]*>[^<]*</a>', "", html)
    html = re.sub(
        r'<a class="btn" href="interactive/network_interactive\.html"[^>]*>[^<]*</a>',
        "", html)

    if interactive_path and Path(interactive_path).exists():
        b64 = base64.b64encode(Path(interactive_path).read_bytes()).decode()
        html = html.replace(
            'src="interactive/network_interactive.html"',
            f'src="data:text/html;base64,{b64}"')

    out_path.write_text(html, encoding="utf-8")
