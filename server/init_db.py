import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "databases"
DB_PATH = DB_DIR / "food_ordering.db"
CREATE_SQL = DB_DIR / "create_tables.sql"
INSERT_SQL = DB_DIR / "insert_data.sql"

RESET_SQL = """
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS OrderItem;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS MenuItem;
DROP TABLE IF EXISTS Store;
DROP TABLE IF EXISTS Driver;
DROP TABLE IF EXISTS Account;

PRAGMA foreign_keys = ON;
"""


def run_sql_file(conn: sqlite3.Connection, sql_path: Path):
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    with sql_path.open("r", encoding="utf-8") as f:
        sql_script = f.read()
    conn.executescript(sql_script)

def main():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        # Drop old tables
        conn.executescript(RESET_SQL)

        # Create tables
        run_sql_file(conn, CREATE_SQL)

        # Insert sample data
        run_sql_file(conn, INSERT_SQL)

        conn.commit()
        print("✅ Database reset and populated successfully.")
        print(f"DB path: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

