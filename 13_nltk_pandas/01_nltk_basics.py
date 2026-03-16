# ============================================================
# NLTK + NLP TEXT PROCESSING — Interview Essentials
# ============================================================
# pip install nltk spacy
# python -m nltk.downloader punkt stopwords averaged_perceptron_tagger wordnet

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize, TweetTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
import re, string

# ── 1. TOKENIZATION ──────────────────────────────────────────
# Break text into words or sentences
text = "LegalTech AI resolved thousands of disputes. The platform grew 80% annually!"

# Word tokenization
words = word_tokenize(text)
print(words)
# ['LegalTech', 'AI', 'resolved', 'thousands', 'disputes', '.', 'The', ...]

# Sentence tokenization
sentences = sent_tokenize(text)
print(sentences)
# ['LegalTech AI resolved thousands of disputes.', 'The platform grew 80% annually!']

# Social media tokenizer (handles hashtags, @mentions)
tt = TweetTokenizer()
tweet_tokens = tt.tokenize("LangChain is #awesome for @AI builders!")
# ['LangChain', 'is', '#awesome', 'for', '@AI', 'builders', '!']

# ── 2. STOPWORD REMOVAL ───────────────────────────────────────
# Stopwords = common words that add little meaning (the, is, at, which)
stop_words = set(stopwords.words("english"))

filtered = [w for w in words if w.lower() not in stop_words and w not in string.punctuation]
print(filtered)
# ['LegalTech', 'AI', 'resolved', 'thousands', 'disputes', 'platform', 'grew', '80', '%', 'annually']

# ── 3. STEMMING vs LEMMATIZATION ─────────────────────────────
# STEMMING: crude rule-based chopping of word endings → faster but less accurate
# LEMMATIZATION: uses vocabulary/morphology to find actual base form → slower but accurate

stemmer    = PorterStemmer()
lemmatizer = WordNetLemmatizer()

words_to_compare = ["running", "runs", "ran", "better", "easily", "studies", "studying"]

for word in words_to_compare:
    stem   = stemmer.stem(word)
    lemma  = lemmatizer.lemmatize(word, pos="v")   # pos="v" for verbs
    print(f"{word:12} | stem: {stem:12} | lemma: {lemma}")

# running      | stem: run          | lemma: run
# runs         | stem: run          | lemma: run
# ran          | stem: ran          | lemma: ran     ← stemmer fails irregular
# better       | stem: better       | lemma: better  ← lemmatizer needs adj pos
# studies      | stem: studi        | lemma: study

# ── 4. POS TAGGING ───────────────────────────────────────────
# Parts of Speech: NN=noun, VB=verb, JJ=adjective, RB=adverb, DT=determiner
tokens = word_tokenize("Chaman built an intelligent document processing system")
tagged = pos_tag(tokens)
print(tagged)
# [('Chaman', 'NNP'), ('built', 'VBD'), ('an', 'DT'), ('intelligent', 'JJ'),
#  ('document', 'NN'), ('processing', 'NN'), ('system', 'NN')]

# Extract only nouns
nouns = [word for word, pos in tagged if pos.startswith("NN")]
print(nouns)  # ['Chaman', 'document', 'processing', 'system']

# ── 5. NAMED ENTITY RECOGNITION (NER) ───────────────────────
# Identifies real-world entities: PERSON, ORGANIZATION, GPE (location), DATE, MONEY
ner_text = "LegalTech AI, a Bangalore-based company, raised funding in March 2024."
tokens   = word_tokenize(ner_text)
tagged   = pos_tag(tokens)
tree     = ne_chunk(tagged)

for subtree in tree:
    if hasattr(subtree, "label"):
        entity = " ".join([word for word, tag in subtree.leaves()])
        print(f"{subtree.label()}: {entity}")
# ORGANIZATION: LegalTech AI
# GPE: Bangalore

# ── 6. TEXT NORMALIZATION PIPELINE ────────────────────────────
# Full pipeline for preparing text for LLM or ML model input

def normalize_text(text: str) -> str:
    """Complete text normalization pipeline."""
    # 1. Lowercase
    text = text.lower()
    # 2. Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # 3. Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)
    # 4. Remove special characters (keep alphanumeric + spaces)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # 5. Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def preprocess_for_nlp(text: str, remove_stops: bool = True) -> list[str]:
    """Full NLP preprocessing pipeline."""
    # 1. Normalize
    text = normalize_text(text)
    # 2. Tokenize
    tokens = word_tokenize(text)
    # 3. Remove stopwords
    if remove_stops:
        stop_words = set(stopwords.words("english"))
        tokens = [t for t in tokens if t not in stop_words]
    # 4. Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    # 5. Remove short tokens
    tokens = [t for t in tokens if len(t) > 2]
    return tokens

# Example
raw = "Please visit https://mycompany.com or email support@mycompany.com for legal-tech solutions!!!"
clean = preprocess_for_nlp(raw)
print(clean)
# ['please', 'visit', 'legal', 'tech', 'solution']

# ── 7. TEXT SIMILARITY (simple) ────────────────────────────
from collections import Counter
import math

def cosine_similarity_text(text1: str, text2: str) -> float:
    """Simple bag-of-words cosine similarity (no embeddings)."""
    vec1 = Counter(preprocess_for_nlp(text1))
    vec2 = Counter(preprocess_for_nlp(text2))

    common = set(vec1.keys()) & set(vec2.keys())
    dot    = sum(vec1[w] * vec2[w] for w in common)
    mag1   = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2   = math.sqrt(sum(v**2 for v in vec2.values()))

    return dot / (mag1 * mag2) if mag1 and mag2 else 0.0

s1 = "Document processing with OCR and machine learning"
s2 = "OCR based document extraction using ML"
print(cosine_similarity_text(s1, s2))   # ~0.4 (similar topics)
