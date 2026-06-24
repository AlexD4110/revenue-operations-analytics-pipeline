import sqlite3
import pandas as pd
from pathlib import Path


DATABASE_PATH = Path("data/database")
REPORTING_PATH = Path("data/reporting")

DB_FILE = DATABASE_PATH / "revenue_operations.db"

# Create the reporting output folder if it does not already exist.
REPORTING_PATH.mkdir(parents=True, exist_ok=True)

# Map each SQLite reporting view to the CSV file it should create.
VIEWS_TO_EXPORT = {
    "vw_sales_pipeline_enriched": "sales_pipeline_enriched.csv",
    "vw_executive_summary": "executive_summary.csv",
    "vw_sales_performance": "sales_performance.csv",
    "vw_product_performance": "product_performance.csv",
    "vw_data_quality_summary": "data_quality_summary.csv"
}


def get_existing_views(connection):
    """Return a set of view names currently available in the SQLite database."""
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'view';
    """

    views = pd.read_sql_query(query, connection)

    return set(views["name"])


def validate_required_views(connection):
    """Confirm that all required reporting views exist before exporting."""
    existing_views = get_existing_views(connection)
    required_views = set(VIEWS_TO_EXPORT.keys())

    missing_views = required_views - existing_views

    if missing_views:
        missing_view_list = ", ".join(sorted(missing_views))

        raise ValueError(
            f"Missing required SQL views: {missing_view_list}. "
            "Run scripts/06_build_sqlite_views.py before exporting reporting files."
        )


def export_view_to_csv(connection, view_name, output_file):
    """Export one SQLite view to a reporting-ready CSV file."""
    query = f"SELECT * FROM {view_name};"

    df = pd.read_sql_query(query, connection)

    df.to_csv(output_file, index=False)

    return len(df)


def main():
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE}. "
            "Run scripts/05_load_to_sql.py first."
        )

    connection = sqlite3.connect(DB_FILE)

    try:
        validate_required_views(connection)

        for view_name, output_filename in VIEWS_TO_EXPORT.items():
            output_file = REPORTING_PATH / output_filename

            row_count = export_view_to_csv(
                connection=connection,
                view_name=view_name,
                output_file=output_file
            )

            print(f"Exported {row_count} rows from {view_name} to {output_file}")

        print("\nReporting files exported successfully.")
        print(f"Reporting folder: {REPORTING_PATH}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()