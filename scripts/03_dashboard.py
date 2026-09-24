# -*- coding: utf-8 -*-
"""
03_dashboard.py
===============
构建「海外运动健康垂类 KOL 营销决策看板」v3（Apple/OpenAI 风格）
- 浅色极简设计：白卡片 + 系统色 + 大留白 + 渐变标题
- 修复文字重叠：图表内不设重复标题、中位播放移入 hover、参考线标注放图表留白区、
  预算金额标签预留坐标空间
- 交互：hover 定制、图例、滚轮缩放；完全自包含（内嵌 plotly.js，无 CDN）
产出：dashboard/sports_fitness_kol_dashboard.html
数据来源：sql_results/*.csv 与 data/processed/sports_fitness_health.csv
"""

import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sql_results"
DASH_DIR = ROOT / "dashboard"
DASH_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 浅色 Apple / OpenAI 风格色板 ----------
BG_PAGE       = "#fbfbfd"          # Apple 浅灰白背景
BG_CARD       = "#ffffff"
BORDER        = "#e8e8ed"
BG_PLOT       = "#ffffff"
GRID_LINE     = "#f0f0f2"
TXT_MAIN      = "#1d1d1f"          # Apple 主文字黑
TXT_SUB       = "#6e6e73"
TXT_WEAK      = "#86868b"

C_BLUE   = "#0071e3"               # Apple 蓝
C_GREEN  = "#34c759"               # Apple 绿
C_ORANGE = "#ff9500"               # Apple 橙
C_PURPLE = "#af52de"
C_PINK   = "#ff2d55"
C_TEAL   = "#30b0c7"
C_GREY   = "#8e8e93"
C_DIM    = "#e8e8ed"               # 弱化条形

PLATFORM_COLORS = {
    "TikTok": C_ORANGE, "YouTube": C_PINK, "Instagram": C_PURPLE,
    "Facebook": C_BLUE, "Twitter": C_GREEN, "LinkedIn": C_GREY,
}
TIER_COLORS = {"Nano": C_PINK, "Micro": C_ORANGE, "Mid-tier": C_BLUE, "Macro": C_GREY}

HOVER = dict(bgcolor="#ffffff", bordercolor="#e5e5ea",
             font=dict(color=TXT_MAIN, size=12))
FONT_STACK = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Segoe UI', 'Microsoft YaHei', Arial"

def base_layout(height, xtitle=None, ytitle=None):
    """图表内不设重复标题（标题在 HTML 卡片头部），保持极简。"""
    return dict(
        height=height, margin=dict(l=8, r=24, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=BG_PLOT,
        font=dict(family=FONT_STACK, size=12, color=TXT_MAIN),
        hoverlabel=HOVER,
        xaxis=dict(showgrid=True, gridcolor=GRID_LINE, zeroline=False,
                   tickfont=dict(color=TXT_SUB), title=dict(text=xtitle, font=dict(color=TXT_WEAK, size=11)),
                   ticksuffix=" "),
        yaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(color=TXT_SUB), title=dict(text=ytitle, font=dict(color=TXT_WEAK, size=11))),
    )

def bar_labels_font():
    return dict(color=TXT_WEAK, size=11)

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

budget_by_platform = model.groupby("Platform")["budget_alloc"].sum().sort_values(ascending=False)
tiktok_share = budget_by_platform["TikTok"] / budget_by_platform.sum() * 100

# ---------- 图1：各内容垂类平均互动率 ----------
q1s = q1.sort_values("avg_er_pct", ascending=True)
colors1 = [C_BLUE if c in ("Sports", "Fitness", "Health") else C_DIM for c in q1s["Category"]]
fig1 = go.Figure(go.Bar(
    x=q1s["avg_er_pct"], y=q1s["Category"], orientation="h",
    marker_color=colors1, marker_cornerradius=6,
    text=q1s["avg_er_pct"].round(1), textposition="outside", textfont=bar_labels_font(),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q1s["posts"]))
fig1.add_vline(x=full_mean, line_dash="dash", line_color=C_ORANGE, line_width=1.5)
fig1.add_annotation(x=full_mean, yref="paper", y=1.02, yanchor="bottom", showarrow=False,
                    text=f"全量均值 {full_mean:.2f}%", font=dict(color=C_ORANGE, size=11))
fig1.update_layout(**base_layout(420, xtitle="平均互动率 %"))

# ---------- 图2：平台对比 ----------
q3s = q3.sort_values("avg_er_pct", ascending=True)
colors2 = [C_ORANGE if p == "TikTok" else C_BLUE for p in q3s["Platform"]]
fig2 = go.Figure(go.Bar(
    x=q3s["avg_er_pct"], y=q3s["Platform"], orientation="h",
    marker_color=colors2, marker_cornerradius=6,
    text=q3s["avg_er_pct"].round(1), textposition="outside", textfont=bar_labels_font(),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 中位播放 %{customdata[0]:,}<br>样本 %{customdata[1]} 帖<extra></extra>",
    customdata=q3s[["median_views", "posts"]]))
