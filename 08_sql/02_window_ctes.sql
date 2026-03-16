-- ============================================================
-- SQL WINDOW FUNCTIONS + CTEs — Interview Essentials
-- ============================================================

-- ── WINDOW FUNCTIONS ─────────────────────────────────────────
-- Perform calculations ACROSS related rows WITHOUT collapsing them
-- Unlike GROUP BY — you keep all individual rows
-- Syntax: FUNCTION() OVER (PARTITION BY col ORDER BY col)

-- ── ROW_NUMBER ────────────────────────────────────────────────
-- Unique sequential number within each partition (no ties)
SELECT
    name,
    department,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num
FROM employees;
-- Each department gets its own numbered sequence: sales gets 1,2,3; HR gets 1,2,3

-- Get top 2 earners per department
SELECT * FROM (
    SELECT
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) t
WHERE rn <= 2;

-- ── RANK vs DENSE_RANK ────────────────────────────────────────
-- RANK: ties get same rank, but creates GAPS (1, 1, 3 — no 2)
-- DENSE_RANK: ties get same rank, NO GAPS (1, 1, 2)

SELECT
    name,
    salary,
    RANK()       OVER (ORDER BY salary DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS rank_no_gaps
FROM employees;

-- Example output:
-- Alice  90000  |  1  |  1
-- Bob    90000  |  1  |  1   (tie)
-- Carol  80000  |  3  |  2   (RANK skips 2, DENSE_RANK doesn't)

-- ── LAG and LEAD ─────────────────────────────────────────────
-- LAG:  look at PREVIOUS row's value
-- LEAD: look at NEXT row's value

SELECT
    month,
    revenue,
    LAG(revenue, 1)  OVER (ORDER BY month) AS prev_month_revenue,
    LEAD(revenue, 1) OVER (ORDER BY month) AS next_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS month_over_month_change
FROM monthly_revenue
ORDER BY month;

-- ── SUM / AVG OVER PARTITION ──────────────────────────────────
-- Running total or aggregate per group — WITHOUT collapsing rows
SELECT
    name,
    department,
    salary,
    SUM(salary) OVER (PARTITION BY department) AS dept_total_salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    salary / SUM(salary) OVER (PARTITION BY department) * 100 AS pct_of_dept
FROM employees;

-- Running sum (cumulative)
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS running_total
FROM transactions;

-- ── NTILE ────────────────────────────────────────────────────
-- Divide rows into N equal buckets
SELECT
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile   -- 1, 2, 3, or 4
FROM employees;

-- ── CTEs — Common Table Expressions ──────────────────────────
-- Name a subquery and reuse it — much cleaner than nested subqueries
-- Syntax: WITH name AS (SELECT ...)

-- Simple CTE
WITH active_users AS (
    SELECT *
    FROM users
    WHERE is_active = true
)
SELECT * FROM active_users WHERE age > 25;

-- Multiple CTEs
WITH
    active_users AS (
        SELECT id, name, email FROM users WHERE is_active = true
    ),
    high_value_orders AS (
        SELECT user_id, SUM(total) AS total_spent
        FROM orders
        WHERE status = 'completed'
        GROUP BY user_id
        HAVING SUM(total) > 10000
    )
SELECT
    u.name,
    u.email,
    o.total_spent
FROM active_users u
INNER JOIN high_value_orders o ON u.id = o.user_id
ORDER BY o.total_spent DESC;

-- ── REAL EXAMPLE: CASE MANAGEMENT QUERY ───────────────────────────
-- All cases per corporate client, grouped by status
WITH client_cases AS (
    SELECT
        c.client_id,
        cl.company_name,
        ca.status,
        COUNT(*)        AS case_count,
        SUM(ca.amount)  AS total_amount,
        AVG(EXTRACT(DAY FROM (ca.resolved_at - ca.created_at))) AS avg_resolution_days
    FROM cases ca
    JOIN clients cl ON ca.client_id = cl.id
    WHERE ca.created_at >= NOW() - INTERVAL '1 year'
    GROUP BY c.client_id, cl.company_name, ca.status
),
client_totals AS (
    SELECT
        client_id,
        company_name,
        SUM(case_count) AS total_cases
    FROM client_cases
    GROUP BY client_id, company_name
)
SELECT
    cc.company_name,
    cc.status,
    cc.case_count,
    cc.total_amount,
    ROUND(cc.avg_resolution_days, 1) AS avg_days,
    ROUND(cc.case_count * 100.0 / ct.total_cases, 2) AS pct_of_total
FROM client_cases cc
JOIN client_totals ct ON cc.client_id = ct.client_id
ORDER BY cc.company_name, cc.case_count DESC;

-- ── RECURSIVE CTE ────────────────────────────────────────────
-- Useful for hierarchical data (org charts, categories, graphs)
WITH RECURSIVE org_chart AS (
    -- Base case: top-level employees (no manager)
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees who report to previous level
    SELECT e.id, e.name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT level, name FROM org_chart ORDER BY level, name;
