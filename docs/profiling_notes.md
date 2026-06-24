# Data Profiling Notes

## Purpose

This document summarizes the initial profiling results for the Maven Analytics CRM Sales Opportunities dataset. The goal of this step is to understand the raw data structure, identify table relationships, review missing values, and document early cleaning or validation needs before building the analytics pipeline.

The file `data_dictionary.csv` is included in the raw dataset and should be used as the initial reference for field definitions.

---

## Source Files Reviewed

The raw dataset includes the following files:

* `accounts.csv`
* `products.csv`
* `sales_pipeline.csv`
* `sales_teams.csv`
* `data_dictionary.csv`

---

## Data Dictionary Reference

The `data_dictionary.csv` file contains 21 field definitions across the dataset.

Columns in `data_dictionary.csv`:

* `Table`
* `Field`
* `Description`

This file should be used to confirm the meaning of each field before cleaning, modeling, or creating KPI logic.

### Key Field Definitions From Data Dictionary

#### accounts

| Field            | Description                       |
| ---------------- | --------------------------------- |
| account          | Company name                      |
| sector           | Industry                          |
| year_established | Year established                  |
| revenue          | Annual revenue in millions of USD |
| employees        | Number of employees               |
| office_location  | Company office location           |
| subsidiary_of    | Parent company, if applicable     |

#### products

| Field       | Description         |
| ----------- | ------------------- |
| product     | Product name        |
| series      | Product series      |
| sales_price | Product sales price |

#### sales_pipeline

| Field          | Description                                  |
| -------------- | -------------------------------------------- |
| opportunity_id | Unique identifier for each sales opportunity |
| sales_agent    | Sales agent assigned to the opportunity      |
| product        | Product associated with the opportunity      |
| account        | Company associated with the opportunity      |
| deal_stage     | Current stage or outcome of the deal         |
| engage_date    | Date the sales process began                 |
| close_date     | Date the opportunity closed                  |
| close_value    | Final value of the closed opportunity        |

#### sales_teams

| Field           | Description                                 |
| --------------- | ------------------------------------------- |
| sales_agent     | Sales agent name                            |
| manager         | Sales manager name                          |
| regional_office | Regional office assigned to the sales agent |

---

# accounts.csv

## Basic Profile

Rows: 85
Columns: 7

Columns:

* account
* sector
* year_established
* revenue
* employees
* office_location
* subsidiary_of

## Data Types

* account: string
* sector: string
* year_established: integer
* revenue: float
* employees: integer
* office_location: string
* subsidiary_of: string

## Missing Values

* subsidiary_of has 70 missing values
* All other fields have 0 missing values

## Duplicate Rows

Duplicate rows: 0

## Primary Key Candidate

`account`

## Notes

The `account` field appears to uniquely identify each company and connects to `sales_pipeline.account`.

The `subsidiary_of` field has many missing values, but this is likely expected because most companies may not be subsidiaries.

Initial cleaning needs:

* Standardize sector spelling
* Correct `technolgy` to `technology`
* Standardize office location names
* Correct `Philipines` to `Philippines`

---

# products.csv

## Basic Profile

Rows: 7
Columns: 3

Columns:

* product
* series
* sales_price

## Data Types

* product: string
* series: string
* sales_price: integer

## Missing Values

No missing values.

## Duplicate Rows

Duplicate rows: 0

## Primary Key Candidate

`product`

## Notes

The `product` field appears to uniquely identify each product and connects to `sales_pipeline.product`.

Initial cleaning needs:

* Confirm product names match exactly between `products.csv` and `sales_pipeline.csv`
* Standardize product naming where needed

Known issue:

* `sales_pipeline.csv` contains `GTXPro`
* `products.csv` contains `GTX Pro`

This mismatch should be cleaned so joins do not fail.

---

# sales_pipeline.csv

## Basic Profile

Rows: 8,800
Columns: 8

Columns:

* opportunity_id
* sales_agent
* product
* account
* deal_stage
* engage_date
* close_date
* close_value

## Data Types

* opportunity_id: string
* sales_agent: string
* product: string
* account: string
* deal_stage: string
* engage_date: string
* close_date: string
* close_value: float

## Missing Values

