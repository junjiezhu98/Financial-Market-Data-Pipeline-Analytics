
import yfinance as yf
import pandas as pd
from pathlib import Path

# 1. Define the stocks we want to analyse
TICKERS = [
    "MU",      # Micron
    "MSFT",      # Microsoft
    "NVDA",      # NVIDIA
    "GOOGL",   # Google
    "QBTS"     # Dwave
]

# 2. Create an empty list to store the downloaded data
all_data = []

# 3. Download historical data for each stock
for ticker in TICKERS:

    print(f"Downloading {ticker}...")

    stock = yf.Ticker(ticker)

    df = stock.history(
        period="3y",
        interval="1d",
        auto_adjust=True
    )

    # Add stock ticker as a column
    df = df.reset_index()
    df["ticker"] = ticker

    all_data.append(df)

# 4. Combine all stocks into one DataFrame
market_data = pd.concat(all_data, ignore_index=True)

# 5. Standardise column names
market_data.columns = [
    col.lower().replace(" ", "_")
    for col in market_data.columns
]

# 6. Save the downloaded data
project_root = Path(__file__).resolve().parent.parent
output_path = project_root / "data" / "market_data.csv"

market_data.to_csv(output_path, index=False)

# 7. Display basic information
print("\nDownload completed!")
print(f"Total records: {len(market_data)}")
print(f"Number of stocks: {market_data['ticker'].nunique()}")

print("\nFirst five records:")
print(market_data.head())

print("\nMissing values:")
print(market_data.isnull().sum())

print(f"\nSaved to: {output_path}")
