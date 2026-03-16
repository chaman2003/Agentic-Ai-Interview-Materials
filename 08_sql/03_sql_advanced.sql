-- ============================================================
-- SQL ADVANCED PATTERNS — Interview & Production Reference
-- ============================================================
-- Topics:
--   1.  Complex aggregations with CASE WHEN
--   2.  Multi-table CTEs
--   3.  Recursive CTEs (hierarchy + date series)
--   4.  Window functions (running totals, moving avg, percentile)
--   5.  PIVOT-style queries
--   6.  String manipulation
--   7.  Date / time operations
--   8.  JSON operations in PostgreSQL
--   9.  Full-text search in PostgreSQL
--   10. Table partitioning
--   11. EXPLAIN ANALYZE examples
-- ============================================================

-- ── SETUP TABLES ─────────────────────────────────────────────
-- Reference schema used throughout this file

CREATE TABLE IF NOT EXISTS employees (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(50),
    salary      NUMERIC(10,2),
    hire_date   DATE,
    manager_id  INT REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT,
    product_id  INT,
    amount      NUMERIC(10,2),
    status      VARCHAR(20),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200),
    category    VARCHAR(50),
    price       NUMERIC(10,2),
    metadata    JSONB
);

CREATE TABLE IF NOT EXISTS categories (
    id          INT PRIMARY KEY,
    name        VARCHAR(100),
    parent_id   INT REFERENCES categories(id)
);


-- ============================================================
-- 1. COMPLEX AGGREGATIONS WITH CASE WHEN
-- ============================================================

-- ── Conditional aggregation: count/sum based on conditions ──
-- "How many orders per status, without pivoting manually?"
SELECT
    customer_id,
    COUNT(*)                                                AS total_orders,
    COUNT(CASE WHEN status = 'completed' THEN 1 END)        AS completed,
    COUNT(CASE WHEN status = 'pending'   THEN 1 END)        AS pending,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END)        AS cancelled,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS completed_revenue,
    -- Cleaner with FILTER (PostgreSQL-specific)
    COUNT(*) FILTER (WHERE status = 'refunded')             AS refunded
FROM orders
GROUP BY customer_id
ORDER BY total_orders DESC;

-- ── Salary band distribution per department ──
SELECT
    department,
    COUNT(*) AS total,
    SUM(CASE WHEN salary < 50000  THEN 1 ELSE 0 END) AS band_junior,
    SUM(CASE WHEN salary BETWEEN 50000 AND 99999 THEN 1 ELSE 0 END) AS band_mid,
    SUM(CASE WHEN salary >= 100000 THEN 1 ELSE 0 END) AS band_senior,
    ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department
ORDER BY department;

-- ── Weighted score calculation ──
SELECT
    product_id,
    COUNT(*) AS review_count,
    ROUND(
        SUM(CASE rating
            WHEN 5 THEN 5.0
            WHEN 4 THEN 4.0
            WHEN 3 THEN 3.0
            WHEN 2 THEN 2.0
            ELSE   1.0
        END) / COUNT(*), 2
    ) AS weighted_avg_rating,
    -- percentage breakdown
    ROUND(100.0 * SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) / COUNT(*), 1) AS five_star_pct
FROM reviews
GROUP BY product_id
HAVING COUNT(*) >= 10  -- only products with enough reviews
ORDER BY weighted_avg_rating DESC;


-- ============================================================
-- 2. MULTI-TABLE CTEs
-- ============================================================

