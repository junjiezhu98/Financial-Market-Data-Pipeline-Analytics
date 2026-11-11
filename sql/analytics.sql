
-- Query 1: Count records for each stock

SELECT
    ticker,
    COUNT(*) AS total_records
FROM market_prices
GROUP BY ticker
ORDER BY total_records DESC;


-- Query 2: Calculate average closing price

SELECT
    ticker,
    ROUND(AVG(close), 2) AS average_close_price
FROM market_prices
GROUP BY ticker
ORDER BY average_close_price DESC;


-- Query 3: Calculate daily trading volume

SELECT
    ticker,
    ROUND(AVG(volume), 0) AS average_daily_volume,
    MAX(volume) AS maximum_daily_volume
FROM market_prices
GROUP BY ticker;


-- Query 4: Find the highest closing price for each stock

SELECT
    ticker,
    MAX(close) AS highest_close_price
FROM market_prices
GROUP BY ticker
ORDER BY highest_close_price DESC;
