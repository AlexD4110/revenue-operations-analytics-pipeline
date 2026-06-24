import pandas as pd
from pathlib import Path


cleaned_path = Path("data/cleaned")

cleaned_files = {
    "accounts": "accounts_clean.csv",
    "products": "products_clean.csv",
    "sales_pipeline": "sales_pipeline_clean.csv",
    "sales_teams": "sales_teams_clean.csv"
}

tables = {}

for table_name, file_name in cleaned_files.items():
    print("=" * 80)
    print(f"Checking cleaned table: {table_name}")

    file_path = cleaned_path / file_name

    if not file_path.exists():
        print(f"Missing file: {file_path}")
        continue

    df = pd.read_csv(file_path)
    tables[table_name] = df

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


print("=" * 80)
print("Relationship checks")

accounts = tables["accounts"]
products = tables["products"]
sales_pipeline = tables["sales_pipeline"]
sales_teams = tables["sales_teams"]

pipeline_products = set(sales_pipeline["product"].dropna().unique())
valid_products = set(products["product"].dropna().unique())
missing_products = pipeline_products - valid_products

print("\nProducts in sales_pipeline but not in products:")
print(missing_products)

pipeline_agents = set(sales_pipeline["sales_agent"].dropna().unique())
valid_agents = set(sales_teams["sales_agent"].dropna().unique())
missing_agents = pipeline_agents - valid_agents

print("\nSales agents in sales_pipeline but not in sales_teams:")
print(missing_agents)

pipeline_accounts = set(sales_pipeline["account"].dropna().unique())
valid_accounts = set(accounts["account"].dropna().unique())
missing_accounts = pipeline_accounts - valid_accounts

print("\nAccounts in sales_pipeline but not in accounts:")
print(missing_accounts)

print("\n" + "=" * 80)
print("Deal stage checks")

print("\nUnique deal stages:")
print(sales_pipeline["deal_stage"].dropna().sort_values().unique())

missing_close_dates_by_stage = (
    sales_pipeline
    .groupby("deal_stage")["close_date"]
    .apply(lambda column: column.isna().sum())
)

print("\nMissing close_date values by deal_stage:")
print(missing_close_dates_by_stage)

missing_close_values_by_stage = (
    sales_pipeline
    .groupby("deal_stage")["close_value"]
    .apply(lambda column: column.isna().sum())
)

print("\nMissing close_value values by deal_stage:")
print(missing_close_values_by_stage)

print("\nCleaned data verification complete.")