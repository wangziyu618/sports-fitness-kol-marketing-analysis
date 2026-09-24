# -*- coding: utf-8 -*-
"""
02_sql_analysis.py
==================
SQL 多维分析与达人分层
- 将清洗后的数据导入 SQLite，运行 9 个业务查询（平台×类别×达人层级×内容形式等维度），
  结果导出到 sql_results/ 目录。
- 同时生成 queries.sql 作为可复现的查询脚本（与 Python 中执行的内容一致）。
"""

import sqlite3
import statistics
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "sports_kol.db"
OUT = ROOT / "sql_results"
OUT.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# SQLite 内置无 MEDIAN，注册自定义聚合函数
class MedianAgg:
    def __init__(self):
        self.vals = []
    def step(self, value):
        if value is not None:
            self.vals.append(float(value))
    def finalize(self):
        if not self.vals:
            return None
        return statistics.median(self.vals)

conn.create_aggregate("MEDIAN", 1, MedianAgg)

# 建表
cur.execute("DROP TABLE IF EXISTS posts")
cur.execute("""
CREATE TABLE posts (
    Post_ID TEXT,
    Timestamp TEXT,
    Platform TEXT,
    Content_Type TEXT,
    Category TEXT,
    Likes INTEGER,
    Comments INTEGER,
    Shares INTEGER,
    Saves INTEGER,
    Views INTEGER,
    Follower_Count INTEGER,
    Engagement_Rate REAL,
    Hour_of_Day INTEGER,
    Day_of_Week TEXT,
    Hashtag_Count INTEGER,
    Content_Length INTEGER,
    Sentiment TEXT,
    Influencer_Tier TEXT,
    Has_Media BOOLEAN,
    Is_Verified BOOLEAN,
    month INTEGER,
    year INTEGER,
    total_engagement INTEGER,
    engagement_per_1k_views REAL,
    engagement_per_1k_followers REAL,
    is_sports_fitness_health BOOLEAN
)
""")
cur.execute("DROP TABLE IF EXISTS sfh")
cur.execute("CREATE TABLE sfh AS SELECT * FROM posts WHERE is_sports_fitness_health = 1")

full = pd.read_csv(ROOT / "data" / "processed" / "full_dataset.csv", encoding="utf-8")
full.to_sql("posts", conn, if_exists="replace", index=False)
cur.execute("DELETE FROM sfh")
sfh = pd.read_csv(ROOT / "data" / "processed" / "sports_fitness_health.csv", encoding="utf-8")
sfh.to_sql("sfh", conn, if_exists="replace", index=False)
conn.commit()
print(f"[建表] posts={pd.read_sql('SELECT COUNT(*) c FROM posts', conn)['c'][0]} 行, "
      f"sfh={pd.read_sql('SELECT COUNT(*) c FROM sfh', conn)['c'][0]} 行")

QUERIES = {
    # Q1 全量：各垂类互动效率对比
    "q1_category_overview": """
        SELECT Category,
               COUNT(*)                              AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views,
               CAST(ROUND(MEDIAN(total_engagement)) AS INT) AS median_engagement
        FROM posts
        GROUP BY Category
        ORDER BY avg_er_pct DESC
    """,
    # Q2 运动健康垂类 vs 其他垂类
    "q2_sfh_vs_others": """
        SELECT CASE WHEN is_sports_fitness_health = 1 THEN 'Sports/Fitness/Health'
                    ELSE 'Others' END                  AS segment,
               COUNT(*)                                AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               ROUND(AVG(engagement_per_1k_views),2)     AS avg_eng_per_1k_views
        FROM posts
        GROUP BY segment
    """,
    # Q3 运动健康垂类：按平台
    "q3_sfh_by_platform": """
        SELECT Platform,
               COUNT(*)                              AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views,
               ROUND(AVG(engagement_per_1k_views),2)     AS avg_eng_per_1k_views
        FROM sfh
        GROUP BY Platform
        ORDER BY avg_er_pct DESC
    """,
    # Q4 运动健康垂类：按达人层级
    "q4_sfh_by_tier": """
        SELECT Influencer_Tier,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Follower_Count)) AS INT) AS median_followers
        FROM sfh
        GROUP BY Influencer_Tier
        ORDER BY avg_er_pct DESC
    """,
    # Q5 运动健康垂类：按内容形式
    "q5_sfh_by_content_type": """
        SELECT Content_Type,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct
        FROM sfh
        GROUP BY Content_Type
        HAVING COUNT(*) >= 20
        ORDER BY avg_er_pct DESC
    """,
    # Q6 运动健康垂类：平台 × 层级交叉
    "q6_sfh_platform_tier": """
        SELECT Platform, Influencer_Tier,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views
        FROM sfh
        GROUP BY Platform, Influencer_Tier
        HAVING COUNT(*) >= 10
        ORDER BY avg_er_pct DESC
    """,
    # Q7 窗口函数：运动健康垂类内按总互动量排名
    "q7_sfh_top_influencers": """
        WITH ranked AS (
            SELECT Platform, Influencer_Tier, Category, total_engagement,
                   RANK() OVER (ORDER BY total_engagement DESC)          AS rnk_engagement,
                   RANK() OVER (PARTITION BY Platform ORDER BY total_engagement DESC) AS rnk_by_platform
            FROM sfh
        )
        SELECT rnk_engagement, Platform, Influencer_Tier, Category, total_engagement
        FROM ranked
        WHERE rnk_engagement <= 10
        ORDER BY rnk_engagement
    """,
    # Q8 运动健康垂类：发布时间（星期几）规律
    "q8_sfh_by_weekday": """
        SELECT Day_of_Week,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views
        FROM sfh
        GROUP BY Day_of_Week
        ORDER BY avg_er_pct DESC
    """,
    # Q9 运动健康垂类：情感倾向 × 互动
    "q9_sfh_by_sentiment": """
        SELECT Sentiment,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct
        FROM sfh
        GROUP BY Sentiment
        ORDER BY avg_er_pct DESC
    """,
}

# 导出 queries.sql（同一套查询，供审阅与复现）
sql_lines = []
for name, sql in QUERIES.items():
    sql_lines.append(f"-- {name}\n{sql.strip()};\n")
(ROOT / "scripts" / "queries.sql").write_text("\n".join(sql_lines), encoding="utf-8")

for name, sql in QUERIES.items():
    try:
        res = pd.read_sql(sql, conn)
        res.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
        print(f"\n===== {name} ({len(res)} 行) =====")
        print(res.to_string(index=False, max_rows=20))
    except Exception as e:
        print(f"\n[错误] {name}: {e}")

conn.close()
print("\n[完成] 所有查询结果已导出至 sql_results/")
