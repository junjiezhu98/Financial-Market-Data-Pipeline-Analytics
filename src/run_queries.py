
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "data" / "market_data.db"
SQL_FILE = PROJECT_ROOT / "sql" / "analytics.sql"

# Connect to database
connection = sqlite3.connect(DATABASE_FILE)

# Read SQL file
with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql_content = file.read()

# Split and execute individual queries
queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

for i, query in enumerate(queries, start=1):

    print(f"\n{'=' * 50}")
    print(f"QUERY {i}")
    print("=" * 50)

    cursor = connection.execute(query)

    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    print(" | ".join(columns))

    for row in rows:
        print(" | ".join(str(value) for value in row))

connection.close()
