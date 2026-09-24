# -*- coding: utf-8 -*-
"""
03_dashboard.py
===============
构建「海外运动健康垂类 KOL 营销决策看板」v2（高级版）
- 深色数据产品风格：Header + 6 张 KPI 指标卡 + 8 张交互图表 + 方法论 Footer
- 交互：hover 定制、图例、滚轮缩放；完全自包含（内嵌 plotly.js，无 CDN）
产出：dashboard/sports_fitness_kol_dashboard.html
数据来源：sql_results/*.csv 与 data/processed/sports_fitness_health.csv
"""

import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sql_results"
DASH_DIR = ROOT / "dashboard"
DASH_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 深色主题色板 ----------
BG_CARD       = "#0f1b30"
BG_PLOT       = "#0b1526"
BORDER        = "rgba(148,163,184,0.16)"
GRID_LINE     = "rgba(148,163,184,0.10)"
TXT_MAIN      = "#f1f5f9"
TXT_SUB       = "#94a3b8"

C_BLUE   = "#38bdf8"
C_ORANGE = "#fb923c"
C_GREEN  = "#34d399"
C_PURPLE = "#a78bfa"
C_PINK   = "#f472b6"
C_RED    = "#f87171"
C_YELLOW = "#fbbf24"
C_GREY   = "#64748b"
C_DIM    = "#334155"

PLATFORM_COLORS = {
    "TikTok": C_ORANGE, "YouTube": C_RED, "Instagram": C_PURPLE,
    "Facebook": C_BLUE, "Twitter": C_GREEN, "LinkedIn": C_GREY,
}

HOVER = dict(bgcolor="#1e293b", bordercolor="rgba(148,163,184,0.35)",
             font=dict(color="#f8fafc", size=12))

def base_layout(title, height, xtitle=None, ytitle=None):
    return dict(
        title=dict(text=title, x=0.02, font=dict(size=15, color=TXT_MAIN)),
        height=height, margin=dict(l=8, r=20, t=56, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG_PLOT,
        font=dict(family="Segoe UI, Microsoft YaHei, Arial", size=12, color=TXT_MAIN),
        hoverlabel=HOVER,
        xaxis=dict(showgrid=True, gridcolor=GRID_LINE, zeroline=False,
                   tickfont=dict(color=TXT_SUB), title=dict(text=xtitle, font=dict(color=TXT_SUB))),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color=TXT_SUB), title=dict(text=ytitle, font=dict(color=TXT_SUB))),
    )

# ---------- 读取数据 ----------
q1 = pd.read_csv(OUT / "q1_category_overview.csv", encoding="utf-8")
q2 = pd.read_csv(OUT / "q2_sfh_vs_others.csv", encoding="utf-8")
q3 = pd.read_csv(OUT / "q3_sfh_by_platform.csv", encoding="utf-8")
q4 = pd.read_csv(OUT / "q4_sfh_by_tier.csv", encoding="utf-8")
q5 = pd.read_csv(OUT / "q5_sfh_by_content_type.csv", encoding="utf-8")
q6 = pd.read_csv(OUT / "q6_sfh_platform_tier.csv", encoding="utf-8")
q8 = pd.read_csv(OUT / "q8_sfh_by_weekday.csv", encoding="utf-8")
model = pd.read_csv(OUT / "scenario_model.csv", encoding="utf-8")
sfh = pd.read_csv(ROOT / "data" / "processed" / "sports_fitness_health.csv", encoding="utf-8")
full = pd.read_csv(ROOT / "data" / "processed" / "full_dataset.csv", encoding="utf-8")

sfh_mean = sfh["Engagement_Rate_winsorized"].mean()       # 8.16
full_mean = full["Engagement_Rate_winsorized"].mean()     # 8.79
others_mean = q2.loc[q2["segment"] == "Others", "avg_er_pct"].iloc[0]
sfh_eng1k = q2.loc[q2["segment"] == "Sports/Fitness/Health", "avg_eng_per_1k_views"].iloc[0]
others_eng1k = q2.loc[q2["segment"] == "Others", "avg_eng_per_1k_views"].iloc[0]

# KPI：预算按平台聚合
budget_by_platform = model.groupby("Platform")["budget_alloc"].sum().sort_values(ascending=False)
tiktok_share = budget_by_platform["TikTok"] / budget_by_platform.sum() * 100

