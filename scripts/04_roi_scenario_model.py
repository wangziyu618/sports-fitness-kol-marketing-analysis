# -*- coding: utf-8 -*-
"""
04_roi_scenario_model.py
========================
佣金制 ROI 情景模型与预算分配模拟

背景：公开数据不含真实投放成本与销售额，因此本脚本构建「透明假设 + 情景模拟」模型，
所有假设参数集中可调，输出结果只用于相对比较（segment 之间的效率排序），
不声称绝对预测。核心逻辑：
  - 佣金制下 ROI = GMV / 佣金，佣金率固定时 ROI 恒为 1/佣金率，
    因此真正的决策变量是「每千元投入能带来的 GMV」与「每帖 GMV 潜力」。
  - 基于 SQL 结果中的分平台×层级中位播放量，按统一假设估算 GMV 与成本，
    给出预算分配权重。

假设参数（可调整）：
  CPM          每千次播放的内容分发成本（美元）
  CVR          播放→购买转化率（简化假设：播放直接转化）
  AOV          平均客单价（美元）
  COMMISSION   纯佣佣金率
  BUDGET       模拟总预算（美元）
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "sql_results"

# 假设参数
CPM = 8.0        # 每千次播放成本 $8
CVR = 0.015      # 1.5% 播放→购买
AOV = 60.0       # 平均客单价 $60
COMMISSION = 0.20  # 纯佣 20%
BUDGET = 100_000.0

# 读取 SQL 交叉结果（平台×层级，n>=10）
df = pd.read_csv(OUT / "q6_sfh_platform_tier.csv", encoding="utf-8")
df = df.rename(columns={
    "posts": "n_posts",
    "avg_er_pct": "avg_er",
    "median_views": "median_views",
})

# 模型计算（全部基于中位播放量）
# 关键改进：线性假设下「每千美元 GMV」在细分间恒定（播放量互相抵消），
# 因此让 CVR 随互动率缩放——高互动内容转化率更高，这是营销中的合理假设（明确标注为假设）。
ref_er = df["avg_er"].mean()
df["cvr_scaled"] = CVR * (df["avg_er"] / ref_er)
df["est_gmv_per_post"] = df["median_views"] * df["cvr_scaled"] * AOV          # 单帖 GMV 潜力
df["est_cost_per_post"] = df["median_views"] / 1000 * CPM                      # 单帖成本
df["est_gmv_per_1k_usd"] = df["est_gmv_per_post"] / df["est_cost_per_post"] * 1000  # 每千美元 GMV
df["roi_commission"] = 1 / COMMISSION                                      # 佣金制 ROI 恒值（公式层面）
df["comm_per_post"] = df["est_gmv_per_post"] * COMMISSION                      # 单帖佣金支出

# 预算分配权重：以「每千美元 GMV」× 样本量 作为权重（兼顾效率与可执行规模）
df["weight"] = df["est_gmv_per_1k_usd"] * df["n_posts"]
df["budget_alloc"] = BUDGET * df["weight"] / df["weight"].sum()

df = df.sort_values("est_gmv_per_1k_usd", ascending=False).reset_index(drop=True)

print("===== 佣金制情景模型：分平台×层级（假设 CPM=$8, CVR随互动率缩放, AOV=$60, 佣金20%） =====")
print(df.round(2).to_string(index=False))

# 敏感性：CVR 与 AOV 变化对「每千美元 GMV」的影响（以效率最优段为例）
ref = df.sort_values("est_gmv_per_1k_usd", ascending=False).iloc[0]
print(f"\n===== 敏感性分析：{ref['Platform']}×{ref['Influencer_Tier']} 每千美元 GMV =====")
sens = []
for cvr in [0.005, 0.01, 0.015, 0.02, 0.03]:
    for aov in [40, 60, 80]:
        gmv = ref["median_views"] * cvr * aov
        cost = ref["median_views"] / 1000 * CPM
        sens.append({"CVR": cvr, "AOV": aov, "est_gmv_per_1k_usd": round(gmv / cost * 1000, 1)})
sens_df = pd.DataFrame(sens).pivot(index="AOV", columns="CVR", values="est_gmv_per_1k_usd")
print(sens_df.round(0).to_string())

# 保存
df.to_csv(OUT / "scenario_model.csv", index=False, encoding="utf-8")
sens_df.to_csv(OUT / "scenario_sensitivity.csv", encoding="utf-8")
print("\n[完成] scenario_model.csv 与 scenario_sensitivity.csv 已导出至 sql_results/")
