-- ============================================================
--  Superstore Sales Analysis — SQL Queries
--  Author : YOUR NAME | Data Analyst
--  DB     : SQLite / PostgreSQL compatible
--  Dataset: superstore_sales.csv (1,200 rows, 2020-2023)
-- ============================================================


-- ════════════════════════════════════════════════════════════
--  QUERY 1 — Category Performance
--  Business Question: Which product category drives the most
--  revenue and profit? What is the profit margin per category?
-- ════════════════════════════════════════════════════════════

SELECT
    Category,
    ROUND(SUM(Sales), 0)                                     AS Total_Sales,
    ROUND(SUM(Profit), 0)                                    AS Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 1)              AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 1)                            AS Avg_Discount_Pct,
    COUNT(*)                                                  AS Total_Orders,
    ROUND(
        100.0 * SUM(CASE WHEN Profit > 0 THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                         AS Profitable_Orders_Pct
FROM sales
GROUP BY Category
ORDER BY Total_Sales DESC;

-- Expected insight: Technology leads revenue, but check if
-- Office Supplies has a higher profit margin per order.


-- ════════════════════════════════════════════════════════════
--  QUERY 2 — Year-over-Year Revenue Trend
--  Business Question: Is the business growing year on year?
--  When did revenue peak and why might it have declined?
-- ════════════════════════════════════════════════════════════

SELECT
    Year,
    ROUND(SUM(Sales), 0)                                     AS Annual_Sales,
    ROUND(SUM(Profit), 0)                                    AS Annual_Profit,
    COUNT(*)                                                  AS Total_Orders,
    ROUND(AVG(Discount) * 100, 1)                            AS Avg_Discount_Pct,
    ROUND(
        100.0 * (SUM(Sales) - LAG(SUM(Sales)) OVER (ORDER BY Year))
        / LAG(SUM(Sales)) OVER (ORDER BY Year), 1
    )                                                         AS YoY_Growth_Pct
FROM sales
GROUP BY Year
ORDER BY Year;

-- Note: LAG() is a Window Function — shows previous year's value
-- This is an advanced SQL concept that interviewers love to test.


-- ════════════════════════════════════════════════════════════
--  QUERY 3 — Regional Sales & Profit Breakdown
--  Business Question: Which regions are most profitable?
--  Are any regions consistently underperforming?
-- ════════════════════════════════════════════════════════════

SELECT
    Region,
    ROUND(SUM(Sales), 0)                                     AS Total_Sales,
    ROUND(SUM(Profit), 0)                                    AS Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 1)              AS Profit_Margin_Pct,
    COUNT(DISTINCT City)                                      AS Cities_Covered,
    COUNT(*)                                                  AS Total_Orders,
    ROUND(SUM(Sales) / COUNT(*), 0)                          AS Avg_Order_Value
FROM sales
GROUP BY Region
ORDER BY Total_Sales DESC;


-- ════════════════════════════════════════════════════════════
--  QUERY 4 — Customer Segment Analysis
--  Business Question: Which customer segment should we
--  prioritise for retention and upsell?
-- ════════════════════════════════════════════════════════════

SELECT
    Segment,
    ROUND(SUM(Sales), 0)                                     AS Total_Sales,
    ROUND(SUM(Profit), 0)                                    AS Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 1)              AS Profit_Margin_Pct,
    COUNT(*)                                                  AS Orders,
    ROUND(AVG(Sales), 0)                                     AS Avg_Order_Value,
    ROUND(AVG(Discount) * 100, 1)                            AS Avg_Discount_Given
FROM sales
GROUP BY Segment
ORDER BY Total_Sales DESC;

-- Insight to look for: Does the segment with highest sales
-- also have the highest margin? If not, why?


-- ════════════════════════════════════════════════════════════
--  QUERY 5 — Impact of Discount on Profitability
--  Business Question: At what discount level do orders
--  start becoming loss-making?
-- ════════════════════════════════════════════════════════════

SELECT
    CASE
        WHEN Discount = 0        THEN '0% (No Discount)'
        WHEN Discount <= 0.10    THEN '1–10%'
        WHEN Discount <= 0.20    THEN '11–20%'
        WHEN Discount <= 0.30    THEN '21–30%'
        ELSE '31–40%'
    END                                                       AS Discount_Band,
    COUNT(*)                                                  AS Orders,
    ROUND(SUM(Sales), 0)                                     AS Total_Sales,
    ROUND(SUM(Profit), 0)                                    AS Total_Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 1)              AS Profit_Margin_Pct,
    ROUND(
        100.0 * SUM(CASE WHEN Profit < 0 THEN 1 ELSE 0 END)
        / COUNT(*), 1
    )                                                         AS Loss_Order_Pct
FROM sales
GROUP BY Discount_Band
ORDER BY Discount_Band;

-- Key finding: At 31–40% discount, loss orders spike heavily.
-- Recommend: Cap discounts at 20% as company policy.


-- ════════════════════════════════════════════════════════════
--  QUERY 6 — Top 5 Sub-Categories by Profit (Bonus)
--  Window Function: RANK() to rank sub-categories
-- ════════════════════════════════════════════════════════════

SELECT
    Sub_Cat                                                   AS Sub_Category,
    ROUND(SUM(Sales), 0)                                     AS Sales,
    ROUND(SUM(Profit), 0)                                    AS Profit,
    ROUND(100.0 * SUM(Profit) / SUM(Sales), 1)              AS Margin_Pct,
    RANK() OVER (ORDER BY SUM(Profit) DESC)                  AS Profit_Rank
FROM sales
GROUP BY Sub_Cat
ORDER BY Profit DESC
LIMIT 5;