# ---------- 图1：各内容垂类平均互动率 ----------
q1s = q1.sort_values("avg_er_pct", ascending=True)
colors1 = [C_GREEN if c in ("Sports", "Fitness", "Health") else C_DIM for c in q1s["Category"]]
fig1 = go.Figure(go.Bar(
    x=q1s["avg_er_pct"], y=q1s["Category"], orientation="h",
    marker_color=colors1, text=q1s["avg_er_pct"].round(1),
    textposition="outside", textfont=dict(color=TXT_SUB, size=11),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q1s["posts"]))
fig1.add_vline(x=full_mean, line_dash="dash", line_color=C_ORANGE, line_width=1.5,
               annotation_text=f"全量均值 {full_mean:.2f}%",
               annotation_position="top left",
               annotation_font=dict(color=C_ORANGE, size=11))
fig1.update_layout(**base_layout("各内容垂类平均互动率（运动/健身/健康高亮）", 420, xtitle="平均互动率 %"))

# ---------- 图2：平台对比 ----------
q3s = q3.sort_values("avg_er_pct", ascending=True)
colors2 = [C_ORANGE if p == "TikTok" else C_BLUE for p in q3s["Platform"]]
fig2 = go.Figure(go.Bar(
    x=q3s["avg_er_pct"], y=q3s["Platform"], orientation="h",
    marker_color=colors2, text=q3s["avg_er_pct"].round(1),
    textposition="outside", textfont=dict(color=TXT_SUB, size=11),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q3s["posts"]))
fig2.add_trace(go.Scatter(
    x=q3s["avg_er_pct"], y=q3s["Platform"], mode="text",
    text=[f"中位播放 {v/1000:.0f}k" for v in q3s["median_views"]],
    textposition="middle right", textfont=dict(color=TXT_SUB, size=11), showlegend=False))
fig2.update_layout(**base_layout("运动健康垂类：各平台平均互动率（TikTok 断层领先）", 380, xtitle="平均互动率 %"))

# ---------- 图3：达人层级 ----------
q4s = q4.sort_values("avg_er_pct", ascending=True)
colors3 = []
for tier in q4s["Influencer_Tier"]:
    colors3.append({"Nano": C_PINK, "Micro": C_ORANGE, "Mid-tier": C_BLUE, "Macro": C_GREY}[tier])
fig3 = go.Figure(go.Bar(
    x=q4s["avg_er_pct"], y=q4s["Influencer_Tier"], orientation="h",
    marker_color=colors3,
    text=[f"{v:.1f}% · n={int(n)}" for v, n in zip(q4s["avg_er_pct"], q4s["posts"])],
    textposition="outside", textfont=dict(color=TXT_SUB, size=11),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q4s["posts"]))
fig3.update_layout(**base_layout("达人层级：粉丝量越低互动率越高（Nano 样本偏小）", 340, xtitle="平均互动率 %"))

# ---------- 图4：内容形式 Top10 ----------
q5t = q5.sort_values("avg_er_pct", ascending=False).head(10)
colors4 = [C_ORANGE] + [C_BLUE] * 9
fig4 = go.Figure(go.Bar(
    x=q5t["avg_er_pct"], y=q5t["Content_Type"], orientation="h",
    marker_color=colors4, text=q5t["avg_er_pct"].round(1),
    textposition="outside", textfont=dict(color=TXT_SUB, size=11),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q5t["posts"]))
fig4.update_layout(**base_layout("内容形式互动率 Top10（Duet/Stitch 领先）", 420, xtitle="平均互动率 %"))

# ---------- 图5：平台 × 达人层级热力图 ----------
q6p = q6.pivot_table(index="Influencer_Tier", columns="Platform", values="avg_er_pct", aggfunc="mean")
tier_order = ["Micro", "Mid-tier", "Macro"]
plat_order = ["TikTok", "Instagram", "Facebook", "Twitter", "YouTube", "LinkedIn"]
q6p = q6p.reindex(index=[t for t in tier_order if t in q6p.index], columns=[p for p in plat_order if p in q6p.columns])
z = q6p.values.astype(float)
z_text = [["–" if pd.isna(v) else f"{v:.1f}" for v in row] for row in z]
fig5 = go.Figure(go.Heatmap(
    z=z, x=list(q6p.columns), y=list(q6p.index),
    text=z_text, texttemplate="%{text}", textfont=dict(color="#0f172a", size=12),
    colorscale=[[0.0, "#0b3b66"], [0.45, "#0e7490"], [0.75, "#22d3ee"], [1.0, "#fde047"]],
    colorbar=dict(title=dict(text="互动率 %", font=dict(color=TXT_SUB, size=11)),
                  thickness=12, tickfont=dict(color=TXT_SUB)),
    hovertemplate="%{y} × %{x}<br>平均互动率 %{z:.1f}%<extra></extra>",
    xgap=4, ygap=4))