fig2.update_layout(**base_layout(380, xtitle="平均互动率 %"))

# ---------- 图3：达人层级 ----------
q4s = q4.sort_values("avg_er_pct", ascending=True)
colors3 = [TIER_COLORS[t] for t in q4s["Influencer_Tier"]]
fig3 = go.Figure(go.Bar(
    x=q4s["avg_er_pct"], y=q4s["Influencer_Tier"], orientation="h",
    marker_color=colors3, marker_cornerradius=6,
    text=[f"{v:.1f}% · n={int(n)}" for v, n in zip(q4s["avg_er_pct"], q4s["posts"])],
    textposition="outside", textfont=bar_labels_font(),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q4s["posts"]))
fig3.update_layout(**base_layout(340, xtitle="平均互动率 %"))

# ---------- 图4：内容形式 Top10 ----------
q5t = q5.sort_values("avg_er_pct", ascending=False).head(10)
colors4 = [C_ORANGE] + [C_BLUE] * 9
fig4 = go.Figure(go.Bar(
    x=q5t["avg_er_pct"], y=q5t["Content_Type"], orientation="h",
    marker_color=colors4, marker_cornerradius=6,
    text=q5t["avg_er_pct"].round(1), textposition="outside", textfont=bar_labels_font(),
    hovertemplate="%{y}<br>平均互动率 %{x:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q5t["posts"]))
fig4.update_layout(**base_layout(420, xtitle="平均互动率 %"))

# ---------- 图5：平台 × 达人层级热力图 ----------
q6p = q6.pivot_table(index="Influencer_Tier", columns="Platform", values="avg_er_pct", aggfunc="mean")
tier_order = ["Micro", "Mid-tier", "Macro"]
plat_order = ["TikTok", "Instagram", "Facebook", "Twitter", "YouTube", "LinkedIn"]
q6p = q6p.reindex(index=[t for t in tier_order if t in q6p.index], columns=[p for p in plat_order if p in q6p.columns])
z = q6p.values.astype(float)
z_text = [["–" if pd.isna(v) else f"{v:.1f}" for v in row] for row in z]
fig5 = go.Figure(go.Heatmap(
    z=z, x=list(q6p.columns), y=list(q6p.index),
    text=z_text, texttemplate="%{text}", textfont=dict(color="#ffffff", size=12),
    colorscale=[[0.0, "#e8f1fd"], [0.35, "#a8c8f0"], [0.65, "#2f6fd6"], [1.0, "#0b3b8c"]],
    colorbar=dict(title=dict(text="互动率 %", font=dict(color=TXT_WEAK, size=11)),
                  thickness=12, tickfont=dict(color=TXT_SUB)),
    hovertemplate="%{y} × %{x}<br>平均互动率 %{z:.1f}%<extra></extra>",
    xgap=4, ygap=4))
fig5.update_layout(**base_layout(400))

# ---------- 图6：粉丝量 vs 互动率散点 ----------
fig6 = go.Figure()
for plat, grp in sfh.groupby("Platform"):
    fig6.add_trace(go.Scatter(
        x=grp["Follower_Count"], y=grp["Engagement_Rate_winsorized"],
        mode="markers", name=plat, opacity=0.7,
        marker=dict(size=6.5, color=PLATFORM_COLORS.get(plat, C_GREY),
                    line=dict(width=0.5, color="#ffffff")),
        hovertemplate=f"{plat}<br>粉丝 %{{x:,}}<br>互动率 %{{y:.1f}}%<extra></extra>"))
fig6.update_layout(**base_layout(400, xtitle="粉丝量（对数）", ytitle="互动率 %（对数）"))
fig6.update_xaxes(type="log"); fig6.update_yaxes(type="log")
fig6.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                               font=dict(color=TXT_SUB, size=11)))

# ---------- 图7：星期发布规律 ----------
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
q8s = q8.set_index("Day_of_Week").reindex(order).reset_index()
fig7 = go.Figure(go.Bar(
    x=q8s["Day_of_Week"], y=q8s["avg_er_pct"], marker_color=C_BLUE, marker_cornerradius=6,
    text=q8s["avg_er_pct"].round(1), textposition="outside", textfont=bar_labels_font(),
    hovertemplate="%{x}<br>平均互动率 %{y:.1f}% · 样本 %{customdata} 帖<extra></extra>",
    customdata=q8s["posts"]))
