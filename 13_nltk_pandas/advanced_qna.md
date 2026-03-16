# NLTK + Pandas — Advanced Q&A

---

## NLP WITH TRANSFORMERS (HuggingFace Basics)

**Q: What is the HuggingFace `transformers` library and how do you use it for NLP tasks?**
```python
from transformers import pipeline

# Sentiment analysis — zero setup, uses a pre-trained model
sentiment = pipeline("sentiment-analysis")
result = sentiment("FastAPI is an amazing framework!")
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Named Entity Recognition (NER)
ner = pipeline("ner", grouped_entities=True)
entities = ner("Elon Musk founded SpaceX in Los Angeles in 2002.")
# [{'entity_group': 'PER', 'word': 'Elon Musk', 'score': 0.99},
#  {'entity_group': 'ORG', 'word': 'SpaceX', 'score': 0.98},
#  {'entity_group': 'LOC', 'word': 'Los Angeles', 'score': 0.97}]

# Summarization
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
summary = summarizer(long_text, max_length=130, min_length=30)

# Text generation
generator = pipeline("text-generation", model="gpt2")
output = generator("The future of AI is", max_new_tokens=50)

# Question answering
qa = pipeline("question-answering")
answer = qa(question="Who founded SpaceX?", context="Elon Musk founded SpaceX.")
# {'answer': 'Elon Musk', 'score': 0.99, 'start': 0, 'end': 9}
```

**Q: How do you use a tokenizer directly for preprocessing?**
```python
from transformers import AutoTokenizer, AutoModel
import torch

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

texts = ["Hello world", "FastAPI is great"]
# Tokenize with padding and truncation
inputs = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
# inputs: {'input_ids': tensor, 'attention_mask': tensor, 'token_type_ids': tensor}

with torch.no_grad():
    outputs = model(**inputs)
    # outputs.last_hidden_state: shape [batch_size, seq_len, hidden_size]
    # CLS token embedding (sentence representation)
    cls_embeddings = outputs.last_hidden_state[:, 0, :]  # [batch_size, 768]
```

**Interview tip:** The CLS token in BERT is trained to represent the whole sentence. Mean pooling of all token embeddings often works better for sentence similarity tasks.

---

## TEXT CLASSIFICATION (TF-IDF + sklearn)

**Q: How do you build a text classifier using TF-IDF and sklearn?**
```python
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report
import joblib

# Sample dataset
df = pd.DataFrame({
    "text": ["I love this product", "Terrible experience", "Average quality",
             "Absolutely fantastic", "Would not recommend", "Pretty decent"],
    "label": ["positive", "negative", "neutral", "positive", "negative", "neutral"]
})

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
)

# Pipeline: TF-IDF vectorization + Logistic Regression
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),       # Unigrams and bigrams
        max_features=50000,        # Vocabulary size cap
        min_df=2,                  # Ignore terms that appear < 2 times
        max_df=0.95,               # Ignore terms in > 95% of docs (common words)
        sublinear_tf=True,         # Apply log(1 + tf) — helps with long docs
    )),
    ("clf", LogisticRegression(C=1.0, max_iter=1000, class_weight="balanced")),
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

print(classification_report(y_test, y_pred))

# Cross-validate for more robust evaluation
scores = cross_val_score(pipeline, df["text"], df["label"], cv=5, scoring="f1_macro")
print(f"CV F1: {scores.mean():.3f} ± {scores.std():.3f}")

# Save and load
joblib.dump(pipeline, "text_classifier.pkl")
loaded = joblib.load("text_classifier.pkl")
```

**Q: When to use TF-IDF + sklearn vs transformers?**

| Criterion | TF-IDF + sklearn | Transformers (BERT etc.) |
|-----------|-----------------|--------------------------|
| Data size | Works on small datasets (100s of samples) | Needs 1000s+ (or fine-tune from pretrained) |
| Speed | Very fast (train + inference) | Slow (GPU recommended) |
| Accuracy | Good for simple classification | State-of-the-art |
| Interpretability | High (feature importances) | Low (black box) |
| Domain specificity | Needs domain data | Transfer learning helps |
| Deployment | Lightweight (few MB) | Heavy (100MB+ models) |

---

## SENTIMENT ANALYSIS