-- ── Customer lifetime value with segmentation ──
WITH
order_stats AS (
    SELECT
        customer_id,
        COUNT(*)                    AS order_count,
        SUM(amount)                 AS lifetime_value,
        MIN(created_at)             AS first_order,
        MAX(created_at)             AS last_order,
        AVG(amount)                 AS avg_order_value
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
customer_segments AS (
    SELECT
        customer_id,
        lifetime_value,
        order_count,
        CASE
            WHEN lifetime_value >= 10000 THEN 'VIP'
            WHEN lifetime_value >= 2000  THEN 'Regular'
            ELSE                              'Occasional'
        END AS segment,
        EXTRACT(DAY FROM (last_order - first_order)) AS active_days
    FROM order_stats
),
segment_summary AS (
    SELECT
        segment,
        COUNT(*)                        AS customer_count,
        ROUND(AVG(lifetime_value), 2)   AS avg_ltv,
        ROUND(AVG(order_count), 1)      AS avg_orders,
        SUM(lifetime_value)             AS total_revenue
    FROM customer_segments
    GROUP BY segment
)
SELECT
    segment,
    customer_count,
    avg_ltv,
    avg_orders,
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) AS revenue_share_pct
FROM segment_summary
ORDER BY avg_ltv DESC;


-- ── Find products never ordered in the last 90 days ──
WITH recent_orders AS (
    SELECT DISTINCT product_id
    FROM orders
    WHERE created_at >= NOW() - INTERVAL '90 days'
      AND status != 'cancelled'
),
inactive_products AS (
    SELECT p.id, p.name, p.category, p.price
    FROM products p
    LEFT JOIN recent_orders ro ON p.id = ro.product_id
    WHERE ro.product_id IS NULL   -- anti-join: not in recent orders
)
SELECT * FROM inactive_products ORDER BY price DESC;


-- ============================================================
-- 3. RECURSIVE CTEs
-- ============================================================

-- ── Org chart: find all direct and indirect reports under manager id=5 ──
WITH RECURSIVE direct_reports AS (
    -- Anchor: the starting manager
    SELECT
        id, name, manager_id,
        0          AS depth,
        name::TEXT AS path
    FROM employees
    WHERE id = 5

    UNION ALL

    -- Recursive: each employee reporting to someone already in the CTE
    SELECT
        e.id, e.name, e.manager_id,
        dr.depth + 1,
        dr.path || ' -> ' || e.name
    FROM employees e
    JOIN direct_reports dr ON e.manager_id = dr.id
)
SELECT depth, name, path
FROM direct_reports
ORDER BY depth, name;


-- ── Category tree: full path for each category ──
WITH RECURSIVE category_path AS (
    -- Anchor: top-level categories (no parent)
    SELECT
        id, name, parent_id,
        name::TEXT AS full_path,
        1          AS level
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT
        c.id, c.name, c.parent_id,
        cp.full_path || ' > ' || c.name,
        cp.level + 1
    FROM categories c
    JOIN category_path cp ON c.parent_id = cp.id
)
SELECT level, full_path, id
FROM category_path
ORDER BY full_path;


-- ── Generate a date series (useful for filling gaps in reports) ──
WITH RECURSIVE date_series AS (
    SELECT '2024-01-01'::DATE AS dt

    UNION ALL

    SELECT (dt + INTERVAL '1 day')::DATE
    FROM date_series
    WHERE dt < '2024-12-31'
)
-- Left join to fill gaps with 0 revenue on days with no orders
SELECT
    ds.dt,
    COALESCE(SUM(o.amount), 0) AS daily_revenue
FROM date_series ds
LEFT JOIN orders o ON o.created_at::DATE = ds.dt AND o.status = 'completed'
GROUP BY ds.dt
ORDER BY ds.dt;


-- ============================================================
-- 4. WINDOW FUNCTIONS — RUNNING TOTALS, MOVING AVG, PERCENTILE
-- ============================================================

