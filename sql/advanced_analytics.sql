
-- ==========================================
-- QUERY 1: Calculate daily stock returns
-- ==========================================

WITH previous_prices AS (
    SELECT
        ticker,
        date,
        close,
        LAG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
        ) AS previous_close
    FROM market_prices
)

SELECT
    ticker,
    date,
    close,
    previous_close,
    ROUND(
        (close - previous_close) * 100.0 / previous_close,
        4
    ) AS daily_return_pct
FROM previous_prices
WHERE previous_close IS NOT NULL
ORDER BY ticker, date;


-- ==========================================
-- QUERY 2: Calculate 20-day moving average
-- ==========================================

WITH moving_averages AS (
    SELECT
        ticker,
        date,
        close,
        AVG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS moving_average_20
    FROM market_prices
)

SELECT
    ticker,
    date,
    close,
    ROUND(moving_average_20, 2) AS moving_average_20
FROM moving_averages
WHERE ticker = 'NVDA'
ORDER BY date DESC
LIMIT 20;


-- ==========================================
-- QUERY 3: Summarise daily returns by stock
-- ==========================================

WITH daily_returns AS (
    SELECT
        ticker,
        date,
        (close - LAG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
        )) * 100.0 /
        LAG(close) OVER (
            PARTITION BY ticker
            ORDER BY date
        ) AS daily_return_pct
    FROM market_prices
)

SELECT
    ticker,
    COUNT(daily_return_pct) AS trading_days,
    ROUND(AVG(daily_return_pct), 4) AS average_daily_return_pct,
    ROUND(MIN(daily_return_pct), 4) AS worst_daily_return_pct,
    ROUND(MAX(daily_return_pct), 4) AS best_daily_return_pct
FROM daily_returns
GROUP BY ticker
ORDER BY average_daily_return_pct DESC;
