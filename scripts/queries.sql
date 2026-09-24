-- q1_category_overview
SELECT Category,
               COUNT(*)                              AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views,
               CAST(ROUND(MEDIAN(total_engagement)) AS INT) AS median_engagement
        FROM posts
        GROUP BY Category
        ORDER BY avg_er_pct DESC;

-- q2_sfh_vs_others
SELECT CASE WHEN is_sports_fitness_health = 1 THEN 'Sports/Fitness/Health'
                    ELSE 'Others' END                  AS segment,
               COUNT(*)                                AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               ROUND(AVG(engagement_per_1k_views),2)     AS avg_eng_per_1k_views
        FROM posts
        GROUP BY segment;

-- q3_sfh_by_platform
SELECT Platform,
               COUNT(*)                              AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views,
               ROUND(AVG(engagement_per_1k_views),2)     AS avg_eng_per_1k_views
        FROM sfh
        GROUP BY Platform
        ORDER BY avg_er_pct DESC;

-- q4_sfh_by_tier
SELECT Influencer_Tier,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct,
               CAST(ROUND(MEDIAN(Follower_Count)) AS INT) AS median_followers
        FROM sfh
        GROUP BY Influencer_Tier
        ORDER BY avg_er_pct DESC;

-- q5_sfh_by_content_type
SELECT Content_Type,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               ROUND(MEDIAN(Engagement_Rate),2)          AS median_er_pct
        FROM sfh
        GROUP BY Content_Type
        HAVING COUNT(*) >= 20
        ORDER BY avg_er_pct DESC;

-- q6_sfh_platform_tier
SELECT Platform, Influencer_Tier,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views
        FROM sfh
        GROUP BY Platform, Influencer_Tier
        HAVING COUNT(*) >= 10
        ORDER BY avg_er_pct DESC;

-- q7_sfh_top_influencers
WITH ranked AS (
            SELECT Platform, Influencer_Tier, Category, total_engagement,
                   RANK() OVER (ORDER BY total_engagement DESC)          AS rnk_engagement,
                   RANK() OVER (PARTITION BY Platform ORDER BY total_engagement DESC) AS rnk_by_platform
            FROM sfh
        )
        SELECT rnk_engagement, Platform, Influencer_Tier, Category, total_engagement
        FROM ranked
        WHERE rnk_engagement <= 10
        ORDER BY rnk_engagement;

-- q8_sfh_by_weekday
SELECT Day_of_Week,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct,
               CAST(ROUND(MEDIAN(Views)) AS INT)         AS median_views
        FROM sfh
        GROUP BY Day_of_Week
        ORDER BY avg_er_pct DESC;

-- q9_sfh_by_sentiment
SELECT Sentiment,
               COUNT(*)                                 AS posts,
               ROUND(AVG(Engagement_Rate_winsorized),2)  AS avg_er_pct
        FROM sfh
        GROUP BY Sentiment
        ORDER BY avg_er_pct DESC;