**Q: How do you run sentiment analysis at scale on a Pandas DataFrame?**
```python
import pandas as pd
from transformers import pipeline

# Load once — expensive operation
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1,           # -1 = CPU, 0 = first GPU
    batch_size=64,       # Process 64 texts at once
    truncation=True,
    max_length=512,
)

df = pd.read_csv("reviews.csv")  # columns: id, text, ...

# Process in batches — DO NOT call pipeline() row by row!
def run_sentiment_batched(texts: list, batch_size: int = 64) -> list:
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_results = sentiment_pipeline(batch)
        results.extend(batch_results)
    return results

predictions = run_sentiment_batched(df["text"].tolist())
df["sentiment"] = [r["label"].lower() for r in predictions]
df["sentiment_score"] = [r["score"] for r in predictions]

# Rule-based fallback for neutral detection (DistilBERT only gives POS/NEG)
df.loc[df["sentiment_score"] < 0.65, "sentiment"] = "neutral"

print(df["sentiment"].value_counts())
```

**VADER — rule-based sentiment for social media text:**
```python
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon")

sid = SentimentIntensityAnalyzer()
text = "The product is okay, not great but not terrible either 😐"
scores = sid.polarity_scores(text)
# {'neg': 0.09, 'neu': 0.74, 'pos': 0.17, 'compound': 0.0772}

# Compound score: -1 (most negative) to +1 (most positive)
def classify_vader(compound: float) -> str:
    if compound >= 0.05:  return "positive"
    elif compound <= -0.05: return "negative"
    else: return "neutral"

df["vader_sentiment"] = df["text"].apply(
    lambda t: classify_vader(sid.polarity_scores(t)["compound"])
)
```

---

## PANDAS ADVANCED

**Q: How do you work with MultiIndex DataFrames?**
```python
import pandas as pd
import numpy as np

# Creating MultiIndex
arrays = [
    ["Engineering", "Engineering", "Marketing", "Marketing"],
    ["Alice", "Bob", "Carol", "Dave"],
]
index = pd.MultiIndex.from_arrays(arrays, names=["department", "employee"])
df = pd.DataFrame({"salary": [90000, 85000, 75000, 80000]}, index=index)

# Selecting with MultiIndex
df.loc["Engineering"]                            # All Engineering rows
df.loc[("Engineering", "Alice")]                 # Specific row
df.loc[(slice(None), "Alice"), :]                # All departments, Alice only
df.xs("Alice", level="employee")                # Cross-section by level name

# Reset to flat index
df_flat = df.reset_index()

# Stack and unstack — pivot between index levels and columns
df_wide = df.unstack(level="employee")   # employees become columns
df_long = df_wide.stack(level="employee")  # back to long format
```

**Q: How do pivot tables work in Pandas?**
```python
# Source data
df = pd.DataFrame({
    "region": ["North", "North", "South", "South", "North"],
    "product": ["Widget", "Gadget", "Widget", "Widget", "Gadget"],
    "sales": [1000, 1500, 800, 900, 2000],
    "units": [10, 15, 8, 9, 20],
})

# Basic pivot table — similar to Excel pivot
pivot = df.pivot_table(
    values=["sales", "units"],
    index="region",
    columns="product",
    aggfunc={"sales": "sum", "units": ["sum", "mean"]},
    fill_value=0,
    margins=True,      # Add totals row/column
)

# pivot_table vs groupby
# pivot_table:  better when you want a 2D result (rows x columns)
# groupby:      more flexible, better for 1D aggregations

# Crosstab — special case for frequency/proportion tables
ct = pd.crosstab(df["region"], df["product"], values=df["sales"], aggfunc="sum")
ct_normalized = pd.crosstab(df["region"], df["product"], normalize="index")  # Row %
```

**Q: How do you work with time series data in Pandas?**
```python
import pandas as pd

# Parse dates on load
df = pd.read_csv("sales.csv", parse_dates=["date"], index_col="date")

# Resampling — aggregate to different frequencies
daily = df.resample("D").sum()          # Daily totals
weekly = df.resample("W").agg({"sales": "sum", "units": "mean"})
monthly = df.resample("ME").sum()       # Month End

# Date arithmetic and filtering
df_2024 = df["2024"]                                    # Full year
df_q1 = df["2024-01":"2024-03"]                         # Date range slice
df["weekday"] = df.index.day_name()
df["is_weekend"] = df.index.dayofweek >= 5

# Shift and lag features
df["sales_lag1"] = df["sales"].shift(1)       # Yesterday's sales
df["sales_lead1"] = df["sales"].shift(-1)     # Tomorrow's sales
df["sales_diff"] = df["sales"].diff(1)        # Day-over-day change
df["sales_pct_change"] = df["sales"].pct_change()  # % change

# Rolling statistics
df["sales_7d_avg"] = df["sales"].rolling(window=7, min_periods=1).mean()
df["sales_30d_std"] = df["sales"].rolling(window=30).std()
df["sales_7d_max"] = df["sales"].rolling(window=7).max()
```

