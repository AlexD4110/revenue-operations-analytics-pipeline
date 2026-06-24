-- Metric views for the local SQLite version of the Revenue Operations Analytics Pipeline.
-- These views transform cleaned CRM tables into dashboard-ready reporting tables.

DROP VIEW IF EXISTS vw_sales_pipeline_enriched;
DROP VIEW IF EXISTS vw_executive_summary;
DROP VIEW IF EXISTS vw_sales_performance;
DROP VIEW IF EXISTS vw_product_performance;
DROP VIEW IF EXISTS vw_data_quality_summary;

-- Enriched opportunity view.
-- This joins the main sales pipeline table to account, product, and sales team dimensions.
CREATE VIEW vw_sales_pipeline_enriched AS
SELECT
    sp.opportunity_id,
    sp.sales_agent,
    st.manager,
    st.regional_office,
    sp.product,
    p.series,
    p.sales_price,
    sp.account,
    a.sector,
    a.revenue AS account_revenue,
    a.employees AS account_employees,
    a.office_location,
    sp.deal_stage,
    sp.engage_date,
    sp.close_date,
    sp.close_value,

    CASE
        WHEN sp.deal_stage = 'Won' THEN 1
        ELSE 0
    END AS is_won,

    CASE
        WHEN sp.deal_stage = 'Lost' THEN 1
        ELSE 0
    END AS is_lost,

    CASE
        WHEN sp.deal_stage IN ('Prospecting', 'Engaging') THEN 1
        ELSE 0
    END AS is_open,

    CASE
        WHEN sp.account IS NULL THEN 1
        ELSE 0
    END AS is_missing_account,

    CASE
        WHEN sp.engage_date IS NOT NULL
             AND sp.close_date IS NOT NULL
        THEN CAST(julianday(sp.close_date) - julianday(sp.engage_date) AS INTEGER)
        ELSE NULL
    END AS days_to_close,

    CASE
        WHEN sp.close_value IS NOT NULL THEN sp.close_value
        ELSE p.sales_price
    END AS estimated_opportunity_value

FROM sales_pipeline sp
LEFT JOIN accounts a
    ON sp.account = a.account
LEFT JOIN products p
    ON sp.product = p.product
LEFT JOIN sales_teams st
    ON sp.sales_agent = st.sales_agent;


-- Executive-level KPI summary.
CREATE VIEW vw_executive_summary AS
SELECT
    COUNT(*) AS total_opportunities,

    SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) AS won_opportunities,

    SUM(CASE WHEN deal_stage = 'Lost' THEN 1 ELSE 0 END) AS lost_opportunities,

    SUM(CASE WHEN deal_stage IN ('Prospecting', 'Engaging') THEN 1 ELSE 0 END) AS open_opportunities,

    ROUND(SUM(CASE WHEN deal_stage = 'Won' THEN close_value ELSE 0 END), 2) AS closed_won_revenue,

    ROUND(SUM(CASE WHEN deal_stage IN ('Prospecting', 'Engaging') THEN estimated_opportunity_value ELSE 0 END), 2) AS estimated_open_pipeline_value,

    ROUND(
        SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(CASE WHEN deal_stage IN ('Won', 'Lost') THEN 1 ELSE 0 END), 0),
        4
    ) AS win_rate,

    ROUND(AVG(CASE WHEN deal_stage IN ('Won', 'Lost') THEN days_to_close ELSE NULL END), 2) AS avg_days_to_close,

    SUM(is_missing_account) AS opportunities_missing_account

FROM vw_sales_pipeline_enriched;


-- Sales performance by sales agent, manager, and regional office.
CREATE VIEW vw_sales_performance AS
SELECT
    sales_agent,
    manager,
    regional_office,

    COUNT(*) AS total_opportunities,

    SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) AS won_opportunities,

    SUM(CASE WHEN deal_stage = 'Lost' THEN 1 ELSE 0 END) AS lost_opportunities,

    SUM(CASE WHEN deal_stage IN ('Prospecting', 'Engaging') THEN 1 ELSE 0 END) AS open_opportunities,

    ROUND(SUM(CASE WHEN deal_stage = 'Won' THEN close_value ELSE 0 END), 2) AS closed_won_revenue,

    ROUND(
        SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(CASE WHEN deal_stage IN ('Won', 'Lost') THEN 1 ELSE 0 END), 0),
        4
    ) AS win_rate,

    ROUND(AVG(CASE WHEN deal_stage IN ('Won', 'Lost') THEN days_to_close ELSE NULL END), 2) AS avg_days_to_close

FROM vw_sales_pipeline_enriched
GROUP BY
    sales_agent,
    manager,
    regional_office;


-- Product performance by product and product series.
CREATE VIEW vw_product_performance AS
SELECT
    product,
    series,

    COUNT(*) AS total_opportunities,

    SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) AS won_opportunities,

    SUM(CASE WHEN deal_stage = 'Lost' THEN 1 ELSE 0 END) AS lost_opportunities,

    SUM(CASE WHEN deal_stage IN ('Prospecting', 'Engaging') THEN 1 ELSE 0 END) AS open_opportunities,

    ROUND(SUM(CASE WHEN deal_stage = 'Won' THEN close_value ELSE 0 END), 2) AS closed_won_revenue,

    ROUND(
        SUM(CASE WHEN deal_stage = 'Won' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(SUM(CASE WHEN deal_stage IN ('Won', 'Lost') THEN 1 ELSE 0 END), 0),
        4
    ) AS win_rate,

    ROUND(AVG(CASE WHEN deal_stage IN ('Won', 'Lost') THEN days_to_close ELSE NULL END), 2) AS avg_days_to_close

FROM vw_sales_pipeline_enriched
GROUP BY
    product,
    series;


-- Data quality monitor view.
CREATE VIEW vw_data_quality_summary AS
SELECT
    rule_name,
    table_name,
    severity,
    status,
    failed_count,
    recommended_action
FROM data_quality_summary;