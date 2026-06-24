import pandas as pd
from pathlib import Path


raw_path = Path("data/raw")

files = [
    "accounts.csv",
    "data_dictionary.csv",
    "products.csv",
    "sales_pipeline.csv",
    "sales_teams.csv"
]


for file in files:
    print("=" * 80)
    print(f"Profiling file: {file}")

    df = pd.read_csv(raw_path / file)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\n")