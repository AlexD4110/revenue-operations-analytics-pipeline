# Revenue Operations Analytics Pipeline

## Overview

This project is an end-to-end revenue operations analytics pipeline built using the Maven Analytics CRM Sales Opportunities dataset. The goal is to simulate how a company transforms raw CRM-style sales data into clean, validated, and dashboard-ready reporting.

The project focuses on the full analytics workflow behind reliable business reporting, including data profiling, data cleaning, relationship checks, data quality validation, SQL modeling, Power BI dashboarding, and stakeholder documentation.

---

## Business Problem

Sales and revenue operations teams often rely on CRM data to track pipeline performance, closed-won revenue, sales activity, account performance, product performance, and regional trends.

However, raw CRM exports can contain issues such as:

* Missing values
* Spelling errors
* Inconsistent product names
* Incomplete account information
* Date fields stored as text
* Values that are not ready for reporting
* Relationship mismatches between tables

If these issues are not identified and corrected, business dashboards may produce inaccurate metrics or fail to connect important records across tables.

This project simulates that real-world problem by taking raw CRM-style data and preparing it for trustworthy reporting.

---

## Dataset

The project uses the Maven Analytics CRM Sales Opportunities dataset.

Raw files used:

* `accounts.csv`
* `products.csv`
* `sales_pipeline.csv`
* `sales_teams.csv`
* `data_dictionary.csv`

The dataset includes sales opportunity records, account information, product details, and sales team assignments.

---

## Current Project Status

The project currently includes:

* Project folder structure
* Python virtual environment setup
* Git version control
* Raw Maven CRM dataset
* Initial data profiling script
* Data profiling notes
* Data dictionary reference
* Data cleaning script
* Cleaned CSV outputs
* Cleaned data verification script
* Drafted data quality validation logic

Future planned work includes:

* Data quality report generation
* SQL table creation
* Loading cleaned data into SQLite
* SQL metric views
* Power BI dashboard pages
* Final stakeholder documentation
* Dashboard screenshots

---

## Project Structure

```text
revenue-operations-analytics-pipeline/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── quality/
│
├── scripts/
│   ├── 01_profile_data.py
│   ├── 02_clean_data.py
│   └── 03_verify_cleaned_data.py
│
├── docs/
│   ├── profiling_notes.md
│   └── project_summary_so_far.md
│
├── sql/
│
├── powerbi/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Data Model

The main table is `sales_pipeline.csv`, which acts as the fact table because it contains the individual sales opportunities.

The supporting dimension tables are:

* `accounts.csv`
* `products.csv`
* `sales_teams.csv`

Initial relationship map:

| From Table     | From Field  | To Table    | To Field    |
| -------------- | ----------- | ----------- | ----------- |
| sales_pipeline | account     | accounts    | account     |
| sales_pipeline | product     | products    | product     |
| sales_pipeline | sales_agent | sales_teams | sales_agent |

This relationship structure will support future SQL joins and Power BI modeling.

---

## Step 1: Data Profiling

The first script created was:

```text
scripts/01_profile_data.py
```

This script reviews the raw CSV files and prints:

* Row and column counts
* Column names
* Data types
* Missing value counts
* Duplicate row counts
* Sample records

The profiling process helped identify the structure of each table before making any changes to the data.

Key findings included:

* `sales_pipeline.csv` contains 8,800 sales opportunity records
* `accounts.csv` contains 85 account records
* `products.csv` contains 7 product records
* `sales_teams.csv` contains 35 sales agent records
* `sales_pipeline.csv` contains missing values in account, engage date, close date, and close value fields
* Some values required cleaning, such as product name mismatches and spelling issues

---

## Step 2: Data Dictionary Review

The dataset includes `data_dictionary.csv`, which was used as the first reference for understanding field definitions.

The data dictionary helped define the meaning of fields such as:

* `account`
* `sector`
* `revenue`
* `employees`
* `opportunity_id`
* `deal_stage`
* `engage_date`
* `close_date`
* `close_value`
* `sales_agent`
* `manager`
* `regional_office`

This information was incorporated into the project documentation to support clear business understanding before building metrics.

---

## Step 3: Data Cleaning

The cleaning script is:

```text
scripts/02_clean_data.py
```

This script reads the raw CSV files, applies cleaning logic, and saves cleaned versions into:

```text
data/cleaned/
```

Cleaned output files include:

* `accounts_clean.csv`
* `products_clean.csv`
* `sales_pipeline_clean.csv`
* `sales_teams_clean.csv`

Cleaning steps currently include:

* Standardizing column names
* Removing leading and trailing spaces from text fields
* Correcting known spelling issues
* Standardizing product names
* Converting date fields into date format
* Converting numeric fields into numeric format

Known corrections applied:

| Original Value | Cleaned Value |
| -------------- | ------------- |
| technolgy      | technology    |
| Philipines     | Philippines   |
| GTXPro         | GTX Pro       |

The raw files are not manually edited. All transformations are completed through repeatable Python scripts.

---

## Step 4: Cleaned Data Verification

The cleaned data verification script is:

```text
scripts/03_verify_cleaned_data.py
```

This script checks whether the cleaned files were created successfully and whether important table relationships work correctly.

The script verifies:

* Cleaned file row and column counts
* Column names
* Data types
* Missing values
* Duplicate rows
* Product relationship between `sales_pipeline` and `products`
* Sales agent relationship between `sales_pipeline` and `sales_teams`
* Account relationship between `sales_pipeline` and `accounts`
* Missing close dates and close values by deal stage

Relationship checks passed successfully:

```text
Products in sales_pipeline but not in products:
set()

