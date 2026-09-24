# -*- coding: utf-8 -*-
"""
03_dashboard.py
===============
构建「海外运动健康垂类 KOL 营销决策看板」（Plotly 交互式 HTML）
产出：dashboard/sports_fitness_kol_dashboard.html
数据来源：sql_results/*.csv 与 data/processed/sports_fitness_health.csv
"""

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sql_results"
DASH_DIR = ROOT / "dashboard"
DASH_DIR.mkdir(parents=True, exist_ok=True)

GREEN = "#1f8a4c"
ORANGE = "#d98a2b"
GREY = "#5c7262"
LIGHT = "#f6f9f6"

q1 = pd.read_csv(OUT / "q1_category_overview.csv", encoding="utf-8")
q3 = pd.read_csv(OUT / "q3_sfh_by_platform.csv", encoding="utf-8")
q4 = pd.read_csv(OUT / "q4_sfh_by_tier.csv", encoding="utf-8")
q5 = pd.read_csv(OUT / "q5_sfh_by_content_type.csv", encoding="utf-8")
q8 = pd.read_csv(OUT / "q8_sfh_by_weekday.csv", encoding="utf-8")
model = pd.read_csv(OUT / "scenario_model.csv", encoding="utf-8")
sfh = pd.read_csv(ROOT / "data" / "processed" / "sports_fitness_health.csv", encoding="utf-8")

model["segment"] = model["Platform"] + " × " + model["Influencer_Tier"]

# ---- 1. 类别对比 ----
q1 = q1.sort_values("avg_er_pct", ascending=True)
colors = [GREEN if c in ("Sports", "Fitness", "Health") else "#cfe3d4" for c in q1["Category"]]
fig1 = go.Figure(go.Bar(
    x=q1["avg_er_pct"], y=q1["Category"], orientation="h",
    marker_color=colors, text=q1["avg_er_pct"].round(1), textposition="outside",
    name="平均互动率(%)"))
fig1.update_layout(title="各内容垂类平均互动率（运动/健身/健康高亮）",
                   xaxis_title="平均互动率 %", height=420, margin=dict(l=10, r=10, t=50, b=10))

# ---- 2. 平台对比 ----
q3 = q3.sort_values("avg_er_pct", ascending=True)
fig2 = go.Figure(go.Bar(
    x=q3["avg_er_pct"], y=q3["Platform"], orientation="h",
    marker_color=GREEN, text=q3["avg_er_pct"].round(1), textposition="outside"))
fig2.add_trace(go.Scatter(
    x=q3["avg_er_pct"], y=q3["Platform"], mode="text",
    text=[f"中位播放 {v/1000:.0f}k" for v in q3["median_views"]],
    textposition="middle right", textfont=dict(color=GREY, size=11), showlegend=False))
fig2.update_layout(title="运动健康垂类：各平台平均互动率",
                   xaxis_title="平均互动率 %", height=380, margin=dict(l=10, r=10, t=50, b=10))

# ---- 3. 达人层级 ----
q4 = q4.sort_values("avg_er_pct", ascending=True)
fig3 = go.Figure(go.Bar(
    x=q4["avg_er_pct"], y=q4["Influencer_Tier"], orientation="h",
    marker_color=ORANGE,
    text=[f"{v:.1f}% (n={int(n)})" for v, n in zip(q4["avg_er_pct"], q4["posts"])],
    textposition="outside"))
fig3.update_layout(title="运动健康垂类：各达人层级平均互动率（n=样本帖数）",
                   xaxis_title="平均互动率 %", height=340, margin=dict(l=10, r=10, t=50, b=10))

# ---- 4. 内容形式 Top10 ----
q5t = q5.sort_values("avg_er_pct", ascending=False).head(10)
fig4 = go.Figure(go.Bar(
    x=q5t["avg_er_pct"], y=q5t["Content_Type"], orientation="h",
    marker_color=GREEN, text=q5t["avg_er_pct"].round(1), textposition="outside"))