-- ── Running total + running count + running average ──
SELECT
    created_at::DATE        AS order_date,
    amount,
    SUM(amount) OVER (
        ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                       AS running_total,
    COUNT(*) OVER (
        ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                       AS running_count,
    AVG(amount) OVER (
        ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                       AS running_avg
FROM orders
WHERE status = 'completed'
ORDER BY created_at;


-- ── 7-day moving average of daily revenue ──
WITH daily AS (
    SELECT
        created_at::DATE AS day,
        SUM(amount)      AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY 1
)
SELECT
    day,
    revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS ma_7d,
    ROUND(AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d
FROM daily
ORDER BY day;


-- ── Salary percentile within department ──
SELECT
    name, department, salary,
    ROUND(
        PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) * 100
    , 1) AS percentile_in_dept,
    NTILE(4) OVER (PARTITION BY department ORDER BY salary) AS quartile,
    CUME_DIST() OVER (PARTITION BY department ORDER BY salary) AS cumulative_dist
FROM employees;


-- ── Top N per group using ROW_NUMBER ──
SELECT * FROM (
    SELECT
        department, name, salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn <= 3;   -- top 3 earners per department


-- ── Month-over-month growth with LAG ──
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', created_at) AS month,
        SUM(amount) AS revenue
    FROM orders WHERE status = 'completed'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month)     AS prev_month,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
              / NULLIF(LAG(revenue) OVER (ORDER BY month), 0)
    , 2)                                   AS mom_growth_pct
FROM monthly
ORDER BY month;


-- ============================================================
-- 5. PIVOT-STYLE QUERIES
-- ============================================================

-- ── Monthly revenue by category (manual PIVOT with CASE) ──
SELECT
    category,
    ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM o.created_at) = 1  THEN o.amount ELSE 0 END), 2) AS jan,
    ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM o.created_at) = 2  THEN o.amount ELSE 0 END), 2) AS feb,
    ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM o.created_at) = 3  THEN o.amount ELSE 0 END), 2) AS mar,
    ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM o.created_at) = 4  THEN o.amount ELSE 0 END), 2) AS apr,
    ROUND(SUM(CASE WHEN EXTRACT(MONTH FROM o.created_at) = 12 THEN o.amount ELSE 0 END), 2) AS dec,
    ROUND(SUM(o.amount), 2) AS total
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE EXTRACT(YEAR FROM o.created_at) = 2024
  AND o.status = 'completed'
GROUP BY category
ORDER BY total DESC;


-- ── Transpose via crosstab (PostgreSQL tablefunc extension) ──
-- Requires: CREATE EXTENSION IF NOT EXISTS tablefunc;
/*
SELECT *
FROM crosstab(
    'SELECT category, TO_CHAR(created_at, ''Mon''), SUM(amount)
     FROM orders JOIN products ON orders.product_id = products.id
     WHERE status = ''completed''
     GROUP BY 1, 2 ORDER BY 1, 2',
    'SELECT DISTINCT TO_CHAR(created_at, ''Mon'') FROM orders ORDER BY 1'
) AS ct(category TEXT, "Jan" NUMERIC, "Feb" NUMERIC, "Mar" NUMERIC);
*/


-- ============================================================
-- 6. STRING MANIPULATION
-- ============================================================

SELECT
    -- Concatenation
    first_name || ' ' || last_name          AS full_name,
    CONCAT(first_name, ' ', last_name)      AS full_name_v2,  -- NULL-safe

    -- Case
    UPPER(email)                            AS email_upper,
    LOWER(email)                            AS email_lower,
    INITCAP(name)                           AS title_case,     -- 'john doe' → 'John Doe'

    -- Trimming
    TRIM(BOTH ' ' FROM name)                AS trimmed,
    LTRIM(name, ' '),                        -- left trim
    RTRIM(name, ' '),                        -- right trim

    -- Length and position
    LENGTH(email)                           AS email_len,
    POSITION('@' IN email)                  AS at_pos,
    STRPOS(email, '@')                      AS at_pos_v2,

    -- Substring extraction
    SUBSTRING(email FROM 1 FOR STRPOS(email,'@')-1)  AS username_from_email,
    SPLIT_PART(email, '@', 2)                         AS domain,  -- 'gmail.com'

    -- Replace and Regex
    REPLACE(phone, '-', '')                 AS phone_digits_only,
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_clean,  -- strip all non-digits
    REGEXP_MATCHES(description, '\d+', 'g') AS numbers_found,

    -- Padding
    LPAD(CAST(id AS TEXT), 6, '0')          AS zero_padded_id,  -- '000042'

    -- Repeat and reverse
    REPEAT('*', LENGTH(card_last4) - 4) || SUBSTRING(card_last4 FROM 5) AS masked_card,
    REVERSE(name)                           AS reversed_name

