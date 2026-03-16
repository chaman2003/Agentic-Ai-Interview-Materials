# ============================================================
# PYTHON PATTERNS & VARIATIONS
# Different ways to write the same thing — know all approaches
# ============================================================

# ── 1. LOOPING OVER A LIST ────────────────────────────────────
nums = [1, 2, 3, 4, 5]

# Version 1: classic for loop
result = []
for n in nums:
    result.append(n * 2)

# Version 2: list comprehension (preferred)
result = [n * 2 for n in nums]

# Version 3: map (functional)
result = list(map(lambda n: n * 2, nums))

# Version 4: map with named function
def double(n): return n * 2
result = list(map(double, nums))

# All produce: [2, 4, 6, 8, 10]

# ── 2. FILTERING A LIST ──────────────────────────────────────
# Version 1: for loop
evens = []
for n in nums:
    if n % 2 == 0:
        evens.append(n)

# Version 2: list comprehension with condition (preferred)
evens = [n for n in nums if n % 2 == 0]

# Version 3: filter (functional)
evens = list(filter(lambda n: n % 2 == 0, nums))

# ── 3. COUNTING OCCURRENCES ───────────────────────────────────
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

# Version 1: manual dict
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1

# Version 2: defaultdict
from collections import defaultdict
counts = defaultdict(int)
for w in words:
    counts[w] += 1

# Version 3: Counter (best and most Pythonic)
from collections import Counter
counts = Counter(words)   # {"apple": 3, "banana": 2, "cherry": 1}
print(counts.most_common(2))  # [("apple", 3), ("banana", 2)]

# ── 4. READING A FILE ─────────────────────────────────────────
# Version 1: old way (can forget to close)
f = open("file.txt", "r")
content = f.read()
f.close()

# Version 2: with statement (always use this!)
with open("file.txt", "r") as f:
    content = f.read()

# Version 3: read all lines as a list
with open("file.txt", "r") as f:
    lines = f.readlines()    # ["line1\n", "line2\n"]

# Version 4: iterate line by line (memory efficient for large files)
with open("file.txt", "r") as f:
    for line in f:
        process(line.strip())

# Version 5: pathlib (modern, cleaner)
from pathlib import Path
content = Path("file.txt").read_text()
lines   = Path("file.txt").read_text().splitlines()

# ── 5. MERGING DICTIONARIES ──────────────────────────────────
a = {"x": 1, "y": 2}
b = {"y": 3, "z": 4}

# Version 1: update (mutates a)
merged = a.copy(); merged.update(b)   # y=3 (b wins)

# Version 2: ** unpacking (Python 3.5+)
merged = {**a, **b}

# Version 3: | operator (Python 3.9+)
merged = a | b

# ── 6. CHECKING IF SOMETHING EXISTS ──────────────────────────
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

# Version 1: for loop
found = None
for u in users:
    if u["id"] == 2:
        found = u
        break

# Version 2: next() with default (best one-liner)
found = next((u for u in users if u["id"] == 2), None)

# Version 3: filter
found = next(filter(lambda u: u["id"] == 2, users), None)

# ── 7. FLATTENING A LIST ─────────────────────────────────────
nested = [[1, 2], [3, 4], [5, 6]]

# Version 1: nested comprehension
flat = [item for sublist in nested for item in sublist]

# Version 2: itertools.chain
from itertools import chain
flat = list(chain.from_iterable(nested))

# Version 3: sum (hacky, readable)
flat = sum(nested, [])   # sum([[1,2],[3,4],[5,6]], []) concatenates to [1,2,3,4,5,6]

# ── 8. CREATING A CLASS — 4 WAYS ─────────────────────────────
# Version 1: traditional class
class Point1:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point1({self.x}, {self.y})"

# Version 2: namedtuple (immutable, less code)
from collections import namedtuple
Point2 = namedtuple("Point2", ["x", "y"])
p = Point2(1, 2)       # p.x = 1, p.y = 2 (immutable!)

# Version 3: dataclass (Python 3.7+ — nice syntax, mutable)
from dataclasses import dataclass, field
@dataclass
class Point3:
    x: float
    y: float
    label: str = ""   # optional with default
    # auto-generates __init__, __repr__, __eq__!

# Version 4: TypedDict (for type hints on dicts — not really a class)
from typing import TypedDict
class Point4(TypedDict):
    x: float
    y: float

p4: Point4 = {"x": 1.0, "y": 2.0}

# ── 9. EXCEPTION HANDLING PATTERNS ───────────────────────────
import json

# Version 1: catch everything (bad — hides bugs)
try:
    data = json.loads("bad json")
except:
    data = {}

# Version 2: catch specific exception (good)
try:
    data = json.loads("bad json")
except json.JSONDecodeError as e:
    print(f"Parse error: {e}")
    data = {}

# Version 3: multiple exceptions
try:
    result = risky_operation()
except (ValueError, TypeError) as e:
    print(f"Value/Type error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected: {e}")
    raise   # re-raise unexpected errors!
finally:
    cleanup()

# Version 4: custom exception hierarchy
class AppError(Exception):
    def __init__(self, message, code=500):
        super().__init__(message)
        self.code = code

class NotFoundError(AppError):
    def __init__(self, resource):
        super().__init__(f"{resource} not found", code=404)

class ValidationError(AppError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}", code=400)

# ── 10. FUNCTIONAL VS OOP VS PROCEDURAL ──────────────────────
users = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 17}]

# Procedural
adults = []
for u in users:
    if u["age"] >= 18:
        adults.append(u["name"].upper())

# Functional (map + filter + chain)
adults = list(map(
    lambda u: u["name"].upper(),
    filter(lambda u: u["age"] >= 18, users)
))

# Python-style (list comprehension — most Pythonic)
adults = [u["name"].upper() for u in users if u["age"] >= 18]

# OOP
class UserManager:
    def __init__(self, users):
        self.users = users

    def get_adult_names(self):
        return [u["name"].upper() for u in self.users if u["age"] >= 18]

manager = UserManager(users)
adults = manager.get_adult_names()

# ── 11. ASYNC VARIATIONS ─────────────────────────────────────
import asyncio

# Sequential async (each waits for previous)
async def sequential():
    r1 = await fetch_user(1)
    r2 = await fetch_order(1)
    return r1, r2

# Concurrent async (all run at same time — much faster)
async def concurrent():
    r1, r2 = await asyncio.gather(
        fetch_user(1),
        fetch_order(1)
    )
    return r1, r2

# With error handling
async def concurrent_safe():
    results = await asyncio.gather(
        fetch_user(1),
        fetch_order(1),
        return_exceptions=True   # don't fail if one fails
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"One task failed: {r}")
        else:
            process(r)
