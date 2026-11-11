
import sqlite3
import pandas as pd
import numpy as np


# --------------------------------------------------
# 1. Load market data from SQLite
# --------------------------------------------------

DB_PATH = "data/market_data.db"

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    """
    SELECT ticker, date, close
    FROM market_prices
    ORDER BY ticker, date
    """,
    conn
)

conn.close()


# --------------------------------------------------
# 2. Data preparation
# --------------------------------------------------

df["date"] = pd.to_datetime(df["date"])
df["close"] = pd.to_numeric(df["close"], errors="coerce")

df = df.dropna(subset=["ticker", "date", "close"])
df = df[df["close"] > 0]

df = df.sort_values(["ticker", "date"]).reset_index(drop=True)


# --------------------------------------------------
# 3. Calculate daily returns
# --------------------------------------------------

df["daily_return"] = (
    df.groupby("ticker")["close"].pct_change()
)


# --------------------------------------------------
# 4. Calculate maximum drawdown
# --------------------------------------------------

def calculate_max_drawdown(group):
    group = group.sort_values("date").copy()

    # Calculate cumulative growth of an initial investment
    wealth = (1 + group["daily_return"].fillna(0)).cumprod()

    # Track the highest value reached so far
    running_peak = wealth.cummax()

    # Calculate drawdown from the previous peak
    drawdown = (wealth / running_peak) - 1

    return drawdown.min() * 100


max_drawdown = (
    df.groupby("ticker")
    .apply(calculate_max_drawdown)
    .rename("max_drawdown_pct")
)


# --------------------------------------------------
# 5. Calculate risk and return statistics
# --------------------------------------------------

summary = df.groupby("ticker")["daily_return"].agg(
    average_daily_return="mean",
    daily_volatility="std",
    min="min",
    max="max"
)

# Annualised volatility (assuming 252 trading days)
summary["annualised_volatility_pct"] = (
    summary["daily_volatility"] * np.sqrt(252) * 100
)

# Compounded cumulative return
summary["cumulative_return_pct"] = (
    df.groupby("ticker")["daily_return"]
    .apply(
        lambda x: ((1 + x.dropna()).prod() - 1) * 100
    )
)

# Maximum drawdown
summary["max_drawdown_pct"] = max_drawdown


# --------------------------------------------------
# 6. Format and display results
# --------------------------------------------------

summary = summary[
    [
        "annualised_volatility_pct",
        "cumulative_return_pct",
        "max_drawdown_pct",
        "min",
        "max"
    ]
]

print("\nRISK ANALYTICS SUMMARY")
print("=" * 90)
print(summary.round(2).to_string())

print("\nMETRIC DEFINITIONS")
print("=" * 90)
print("Annualised volatility : Annualised standard deviation of daily returns.")
print("Cumulative return     : Compounded return over the observation period.")
print("Maximum drawdown      : Largest peak-to-trough percentage decline.")
print("Minimum daily return  : Worst observed daily return.")
print("Maximum daily return  : Best observed daily return.")


# --------------------------------------------------
# 7. Export results
# --------------------------------------------------

summary.round(2).to_csv(
    "reports/risk_analytics_summary.csv"
)

print("\nResults saved to reports/risk_analytics_summary.csv")
