
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Load the downloaded market data
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "market_data.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "cleaned_market_data.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "data_quality_report.txt"

df = pd.read_csv(INPUT_FILE)

print("Original dataset shape:", df.shape)

# --------------------------------------------------
# 2. Standardise data types
# --------------------------------------------------

df["date"] = pd.to_datetime(df["date"], utc=True)

numeric_columns = ["open", "high", "low", "close", "volume"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["ticker"] = df["ticker"].astype("string").str.strip()

# --------------------------------------------------
# 3. Initialise quality report
# --------------------------------------------------

report = []

report.append("FINANCIAL MARKET DATA QUALITY REPORT")
report.append("=" * 45)

# Check missing values
missing_values = df.isnull().sum()

report.append("\n1. Missing values:")
report.append(str(missing_values))

# Check duplicate records
duplicate_count = df.duplicated(
    subset=["date", "ticker"]
).sum()

report.append(f"\n2. Duplicate records: {duplicate_count}")

# Check invalid prices
invalid_price_count = (
    (df[numeric_columns[:4]] <= 0).any(axis=1)
).sum()

report.append(f"\n3. Records with non-positive prices: {invalid_price_count}")

# Check invalid volume
invalid_volume_count = (df["volume"] < 0).sum()

report.append(f"\n4. Records with negative volume: {invalid_volume_count}")

# Check price consistency
invalid_range_count = (
    (df["high"] < df["low"]) |
    (df["close"] > df["high"]) |
    (df["close"] < df["low"]) |
    (df["open"] > df["high"]) |
    (df["open"] < df["low"])
).sum()

report.append(f"\n5. Records with inconsistent price ranges: {invalid_range_count}")

# --------------------------------------------------
# 4. Remove duplicate and invalid records
# --------------------------------------------------

df = df.drop_duplicates(
    subset=["date", "ticker"],
    keep="last"
)

# Remove rows with missing essential fields
df = df.dropna(
    subset=["date", "ticker", "open", "high", "low", "close", "volume"]
)

# Remove invalid prices and volumes
df = df[
    (df[["open", "high", "low", "close"]] > 0).all(axis=1)
]

df = df[df["volume"] >= 0]

# Remove inconsistent price records
df = df[
    (df["high"] >= df["low"]) &
    (df["close"] <= df["high"]) &
    (df["close"] >= df["low"]) &
    (df["open"] <= df["high"]) &
    (df["open"] >= df["low"])
]

# --------------------------------------------------
# 5. Check for missing trading dates
# --------------------------------------------------

report.append("\n6. Potential missing trading dates:")

for ticker, group in df.groupby("ticker"):

    dates = group["date"].sort_values()

    # A gap greater than 4 calendar days is flagged
    gaps = dates.diff().dt.days

    suspicious_gaps = dates[gaps > 4]

    report.append(
        f"{ticker}: {len(suspicious_gaps)} potential gaps"
    )

# --------------------------------------------------
# 6. Save cleaned data and report
# --------------------------------------------------

df = df.sort_values(["ticker", "date"])

df.to_csv(OUTPUT_FILE, index=False)

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT_FILE, "w", encoding="utf-8") as file:
    file.write("\n".join(report))

# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\nData cleaning completed!")

print("Original records:", len(pd.read_csv(INPUT_FILE)))
print("Cleaned records:", len(df))
print("Removed records:", len(pd.read_csv(INPUT_FILE)) - len(df))

print("\nCleaned dataset shape:", df.shape)

print("\nQuality report:")
print("\n".join(report))

print(f"\nCleaned data saved to: {OUTPUT_FILE}")
print(f"Quality report saved to: {REPORT_FILE}")