Sales agents in sales_pipeline but not in sales_teams:
set()

Accounts in sales_pipeline but not in accounts:
set()
```

This confirms that the cleaned data can be reliably joined across the core CRM tables.

---

## Initial Deal Stage Review

The cleaned `sales_pipeline` table includes four deal stages:

* Prospecting
* Engaging
* Won
* Lost

Missing close dates and close values only appear in open pipeline stages:

* Engaging
* Prospecting

This makes business sense because open opportunities may not have closed yet.

---

## Tools Used

Current tools:

* Python
* Pandas
* Git
* GitHub
* Markdown
* VS Code

Planned tools:

* SQLite
* SQL
* Power BI
* Power Query

---

## How to Run the Current Project

Clone the repository:

```bash
git clone https://github.com/AlexD4110/revenue-operations-analytics-pipeline.git
cd revenue-operations-analytics-pipeline
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the profiling script:

```bash
python scripts/01_profile_data.py
```

Run the cleaning script:

```bash
python scripts/02_clean_data.py
```

Run the cleaned data verification script:

```bash
python scripts/03_verify_cleaned_data.py
```

---

## Key Concepts Demonstrated So Far

This project currently demonstrates:

* Data profiling
* Data cleaning
* Repeatable Python scripting
* Raw vs cleaned data separation
* Fact and dimension table identification
* Primary key and foreign key thinking
* Relationship validation
* Business rule documentation
* Version control with Git
* Technical documentation in Markdown

---

## Next Steps

Planned next steps:

1. Finalize and run the data quality validation script
2. Create a structured data quality report
3. Create SQL table definitions
4. Load cleaned data into SQLite
5. Build SQL views for business KPIs
6. Create Power BI dashboard pages
7. Add dashboard screenshots
8. Finalize stakeholder documentation

---

## Future Dashboard Pages

The final Power BI dashboard is planned to include:

### Executive Overview

High-level revenue and pipeline performance.

### Sales Performance

Sales agent, manager, product, and regional performance.

### Pipeline Health

Open opportunities, stalled deals, and stage-level analysis.

### Data Quality Monitor

Validation results and reporting trust indicators.

---

## Project Summary

This project simulates a real revenue operations reporting workflow. It starts with raw CRM-style sales data, profiles the files with Python, reviews the data dictionary, identifies the fact and dimension tables, and creates repeatable cleaning scripts.

After cleaning the data, the project verifies that the key relationships between opportunities, accounts, products, and sales teams work correctly. This ensures the cleaned data is ready for validation, SQL modeling, and dashboard reporting.

The main goal of the project is to demonstrate how messy business data can be transformed into clean, reliable, and documented reporting data.