FROM users;


-- ── Full name search with similarity (fuzzy) ──
-- Requires: CREATE EXTENSION pg_trgm;
SELECT name, similarity(name, 'John Smyth') AS sim
FROM users
WHERE name % 'John Smyth'    -- trigram match
ORDER BY sim DESC
LIMIT 10;


-- ============================================================
-- 7. DATE / TIME OPERATIONS
-- ============================================================

SELECT
    -- Current timestamps
    NOW()                               AS now_with_tz,
    CURRENT_TIMESTAMP                   AS current_ts,
    CURRENT_DATE                        AS today,

    -- Extraction
    EXTRACT(YEAR  FROM hire_date)       AS hire_year,
    EXTRACT(MONTH FROM hire_date)       AS hire_month,
    EXTRACT(DOW   FROM hire_date)       AS day_of_week,   -- 0=Sunday
    EXTRACT(EPOCH FROM NOW())           AS unix_timestamp,

    -- Truncation
    DATE_TRUNC('month', hire_date)      AS start_of_month,
    DATE_TRUNC('week',  hire_date)      AS start_of_week,
    DATE_TRUNC('year',  hire_date)      AS start_of_year,

    -- Arithmetic
    hire_date + INTERVAL '90 days'      AS probation_end,
    NOW() - hire_date                   AS tenure_interval,
    EXTRACT(DAY FROM (NOW() - hire_date::TIMESTAMPTZ)) AS tenure_days,
    AGE(NOW(), hire_date::TIMESTAMPTZ)  AS tenure_human,   -- '3 years 2 mons 5 days'

    -- Formatting
    TO_CHAR(hire_date, 'DD Mon YYYY')   AS formatted_date,  -- '15 Mar 2022'
    TO_CHAR(hire_date, 'YYYY-MM-DD')    AS iso_date,
    TO_CHAR(NOW(), 'HH24:MI:SS')        AS time_only,

    -- Parsing
    TO_DATE('15/03/2022', 'DD/MM/YYYY') AS parsed_date,
    TO_TIMESTAMP('2022-03-15 14:30', 'YYYY-MM-DD HH24:MI') AS parsed_ts

FROM employees;


-- ── Business days between two dates (simple approximation) ──
SELECT
    start_date, end_date,
    (end_date - start_date)  -- total days
    - 2 * ((end_date - start_date) / 7)  -- subtract weekends
    AS approx_business_days
FROM projects;


-- ── Records in the last N days/hours ──
SELECT * FROM orders WHERE created_at >= NOW() - INTERVAL '7 days';
SELECT * FROM orders WHERE created_at >= NOW() - INTERVAL '1 hour';
SELECT * FROM orders
WHERE created_at BETWEEN DATE_TRUNC('month', NOW()) AND NOW();  -- this month


-- ============================================================
-- 8. JSON OPERATIONS IN POSTGRESQL
-- ============================================================

-- Schema: products.metadata is JSONB
-- Example: {"brand": "Nike", "sizes": [8,9,10], "specs": {"weight": 250, "color": "red"}}

SELECT
    id,
    name,
    -- Access JSON field (returns JSONB)
    metadata -> 'brand'                     AS brand_json,       -- "Nike" (with quotes)
    -- Access JSON field as text
    metadata ->> 'brand'                    AS brand_text,       -- Nike (without quotes)
    -- Nested access
    metadata -> 'specs' ->> 'color'         AS color,
    -- Array element
    metadata -> 'sizes' -> 0               AS first_size,        -- 8
    -- Array length
    jsonb_array_length(metadata -> 'sizes') AS size_count,

    -- Extract all keys
    jsonb_object_keys(metadata)             AS keys              -- returns set of text

