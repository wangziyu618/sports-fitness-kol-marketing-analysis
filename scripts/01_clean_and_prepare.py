# -*- coding: utf-8 -*-
"""
01_clean_and_prepare.py
=======================
数据清洗与特征工程
- 数据源：Kaggle "Social Media Engagement Dataset" (aviral342)
  URL: https://www.kaggle.com/datasets/aviral342/social-media-engagement-dataset
- 产出：
  1) data/processed/full_dataset.csv            清洗后的全量数据（5000 条）
  2) data/processed/sports_fitness_health.csv   运动/健身/健康垂类子集（1191 条）
- 说明：
  原规划中的主数据集 "Social Media Sponsorship & Engagement Dataset" (omenkj)
  经质量评估后排除——其互动指标近乎恒定（views≈1.0万±4%、likes≈1500±5%），
  疑为合成数据，无法支撑有意义的统计分析。本脚本仅基于指标分布真实的
  Social Media Engagement Dataset 构建分析。
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "engagement" / "social_media_engagement_dataset.csv"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPORTS_CATS = ["Sports", "Fitness", "Health"]

# 1. 读取
df = pd.read_csv(RAW, encoding="utf-8")
print(f"[1] 原始行数: {len(df)}")

# 2. 类型与日期
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df["month"] = df["Timestamp"].dt.month
df["year"] = df["Timestamp"].dt.year
print(f"[2] 日期范围: {df['Timestamp'].min()} -> {df['Timestamp'].max()}，无效日期 {df['Timestamp'].isna().sum()} 行")

# 3. 派生指标
df["total_engagement"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
# 每千次播放互动量（消除播放量差异后的效率指标）
df["engagement_per_1k_views"] = df["total_engagement"] / df["Views"] * 1000
# 每千粉丝互动量
df["engagement_per_1k_followers"] = df["total_engagement"] / df["Follower_Count"] * 1000

# 4. 异常值处理（winsorize 到 99 分位，保留原列并新增 _winsorized 列）
for col in ["Engagement_Rate", "Views", "Likes", "total_engagement"]:
    hi = df[col].quantile(0.99)
    df[f"{col}_winsorized"] = df[col].clip(upper=hi)
    print(f"[4] {col} 99分位={hi:.2f}，封顶后最大={df[f'{col}_winsorized'].max():.2f}")

# 5. 垂类标记
df["is_sports_fitness_health"] = df["Category"].isin(SPORTS_CATS)
print(f"[5] 运动/健身/健康垂类行数: {df['is_sports_fitness_health'].sum()}")

# 6. 达人层级规范化（统一英文小写便于 SQL 处理）
df["influencer_tier_norm"] = df["Influencer_Tier"].str.strip().str.lower()

# 7. 写出
df.to_csv(OUT_DIR / "full_dataset.csv", index=False, encoding="utf-8")
subset = df[df["is_sports_fitness_health"]].copy()
subset.to_csv(OUT_DIR / "sports_fitness_health.csv", index=False, encoding="utf-8")
print(f"[7] 已写出 full_dataset.csv（{len(df)} 行）与 sports_fitness_health.csv（{len(subset)} 行）")

# 8. 输出关键摘要
print("\n===== 全量数据摘要 =====")
print(f"平台分布:\n{df['Platform'].value_counts()}")
print(f"\n类别分布:\n{df['Category'].value_counts()}")
print(f"\n达人层级分布:\n{df['Influencer_Tier'].value_counts()}")
print(f"\n互动率(Engagement_Rate) 描述:\n{df['Engagement_Rate'].describe()}")
print("\n===== 运动健康垂类摘要 =====")
print(subset.groupby("Category").agg(
    帖子数=("Post_ID", "count"),
    中位播放=("Views", "median"),
    中位互动率=("Engagement_Rate", "median"),
    平均互动率=("Engagement_Rate", "mean"),
).round(2))
