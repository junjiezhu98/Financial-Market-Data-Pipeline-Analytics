
-- ==========================================
-- QUERY 1: Calculate daily returns
-- ==========================================

WITH daily_returns AS (
    SELECT
        ticker,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
        ) AS previous_close
    FROM market_prices
),

returns AS (
    SELECT
        ticker,
        date,
        close,
        (close / previous_close - 1.0) AS daily_return
    FROM daily_returns
    WHERE previous_close IS NOT NULL
)

-- ==========================================
-- QUERY 2: Calculate cumulative returns
-- ==========================================

SELECT
    ticker,
    ROUND(
        (
            EXP(SUM(LN(1.0 + daily_return))) - 1
        ) * 100,
        2
    ) AS cumulative_return_pct
FROM returns
WHERE daily_return > -1
GROUP BY ticker
ORDER BY cumulative_return_pct DESC;
