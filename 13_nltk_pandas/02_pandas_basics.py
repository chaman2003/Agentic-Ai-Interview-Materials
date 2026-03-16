# ============================================================
# PANDAS — Interview Essentials + Data Handling
# ============================================================
# pip install pandas

import pandas as pd
import numpy as np
from io import StringIO

# ── 1. CREATING DATAFRAMES ────────────────────────────────────
# From dict (most common)
df = pd.DataFrame({
    "name":       ["Alice", "Bob", "Charlie", "Diana", "Eve"],
    "department": ["Engineering", "Sales", "Engineering", "HR", "Sales"],
    "salary":     [90000, 55000, 85000, 60000, 58000],
    "age":        [28, 35, 30, 27, 32],
    "active":     [True, True, False, True, True]
})

# From CSV
# df = pd.read_csv("employees.csv")

# From JSON string
json_str = '[{"id": 1, "name": "Case A"}, {"id": 2, "name": "Case B"}]'
df_json = pd.read_json(StringIO(json_str))

# ── 2. INSPECTING DATA ────────────────────────────────────────
print(df.head(3))           # first 3 rows
print(df.tail(2))           # last 2 rows
print(df.shape)             # (5, 5) — rows, cols
print(df.info())            # dtypes, null counts, memory
print(df.describe())        # count, mean, std, min, max for numerics
print(df.columns.tolist())  # ['name', 'department', 'salary', 'age', 'active']
print(df.dtypes)            # dtype of each column

# ── 3. SELECTING DATA ─────────────────────────────────────────
# Single column → Series
names = df["name"]

# Multiple columns → DataFrame
subset = df[["name", "salary"]]

# Row by integer position
row  = df.iloc[0]          # first row
rows = df.iloc[0:3]        # rows 0, 1, 2

# Row by label/condition
row  = df.loc[0]
rows = df.loc[df["active"] == True]

# ── 4. FILTERING ─────────────────────────────────────────────
# Single condition
engineers = df[df["department"] == "Engineering"]

# Multiple conditions (use & and |, wrap each in parentheses)
senior_engineers = df[(df["department"] == "Engineering") & (df["salary"] > 87000)]

# isin — check multiple values
sales_hr = df[df["department"].isin(["Sales", "HR"])]

# String contains
alice_etc = df[df["name"].str.contains("a", case=False)]

# Null checks
nulls     = df[df["salary"].isna()]
not_nulls = df[df["salary"].notna()]

# ── 5. ADDING / MODIFYING COLUMNS ────────────────────────────
df["salary_lakh"] = df["salary"] / 100_000              # derived column
df["level"]       = df["salary"].apply(lambda s: "Senior" if s > 80000 else "Junior")
df["full_info"]   = df["name"] + " (" + df["department"] + ")"   # string concat

# ── 6. GROUPBY + AGGREGATION ──────────────────────────────────
# Like SQL GROUP BY
dept_stats = df.groupby("department").agg(
    headcount   = ("name",    "count"),
    avg_salary  = ("salary",  "mean"),
    max_salary  = ("salary",  "max"),
    min_age     = ("age",     "min")
).reset_index()

print(dept_stats)
#    department  headcount  avg_salary  max_salary  min_age
# 0  Engineering         2     87500.0       90000       28
# 1  HR                  1     60000.0       60000       27
# 2  Sales               2     56500.0       58000       32

# Value counts (like SELECT col, COUNT(*) GROUP BY col)
dept_counts = df["department"].value_counts()
# Engineering    2
# Sales          2
# HR             1

# ── 7. MERGE / JOIN ───────────────────────────────────────────
# Like SQL JOIN

employees = pd.DataFrame({
    "emp_id":     [1, 2, 3, 4],
    "name":       ["Alice", "Bob", "Charlie", "Diana"],
    "dept_id":    [10, 20, 10, 30]
})

departments = pd.DataFrame({
    "dept_id":   [10, 20, 30],
    "dept_name": ["Engineering", "Sales", "HR"]
})

# Inner join (only matches)
merged = pd.merge(employees, departments, on="dept_id", how="inner")

# Left join (all employees, even if no dept)
left = pd.merge(employees, departments, on="dept_id", how="left")

# ── 8. HANDLING NULLS ─────────────────────────────────────────
df_with_nulls = pd.DataFrame({
    "name":   ["Alice", None, "Charlie"],
    "salary": [90000, None, 85000]
})

df_with_nulls["salary"].fillna(0)                    # fill nulls with 0
df_with_nulls["salary"].fillna(df["salary"].mean())  # fill with mean
df_with_nulls.dropna()                               # drop rows with any null
df_with_nulls.dropna(subset=["name"])                # drop only if name is null

# ── 9. TEXT OPERATIONS ────────────────────────────────────────
# pandas .str accessor for string columns — vectorized, fast
df["name_upper"]     = df["name"].str.upper()
df["name_lower"]     = df["name"].str.lower()
df["name_len"]       = df["name"].str.len()
df["name_clean"]     = df["name"].str.strip().str.replace(r"\s+", " ", regex=True)
df["is_alice"]       = df["name"].str.contains("Alice", case=False, na=False)
df["first_letter"]   = df["name"].str[0]
names_list           = df["name"].str.split(" ")      # split into list

# ── 10. SORTING ───────────────────────────────────────────────
by_salary     = df.sort_values("salary", ascending=False)
by_dept_name  = df.sort_values(["department", "name"])   # multi-column sort

# ── 11. CONVERTING TO OTHER FORMATS ──────────────────────────
records = df.to_dict("records")    # [{"name": "Alice", "salary": 90000}, ...]
as_json = df.to_json(orient="records")  # JSON string
as_csv  = df.to_csv(index=False)        # CSV string without row numbers
as_list = df.values.tolist()            # list of lists

# ── 12. PRACTICAL EXAMPLE — Process LLM Output ────────────────
def process_llm_extractions(raw_extractions: list[dict]) -> pd.DataFrame:
    """Process a list of LLM-extracted records and clean them."""
    df = pd.DataFrame(raw_extractions)

    # Normalize text columns
    for col in ["name", "company", "role"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title().fillna("Unknown")

    # Convert salary strings to numbers
    if "salary" in df.columns:
        df["salary"] = pd.to_numeric(
            df["salary"].str.replace(r"[^0-9]", "", regex=True),
            errors="coerce"
        ).fillna(0)

    # Drop duplicates
    df = df.drop_duplicates(subset=["name", "company"])

    # Sort
    df = df.sort_values("name").reset_index(drop=True)

    return df
