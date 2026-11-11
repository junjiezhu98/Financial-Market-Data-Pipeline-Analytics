
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_FILE = PROJECT_ROOT / "data" / "market_data.db"
SQL_FILE = PROJECT_ROOT / "sql" / "advanced_analytics.sql"

connection = sqlite3.connect(DATABASE_FILE)

with open(SQL_FILE, "r", encoding="utf-8") as file:
    sql_content = file.read()

queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

for i, query in enumerate(queries, start=1):

    print(f"\n{'=' * 60}")
    print(f"ADVANCED QUERY {i}")
    print("=" * 60)

    cursor = connection.execute(query)

    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()

    print(" | ".join(columns))

    for row in rows:
        print(" | ".join(
            str(value) if value is not None else "NULL"
            for value in row
        ))

connection.close()
