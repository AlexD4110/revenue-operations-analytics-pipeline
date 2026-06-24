import sqlite3
import pandas as pd
from pathlib import Path


DATABASE_PATH = Path("data/database")
SQL_PATH = Path("sql/sqlite")

DB_FILE = DATABASE_PATH / "revenue_operations.db"
METRIC_VIEWS_FILE = SQL_PATH / "01_metric_views.sql"


def execute_sql_file(connection, sql_file):
    """Execute a SQL script against the SQLite database."""
    sql_script = sql_file.read_text()

    connection.executescript(sql_script)
    connection.commit()


def get_created_views(connection):
    """Return the list of views currently available in the SQLite database."""
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'view'
        ORDER BY name;
    """

    return pd.read_sql_query(query, connection)


def preview_view(connection, view_name):
    """Return a small preview from a SQL view."""
    query = f"SELECT * FROM {view_name} LIMIT 5;"
    return pd.read_sql_query(query, connection)


def main():
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE}. Run scripts/05_load_to_sql.py first."
        )

    if not METRIC_VIEWS_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {METRIC_VIEWS_FILE}")

    connection = sqlite3.connect(DB_FILE)

    try:
        execute_sql_file(connection, METRIC_VIEWS_FILE)

        views = get_created_views(connection)

        print("Metric views created successfully.")
        print("\nAvailable views:")
        print(views.to_string(index=False))

        print("\nExecutive summary preview:")
        print(preview_view(connection, "vw_executive_summary").to_string(index=False))

        print("\nSales performance preview:")
        print(preview_view(connection, "vw_sales_performance").to_string(index=False))

    finally:
        connection.close()


if __name__ == "__main__":
    main()