fig5.update_layout(**base_layout("平台 × 达人层级：平均互动率矩阵（TikTok×Micro 最强组合）", 400))
fig5.update_layout(coloraxis_showscale=True)

# ---------- 图6：粉丝量 vs 互动率散点 ----------
fig6 = go.Figure()
for plat, grp in sfh.groupby("Platform"):
    fig6.add_trace(go.Scatter(
        x=grp["Follower_Count"], y=grp["Engagement_Rate_winsorized"],
        mode="markers", name=plat, opacity=0.65,
        marker=dict(size=7, color=PLATFORM_COLORS.get(plat, C_GREY),
                    line=dict(width=0.5, color="rgba(255,255,255,0.35)")),
        hovertemplate=f"{plat}<br>粉丝 %{{x:,}}<br>互动率 %{{y:.1f}}%<extra></extra>"))
fig6.update_layout(**base_layout("粉丝量与互动率：小账号互动效率显著更高（对数轴）", 400,
                                 xtitle="粉丝量（对数）", ytitle="互动率 %（对数）"))
fig6.update_xaxes(type="log"); fig6.update_yaxes(type="log")
fig6.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=TXT_SUB, size=11)))

# ---------- 图7：星期发布规律 ----------
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
q8s = q8.set_index("Day_of_Week").reindex(order).reset_index()
fig7 = go.Figure(go.Bar(
    x=q8s["Day_of_Week"], y=q8s["avg_er_pct"], marker_color=C_BLUE,
    text=q8s["avg_er_pct"].round(1), textposition="outside",
    textfont=dict(color=TXT_SUB, size=11),
    hovertemplate="%{x}<br>平均互动率 %{y:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q8s["posts"]))
fig7.add_hline(y=sfh_mean, line_dash="dash", line_color=C_ORANGE, line_width=1.5,
               annotation_text=f"垂类均值 {sfh_mean:.2f}%",
               annotation_position="top right",
               annotation_font=dict(color=C_ORANGE, size=11))
fig7.update_layout(**base_layout("星期发布与互动率：周末发布表现更好", 340, ytitle="平均互动率 %"))

# ---------- 图8：预算分配（平台堆叠） ----------
model_t = model[model["budget_alloc"] > 0].copy()
tier_colors = {"Micro": C_BLUE, "Mid-tier": C_PURPLE, "Macro": C_GREY}
fig8 = go.Figure()
for tier, color in tier_colors.items():
    d = model_t[model_t["Influencer_Tier"] == tier]
    d = d.set_index("Platform").reindex(budget_by_platform.index).fillna(0).reset_index()
    fig8.add_trace(go.Bar(
        x=d["Platform"], y=d["budget_alloc"], name=tier,
        marker_color=color,
        hovertemplate="%{x} × " + tier + "<br>预算 $%{y:,.0f}<extra></extra>"))
total_by_platform = budget_by_platform.reindex(budget_by_platform.index).round(0)
fig8.add_trace(go.Scatter(
    x=budget_by_platform.index, y=budget_by_platform.values,
    mode="text",
    text=[f"${v/1000:.1f}K" for v in budget_by_platform.values],
    textposition="top center", textfont=dict(color=TXT_MAIN, size=11), showlegend=False))
fig8.update_layout(**base_layout("$100K 预算分配模拟：TikTok 组合获 51% 优先投入", 400, ytitle="预算（美元）"))
fig8.update_layout(barmode="stack",
                   legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=TXT_SUB, size=11)))

