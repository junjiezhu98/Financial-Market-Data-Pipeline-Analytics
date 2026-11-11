
import pandas as pd
import sqlite3
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "cleaned_market_data.csv"
DATABASE_FILE = PROJECT_ROOT / "data" / "market_data.db"

# Load cleaned data
df = pd.read_csv(INPUT_FILE)

# Convert date column
df["date"] = pd.to_datetime(df["date"], utc=True)

# Connect to SQLite database
connection = sqlite3.connect(DATABASE_FILE)

# Load data into SQL table
df.to_sql(
    name="market_prices",
    con=connection,
    if_exists="replace",
    index=False
)

# Create an index to improve query performance
connection.execute("""
    CREATE INDEX IF NOT EXISTS idx_ticker_date
    ON market_prices (ticker, date)
""")

connection.commit()

# Verify the loaded data
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM market_prices")
record_count = cursor.fetchone()[0]

cursor.execute("""
    SELECT DISTINCT ticker
    FROM market_prices
    ORDER BY ticker
""")

tickers = cursor.fetchall()

print("Database created successfully!")
print("Total records:", record_count)
print("Tickers:", [ticker[0] for ticker in tickers])

connection.close()
