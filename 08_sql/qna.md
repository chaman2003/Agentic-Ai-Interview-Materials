# SQL Q&A — Interview Ready (Comprehensive)

---

## SQL BASICS

**Q: What is the difference between WHERE and HAVING?**
A:
- `WHERE` filters individual rows BEFORE grouping
- `HAVING` filters groups AFTER `GROUP BY`
- You cannot use aggregate functions in WHERE; you can in HAVING
```sql
SELECT dept, COUNT(*) AS cnt, AVG(salary) AS avg_sal
FROM employees
WHERE salary > 30000          -- filter rows BEFORE grouping
GROUP BY dept
HAVING COUNT(*) > 5           -- filter groups AFTER grouping
   AND AVG(salary) > 60000;
```

**Q: What is the difference between DELETE, TRUNCATE, and DROP?**
A:
- `DELETE` — removes rows one by one, WHERE clause supported, can be rolled back, triggers fire, slow on large tables
- `TRUNCATE` — removes ALL rows at once, no WHERE clause, DDL operation (auto-commits in most DBs), extremely fast, resets identity/serial columns
- `DROP` — removes the entire table structure AND data permanently
```sql
DELETE FROM users WHERE created_at < '2020-01-01';  -- logged, rollback-able
TRUNCATE TABLE session_logs;                         -- wipes all rows fast
DROP TABLE temp_staging;                             -- table is gone
```

**Q: What is the difference between CHAR, VARCHAR, and TEXT?**
A:
- `CHAR(n)` — fixed-length, always uses n bytes, pads with spaces. Best for fixed codes (ISO country codes, MD5 hashes).
- `VARCHAR(n)` — variable-length up to n. Uses only as many bytes as needed.
- `TEXT` — unlimited variable-length string. No length limit. Slight overhead for very short strings.

**Q: What is NULL and how does it behave in SQL?**
A: NULL means "unknown" or "missing". Key behaviors:
- `NULL = NULL` is FALSE — use `IS NULL` or `IS NOT NULL`
- Any arithmetic with NULL returns NULL: `5 + NULL = NULL`
- Aggregate functions (SUM, COUNT, AVG) ignore NULLs — except `COUNT(*)`
- `COALESCE(a, b, c)` returns the first non-NULL value
```sql
SELECT COALESCE(phone, email, 'no contact') AS contact FROM users;
SELECT * FROM orders WHERE shipped_at IS NULL;    -- not: = NULL
```

