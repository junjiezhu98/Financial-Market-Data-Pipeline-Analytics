
import pandas as pd


def validate_market_data(df):
    """Return data-quality issues found in market data."""

    issues = {}

    issues["missing_values"] = int(df.isnull().sum().sum())

    issues["duplicate_records"] = int(
        df.duplicated(subset=["date", "ticker"]).sum()
    )

    price_columns = ["open", "high", "low", "close"]

    issues["invalid_prices"] = int(
        (df[price_columns] <= 0).any(axis=1).sum()
    )

    issues["negative_volume"] = int(
        (df["volume"] < 0).sum()
    )

    issues["inconsistent_prices"] = int(
        (
            (df["high"] < df["low"]) |
            (df["close"] > df["high"]) |
            (df["close"] < df["low"]) |
            (df["open"] > df["high"]) |
            (df["open"] < df["low"])
        ).sum()
    )

    return issues


def test_quality_checks_detect_invalid_price():

    test_data = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "ticker": ["AAPL", "AAPL"],
        "open": [100, 105],
        "high": [110, 115],
        "low": [95, 100],
        "close": [105, -5],
        "volume": [1000, 1200]
    })

    results = validate_market_data(test_data)

    assert results["invalid_prices"] == 1


def test_quality_checks_detect_duplicates():

    test_data = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-01"],
        "ticker": ["AAPL", "AAPL"],
        "open": [100, 100],
        "high": [110, 110],
        "low": [95, 95],
        "close": [105, 105],
        "volume": [1000, 1000]
    })

    results = validate_market_data(test_data)

    assert results["duplicate_records"] == 1
