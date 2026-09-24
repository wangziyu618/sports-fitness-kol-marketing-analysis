# 海外运动健康垂类 KOL 营销效果与预算分配分析

> Sports / Fitness / Health KOL Marketing Performance & Budget Allocation Analysis

一个基于公开数据的全链路营销分析项目：**Python 数据清洗 → SQL 多维分析 → Plotly 交互式决策看板 → 纯佣制 ROI 情景模型 → 策略报告**。面向运动品牌出海场景，回答「KOL 预算应该怎么分配」。

## 项目动机

这是一个**独立的营销数据分析项目**，与任何实习经历无关。围绕「运动健康垂类 KOL 营销效果如何、预算应该怎么分配」这一商业问题，基于公开社媒数据完成从数据清洗到决策建议的全链路分析，目标是：
- 完整呈现「数据处理 → 多维分析 → 可视化 → 情景建模 → 策略建议」的分析闭环；
- 锻炼 Python / SQL / 数据可视化 / 商业策略四项数据分析核心能力；
- 理解运动健康垂类内容生态、平台差异与达人分层运营逻辑。

## 数据源

| 数据 | 说明 |
|---|---|
| [Social Media Engagement Dataset](https://www.kaggle.com/datasets/aviral342/social-media-engagement-dataset)（Kaggle） | **唯一数据源**。5,000 条社媒帖，覆盖 12 个内容垂类、6 个平台（Instagram / TikTok / YouTube / Facebook / Twitter / LinkedIn），含互动率、播放、粉丝量、达人层级、内容形式等字段；其中运动健康垂类（Sports + Fitness + Health）1,191 帖 |

**外部参考基准**（不是数据源，仅用于结论交叉验证）：StarNgage Fitness Creator Engagement Benchmarks（健身垂类创作者互动率基准报告）。

> 数据质量说明：分析前曾评估另一个候选公开数据集，因其互动指标近乎恒定（播放量集中在 9.7k-10.5k、点赞 1.3k-1.7k，疑为合成数据）而排除，最终全部分析仅使用上述一个数据源。

## 目录结构

```
sports-fitness-kol-marketing-analysis/
├── data/
│   ├── raw/                        # 原始数据集（Kaggle 下载）
│   └── processed/                  # 清洗后数据（全量 5,000 + 运动健康子集 1,191）
├── scripts/
│   ├── 01_clean_and_prepare.py     # 数据清洗与特征工程
│   ├── 02_sql_analysis.py          # SQLite 建表 + 9 个业务查询 + 结果导出
│   ├── queries.sql                 # 同一套 SQL 查询脚本（可独立审阅/复现）
│   ├── 03_dashboard.py             # Plotly 交互式决策看板生成
│   └── 04_roi_scenario_model.py    # 纯佣制 ROI 情景模型 + 预算分配模拟
├── dashboard/
│   └── sports_fitness_kol_dashboard.html   # 交互式看板（浏览器打开）
├── sql_results/                    # 9 个 SQL 查询结果 + 情景模型输出（CSV）
├── report/
│   └── strategy_report.md          # 策略报告（核心发现 + 预算建议 + 基准验证）
└── README.md
```

## 运行方式

```bash
pip install pandas numpy plotly

python scripts/01_clean_and_prepare.py   # 清洗：产出 processed/*.csv
python scripts/02_sql_analysis.py        # SQL：产出 sql_results/*.csv + queries.sql
python scripts/03_dashboard.py           # 看板：产出 dashboard/*.html
python scripts/04_roi_scenario_model.py  # 模型：产出 scenario_model.csv
```

> 原始数据需从 Kaggle 下载放入 `data/raw/`（数据集较小，仅约 2 MB）。

## 核心结论（详见 `report/strategy_report.md`）

1. **TikTok 断层领先**：运动健康垂类平均互动率 22.96%，为 Instagram（6.51%）的 3.5 倍；Top10 互动榜全部来自 TikTok。
2. **小体量达人效率更高**：Micro 32.5% > Mid-tier 11.5% > Macro 3.4%；Duet/Stitch/Video 等互动型内容形式显著优于图文。
3. **$100K 预算建议**：51% 押注 TikTok（Macro 放量 + Micro/Mid 测试），28% 给 Instagram（侧重 Micro）；纯佣制下 ROI 比率由佣金率锁定，核心杠杆是达人筛选质量与 GMV 产出效率。
4. 关键结论经 StarNgage 行业基准交叉验证，方向一致。

## 简历可用摘要

> Built a full-pipeline KOL marketing analysis on a 5,000-post public social dataset, filtering 1,191 sports/fitness/health posts; found TikTok's avg engagement rate (22.96%) 3.5x higher than Instagram's in this vertical, and micro-influencers outperform macro by ~10x; delivered a $100K budget-allocation model under a pure-commission ROI framework, cross-validated against industry benchmarks.

## 声明

- 公开数据集不含真实投放成本与销售额，ROI 与预算分配为显式假设下的情景模拟，仅用于相对比较；
- 所有脚本与查询可复现，数字可追溯到代码与原始数据。
