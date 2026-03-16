# ============================================================
# COLLECTIONS + LOGGING + FILE I/O — Interview Essentials
# ============================================================

from collections import defaultdict, Counter, deque
import logging
import json
from pathlib import Path

# ── DEFAULTDICT ───────────────────────────────────────────────
# Like a regular dict but automatically creates a default value for missing keys
# Avoids KeyError when accessing a key that doesn't exist

# Without defaultdict — would need:
# if "fruits" not in d: d["fruits"] = []
# d["fruits"].append("apple")

# With defaultdict:
d = defaultdict(list)   # default value is an empty list
d["fruits"].append("apple")
d["fruits"].append("banana")
d["vegs"].append("carrot")
print(dict(d))  # {'fruits': ['apple', 'banana'], 'vegs': ['carrot']}

# Group words by first letter
words = ["apple", "ant", "bat", "ball", "cat"]
grouped = defaultdict(list)
for word in words:
    grouped[word[0]].append(word)
print(dict(grouped))    # {'a': ['apple', 'ant'], 'b': ['bat', 'ball'], 'c': ['cat']}

# defaultdict(int) — default value is 0, great for counting
counter = defaultdict(int)
for char in "hello world":
    counter[char] += 1
print(dict(counter))


# ── COUNTER ───────────────────────────────────────────────────
# Count occurrences of things

nums = [1, 1, 2, 3, 2, 1, 4]
c = Counter(nums)
print(c)                    # Counter({1: 3, 2: 2, 3: 1, 4: 1})
print(c[1])                  # 3 — count of 1s
print(c.most_common(2))      # [(1, 3), (2, 2)] — top 2

# Count characters in a string
c = Counter("mississippi")
print(c)    # Counter({'s': 4, 'i': 4, 'p': 2, 'm': 1})

# Subtract counts
c.subtract("ssi")
print(c["s"])   # 2 (was 4, minus 2)


# ── DEQUE ─────────────────────────────────────────────────────
# Double-ended queue — O(1) append/pop from BOTH ends
# Regular list: pop(0) is O(n) because it shifts all elements
# Deque: popleft() is O(1)

dq = deque([1, 2, 3])
dq.append(4)        # add to right  → [1, 2, 3, 4]
dq.appendleft(0)    # add to left   → [0, 1, 2, 3, 4]
dq.pop()            # remove right  → [0, 1, 2, 3]
dq.popleft()        # remove left   → [1, 2, 3]
print(dq)

# Use as a sliding window (maxlen)
recent = deque(maxlen=3)   # automatically removes oldest when full
recent.append(1)           # [1]
recent.append(2)           # [1, 2]
recent.append(3)           # [1, 2, 3]
recent.append(4)           # [2, 3, 4] — 1 was removed


# ── LOGGING ───────────────────────────────────────────────────
# Always use logging in production — not print()

# Get a named logger (best practice)
logger = logging.getLogger(__name__)

# Configure logging (do this once at app startup)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Log levels (from lowest to highest severity):
logger.debug("Dev detail — variable x=5")          # DEBUG
logger.info("User logged in successfully")           # INFO
logger.warning("Disk space below 10%")              # WARNING
logger.error("Database connection failed")           # ERROR
logger.critical("Server is completely down!")        # CRITICAL

# In production: set level to INFO or WARNING to reduce noise
# logging.basicConfig(level=logging.INFO)

# Log with extra data
user_id = 42
logger.info(f"Processing request for user {user_id}")

# Log exceptions
try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("Division failed")   # logs traceback automatically


# ── FILE I/O ─────────────────────────────────────────────────
# Always use 'with' — guarantees file is closed

# Write a file
with open("sample.txt", "w") as f:
    f.write("Hello World\n")
    f.write("Line 2\n")

# Read entire file
with open("sample.txt", "r") as f:
    content = f.read()
    print(content)

# Read line by line (memory efficient for large files)
with open("sample.txt", "r") as f:
    for line in f:
        print(line.strip())

# Append to file
with open("sample.txt", "a") as f:
    f.write("Appended line\n")

# Using pathlib (cleaner, modern way)
p = Path("data/config.txt")
# p.read_text()   — read entire file
# p.write_text("content")   — write entire file
# p.exists()   — check if file exists
# p.parent.mkdir(parents=True, exist_ok=True)  — create dirs

# ── JSON ─────────────────────────────────────────────────────
data = {"name": "Chaman", "age": 21, "skills": ["Python", "Flask"]}

# Python dict → JSON string
json_string = json.dumps(data, indent=2)
print(json_string)

# JSON string → Python dict
loaded = json.loads(json_string)
print(loaded["name"])   # Chaman

# Read JSON from file
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    config = {}

# Write JSON to file
with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