fig4.update_layout(title="运动健康垂类：内容形式互动率 Top10",
                   xaxis_title="平均互动率 %", height=420, margin=dict(l=10, r=10, t=50, b=10))

# ---- 5. 散点：粉丝量 vs 互动率（按平台着色） ----
fig5 = go.Figure()
for plat, grp in sfh.groupby("Platform"):
    fig5.add_trace(go.Scatter(
        x=grp["Follower_Count"], y=grp["Engagement_Rate_winsorized"],
        mode="markers", name=plat, opacity=0.6,
        marker=dict(size=7)))
fig5.update_layout(title="运动健康垂类：粉丝量 vs 互动率（对数轴，按平台）",
                   xaxis=dict(title="粉丝量", type="log"),
                   yaxis=dict(title="互动率 %", type="log"),
                   height=420, margin=dict(l=10, r=10, t=50, b=10))

# ---- 6. 星期分布 ----
q8 = q8.sort_values("avg_er_pct", ascending=True)
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
q8["Day_of_Week"] = pd.Categorical(q8["Day_of_Week"], categories=order, ordered=True)
q8 = q8.sort_values("Day_of_Week")
fig6 = go.Figure(go.Bar(
    x=q8["Day_of_Week"], y=q8["avg_er_pct"], marker_color=GREEN,
    text=q8["avg_er_pct"].round(1), textposition="outside"))
fig6.update_layout(title="运动健康垂类：星期几发布与平均互动率",
                   yaxis_title="平均互动率 %", height=340, margin=dict(l=10, r=10, t=50, b=10))

# ---- 7. 预算分配 ----
model = model.sort_values("budget_alloc", ascending=True)
fig7 = go.Figure(go.Bar(
    x=model["budget_alloc"], y=model["segment"], orientation="h",
    marker_color=[GREEN if "TikTok" in s else "#cfe3d4" for s in model["segment"]],
    text=model["budget_alloc"].round(0).astype(int), textposition="outside"))
fig7.update_layout(title="$100K 预算分配模拟（效率×供给加权）",
                   xaxis_title="美元", height=520, margin=dict(l=10, r=10, t=50, b=10))

# ---- 组装 ----
fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=("各内容垂类平均互动率", "平台对比（运动健康垂类）",
                    "达人层级对比", "内容形式 Top10",
                    "粉丝量 vs 互动率散点", "星期发布规律",
                    "预算分配模拟", None),
    specs=[[{"type": "xy"}, {"type": "xy"}]] * 4,
    vertical_spacing=0.12, horizontal_spacing=0.08)

for trace in fig1.data: fig.add_trace(trace, row=1, col=1)
for trace in fig2.data: fig.add_trace(trace, row=1, col=2)
for trace in fig3.data: fig.add_trace(trace, row=2, col=1)
for trace in fig4.data: fig.add_trace(trace, row=2, col=2)
for trace in fig5.data: fig.add_trace(trace, row=3, col=1)
for trace in fig6.data: fig.add_trace(trace, row=3, col=2)
for trace in fig7.data: fig.add_trace(trace, row=4, col=1)

fig.update_layout(
    title=dict(text="海外运动健康垂类 KOL 营销决策看板<br><span style='font-size:13px;color:#5c7262'>数据源：Kaggle Social Media Engagement Dataset (5,000 帖 / 运动健康垂类 1,191 帖) · 互动率口径为数据集自带 Engagement_Rate，平均值已按 99 分位封顶</span>",
               x=0.03),
    height=1900, template="plotly_white",
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0.3),
    margin=dict(l=40, r=30, t=120, b=30),
    font=dict(family="Microsoft YaHei, Arial", size=12))

html_path = DASH_DIR / "sports_fitness_kol_dashboard.html"
pio.write_html(fig, html_path, include_plotlyjs="cdn", full_html=True,
               config={"displaylogo": False})
print(f"[完成] 看板已生成: {html_path} ({html_path.stat().st_size/1024:.0f} KB)")