FROM products
WHERE metadata IS NOT NULL;


-- ── Filter on JSON field ──
SELECT * FROM products
WHERE metadata ->> 'brand' = 'Nike'
  AND (metadata -> 'specs' ->> 'weight')::INT > 200;

-- ── JSON containment operator @> ──
SELECT * FROM products
WHERE metadata @> '{"brand": "Nike"}';  -- faster with GIN index

-- ── JSON path query (PostgreSQL 12+) ──
SELECT * FROM products
WHERE metadata @? '$.sizes[*] ? (@ > 9)';  -- has any size > 9

-- ── Aggregating into JSON ──
SELECT
    customer_id,
    jsonb_agg(
        jsonb_build_object('order_id', id, 'amount', amount, 'status', status)
        ORDER BY created_at
    ) AS orders_json
FROM orders
GROUP BY customer_id;

-- ── jsonb_set: update a nested field ──
UPDATE products
SET metadata = jsonb_set(metadata, '{specs,color}', '"blue"', false)
WHERE id = 42;

-- ── Expand JSONB array into rows ──
SELECT id, jsonb_array_elements_text(metadata -> 'sizes')::INT AS size
FROM products
WHERE metadata ? 'sizes';


-- ── Build GIN index for fast JSON queries ──
CREATE INDEX idx_products_metadata ON products USING GIN(metadata);
CREATE INDEX idx_products_brand    ON products((metadata ->> 'brand'));


-- ============================================================
-- 9. FULL-TEXT SEARCH IN POSTGRESQL
-- ============================================================

-- ── Basic full-text search ──
SELECT id, name, description
FROM products
WHERE to_tsvector('english', name || ' ' || COALESCE(description, ''))
      @@ to_tsquery('english', 'running & shoes');

-- ── With relevance ranking (ts_rank) ──
SELECT
    id, name,
    ts_rank(
        to_tsvector('english', name || ' ' || COALESCE(description, '')),
        to_tsquery('english', 'lightweight & running')
    ) AS rank
FROM products
WHERE to_tsvector('english', name || ' ' || COALESCE(description, ''))
      @@ to_tsquery('english', 'lightweight & running')
ORDER BY rank DESC
LIMIT 20;

-- ── Store tsvector in generated column for performance ──
ALTER TABLE products
ADD COLUMN search_vector TSVECTOR
    GENERATED ALWAYS AS (
        to_tsvector('english', COALESCE(name,'') || ' ' || COALESCE(description,''))
    ) STORED;

CREATE INDEX idx_products_fts ON products USING GIN(search_vector);

-- Now query uses the index:
SELECT id, name FROM products
WHERE search_vector @@ plainto_tsquery('english', 'trail running shoes');

-- ── Phrase search and OR ──
SELECT * FROM articles
WHERE search_vector @@ to_tsquery('english', 'machine <-> learning');  -- exact phrase
SELECT * FROM articles
WHERE search_vector @@ to_tsquery('english', 'python | javascript');   -- either word

-- ── Highlighting matches ──
SELECT
    id,
    ts_headline(
        'english', description,
        to_tsquery('english', 'running & shoes'),
        'StartSel=<b>, StopSel=</b>, MaxWords=30, MinWords=15'
    ) AS highlighted
FROM products
WHERE search_vector @@ to_tsquery('english', 'running & shoes');


-- ============================================================
-- 10. TABLE PARTITIONING
-- ============================================================