fig7.add_hline(y=sfh_mean, line_dash="dash", line_color=C_ORANGE, line_width=1.5)
fig7.update_layout(**base_layout(340, ytitle="平均互动率 %"))

# ---------- 图8：预算分配（平台堆叠） ----------
model_t = model[model["budget_alloc"] > 0].copy()
fig8 = go.Figure()
for tier, color in {"Micro": C_BLUE, "Mid-tier": C_PURPLE, "Macro": C_GREY}.items():
    d = model_t[model_t["Influencer_Tier"] == tier]
    d = d.set_index("Platform").reindex(budget_by_platform.index).fillna(0).reset_index()
    fig8.add_trace(go.Bar(
        x=d["Platform"], y=d["budget_alloc"], name=tier,
        marker_color=color, marker_cornerradius=4,
        hovertemplate="%{x} × " + tier + "<br>预算 $%{y:,.0f}<extra></extra>"))
fig8.add_trace(go.Scatter(
    x=budget_by_platform.index, y=budget_by_platform.values, mode="text",
    text=[f"${v/1000:.1f}K" for v in budget_by_platform.values],
    textposition="top center", textfont=dict(color=TXT_MAIN, size=11, weight=600), showlegend=False))
fig8.update_layout(**base_layout(400, ytitle="预算（美元）"))
fig8.update_layout(barmode="stack",
                   yaxis=dict(range=[0, budget_by_platform.max() * 1.18], showgrid=True,
                              gridcolor=GRID_LINE, zeroline=False,
                              tickfont=dict(color=TXT_SUB),
                              title=dict(text="预算（美元）", font=dict(color=TXT_WEAK, size=11))),
                   legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                               font=dict(color=TXT_SUB, size=11)))

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
     "note": "n=102 帖，远超 Macro 3.44%", "accent": C_PURPLE},
    {"label": "预算建议：TikTok 组合", "value": f"{tiktok_share:.1f}", "unit": "%",
     "note": f"$100K 预算中分配 ${budget_by_platform['TikTok']/1000:.1f}K", "accent": C_ORANGE},
]

# ---------- 组装 HTML ----------
PLOTLY_JS = (Path(plotly.__file__).parent / "package_data" / "plotly.min.js").read_text(encoding="utf-8")

figs = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]
specs = [
    {"id": "chart1", "title": "各内容垂类平均互动率",
     "desc": "运动 / 健身 / 健康高亮 · 虚线为全量均值 8.79%"},
    {"id": "chart2", "title": "平台平均互动率对比",
     "desc": "TikTok 22.96% 断层第一 · 悬停查看中位播放"},
    {"id": "chart3", "title": "达人层级互动率",
     "desc": "层级越低互动率越高 · Nano n=18 样本偏小"},
    {"id": "chart4", "title": "内容形式互动率 Top10",
     "desc": "Duet / Stitch 交互型内容领先"},
    {"id": "chart5", "title": "平台 × 达人层级互动率矩阵",
     "desc": "TikTok × Micro 81.8% 为最强组合"},
    {"id": "chart6", "title": "粉丝量 vs 互动率",
     "desc": "对数轴 · 小账号互动效率显著更高"},
    {"id": "chart7", "title": "星期发布与互动率",
     "desc": "周末发布表现更好 · 虚线为垂类均值 8.16%"},
    {"id": "chart8", "title": "$100K 预算分配模拟",
     "desc": "按 效率 × 供给 加权 · TikTok 组合获 51%"},
]

