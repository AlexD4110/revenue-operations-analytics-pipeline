import sqlite3
import pandas as pd
from pathlib import Path


CLEANED_PATH = Path("data/cleaned")
QUALITY_PATH = Path("data/quality")
DATABASE_PATH = Path("data/database")
DATABASE_PATH.mkdir(parents=True, exist_ok=True)

DB_FILE = DATABASE_PATH / "revenue_operations.db"

TABLES_TO_LOAD = {
    "accounts": CLEANED_PATH / "accounts_clean.csv",
    "products": CLEANED_PATH / "products_clean.csv",
    "sales_pipeline": CLEANED_PATH / "sales_pipeline_clean.csv",
    "sales_teams": CLEANED_PATH / "sales_teams_clean.csv",
    "data_quality_summary": QUALITY_PATH / "data_quality_summary.csv",
    "data_quality_detail": QUALITY_PATH / "data_quality_detail.csv"
}


def load_csv_to_sql(connection, table_name, file_path):
    """Load one CSV file into a SQLite table."""
    df = pd.read_csv(file_path)

    df.to_sql(
        name=table_name,
        con=connection,
        if_exists="replace",
        index=False
    )

    return len(df)


def main():
    connection = sqlite3.connect(DB_FILE)

    try:
        for table_name, file_path in TABLES_TO_LOAD.items():
            if not file_path.exists():
                raise FileNotFoundError(f"Missing required file: {file_path}")

            row_count = load_csv_to_sql(
                connection=connection,
                table_name=table_name,
                file_path=file_path
            )

            print(f"Loaded {row_count} rows into table: {table_name}")

        connection.commit()

        print("\nSQLite database created successfully.")
        print(f"Database saved to: {DB_FILE}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()