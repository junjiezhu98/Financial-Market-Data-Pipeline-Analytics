
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


# --------------------------------------------------
# 1. Load market data
# --------------------------------------------------

DB_PATH = "data/market_data.db"
REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)

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

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(["ticker", "date"])


# --------------------------------------------------
# 2. Calculate daily and cumulative returns
# --------------------------------------------------

df["daily_return"] = (
    df.groupby("ticker")["close"].pct_change()
)

df["cumulative_return"] = (
    df.groupby("ticker")["daily_return"]
    .transform(lambda x: (1 + x.fillna(0)).cumprod() - 1)
)

df["cumulative_return_pct"] = (
    df["cumulative_return"] * 100
)


# --------------------------------------------------
# 3. Calculate annualised volatility
# --------------------------------------------------

risk_summary = df.groupby("ticker")["daily_return"].agg(
    daily_volatility="std"
)

risk_summary["annualised_volatility_pct"] = (
    risk_summary["daily_volatility"] * np.sqrt(252) * 100
)


# --------------------------------------------------
# 4. Calculate maximum drawdown
# --------------------------------------------------

def calculate_max_drawdown(group):
    wealth = (1 + group["daily_return"].fillna(0)).cumprod()
    running_peak = wealth.cummax()
    drawdown = wealth / running_peak - 1

    return drawdown.min() * 100


risk_summary["max_drawdown_pct"] = (
    df.groupby("ticker")
    .apply(calculate_max_drawdown)
)


# --------------------------------------------------
# 5. Chart 1: Cumulative returns
# --------------------------------------------------

plt.figure(figsize=(12, 6))

for ticker, group in df.groupby("ticker"):
    plt.plot(
        group["date"],
        group["cumulative_return_pct"],
        label=ticker,
        linewidth=1.8
    )

plt.title("Cumulative Stock Returns", fontsize=15)
plt.xlabel("Date")
plt.ylabel("Cumulative Return (%)")
plt.legend(title="Ticker")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    f"{REPORT_DIR}/cumulative_returns.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 6. Chart 2: Annualised volatility
# --------------------------------------------------

volatility = risk_summary[
    "annualised_volatility_pct"
].sort_values(ascending=False)

plt.figure(figsize=(10, 6))

volatility.plot(kind="bar")

plt.title("Annualised Volatility by Stock", fontsize=15)
plt.xlabel("Ticker")
plt.ylabel("Annualised Volatility (%)")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(
    f"{REPORT_DIR}/annualised_volatility.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 7. Chart 3: Maximum drawdown
# --------------------------------------------------

drawdown = risk_summary[
    "max_drawdown_pct"
].sort_values()

plt.figure(figsize=(10, 6))

drawdown.plot(kind="bar")

plt.title("Maximum Drawdown by Stock", fontsize=15)
plt.xlabel("Ticker")
plt.ylabel("Maximum Drawdown (%)")
plt.xticks(rotation=0)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(
    f"{REPORT_DIR}/maximum_drawdown.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 8. Export risk summary
# --------------------------------------------------

risk_summary[
    [
        "annualised_volatility_pct",
        "max_drawdown_pct"
    ]
].round(2).to_csv(
    f"{REPORT_DIR}/risk_summary.csv"
)


print("\nVISUALISATION COMPLETED")
print("=" * 50)
print("Generated files:")
print("- reports/cumulative_returns.png")
print("- reports/annualised_volatility.png")
print("- reports/maximum_drawdown.png")
print("- reports/risk_summary.csv")
