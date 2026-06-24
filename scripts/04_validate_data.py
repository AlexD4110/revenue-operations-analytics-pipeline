import pandas as pd
from pathlib import Path


CLEANED_PATH = Path("data/cleaned")
QUALITY_PATH = Path("data/quality")
QUALITY_PATH.mkdir(parents=True, exist_ok=True)

APPROVED_DEAL_STAGES = {"Prospecting", "Engaging", "Won", "Lost"}

SEVERITY_ORDER = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4
}


def load_cleaned_data():
    """Load cleaned CRM tables into pandas DataFrames."""
    accounts = pd.read_csv(CLEANED_PATH / "accounts_clean.csv")
    products = pd.read_csv(CLEANED_PATH / "products_clean.csv")
    sales_pipeline = pd.read_csv(CLEANED_PATH / "sales_pipeline_clean.csv")
    sales_teams = pd.read_csv(CLEANED_PATH / "sales_teams_clean.csv")

    return accounts, products, sales_pipeline, sales_teams


def prepare_date_fields(sales_pipeline):
    """Convert date columns to datetime before date-based validation."""
    sales_pipeline = sales_pipeline.copy()

    sales_pipeline["engage_date"] = pd.to_datetime(
        sales_pipeline["engage_date"],
        errors="coerce"
    )

    sales_pipeline["close_date"] = pd.to_datetime(
        sales_pipeline["close_date"],
        errors="coerce"
    )

    return sales_pipeline


def create_validation_outputs(
    rule_name,
    table_name,
    severity,
    failed_records,
    id_column,
    recommended_action,
    issue_description
):
    """Create summary and detail outputs for a single validation rule."""
    failed_count = len(failed_records)
    status = "Pass" if failed_count == 0 else "Fail"

    summary_record = {
        "rule_name": rule_name,
        "table_name": table_name,
        "severity": severity,
        "status": status,
        "failed_count": failed_count,
        "recommended_action": recommended_action
    }

    detail_records = []

    if failed_count > 0 and id_column in failed_records.columns:
        for _, row in failed_records.iterrows():
            detail_records.append({
                "rule_name": rule_name,
                "table_name": table_name,
                "severity": severity,
                "record_id": row[id_column],
                "issue_description": issue_description,
                "recommended_action": recommended_action
            })

    return summary_record, detail_records


def append_validation_result(
    summary_results,
    detail_results,
    rule_name,
    table_name,
    severity,
    failed_records,
    id_column,
    recommended_action,
    issue_description
):
    """Append one rule's summary and failed-record details to the report outputs."""
    summary_record, detail_records = create_validation_outputs(
        rule_name=rule_name,
        table_name=table_name,
        severity=severity,
        failed_records=failed_records,
        id_column=id_column,
        recommended_action=recommended_action,
        issue_description=issue_description
    )

    summary_results.append(summary_record)
    detail_results.extend(detail_records)


