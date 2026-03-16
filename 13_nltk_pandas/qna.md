# NLTK + Pandas Q&A — Interview Ready

---

## NLTK / NLP

**Q: What is tokenization?**
A: Breaking text into smaller units. Word tokenization splits into individual words/punctuation. Sentence tokenization splits into sentences. `nltk.word_tokenize()` and `nltk.sent_tokenize()`.

**Q: What is the difference between stemming and lemmatization?**
A:
- **Stemming** — crude chopping of word endings using rules. Fast. Less accurate. "Running" → "run", "better" → "better" (fails).
- **Lemmatization** — uses vocabulary and morphological analysis to find the true base form. Slower. More accurate. "Running" → "run", "better" → "good" (with adjective POS context).
- For LLM preprocessing: use lemmatization for quality, stemming for speed when quality matters less.

**Q: What are stopwords?**
A: Common words that carry little meaning in most NLP tasks: "the", "is", "at", "which", "on". Removing them reduces noise. `nltk.corpus.stopwords.words("english")`. Don't remove them for sentiment analysis or tasks where "not" matters.

**Q: What is POS tagging?**
A: Parts-of-speech tagging — labels each word as noun (NN), verb (VB), adjective (JJ), etc. Used to understand sentence structure and improve NER and lemmatization accuracy.

**Q: What is NER?**
A: Named Entity Recognition — identifies real-world entities in text: PERSON, ORGANIZATION, GPE (location), DATE, MONEY. `nltk.ne_chunk(pos_tagged_tokens)`.

**Q: What is a text normalization pipeline?**
A: A sequence of transformations to clean text before processing: lowercase → remove URLs → remove special chars → tokenize → remove stopwords → lemmatize. Makes different forms of the same word comparable.

---

## PANDAS

**Q: What is the difference between a Series and a DataFrame?**
A: Series = one-dimensional labeled array (like a single column). DataFrame = two-dimensional table with rows and columns. A DataFrame is a collection of Series sharing the same index.

**Q: What is the difference between `loc` and `iloc`?**
A:
- `loc` — label-based indexing. `df.loc[0]` gets row with index label 0. `df.loc[df["age"] > 25]` filters by condition.
- `iloc` — integer position-based. `df.iloc[0]` always gets the first row regardless of index.

**Q: How do you filter a DataFrame on multiple conditions?**
A: Use `&` (AND) and `|` (OR). Each condition MUST be in parentheses:
```python
result = df[(df["dept"] == "Engineering") & (df["salary"] > 80000)]
```

**Q: What is `groupby().agg()`?**
A: Groups rows by a column and computes aggregations for each group — like SQL `GROUP BY`. `.agg()` lets you compute multiple aggregations at once with custom column names.

**Q: What is `apply()` and when should you avoid it?**
A: Applies a function to each row or column. Powerful but SLOW — it's a Python loop under the hood. Prefer vectorized operations (`.str.`, arithmetic, built-in aggregations) whenever possible.

**Q: How do you handle missing values in Pandas?**
A: `df.isna()` to detect. `df.dropna()` to remove rows. `df.fillna(value)` to fill. `df.fillna(df.mean())` to fill with column mean.

**Q: What does `to_dict("records")` return?**
A: A list of dicts, one per row. `[{"name": "Alice", "salary": 90000}, ...]`. Most useful for converting DataFrame back to JSON/dict format.

**Q: When would you use Pandas in an AI/ML project?**
A: Reading and cleaning datasets, exploring data distributions, processing LLM extraction outputs, building evaluation datasets, preparing features for ML models, handling tabular data from CSVs/databases.