**Q: How do window functions (rolling, expanding, ewm) work?**
```python
# Rolling — fixed window size
df["rolling_mean_7"] = df["value"].rolling(7).mean()
df["rolling_sum_7"] = df["value"].rolling(7).sum()

# Expanding — grows from start to current row (cumulative)
df["cumulative_max"] = df["value"].expanding().max()
df["running_average"] = df["value"].expanding().mean()

# EWM — Exponentially Weighted Moving average (recent values weighted more)
df["ewm_span10"] = df["value"].ewm(span=10, adjust=False).mean()

# GroupBy + Rolling — rolling within each group
df["group_rolling_mean"] = (
    df.groupby("category")["value"]
    .transform(lambda x: x.rolling(7, min_periods=1).mean())
)
```

---

## PANDAS PERFORMANCE

**Q: Vectorization vs apply — when and why?**
```python
import pandas as pd
import numpy as np
import time

df = pd.DataFrame({"a": range(1_000_000), "b": range(1_000_000)})

# SLOW — Python loop (apply is essentially a for loop)
start = time.perf_counter()
df["result_slow"] = df.apply(lambda row: row["a"] + row["b"], axis=1)
print(f"apply: {time.perf_counter() - start:.3f}s")  # ~3-5s

# FAST — vectorized numpy operation
start = time.perf_counter()
df["result_fast"] = df["a"] + df["b"]
print(f"vectorized: {time.perf_counter() - start:.3f}s")  # ~0.01s

# Rule: if you can express the operation using pandas/numpy built-ins → do it
# Reserve apply() for:
# - Complex conditional logic that can't be expressed vectorially
# - Calling external functions
# - Operations that truly need row-level context

# np.where — vectorized if/else (much faster than apply with conditionals)
df["category"] = np.where(df["a"] > 500_000, "high", "low")  # Fast
# vs
df["category_slow"] = df["a"].apply(lambda x: "high" if x > 500_000 else "low")  # Slow
```

**Q: How do you handle large CSV files that don't fit in memory?**
```python
# Option 1: chunked processing
chunk_size = 100_000
results = []
for chunk in pd.read_csv("huge_file.csv", chunksize=chunk_size, dtype={"id": "int32"}):
    # Process each chunk independently
    chunk_filtered = chunk[chunk["amount"] > 100]
    results.append(chunk_filtered.groupby("category")["amount"].sum())

final_result = pd.concat(results).groupby(level=0).sum()

# Option 2: dtype optimization before loading
dtypes = {
    "id": "int32",                # vs default int64 — 2x smaller
    "category": "category",       # vs object — up to 90% smaller for low cardinality
    "price": "float32",           # vs float64 — 2x smaller
    "is_active": "bool",          # vs int64 — 8x smaller
}
df = pd.read_csv("file.csv", dtype=dtypes, usecols=["id", "category", "price"])

# Check memory usage
print(df.memory_usage(deep=True).sum() / 1024**2, "MB")
df.info(memory_usage="deep")

# Option 3: Polars (drop-in faster alternative, lazy evaluation)
import polars as pl
df = pl.scan_csv("huge_file.csv")          # Lazy — doesn't load yet
result = df.filter(pl.col("amount") > 100).groupby("category").agg(
    pl.col("amount").sum()
).collect()                                # Execute now
```

**Q: dtype optimization deep dive:**
```python
# Convert object columns with low cardinality to category
for col in df.select_dtypes("object").columns:
    n_unique = df[col].nunique()
    if n_unique / len(df) < 0.05:   # < 5% unique values
        df[col] = df[col].astype("category")

# Downcast numerics
df["int_col"] = pd.to_numeric(df["int_col"], downcast="integer")   # int64 → int8/16/32
df["float_col"] = pd.to_numeric(df["float_col"], downcast="float") # float64 → float32

# Reduce datetime precision
df["date"] = pd.to_datetime(df["date"]).dt.floor("s")  # Remove nanosecond precision
```

---

## PANDAS VISUALIZATION PATTERNS

**Q: How do you create data visualizations directly from Pandas?**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sales.csv", parse_dates=["date"], index_col="date")

# Pandas built-in plotting (wraps matplotlib)
df["revenue"].plot(title="Revenue Over Time", figsize=(12, 4))
plt.tight_layout()
plt.savefig("revenue.png", dpi=150)

# Multiple series
df[["revenue", "costs"]].plot(kind="area", alpha=0.7, title="Revenue vs Costs")