# ---------- KPI 数据 ----------
kpis = [
    {"label": "运动健康垂类样本", "value": "1,191", "unit": "帖",
     "note": f"占全量 5,000 帖的 {1191/5000*100:.1f}%"},
    {"label": "垂类平均互动率", "value": f"{sfh_mean:.2f}", "unit": "%",
     "note": f"全量均值 {full_mean:.2f}%", "accent": C_BLUE},
    {"label": "互动效率", "value": f"{sfh_eng1k:.0f}", "unit": "次/千播放",
     "note": f"其他垂类 {others_eng1k:.0f}（+{(sfh_eng1k/others_eng1k-1)*100:.1f}%）", "accent": C_GREEN},
    {"label": "TikTok 平均互动率", "value": "22.96", "unit": "%",
     "note": "6 平台中排名第 1（约为次名的 2 倍）", "accent": C_ORANGE},
    {"label": "Micro 达人互动率", "value": "32.48", "unit": "%",
     "note": "n=102 帖，远超 Macro 3.44%", "accent": C_YELLOW},
    {"label": "预算建议：TikTok 组合", "value": f"{tiktok_share:.1f}", "unit": "%",
     "note": f"$100K 预算中分配 ${budget_by_platform['TikTok']/1000:.1f}K", "accent": C_ORANGE},
]

# ---------- 组装 HTML ----------
PLOTLY_JS = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8")

figs = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]
specs = [
    {"id": "chart1", "title": "01 · 垂类对比", "desc": "运动/健身/健康 3 类高亮，虚线为全量均值"},
    {"id": "chart2", "title": "02 · 平台对比", "desc": "TikTok 平均互动率 22.96%，断层第一"},
    {"id": "chart3", "title": "03 · 达人层级", "desc": "层级越低互动率越高，Nano 样本 n=18 需谨慎"},
    {"id": "chart4", "title": "04 · 内容形式 Top10", "desc": "Duet / Stitch / Community Post 交互型内容领先"},
    {"id": "chart5", "title": "05 · 平台 × 层级矩阵", "desc": "TikTok×Micro 平均互动率 81.8%，为最强组合"},
    {"id": "chart6", "title": "06 · 粉丝量 vs 互动率", "desc": "对数轴散点，小账号互动效率显著更高"},
    {"id": "chart7", "title": "07 · 星期发布规律", "desc": "周末发布互动率更高，虚线为垂类均值"},
    {"id": "chart8", "title": "08 · 预算分配模拟", "desc": "$100K 按 效率×供给 加权，TikTok 组合获 51%"},
]

kpi_html = "".join(
    f'''<div class="kpi-card">
      <div class="kpi-label">{k["label"]}</div>
      <div class="kpi-value" style="color:{k.get('accent', '#f8fafc')}">{k["value"]}<span class="kpi-unit">{k["unit"]}</span></div>
      <div class="kpi-note">{k["note"]}</div>
    </div>''' for k in kpis)

chart_cards = "".join(
    f'''<div class="chart-card">
      <div class="chart-head">
        <div class="chart-title">{s["title"]}</div>
        <div class="chart-desc">{s["desc"]}</div>
      </div>
      <div id="{s["id"]}" class="chart-body"></div>
    </div>''' for s in specs)

