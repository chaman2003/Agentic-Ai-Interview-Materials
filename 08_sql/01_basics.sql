-- ============================================================
-- SQL BASICS — Interview Essentials
-- ============================================================

-- ── SELECT ──────────────────────────────────────────────────
SELECT * FROM users;                     -- all columns
SELECT name, email FROM users;           -- specific columns
SELECT name AS full_name FROM users;     -- alias column

-- With conditions
SELECT name, email
FROM users
WHERE age > 25
  AND is_active = true
ORDER BY name ASC
LIMIT 10;

-- ── INSERT ──────────────────────────────────────────────────
INSERT INTO users (name, email, age)
VALUES ('Chaman', 'c@y.com', 21);

-- Insert multiple
INSERT INTO users (name, email) VALUES
    ('Alice', 'a@y.com'),
    ('Bob',   'b@y.com');

-- ── UPDATE ──────────────────────────────────────────────────
UPDATE users
SET email = 'new@y.com', age = 22
WHERE id = 1;

-- IMPORTANT: Always use WHERE with UPDATE or you'll update every row!

-- ── DELETE ──────────────────────────────────────────────────
DELETE FROM users WHERE id = 1;
-- Always use WHERE! Without it, deletes ALL rows.

-- ── WHERE OPERATORS ─────────────────────────────────────────
SELECT * FROM users
WHERE age BETWEEN 18 AND 30;       -- inclusive range

SELECT * FROM users
WHERE name LIKE 'Ch%';             -- starts with 'Ch' (% = wildcard)

SELECT * FROM users
WHERE name LIKE '%aman';           -- ends with 'aman'

SELECT * FROM users
WHERE email LIKE '%@gmail.com';    -- contains @gmail.com

SELECT * FROM users
WHERE city IN ('Bangalore', 'Mumbai', 'Delhi');

SELECT * FROM users
WHERE city NOT IN ('Chennai');

SELECT * FROM users
WHERE phone IS NULL;               -- check for null

SELECT * FROM users
WHERE phone IS NOT NULL;

-- ── AGGREGATE FUNCTIONS ──────────────────────────────────────
SELECT COUNT(*)    FROM users;                 -- count all rows
SELECT COUNT(age)  FROM users;                 -- count non-null age
SELECT AVG(salary) FROM employees;             -- average
SELECT SUM(amount) FROM orders;                -- sum
SELECT MIN(salary) FROM employees;             -- min
SELECT MAX(salary) FROM employees;             -- max

-- ── GROUP BY ─────────────────────────────────────────────────
-- Group rows with the same value and aggregate
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department;

SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;

-- ── HAVING ───────────────────────────────────────────────────
-- Filter GROUPS (like WHERE but for GROUP BY results)
-- WHERE filters rows BEFORE grouping
-- HAVING filters groups AFTER grouping

SELECT department, COUNT(*) AS emp_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 5;     -- only departments with more than 5 employees

SELECT department, AVG(salary) AS avg_sal
FROM employees
WHERE is_active = true           -- filter rows first
GROUP BY department
HAVING AVG(salary) > 50000;      -- then filter groups

-- ── JOINS ────────────────────────────────────────────────────
-- INNER JOIN: only rows that match in BOTH tables
SELECT u.name, o.total, o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN: ALL rows from left table, matching from right (NULL if no match)
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- Shows all users, including those with NO orders (o.total will be NULL)

-- RIGHT JOIN: ALL rows from right table
SELECT u.name, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN: ALL rows from both tables
SELECT u.name, o.total
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- Multiple joins
SELECT u.name, o.total, p.name AS product_name
FROM users u
JOIN orders o        ON u.id = o.user_id
JOIN order_items oi  ON o.id = oi.order_id
JOIN products p      ON oi.product_id = p.id
WHERE o.status = 'completed';

-- ── SUBQUERIES ───────────────────────────────────────────────
-- Query inside another query
SELECT name
FROM users
WHERE id IN (
    SELECT user_id FROM orders WHERE total > 1000
);

-- Subquery in FROM
SELECT dept, avg_salary
FROM (
    SELECT department AS dept, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY department
) AS dept_averages
WHERE avg_salary > 60000;

-- ── DISTINCT ─────────────────────────────────────────────────
SELECT DISTINCT city FROM users;   -- unique cities only

-- ── CREATE TABLE ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cases (
    id          SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    title       VARCHAR(200) NOT NULL,
    status      VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open','in_progress','resolved','closed')),
    amount      DECIMAL(12,2),
    party_a     VARCHAR(200) NOT NULL,
    party_b     VARCHAR(200) NOT NULL,
    mediator_id INTEGER REFERENCES mediators(id),   -- foreign key
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- ── INDEXES ──────────────────────────────────────────────────
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_mediator ON cases(mediator_id);
CREATE UNIQUE INDEX idx_cases_number ON cases(case_number);