# Bar chart — value counts
df["category"].value_counts().plot(kind="bar", rot=45)

# Histogram
df["order_value"].plot(kind="hist", bins=50, edgecolor="black")

# Scatter matrix
from pandas.plotting import scatter_matrix
scatter_matrix(df[["revenue", "units", "margin"]], alpha=0.5, figsize=(10, 10))

# Seaborn for better aesthetics
import seaborn as sns
monthly = df.resample("ME").sum().reset_index()
sns.lineplot(data=monthly, x="date", y="revenue", hue="region")

# Plotly for interactive charts (good for dashboards)
import plotly.express as px
fig = px.line(monthly, x="date", y="revenue", color="region", title="Monthly Revenue")
fig.write_html("revenue_interactive.html")
```

---

## COMMON PANDAS INTERVIEW TRAPS

**Trap 1: SettingWithCopyWarning — chained assignment**
```python
# WRONG — may or may not modify the original df (undefined behavior)
df[df["age"] > 30]["salary"] = 100000  # Chained assignment — modifies a copy

# CORRECT — use .loc
df.loc[df["age"] > 30, "salary"] = 100000

# If you intentionally want a copy
subset = df[df["age"] > 30].copy()
subset["salary"] = 100000  # Safe — explicit copy
```

**Trap 2: `iterrows()` is extremely slow**
```python
# WRONG — iterrows() returns copies of each row, very slow
for idx, row in df.iterrows():
    df.at[idx, "doubled"] = row["value"] * 2

# CORRECT — vectorized
df["doubled"] = df["value"] * 2

# If you must iterate: itertuples() is 10-100x faster than iterrows()
for row in df.itertuples():
    print(row.value)  # Named tuple access — no copy
```

**Trap 3: `inplace=True` doesn't actually save memory**
```python
# Common misconception: inplace=True saves memory
df.drop(columns=["col"], inplace=True)   # Creates a copy internally anyway
df = df.drop(columns=["col"])            # Equivalent — prefer this (clear intent)
```

**Trap 4: `merge` vs `join` vs `concat`**
```python
# merge — SQL-style join on columns (most flexible)
result = pd.merge(left, right, on="user_id", how="left")

# join — index-based join (faster when using index)
result = left.join(right, on="user_id", how="left")

# concat — stack DataFrames vertically or horizontally
vertical = pd.concat([df1, df2], ignore_index=True)    # Stack rows
horizontal = pd.concat([df1, df2], axis=1)             # Stack columns
```

**Trap 5: Mutable default argument with DataFrames**
```python
# WRONG — df is modified in-place between calls
def add_col(df, val, cols=[]):         # Mutable default!
    cols.append(val)
    df["new"] = val
    return df

# CORRECT
def add_col(df, val, cols=None):
    if cols is None: cols = []
    cols.append(val)
    df = df.copy()
    df["new"] = val
    return df
```

**Trap 6: `groupby` with observed=False (Pandas 2.x change)**
```python
# Pandas 2.0: groupby on category dtype defaults to observed=False
# (includes empty groups) — often surprises people
df["cat_col"] = df["cat_col"].astype("category")
# Old behavior (all groups): df.groupby("cat_col", observed=False)["val"].sum()
# New behavior (only observed): df.groupby("cat_col", observed=True)["val"].sum()
```

---

## NUMPY vs PANDAS DECISIONS

**Q: When do you use NumPy directly vs Pandas?**

| Use Case | NumPy | Pandas |
|----------|-------|--------|
| Numerical computation, linear algebra | Yes | No |
| Matrix operations, dot products | Yes | No |
| Homogeneous arrays (all same dtype) | Yes | No |
| Heterogeneous tabular data (mixed types) | No | Yes |
| Time series with dates | No | Yes |
| Data that needs labels/column names | No | Yes |
| GroupBy, pivot, merge operations | No | Yes |
| I/O (CSV, Excel, Parquet, SQL) | No | Yes |
| Performance-critical inner loops | Yes | No (use numpy under hood) |

```python
import numpy as np
import pandas as pd

# Use NumPy for pure math
matrix = np.array([[1, 2], [3, 4]])
eigenvalues = np.linalg.eigvals(matrix)
correlation = np.corrcoef(array1, array2)

# Extract NumPy arrays from Pandas for performance
arr = df["values"].to_numpy()            # Fast conversion
result = np.log1p(arr)                   # NumPy ufunc on array
df["log_values"] = result                # Back to Pandas

# Pandas uses NumPy internally
# df.values returns the underlying numpy array (avoid — use to_numpy() instead)
# df.to_numpy() is the preferred modern API
```