import plotly.io as pio
fig_json = json.dumps([json.loads(pio.to_json(f)) for f in figs], ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>海外运动健康垂类 KOL 营销决策看板</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family:"Segoe UI","Microsoft YaHei",-apple-system,Arial,sans-serif;
  background:linear-gradient(180deg,#0f172a 0%,#0b1220 55%,#0a0f1c 100%);
  color:#f1f5f9; min-height:100vh; padding:28px 32px 40px;
}}
.wrap {{ max-width:1500px; margin:0 auto; }}
header {{ display:flex; align-items:flex-end; justify-content:space-between; flex-wrap:wrap; gap:14px; margin-bottom:24px; }}
h1 {{ font-size:26px; font-weight:700; letter-spacing:.3px; }}
h1 .dot {{ color:#38bdf8; }}
.sub {{ color:#94a3b8; font-size:13px; margin-top:6px; line-height:1.6; }}
.badge {{ display:inline-flex; align-items:center; gap:6px; font-size:12px; color:#94a3b8;
  background:rgba(148,163,184,.08); border:1px solid rgba(148,163,184,.18);
  padding:6px 12px; border-radius:999px; }}
.badge .tag {{ color:#38bdf8; font-weight:600; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-bottom:24px; }}
.kpi-card {{ background:linear-gradient(160deg,#16223b 0%,#101a2e 100%);
  border:1px solid {BORDER}; border-radius:14px; padding:18px 18px 16px;
  transition:transform .15s ease, border-color .15s ease, box-shadow .15s ease; }}
.kpi-card:hover {{ transform:translateY(-2px); border-color:rgba(56,189,248,.45);
  box-shadow:0 8px 24px rgba(0,0,0,.35); }}
.kpi-label {{ font-size:12px; color:#94a3b8; margin-bottom:8px; }}
.kpi-value {{ font-size:30px; font-weight:700; line-height:1; }}
.kpi-unit {{ font-size:13px; font-weight:500; color:#94a3b8; margin-left:4px; }}
.kpi-note {{ font-size:11px; color:#64748b; margin-top:8px; line-height:1.5; }}
.chart-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }}
.chart-card {{ background:linear-gradient(165deg,#111c31 0%,#0d1728 100%);
  border:1px solid {BORDER}; border-radius:14px; padding:16px 16px 8px; }}
.chart-head {{ display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom:4px; padding:0 6px; }}
.chart-title {{ font-size:14px; font-weight:600; color:#e2e8f0; }}
.chart-desc {{ font-size:11px; color:#64748b; text-align:right; }}
.chart-body {{ width:100%; }}
footer {{ margin-top:24px; padding-top:16px; border-top:1px solid rgba(148,163,184,.12);
  font-size:12px; color:#64748b; line-height:1.8; }}
footer b {{ color:#94a3b8; }}
@media (max-width:1180px) {{
  .kpi-grid {{ grid-template-columns:repeat(3,1fr); }}
  .chart-grid {{ grid-template-columns:1fr; }}
}}
@media (max-width:640px) {{
  body {{ padding:16px 12px 28px; }}
  .kpi-grid {{ grid-template-columns:repeat(2,1fr); }}
  h1 {{ font-size:20px; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>海外运动健康垂类 <span class="dot">KOL</span> 营销决策看板</h1>
      <div class="sub">基于 Kaggle Social Media Engagement Dataset（5,000 帖，运动/健身/健康垂类 1,191 帖）的互动率多维分析与 $100K 预算分配模拟 · 互动率口径为数据集自带 Engagement_Rate，均值按 99 分位封顶</div>
    </div>
    <div class="badge"><span class="tag">PROJECT</span> sports-fitness-kol-marketing-analysis · 公开数据 · 可复现</div>
  </header>

  <section class="kpi-grid">
    {kpi_html}
  </section>

  <section class="chart-grid">
    {chart_cards}
  </section>

  <footer>
    <b>方法论与边界：</b>① 数据源唯一：Kaggle <i>Social Media Engagement Dataset</i>（aviral342），清洗脚本 <code>scripts/01_clean_and_prepare.py</code>；② 分析链路：Python 清洗 → SQLite 多维查询（9 个业务问题）→ Plotly 可视化，全部代码可复现；③ 曾排除的 <i>Social Media Sponsorship &amp; Engagement</i>（52K 条）因互动指标近乎恒定、疑似合成数据未采用；④ 预算模型为情景测算（佣金 20%、CPM $8、AOV $60、CVR 随互动率缩放），参数可调，非真实收益承诺；⑤ 互动率均值已按 99 分位 winsorize 降低极端值影响；Nano 层级样本量小（n=18），结论需谨慎解读。
  </footer>
</div>

<script>
{PLOTLY_JS}
</script>
<script>
const SPECS = {fig_json};
const CONFIG = {{displaylogo:false, scrollZoom:true,
  modeBarButtonsToRemove:["lasso2d","select2d","autoScale2d"]}};
function mount(id, spec){{
  Plotly.newPlot(id, spec.data, spec.layout, CONFIG);
}}
window.addEventListener("resize", () => {{
  SPECS.forEach((_, i) => {{
    const el = document.getElementById("chart" + (i+1));
    if (el) Plotly.Plots.resize(el);
  }});
}});
["chart1","chart2","chart3","chart4","chart5","chart6","chart7","chart8"]
  .forEach((id, i) => mount(id, SPECS[i]));
</script>
</body>
</html>"""

html_path = DASH_DIR / "sports_fitness_kol_dashboard.html"
html_path.write_text(html, encoding="utf-8")
print(f"[完成] 看板已生成: {html_path} ({html_path.stat().st_size/1024:.0f} KB)")