**Q: What is the difference between UNION and UNION ALL?**
A:
- `UNION` removes duplicate rows (performs a DISTINCT operation — extra sort/hash step)
- `UNION ALL` keeps ALL rows including duplicates (faster, use when duplicates don't matter)
```sql
SELECT user_id FROM orders_2023
UNION ALL                          -- faster: keeps duplicates
SELECT user_id FROM orders_2024;

SELECT city FROM customers
UNION                              -- deduplicates the result
SELECT city FROM suppliers;
```

**Q: What is a PRIMARY KEY vs UNIQUE constraint?**
A:
- `PRIMARY KEY` — uniquely identifies each row, cannot be NULL, only ONE per table, automatically creates a clustered index
- `UNIQUE` — enforces uniqueness, CAN contain one NULL (in most DBs), multiple per table
```sql
CREATE TABLE users (
    id        SERIAL PRIMARY KEY,          -- not null, unique, clustered index
    email     VARCHAR(255) UNIQUE,         -- unique but nullable
    username  VARCHAR(100) UNIQUE NOT NULL -- unique and not null
);
```

**Q: What is a FOREIGN KEY and what does ON DELETE CASCADE do?**
A: A FOREIGN KEY references the PRIMARY KEY of another table, enforcing referential integrity. `ON DELETE CASCADE` automatically deletes child rows when the parent is deleted.
```sql
CREATE TABLE orders (
    id      SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    -- deleting a user auto-deletes all their orders
    product_id INT REFERENCES products(id) ON DELETE RESTRICT
    -- RESTRICT prevents deleting a product if orders reference it
);
```

**Q: What are constraints and what types exist?**
A: Rules enforced at the DB level:
- `NOT NULL` — column must have a value
- `UNIQUE` — all values must be distinct
- `PRIMARY KEY` — NOT NULL + UNIQUE, identifies rows
- `FOREIGN KEY` — references another table
- `CHECK` — custom condition: `CHECK (age >= 18)`, `CHECK (status IN ('active', 'inactive'))`
- `DEFAULT` — value used when none provided: `DEFAULT NOW()`

**Q: What is the difference between INNER JOIN and LEFT JOIN with a concrete example?**
A:
```sql
-- Tables: customers (1,2,3) and orders (customer 1 has 2 orders, customer 2 has 1, customer 3 has none)

-- INNER JOIN: only customers WITH orders
SELECT c.name, o.amount
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id;
-- Returns: 3 rows (customers 1 and 2 only)

-- LEFT JOIN: ALL customers, NULL for those without orders
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;
-- Returns: 4 rows (customer 3 gets NULL for amount)

-- Find customers with NO orders (anti-join pattern)
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;
```

**Q: What is the difference between BETWEEN, IN, and LIKE?**
A:
- `BETWEEN a AND b` — inclusive range check (same as `>= a AND <= b`)
- `IN (list)` — matches any value in list. `IN (subquery)` also valid
- `LIKE` — pattern matching: `%` = any chars, `_` = single char. Case-insensitive in some DBs
```sql
WHERE age BETWEEN 18 AND 65
WHERE status IN ('active', 'pending', 'processing')
WHERE email LIKE '%@gmail.com'     -- ends with
WHERE code LIKE 'A___'             -- starts with A, exactly 4 chars
WHERE name ILIKE '%smith%'         -- PostgreSQL case-insensitive
```

**Q: What is the ORDER BY clause and how does NULLS FIRST/LAST work?**
A: `ORDER BY` sorts the result. Default is ASC. Multiple columns: sorts by first, ties broken by second.
```sql
SELECT * FROM employees
ORDER BY department ASC, salary DESC;   -- dept alphabetically, highest salary first

-- NULL sorting (PostgreSQL)
ORDER BY last_login DESC NULLS LAST;    -- active users first, never-logged-in at end
ORDER BY priority ASC NULLS FIRST;     -- unset priorities first
```

**Q: What is LIMIT and OFFSET and what are the performance issues?**
A: `LIMIT n` returns at most n rows. `OFFSET n` skips first n rows. Used for pagination.
Problem: `OFFSET 10000` still scans 10,000 rows then discards them — very slow on large tables.
```sql
-- Standard pagination (slow for large offsets)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 980;

-- Keyset/cursor pagination (much faster)
SELECT * FROM products
WHERE id > 980          -- last seen id from previous page
ORDER BY id
LIMIT 20;
```

**Q: What is the difference between COUNT(*), COUNT(col), and COUNT(DISTINCT col)?**
A:
- `COUNT(*)` — counts ALL rows including NULLs
- `COUNT(col)` — counts rows where col is NOT NULL
- `COUNT(DISTINCT col)` — counts unique non-NULL values
```sql
SELECT
    COUNT(*)                AS total_rows,
    COUNT(email)            AS rows_with_email,    -- excludes NULLs
    COUNT(DISTINCT country) AS unique_countries
FROM users;
```

**Q: What are aggregate functions and which ignore NULLs?**
A: ALL standard aggregate functions (SUM, AVG, MIN, MAX, COUNT(col)) ignore NULL values. Only `COUNT(*)` includes rows with NULLs.
```sql
SELECT
    SUM(salary)       AS total_payroll,
    AVG(salary)       AS avg_salary,        -- NULL salaries excluded from average
    MIN(hire_date)    AS earliest_hire,
    MAX(salary)       AS highest_salary,
    STDDEV(salary)    AS salary_stddev,     -- standard deviation
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median_salary
FROM employees;
```

**Q: What is a self-join and when do you use it?**
A: Joining a table to itself. Used for hierarchical data (employees and their managers) or comparing rows within the same table.
```sql
-- Find each employee and their manager's name
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find all pairs of employees in the same department (no duplicates)
SELECT a.name, b.name, a.department
FROM employees a
JOIN employees b ON a.department = b.department AND a.id < b.id;
```

**Q: What is a CROSS JOIN?**
A: Produces the Cartesian product of two tables — every row from table A combined with every row from table B. Rarely used intentionally, but useful for generating combinations.
```sql
-- Generate all size-color combinations for a product
SELECT sizes.size, colors.color
FROM sizes CROSS JOIN colors;
-- 3 sizes × 4 colors = 12 rows
```

**Q: What is the CASE expression?**
A: SQL's if-else. Can be used anywhere an expression is valid (SELECT, WHERE, ORDER BY, GROUP BY).
```sql
-- Simple CASE
SELECT name,
    CASE status
        WHEN 'A' THEN 'Active'
        WHEN 'I' THEN 'Inactive'
        ELSE 'Unknown'
    END AS status_label
FROM users;

-- Searched CASE (more flexible)
SELECT name, salary,
    CASE
        WHEN salary < 40000  THEN 'Junior'
        WHEN salary < 80000  THEN 'Mid-level'
        WHEN salary < 120000 THEN 'Senior'
        ELSE 'Executive'
    END AS level
FROM employees;
```

**Q: What is the difference between EXISTS and IN?**
A:
- `IN` — evaluates the full subquery result set, then checks membership. Can be slow if the subquery returns many rows. Fails if subquery has NULLs (NULL != anything).
- `EXISTS` — stops as soon as it finds ONE matching row (short-circuit). Better for large datasets. Not affected by NULLs.
```sql
-- IN: gets all dept_ids then checks membership
SELECT name FROM employees WHERE dept_id IN (SELECT id FROM departments WHERE active = true);

-- EXISTS: stops at first match per employee row
SELECT e.name FROM employees e
WHERE EXISTS (SELECT 1 FROM departments d WHERE d.id = e.dept_id AND d.active = true);
```

**Q: What is a subquery vs a derived table vs a CTE?**
A:
- **Subquery** — inline query inside another query. Can go in SELECT, FROM, WHERE clauses.
- **Derived table** — subquery in the FROM clause given an alias. Computed once.
- **CTE** — named subquery defined with `WITH`. Readable, reusable within the same query. Some DBs materialize it (compute once), others inline it.
```sql
-- Subquery in WHERE
SELECT name FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);

-- Derived table in FROM
SELECT dept, avg_sal FROM (SELECT dept, AVG(salary) AS avg_sal FROM employees GROUP BY dept) AS dept_stats WHERE avg_sal > 70000;

-- CTE
WITH dept_stats AS (SELECT dept, AVG(salary) AS avg_sal FROM employees GROUP BY dept)
SELECT dept, avg_sal FROM dept_stats WHERE avg_sal > 70000;
```

**Q: What is COALESCE vs NULLIF vs ISNULL?**
A:
- `COALESCE(a, b, c)` — returns first non-NULL: portable, standard SQL
- `NULLIF(a, b)` — returns NULL if a equals b, otherwise returns a. Useful to avoid division by zero
- `ISNULL(a, b)` — SQL Server specific, equivalent to `COALESCE(a, b)` with two args
```sql
SELECT COALESCE(nickname, first_name, 'Anonymous') AS display_name FROM users;
SELECT total / NULLIF(count, 0) AS avg FROM stats;  -- avoids divide-by-zero
```

---

## JOIN TYPES

**Q: Explain all JOIN types with examples.**
A:
```sql
-- INNER JOIN — intersection, rows matching in BOTH tables
SELECT e.name, d.dept_name FROM employees e INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT JOIN — all rows from LEFT, NULLs for non-matching RIGHT
SELECT e.name, d.dept_name FROM employees e LEFT JOIN departments d ON e.dept_id = d.id;

-- RIGHT JOIN — all rows from RIGHT, NULLs for non-matching LEFT (rarely used; flip LEFT instead)
SELECT e.name, d.dept_name FROM employees e RIGHT JOIN departments d ON e.dept_id = d.id;

-- FULL OUTER JOIN — all rows from both, NULLs on either side when no match
SELECT e.name, d.dept_name FROM employees e FULL OUTER JOIN departments d ON e.dept_id = d.id;

-- CROSS JOIN — cartesian product, every combination
SELECT p.product, c.color FROM products p CROSS JOIN colors c;

-- SELF JOIN — join table to itself
SELECT e.name AS emp, m.name AS mgr FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;
```

**Q: What is an anti-join and how do you write one?**
A: Returns rows in table A that have NO matching rows in table B. Two patterns:
```sql
-- Pattern 1: LEFT JOIN with IS NULL (readable)
SELECT c.* FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;    -- customers who never ordered

-- Pattern 2: NOT EXISTS (often faster)
SELECT c.* FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- Pattern 3: NOT IN (avoid if subquery can return NULLs)
SELECT * FROM customers WHERE id NOT IN (SELECT customer_id FROM orders WHERE customer_id IS NOT NULL);
```

---

## WINDOW FUNCTIONS

**Q: What are ROW_NUMBER, RANK, and DENSE_RANK? When do you use each?**
A:
```sql
SELECT name, department, salary,
    ROW_NUMBER()  OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    -- Always unique: 1, 2, 3, 4 — no ties
    RANK()        OVER (PARTITION BY department ORDER BY salary DESC) AS rnk,
    -- Ties get same rank, gaps created: 1, 1, 3, 4 (skips 2)
    DENSE_RANK()  OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rnk
    -- Ties get same rank, no gaps: 1, 1, 2, 3
FROM employees;

-- Use ROW_NUMBER to get exactly TOP-N per group (no ties)
-- Use RANK if ties should both qualify for top spots
-- Use DENSE_RANK for medal-style ranking where gaps don't make sense
```

**Q: What are LAG and LEAD window functions?**
A: Access a value from a previous (LAG) or following (LEAD) row without a self-join.
```sql
SELECT
    date,
    revenue,
    LAG(revenue, 1, 0) OVER (ORDER BY date)  AS prev_day_revenue,
    LEAD(revenue, 1, 0) OVER (ORDER BY date) AS next_day_revenue,
    revenue - LAG(revenue) OVER (ORDER BY date) AS day_over_day_change
FROM daily_sales;

-- Month-over-month growth rate
SELECT month, revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) /
          NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS growth_pct
FROM monthly_revenue;
```

**Q: What is NTILE? What are FIRST_VALUE and LAST_VALUE?**
A:
```sql
-- NTILE(n): divides rows into n equal buckets
SELECT name, salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile   -- 1=bottom 25%, 4=top 25%
FROM employees;

-- FIRST_VALUE / LAST_VALUE: get first/last value in the window frame
SELECT name, department, salary,
    FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary DESC) AS dept_max,
    LAST_VALUE(salary)  OVER (
        PARTITION BY department ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS dept_min   -- NOTE: requires full frame specification
FROM employees;
```

**Q: What are running totals and moving averages with window functions?**
A:
```sql
-- Running total (cumulative sum)
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;

-- 7-day moving average
SELECT date, revenue,
    AVG(revenue) OVER (ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM daily_sales;

-- Percentage of total within group
SELECT department, name, salary,
    ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY department), 2) AS pct_of_dept
FROM employees;
```

---

## CTEs

**Q: What is a CTE and how does it differ from a subquery?**
A: A Common Table Expression (CTE) is a named temporary result set defined at the top of a query using `WITH`. Benefits over subqueries: readable, reusable within the same query, can reference previous CTEs.
```sql
-- Multiple CTEs: each can reference previous ones
WITH
active_users AS (
    SELECT id, name, email FROM users WHERE status = 'active'
),
user_orders AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(total) AS lifetime_value
    FROM orders
    GROUP BY user_id
),
vip_users AS (
    SELECT u.name, u.email, uo.lifetime_value
    FROM active_users u
    JOIN user_orders uo ON u.id = uo.user_id
    WHERE uo.lifetime_value > 10000
)
SELECT * FROM vip_users ORDER BY lifetime_value DESC;
```

**Q: What is a recursive CTE and when do you use it?**
A: A CTE that references itself. Used for hierarchical data (org charts, category trees, paths in graphs). Structure: anchor member UNION ALL recursive member.
```sql
-- Traverse org chart: find all reports under a manager
WITH RECURSIVE org_tree AS (
    -- Anchor: start with the top-level manager
    SELECT id, name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL    -- CEO / root

    UNION ALL

    -- Recursive: find each employee's direct reports
    SELECT e.id, e.name, e.manager_id, ot.level + 1
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT level, name FROM org_tree ORDER BY level, name;

-- Generate a sequence of dates
WITH RECURSIVE date_series AS (
    SELECT '2024-01-01'::date AS dt
    UNION ALL
    SELECT dt + 1 FROM date_series WHERE dt < '2024-01-31'
)
SELECT dt FROM date_series;
```

---

## INDEXES

**Q: What is an index and what are the trade-offs?**
A: A separate data structure (typically a B-tree) that the DB maintains to speed up lookups on a column. Trade-offs:
- FASTER reads (queries that filter/sort/join on indexed columns)
- SLOWER writes (INSERT/UPDATE/DELETE must also update the index)
- MORE storage
- Too many indexes hurts write-heavy workloads

**Q: What are the different types of indexes?**
A:
```sql
-- B-tree (default): good for equality and range queries
CREATE INDEX idx_users_email ON users(email);

-- UNIQUE index: enforces uniqueness + speeds up lookup
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index: covers multiple columns
-- Order matters! (a, b) covers queries on (a) and (a, b) but NOT (b) alone
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index: only indexes rows matching a condition (smaller, faster)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Expression index: index on a function result
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- Full-text search index (PostgreSQL)
CREATE INDEX idx_products_fts ON products USING GIN(to_tsvector('english', description));

-- Hash index: exact equality only, no range queries
CREATE INDEX idx_session_token ON sessions USING HASH(token);
```

**Q: What is the difference between a clustered and non-clustered index?**
A:
- **Clustered index** — the actual table rows are physically stored in the index order. Only ONE per table. In PostgreSQL, the PRIMARY KEY creates a heap table (not clustered by default); use `CLUSTER` command to reorder.
- **Non-clustered index** — a separate structure with pointers to the actual row locations. Multiple per table.

**Q: When should you NOT add an index?**
A:
- Small tables (full scan is faster than index + lookup)
- Columns with very low cardinality (e.g., a boolean column — index is rarely selective enough)
- Write-heavy tables where index maintenance overhead outweighs read gains
- Columns rarely used in WHERE/JOIN/ORDER BY clauses
- Temporary or staging tables

---

## TRANSACTIONS AND ISOLATION LEVELS

**Q: What are ACID properties?**
A:
- **Atomicity** — all operations in a transaction succeed or ALL are rolled back. No partial state.
- **Consistency** — a transaction brings the DB from one valid state to another (constraints, rules maintained).
- **Isolation** — concurrent transactions don't see each other's in-progress changes.
- **Durability** — once committed, data survives crashes (written to disk/WAL).
```sql
BEGIN;
    UPDATE accounts SET balance = balance - 500 WHERE id = 1;  -- debit
    UPDATE accounts SET balance = balance + 500 WHERE id = 2;  -- credit
COMMIT;    -- both changes become permanent
-- If second UPDATE fails, ROLLBACK undoes the first too (Atomicity)
```

**Q: What are the four isolation levels and what problems do they prevent?**
A:

| Isolation Level   | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------------------|------------|---------------------|--------------|
| READ UNCOMMITTED  | Possible   | Possible            | Possible     |
| READ COMMITTED    | Prevented  | Possible            | Possible     |
| REPEATABLE READ   | Prevented  | Prevented           | Possible     |
| SERIALIZABLE      | Prevented  | Prevented           | Prevented    |

- **Dirty Read** — reading uncommitted data from another transaction
- **Non-Repeatable Read** — reading same row twice, getting different values (another TX updated it)
- **Phantom Read** — re-running a range query returns different rows (another TX inserted)

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
    SELECT balance FROM accounts WHERE id = 1;  -- reads consistent snapshot
    -- ... other work ...
    SELECT balance FROM accounts WHERE id = 1;  -- same result even if others committed changes
COMMIT;
```

**Q: What is a deadlock and how do you prevent it?**
A: Deadlock occurs when two transactions each hold a lock the other needs, waiting forever. Prevention strategies:
1. Always acquire locks in the same order across all transactions
2. Keep transactions short — acquire locks late, release early
3. Use `SELECT ... FOR UPDATE SKIP LOCKED` for queue-like patterns
4. Set appropriate lock timeouts: `SET lock_timeout = '5s'`

---

## STORED PROCEDURES vs FUNCTIONS

**Q: What is the difference between a stored procedure and a function in PostgreSQL?**
A:
- **Function** — returns a value (scalar or table), can be used in SELECT expressions, cannot use COMMIT/ROLLBACK inside
- **Stored Procedure** (PostgreSQL 11+) — called with CALL, can manage transactions internally, cannot return values directly
```sql
-- Function: returns a value, used in expressions
CREATE OR REPLACE FUNCTION get_user_age(user_id INT) RETURNS INT AS $$
    SELECT EXTRACT(YEAR FROM AGE(birth_date)) FROM users WHERE id = user_id;
$$ LANGUAGE SQL;

SELECT name, get_user_age(id) AS age FROM users;

-- Stored Procedure: transaction control, no return value
CREATE OR REPLACE PROCEDURE transfer_funds(from_id INT, to_id INT, amount NUMERIC) AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount WHERE id = from_id;
    UPDATE accounts SET balance = balance + amount WHERE id = to_id;
    COMMIT;
END;
$$ LANGUAGE plpgsql;

CALL transfer_funds(1, 2, 500.00);
```

---

## VIEWS AND MATERIALIZED VIEWS

**Q: What is the difference between a view and a materialized view?**
A:
- **View** — a saved SQL query, not stored data. Every access re-runs the query. Always up to date. No storage overhead.
- **Materialized View** — the query result is physically stored. Requires explicit refresh. Much faster to query (especially for complex aggregations). Stale until refreshed.

```sql
-- Regular view: always fresh, always runs underlying query
CREATE VIEW active_user_summary AS
SELECT u.id, u.name, COUNT(o.id) AS order_count
FROM users u LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
GROUP BY u.id, u.name;

-- Materialized view: stored result, fast reads
CREATE MATERIALIZED VIEW monthly_revenue_summary AS
SELECT DATE_TRUNC('month', created_at) AS month,
       SUM(total) AS revenue,
       COUNT(*) AS order_count
FROM orders GROUP BY 1;

-- Refresh (can be scheduled via pg_cron or application)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue_summary;
-- CONCURRENTLY: allows reads during refresh (needs unique index on the view)
```

---

## QUERY OPTIMIZATION — EXPLAIN ANALYZE

**Q: How do you use EXPLAIN ANALYZE and what do you look for?**
A:
```sql
EXPLAIN ANALYZE
SELECT e.name, d.name AS dept
FROM employees e
JOIN departments d ON e.dept_id = d.id
WHERE e.salary > 80000;

-- Key things to look for:
-- 1. Seq Scan vs Index Scan (Seq on large tables = missing index)
-- 2. High "rows" estimate vs actual rows (bad statistics → run ANALYZE)
-- 3. Hash Join vs Nested Loop vs Merge Join
-- 4. High "actual time" nodes — where the bottleneck is
-- 5. "cost=X..Y" — estimated cost, not real time
-- 6. "actual time=X..Y rows=N loops=N" — real measured time
```

```sql
-- Useful EXPLAIN options
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
-- BUFFERS: shows cache hits vs disk reads
-- FORMAT JSON: machine-readable for tools like explain.dalibo.com
```

**Q: What are the common causes of slow queries?**
A:
1. Missing index — Sequential scan on large table
2. Wrong join order — small driving table is better
3. SELECT * — fetching unnecessary columns, prevents index-only scans
4. N+1 queries — executing a query per row instead of joining
5. Implicit type cast — `WHERE user_id = '123'` when user_id is INT prevents index use
6. Functions on indexed columns — `WHERE LOWER(email) = 'x'` blocks index (use expression index)
7. Stale statistics — run `ANALYZE table_name` or `VACUUM ANALYZE`

---

## NORMALIZATION

**Q: What are the normal forms? Explain 1NF through BCNF.**
A:

**1NF (First Normal Form):**
- Each column holds atomic (indivisible) values — no arrays, no comma-separated lists
- Each row is unique (has a primary key)
- No repeating column groups

**2NF (Second Normal Form):**
- Must be in 1NF
- No partial dependencies: every non-key column must depend on the WHOLE primary key (matters for composite keys)
- If a table has PK (student_id, course_id) and stores student_name (depends only on student_id), that violates 2NF → move student_name to a Students table

**3NF (Third Normal Form):**
- Must be in 2NF
- No transitive dependencies: non-key columns must depend ONLY on the PK, not on other non-key columns
- If you store zip_code and city, and city depends on zip_code (not directly on the PK), that violates 3NF → split into a ZipCodes table

**BCNF (Boyce-Codd Normal Form):**
- Stricter version of 3NF: every determinant must be a candidate key
- Handles edge cases 3NF misses when there are multiple overlapping candidate keys

**Q: When do you denormalize and why?**
A: Denormalize when read performance is critical and data doesn't change frequently. Trade-off: faster reads, risk of update anomalies.
- Analytics/reporting tables: pre-aggregate data, store redundant totals
- NoSQL documents: embed related data to avoid joins
- Caching layer: store precomputed results in Redis

---

## SQL vs NoSQL

**Q: When do you choose SQL over NoSQL?**
A: Choose SQL (relational DB) when:
- Data has clear relationships and structure (ACID required)
- Complex queries with joins and aggregations needed
- Data integrity is critical (financial, medical records)
- Existing team expertise
- Compliance requirements demand audit trails

Choose NoSQL when:
- Flexible/evolving schema (documents: MongoDB)
- Massive write throughput (Cassandra, DynamoDB)
- Key-value caching (Redis)
- Graph relationships (Neo4j)
- Full-text search (Elasticsearch)
- Horizontal scale is the primary concern over strict consistency

**Q: What is eventual consistency vs strong consistency?**
A:
- **Strong consistency** — after a write, ALL subsequent reads see the new data. SQL databases default to this within a transaction.
- **Eventual consistency** — after a write, reads will EVENTUALLY return the new value, but might temporarily return stale data. Used in distributed NoSQL (DynamoDB, Cassandra) for availability and partition tolerance. Acceptable for social feeds, analytics counters, product recommendations.