kpi_html = "".join(
    f'''<div class="kpi-card">
      <div class="kpi-label">{k["label"]}</div>
      <div class="kpi-value" style="color:{k.get('accent', TXT_MAIN)}">{k["value"]}<span class="kpi-unit">{k["unit"]}</span></div>
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
  font-family:{FONT_STACK};
  background:{BG_PAGE};
  color:{TXT_MAIN};
  min-height:100vh;
  padding:64px 40px 72px;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:1440px; margin:0 auto; }}
header {{ max-width:1000px; margin:0 auto 56px; text-align:center; }}
.eyebrow {{ font-size:13px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{C_BLUE}; margin-bottom:14px; }}
h1 {{ font-size:52px; font-weight:700; letter-spacing:-.5px; line-height:1.08; margin-bottom:16px;
  background:linear-gradient(92deg,{C_BLUE} 0%,{C_PURPLE} 60%,{C_PINK} 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
.sub {{ font-size:17px; color:{TXT_SUB}; line-height:1.7; max-width:780px; margin:0 auto 26px; }}
.badge {{ display:inline-flex; align-items:center; gap:8px; font-size:12.5px; color:{TXT_SUB};
  background:#f2f2f7; border:1px solid #e5e5ea; padding:7px 16px; border-radius:999px; }}
.badge .tag {{ color:{C_BLUE}; font-weight:600; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:36px; }}
.kpi-card {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:18px; padding:24px 24px 20px;
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease; }}
.kpi-card:hover {{ transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,.07); border-color:#d9d9de; }}
.kpi-label {{ font-size:13px; font-weight:500; color:{TXT_WEAK}; margin-bottom:12px; }}
.kpi-value {{ font-size:38px; font-weight:700; letter-spacing:-.5px; line-height:1; }}
.kpi-unit {{ font-size:14px; font-weight:500; color:{TXT_WEAK}; margin-left:5px; }}
.kpi-note {{ font-size:12px; color:{TXT_SUB}; margin-top:12px; line-height:1.5; }}
.chart-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:20px; }}
.chart-card {{ background:{BG_CARD}; border:1px solid {BORDER}; border-radius:18px; padding:22px 22px 12px;
  transition:transform .18s ease, box-shadow .18s ease; }}
.chart-card:hover {{ transform:translateY(-2px); box-shadow:0 10px 30px rgba(0,0,0,.05); }}
.chart-head {{ display:flex; align-items:baseline; justify-content:space-between; gap:16px;
  padding:0 6px 4px; border-bottom:1px solid #f2f2f7; margin-bottom:10px; }}
.chart-title {{ font-size:16px; font-weight:600; color:{TXT_MAIN}; }}
.chart-desc {{ font-size:12px; color:{TXT_WEAK}; text-align:right; }}
.chart-body {{ width:100%; }}
footer {{ max-width:1000px; margin:56px auto 0; padding-top:24px; border-top:1px solid {BORDER};
  font-size:12.5px; color:{TXT_WEAK}; line-height:1.9; text-align:center; }}
footer b {{ color:{TXT_SUB}; }}
@media (max-width:1180px) {{
  body {{ padding:48px 24px 56px; }}
  h1 {{ font-size:42px; }}
  .chart-grid {{ grid-template-columns:1fr; }}
}}
@media (max-width:760px) {{
  body {{ padding:36px 16px 48px; }}
  h1 {{ font-size:32px; }}
  .kpi-grid {{ grid-template-columns:1fr; }}
  .chart-desc {{ display:none; }}
  .kpi-value {{ font-size:32px; }}
}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="eyebrow">Portfolio Project</div>
    <h1>海外运动健康垂类 KOL 营销决策看板</h1>
    <div class="sub">基于 Kaggle Social Media Engagement Dataset（5,000 帖，运动 / 健身 / 健康垂类 1,191 帖）的互动率多维分析与 $100K 预算分配模拟 · 互动率口径为数据集自带 Engagement_Rate，均值按 99 分位封顶</div>
    <div class="badge"><span class="tag">PROJECT</span> sports-fitness-kol-marketing-analysis · 公开数据 · 可复现</div>
  </header>

  <section class="kpi-grid">
    {kpi_html}
  </section>

  <section class="chart-grid">
    {chart_cards}
  </section>

  <footer>
    <b>方法论与边界</b><br>
    ① 数据源唯一：Kaggle <i>Social Media Engagement Dataset</i>（aviral342），清洗脚本 <code>scripts/01_clean_and_prepare.py</code>；② 分析链路：Python 清洗 → SQLite 多维查询（9 个业务问题）→ Plotly 可视化，全部代码可复现；③ 曾排除的 <i>Social Media Sponsorship &amp; Engagement</i>（52K 条）因互动指标近乎恒定、疑似合成数据未采用；④ 预算模型为情景测算（佣金 20%、CPM $8、AOV $60、CVR 随互动率缩放），参数可调，非真实收益承诺；⑤ 互动率均值已按 99 分位 winsorize 降低极端值影响；Nano 层级样本量小（n=18），结论需谨慎解读。
  </footer>
</div>

<script>
{PLOTLY_JS}
</script>
<script>
const SPECS = {fig_json};
const CONFIG = {{displaylogo:false, scrollZoom:true,
  modeBarButtonsToRemove:["lasso2d","select2d","autoScale2d"]}};
["chart1","chart2","chart3","chart4","chart5","chart6","chart7","chart8"]
  .forEach((id, i) => Plotly.newPlot(id, SPECS[i].data, SPECS[i].layout, CONFIG));
window.addEventListener("resize", () => {{
  ["chart1","chart2","chart3","chart4","chart5","chart6","chart7","chart8"]
    .forEach(id => {{ const el = document.getElementById(id); if (el) Plotly.Plots.resize(el); }});
}});
</script>
</body>
</html>"""

html_path = DASH_DIR / "sports_fitness_kol_dashboard.html"
html_path.write_text(html, encoding="utf-8")
print(f"[完成] 看板已生成: {html_path} ({html_path.stat().st_size/1024:.0f} KB)")