-- ── Range partitioning: partition orders by year ──
CREATE TABLE orders_partitioned (
    id          BIGSERIAL,
    customer_id INT,
    amount      NUMERIC(10,2),
    status      VARCHAR(20),
    created_at  TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions for each year (or month for high-volume tables)
CREATE TABLE orders_2023 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE orders_2025 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indexes on partition key are automatically propagated to sub-tables
CREATE INDEX ON orders_partitioned(created_at);

-- ── List partitioning: by region ──
CREATE TABLE sales (
    id     BIGSERIAL,
    region VARCHAR(20) NOT NULL,
    amount NUMERIC
) PARTITION BY LIST (region);

CREATE TABLE sales_us   PARTITION OF sales FOR VALUES IN ('US', 'CA');
CREATE TABLE sales_eu   PARTITION OF sales FOR VALUES IN ('UK', 'DE', 'FR');
CREATE TABLE sales_apac PARTITION OF sales FOR VALUES IN ('AU', 'JP', 'SG');

-- ── Hash partitioning: distribute by customer_id ──
CREATE TABLE events (
    id          BIGSERIAL,
    customer_id INT NOT NULL,
    event_type  VARCHAR(50),
    occurred_at TIMESTAMPTZ
) PARTITION BY HASH (customer_id);

CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);


-- ============================================================
-- 11. EXPLAIN ANALYZE — READING QUERY PLANS
-- ============================================================

-- ── Example 1: Spot a sequential scan and fix it ──

-- BAD: no index on status, full table scan
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
/*
Seq Scan on orders  (cost=0.00..8450.00 rows=423 width=72)
                    (actual time=0.021..89.432 rows=418 loops=1)
  Filter: ((status)::text = 'pending'::text)
  Rows Removed by Filter: 41582
Planning Time: 0.5 ms
Execution Time: 89.6 ms
*/

-- FIX: create a partial index
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';  -- partial index: only pending rows

-- AFTER: uses Index Scan
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at;
/*
Index Scan using idx_orders_pending on orders
  (cost=0.29..42.30 rows=418 width=72)
  (actual time=0.038..1.241 rows=418 loops=1)
Execution Time: 1.5 ms   ← 60x faster
*/


-- ── Example 2: Hash Join vs Nested Loop ──
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT e.name, d.dept_name
FROM employees e
JOIN departments d ON e.dept_id = d.id
WHERE d.location = 'New York';
/*
Hash Join  (cost=...) (actual time=2.1..45.2 rows=1200 loops=1)
  Hash Cond: (e.dept_id = d.id)
  Buffers: shared hit=890 read=12   ← "read=12" means disk reads; ideally 0
  -> Seq Scan on employees  ...
  -> Hash  ...
       -> Seq Scan on departments  (Filter: location='New York')
*/
-- Fix: index departments(location) and departments(id)


-- ── Example 3: Forcing index use / disable seq scan (for debugging) ──
SET enable_seqscan = OFF;    -- force planner to use index (testing only!)
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;
SET enable_seqscan = ON;     -- restore default


-- ── Example 4: Analyzing a slow aggregation ──
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, SUM(amount)
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY customer_id
HAVING SUM(amount) > 1000;
/*
HashAggregate  (cost=3420.00..3821.00 rows=2340 width=12)
               (actual time=234.1..312.4 rows=2189 loops=1)
  Filter: (sum(amount) > 1000)
  -> Index Scan using idx_orders_date on orders
       (actual time=0.048..98.7 rows=84321 loops=1)
Execution Time: 321 ms
*/
-- HashAggregate with many rows → consider covering index (customer_id, created_at, amount)


-- ── Useful EXPLAIN idioms ──
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT * FROM orders WHERE id = 1;
-- Paste JSON output into explain.dalibo.com for visual plan

-- Quick check: is query using index?
EXPLAIN SELECT * FROM orders WHERE email = 'test@example.com';
-- Look for "Index Scan" vs "Seq Scan"

-- Check table statistics are fresh
ANALYZE orders;         -- update column statistics
VACUUM ANALYZE orders;  -- reclaim space + update statistics
