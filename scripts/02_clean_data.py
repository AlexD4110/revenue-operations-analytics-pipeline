import pandas as pd
from pathlib import Path


raw_path = Path("data/raw")
cleaned_path = Path("data/cleaned")
cleaned_path.mkdir(parents=True, exist_ok=True)


def clean_column_names(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def clean_text_columns(df):
    df = df.copy()

    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = df[column].astype("string").str.strip()

    return df


def clean_accounts(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)

    df["sector"] = df["sector"].replace({
        "technolgy": "technology"
    })

    df["office_location"] = df["office_location"].replace({
        "Philipines": "Philippines"
    })

    df["year_established"] = pd.to_numeric(df["year_established"], errors="coerce").astype("Int64")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df["employees"] = pd.to_numeric(df["employees"], errors="coerce").astype("Int64")

    return df


def clean_products(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)

    df["sales_price"] = pd.to_numeric(df["sales_price"], errors="coerce")

    return df


def clean_sales_pipeline(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)

    # Standardize known product naming mismatch between sales_pipeline and products.
    df["product"] = df["product"].replace({
        "GTXPro": "GTX Pro"
    })

    df["deal_stage"] = df["deal_stage"].str.title()
    df["engage_date"] = pd.to_datetime(df["engage_date"], errors="coerce")
    df["close_date"] = pd.to_datetime(df["close_date"], errors="coerce")
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")

    return df


def clean_sales_teams(df):
    df = clean_column_names(df)
    df = clean_text_columns(df)

    return df


accounts = pd.read_csv(raw_path / "accounts.csv")
products = pd.read_csv(raw_path / "products.csv")
sales_pipeline = pd.read_csv(raw_path / "sales_pipeline.csv")
sales_teams = pd.read_csv(raw_path / "sales_teams.csv")

accounts_clean = clean_accounts(accounts)
products_clean = clean_products(products)
sales_pipeline_clean = clean_sales_pipeline(sales_pipeline)
sales_teams_clean = clean_sales_teams(sales_teams)

accounts_clean.to_csv(cleaned_path / "accounts_clean.csv", index=False)
products_clean.to_csv(cleaned_path / "products_clean.csv", index=False)
sales_pipeline_clean.to_csv(cleaned_path / "sales_pipeline_clean.csv", index=False)
sales_teams_clean.to_csv(cleaned_path / "sales_teams_clean.csv", index=False)

print("Cleaned data files created successfully.")
print(f"Cleaned files saved to: {cleaned_path}")