* account: 1,425 missing values
* engage_date: 500 missing values
* close_date: 2,089 missing values
* close_value: 2,089 missing values
* opportunity_id: 0 missing values
* sales_agent: 0 missing values
* product: 0 missing values
* deal_stage: 0 missing values

## Duplicate Rows

Duplicate rows: 0

## Primary Key Candidate

`opportunity_id`

## Foreign Key Candidates

* `account` connects to `accounts.account`
* `product` connects to `products.product`
* `sales_agent` connects to `sales_teams.sales_agent`

## Date Columns

* engage_date
* close_date

## Money Columns

* close_value

## Notes

This is the main fact table for the project because it contains the individual sales opportunities.

This table will support metrics such as:

* Total pipeline value
* Closed-won revenue
* Win rate
* Average deal size
* Average days to close
* Sales agent performance
* Product performance
* Regional performance

Initial cleaning needs:

* Convert `engage_date` to a date field
* Convert `close_date` to a date field
* Convert `close_value` to a numeric field
* Standardize product names
* Standardize deal stage formatting

Initial validation needs:

* Check whether missing `close_date` values are acceptable based on `deal_stage`
* Check whether missing `close_value` values are acceptable based on `deal_stage`
* Check whether missing `account` values should be treated as data quality issues
* Check whether every `sales_agent` exists in `sales_teams.csv`
* Check whether every `product` exists in `products.csv`
* Check whether every populated `account` exists in `accounts.csv`

---

# sales_teams.csv

## Basic Profile

Rows: 35
Columns: 3

Columns:

* sales_agent
* manager
* regional_office

## Data Types

* sales_agent: string
* manager: string
* regional_office: string

## Missing Values

No missing values.

## Duplicate Rows

Duplicate rows: 0

## Primary Key Candidate

`sales_agent`

## Notes

The `sales_agent` field appears to uniquely identify each sales agent and connects to `sales_pipeline.sales_agent`.

This table will support sales performance reporting by:

* Sales agent
* Manager
* Regional office

Initial cleaning needs:

* Standardize text formatting
* Confirm every sales agent in `sales_pipeline.csv` exists in `sales_teams.csv`

---

# Initial Relationship Map

## Fact Table

`sales_pipeline.csv`

This table represents sales opportunities and will be the central table in the data model.

## Dimension Tables

`accounts.csv`

Describes the company/account associated with each opportunity.

`products.csv`

Describes the product associated with each opportunity.

`sales_teams.csv`

Describes the sales agent, manager, and regional office associated with each opportunity.

## Relationship Logic

| From Table     | From Field  | To Table    | To Field    |
| -------------- | ----------- | ----------- | ----------- |
| sales_pipeline | account     | accounts    | account     |
| sales_pipeline | product     | products    | product     |
| sales_pipeline | sales_agent | sales_teams | sales_agent |

---

# Initial Cleaning Plan

The first cleaning script should:

1. Standardize column names
2. Remove leading and trailing spaces from text fields
3. Correct known typos
4. Standardize product names
5. Convert date fields to date format
6. Convert money fields to numeric format
7. Save cleaned files to `data/cleaned`

The raw files should not be manually edited. All changes should be made through repeatable Python scripts.

---

# Initial Validation Plan

Validation should happen after cleaning.

Initial validation rules should include:

1. Every opportunity must have a valid `opportunity_id`
2. Every populated `sales_pipeline.account` should exist in `accounts.account`
3. Every `sales_pipeline.product` should exist in `products.product`
4. Every `sales_pipeline.sales_agent` should exist in `sales_teams.sales_agent`
5. Won opportunities should have a `close_date`
6. Won opportunities should have a positive `close_value`
7. Lost opportunities should have a `close_date`
8. Open opportunities may have missing `close_date` and `close_value`
9. `close_date` should not occur before `engage_date`
10. Product names should match consistently across tables

---

# Key Early Observations

The dataset is clean enough to use as a base project, but it contains enough realistic issues to support a strong data cleaning and validation workflow.

Important issues already identified:

* `technolgy` should be corrected to `technology`
* `Philipines` should be corrected to `Philippines`
* `GTXPro` should be standardized to `GTX Pro`
* 1,425 opportunities are missing account values
* 500 opportunities are missing engage dates
* 2,089 opportunities are missing close dates
* 2,089 opportunities are missing close values

These issues will become useful talking points because they show how raw CRM-style data can affect reporting quality if not cleaned and validated.
