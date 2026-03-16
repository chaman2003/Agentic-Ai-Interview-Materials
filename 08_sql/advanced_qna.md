# SQL — Advanced Q&A, Tricky Queries & Optimization

---

## QUERY EXECUTION ORDER

**Q: In what order does SQL actually execute a query?**
A: This is different from the order you WRITE it:
```
1. FROM / JOIN     — get the tables
2. WHERE           — filter rows
3. GROUP BY        — group rows
4. HAVING          — filter groups
5. SELECT          — choose columns / compute expressions
6. DISTINCT        — remove duplicates
7. ORDER BY        — sort results
8. LIMIT / OFFSET  — paginate
```
**Why it matters:** You can't use a SELECT alias in WHERE because WHERE runs before SELECT.
```sql
-- WRONG — alias doesn't exist yet when WHERE runs
SELECT salary * 2 AS doubled FROM employees WHERE doubled > 100000;

-- CORRECT — use original expression or wrap in subquery
SELECT salary * 2 AS doubled FROM employees WHERE salary * 2 > 100000;
```

---

## TRICKY SQL QUESTIONS

**Q: Find employees who earn more than their department's average salary.**
```sql
SELECT e.name, e.salary, d.avg_salary
FROM employees e
JOIN (
    SELECT department, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
) d ON e.department = d.department
WHERE e.salary > d.avg_salary;

-- Better with window function:
SELECT name, salary, department
FROM (
    SELECT name, salary, department,
           AVG(salary) OVER (PARTITION BY department) AS dept_avg
    FROM employees
) t
WHERE salary > dept_avg;
```

---

**Q: Find the second highest salary.**
```sql
-- Method 1: OFFSET
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;

-- Method 2: MAX with subquery
SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);

-- Method 3: DENSE_RANK (handles ties correctly)
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM employees
) t WHERE rnk = 2;
```

---

**Q: What is the difference between DELETE, TRUNCATE, and DROP?**

| Command | Removes | WHERE clause? | Rollback? | Resets auto-increment? |
|---------|---------|---------------|-----------|----------------------|
| DELETE | Selected rows | Yes | Yes | No |
| TRUNCATE | All rows | No | No (usually) | Yes |
| DROP | Entire table | No | No | N/A (table gone) |

---

**Q: Find duplicate emails in a users table and delete duplicates keeping the latest.**
```sql
-- Step 1: Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;

-- Step 2: Delete older duplicates keeping max(id) per email
DELETE FROM users
WHERE id NOT IN (
    SELECT MAX(id) FROM users GROUP BY email
);
```

---

**Q: Write a query to get a running total of orders per customer.**
```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) AS running_total
FROM orders;
```

---

## INDEXES IN DEPTH

**Q: What is a composite index and how does it work?**
A: Index on multiple columns. The ORDER matters — the index is most useful for queries that use the LEFTMOST prefix of the index columns.
```sql
CREATE INDEX idx_name ON orders(customer_id, status, created_at);

-- Uses index:  WHERE customer_id = 1
-- Uses index:  WHERE customer_id = 1 AND status = 'open'
-- Uses index:  WHERE customer_id = 1 AND status = 'open' AND created_at > ...
-- SKIPS index: WHERE status = 'open'           ← missing leftmost column
-- SKIPS index: WHERE created_at > '2024-01-01' ← missing leftmost column
```

**Q: What is a covering index?**
A: An index that contains ALL columns needed by a query — so the database can answer without ever touching the main table:
```sql
-- Query only needs id, email, name
CREATE INDEX idx_covering ON users(email, name);  -- email + name in index
SELECT name FROM users WHERE email = 'x@y.com';
-- Can be answered purely from the index — very fast (index-only scan)
```

**Q: When do indexes hurt performance?**
A:
1. Write-heavy tables (every INSERT/UPDATE/DELETE must update the index too)
2. Low cardinality columns (e.g., boolean — only 2 distinct values, index barely helps)
3. Very small tables (full scan is faster than index + random I/O)

---

## TRANSACTIONS AND ISOLATION

**Q: What are ACID properties?**
A:
- **Atomicity** — all or nothing. If any step fails, the whole transaction rolls back.
- **Consistency** — database must be in valid state before and after transaction.
- **Isolation** — concurrent transactions can't see each other's uncommitted changes.
- **Durability** — committed transactions survive crashes (written to disk).

**Q: What are transaction isolation levels?**

| Level | Dirty Read | Non-repeatable Read | Phantom Read |
|-------|-----------|---------------------|--------------|
| READ UNCOMMITTED | ✓ possible | ✓ possible | ✓ possible |
| READ COMMITTED | ✗ prevented | ✓ possible | ✓ possible |
| REPEATABLE READ | ✗ prevented | ✗ prevented | ✓ possible |
| SERIALIZABLE | ✗ prevented | ✗ prevented | ✗ prevented |

PostgreSQL default: **READ COMMITTED**.
- **Dirty read** — read another transaction's uncommitted changes
- **Non-repeatable read** — same row reads return different values in same transaction
- **Phantom read** — same query returns different rows in same transaction (new rows inserted)

```sql
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

---

## QUERY OPTIMIZATION

**Q: How do you analyze and optimize a slow query in Postgres?**
```sql
-- EXPLAIN: shows the query plan (what indexes it plans to use)
EXPLAIN SELECT * FROM users WHERE email = 'x@y.com';

-- EXPLAIN ANALYZE: actually runs the query, shows real timings
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'x@y.com';

-- Look for:
-- Seq Scan (no index) → add an index
-- Nested Loop with large sets → might need a composite index
-- Sort  → add index on ORDER BY column
-- High "rows" estimate way off from actual → run ANALYZE to refresh statistics
```

**Q: What is `VACUUM` in PostgreSQL?**
A: PostgreSQL uses MVCC (Multi-Version Concurrency Control) — deleted/updated rows aren't immediately removed, "dead tuples" are left behind. `VACUUM` cleans them up and reclaims space. `AUTOVACUUM` runs this automatically.

---

## ADVANCED PATTERNS

**Q: What is a materialized view?**
A: A cached result of a query stored as a real table. Unlike a regular view (re-runs query every time), a materialized view stores the result. Refresh manually with `REFRESH MATERIALIZED VIEW`.
```sql
CREATE MATERIALIZED VIEW daily_stats AS
SELECT date_trunc('day', created_at) AS day,
       COUNT(*) AS case_count,
       SUM(amount) AS total_amount
FROM cases GROUP BY 1;

-- Refresh (e.g., run nightly via cron)
REFRESH MATERIALIZED VIEW daily_stats;
```
Use for: expensive reports, dashboards, denormalized data for fast reads.

**Q: What is the difference between UNION and UNION ALL in performance?**
A: `UNION ALL` is always faster — it just concatenates the results. `UNION` has to deduplicate, which requires a sort operation. Use `UNION ALL` unless you specifically need deduplication.