def main():
    accounts, products, sales_pipeline, sales_teams = load_cleaned_data()
    sales_pipeline = prepare_date_fields(sales_pipeline)

    summary_results = []
    detail_results = []

    # Rule 1: Opportunity IDs should be unique.
    duplicate_opportunities = sales_pipeline[
        sales_pipeline.duplicated(subset=["opportunity_id"], keep=False)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Opportunity IDs should be unique",
        table_name="sales_pipeline",
        severity="Critical",
        failed_records=duplicate_opportunities,
        id_column="opportunity_id",
        recommended_action="Review duplicate opportunity IDs and keep one trusted record per opportunity.",
        issue_description="Duplicate opportunity_id found in sales_pipeline."
    )

    # Rule 2: Deal stages should only contain approved values.
    invalid_deal_stages = sales_pipeline[
        ~sales_pipeline["deal_stage"].isin(APPROVED_DEAL_STAGES)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Deal stage should be an approved value",
        table_name="sales_pipeline",
        severity="High",
        failed_records=invalid_deal_stages,
        id_column="opportunity_id",
        recommended_action="Standardize deal_stage values to Prospecting, Engaging, Won, or Lost.",
        issue_description="deal_stage contains a value outside the approved list."
    )

    # Rule 3: Products in the pipeline should match the products dimension table.
    valid_products = set(products["product"].dropna().unique())

    invalid_products = sales_pipeline[
        sales_pipeline["product"].notna()
        & ~sales_pipeline["product"].isin(valid_products)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Opportunity product should exist in products table",
        table_name="sales_pipeline",
        severity="Critical",
        failed_records=invalid_products,
        id_column="opportunity_id",
        recommended_action="Correct product names or update the products dimension table.",
        issue_description="Product value does not match a product in the products table."
    )

    # Rule 4: Sales agents in the pipeline should match the sales teams dimension table.
    valid_sales_agents = set(sales_teams["sales_agent"].dropna().unique())

    invalid_sales_agents = sales_pipeline[
        sales_pipeline["sales_agent"].notna()
        & ~sales_pipeline["sales_agent"].isin(valid_sales_agents)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Opportunity sales agent should exist in sales teams table",
        table_name="sales_pipeline",
        severity="Critical",
        failed_records=invalid_sales_agents,
        id_column="opportunity_id",
        recommended_action="Correct sales agent names or update the sales teams dimension table.",
        issue_description="sales_agent does not match a sales_agent in the sales_teams table."
    )

    # Rule 5: Populated accounts in the pipeline should match the accounts dimension table.
    valid_accounts = set(accounts["account"].dropna().unique())

    invalid_accounts = sales_pipeline[
        sales_pipeline["account"].notna()
        & ~sales_pipeline["account"].isin(valid_accounts)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Opportunity account should exist in accounts table",
        table_name="sales_pipeline",
        severity="High",
        failed_records=invalid_accounts,
        id_column="opportunity_id",
        recommended_action="Correct account names or update the accounts dimension table.",
        issue_description="Account value does not match an account in the accounts table."
    )

    # Rule 6: Missing accounts limit account-level reporting.
    missing_accounts = sales_pipeline[
        sales_pipeline["account"].isna()
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Opportunity should have an account when available",
        table_name="sales_pipeline",
        severity="Medium",
        failed_records=missing_accounts,
        id_column="opportunity_id",
        recommended_action="Review opportunities without accounts because they cannot be included in account-level reporting.",
        issue_description="Opportunity is missing an account value."
    )

    # Rule 7: Deals beyond prospecting should have an engagement date.
    missing_required_engage_dates = sales_pipeline[
        sales_pipeline["deal_stage"].isin(["Engaging", "Won", "Lost"])
        & sales_pipeline["engage_date"].isna()
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Non-prospecting opportunities should have an engage date",
        table_name="sales_pipeline",
        severity="High",
        failed_records=missing_required_engage_dates,
        id_column="opportunity_id",
        recommended_action="Add engage dates for opportunities that have moved beyond prospecting.",
        issue_description="Opportunity moved beyond prospecting but is missing engage_date."
    )

    # Rule 8: Won opportunities should have close dates.
    won_missing_close_date = sales_pipeline[
        (sales_pipeline["deal_stage"] == "Won")
        & sales_pipeline["close_date"].isna()
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Won opportunities should have a close date",
        table_name="sales_pipeline",
        severity="Critical",
        failed_records=won_missing_close_date,
        id_column="opportunity_id",
        recommended_action="Add close dates for won opportunities.",
        issue_description="Won opportunity is missing close_date."
    )

    # Rule 9: Lost opportunities should have close dates.
    lost_missing_close_date = sales_pipeline[
        (sales_pipeline["deal_stage"] == "Lost")
        & sales_pipeline["close_date"].isna()
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Lost opportunities should have a close date",
        table_name="sales_pipeline",
        severity="High",
        failed_records=lost_missing_close_date,
        id_column="opportunity_id",
        recommended_action="Add close dates for lost opportunities.",
        issue_description="Lost opportunity is missing close_date."
    )

    # Rule 10: Won opportunities should have positive close values.
    won_invalid_close_value = sales_pipeline[
        (sales_pipeline["deal_stage"] == "Won")
        & (
            sales_pipeline["close_value"].isna()
            | (sales_pipeline["close_value"] <= 0)
        )
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Won opportunities should have a positive close value",
        table_name="sales_pipeline",
        severity="Critical",
        failed_records=won_invalid_close_value,
        id_column="opportunity_id",
        recommended_action="Add or correct close values for won opportunities.",
        issue_description="Won opportunity is missing close_value or has a non-positive close_value."
    )

    # Rule 11: Close date should not occur before engage date.
    close_before_engage = sales_pipeline[
        sales_pipeline["engage_date"].notna()
        & sales_pipeline["close_date"].notna()
        & (sales_pipeline["close_date"] < sales_pipeline["engage_date"])
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Close date should not occur before engage date",
        table_name="sales_pipeline",
        severity="High",
        failed_records=close_before_engage,
        id_column="opportunity_id",
        recommended_action="Review date fields and correct records where close_date occurs before engage_date.",
        issue_description="close_date occurs before engage_date."
    )

    # Rule 12: Account names should be unique.
    duplicate_accounts = accounts[
        accounts.duplicated(subset=["account"], keep=False)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Account names should be unique",
        table_name="accounts",
        severity="High",
        failed_records=duplicate_accounts,
        id_column="account",
        recommended_action="Review duplicate account names and determine whether records should be merged.",
        issue_description="Duplicate account name found in accounts table."
    )

    # Rule 13: Product names should be unique.
    duplicate_products = products[
        products.duplicated(subset=["product"], keep=False)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Product names should be unique",
        table_name="products",
        severity="High",
        failed_records=duplicate_products,
        id_column="product",
        recommended_action="Review duplicate product names and keep one trusted product record.",
        issue_description="Duplicate product name found in products table."
    )

    # Rule 14: Sales agent names should be unique.
    duplicate_sales_agents = sales_teams[
        sales_teams.duplicated(subset=["sales_agent"], keep=False)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Sales agent names should be unique",
        table_name="sales_teams",
        severity="High",
        failed_records=duplicate_sales_agents,
        id_column="sales_agent",
        recommended_action="Review duplicate sales agent records and keep one trusted sales team record.",
        issue_description="Duplicate sales agent found in sales_teams table."
    )

    # Rule 15: Product prices should be positive.
    invalid_sales_prices = products[
        products["sales_price"].isna()
        | (products["sales_price"] <= 0)
    ]

    append_validation_result(
        summary_results=summary_results,
        detail_results=detail_results,
        rule_name="Product sales price should be positive",
        table_name="products",
        severity="High",
        failed_records=invalid_sales_prices,
        id_column="product",
        recommended_action="Review product pricing and correct missing or non-positive sales prices.",
        issue_description="Product sales_price is missing or non-positive."
    )

    summary_report = pd.DataFrame(summary_results)
    detail_report = pd.DataFrame(detail_results)

    summary_report["severity_sort"] = summary_report["severity"].map(SEVERITY_ORDER)

    summary_report = summary_report.sort_values(
        by=["status", "severity_sort", "failed_count"],
        ascending=[True, True, False]
    )

    summary_report = summary_report.drop(columns=["severity_sort"])

    summary_report.to_csv(
        QUALITY_PATH / "data_quality_summary.csv",
        index=False
    )

    detail_report.to_csv(
        QUALITY_PATH / "data_quality_detail.csv",
        index=False
    )

    print(summary_report)

    print("\nData quality summary and detail reports created successfully.")
    print(f"Summary report saved to: {QUALITY_PATH / 'data_quality_summary.csv'}")
    print(f"Detail report saved to: {QUALITY_PATH / 'data_quality_detail.csv'}")


if __name__ == "__main__":
    main()