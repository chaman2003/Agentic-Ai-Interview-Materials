# ============================================================
# GENERATORS + CONTEXT MANAGERS — Interview Essentials
# ============================================================

import time
import contextlib

# ── GENERATORS ───────────────────────────────────────────────
# A generator uses 'yield' instead of 'return'
# It is LAZY — produces values ONE AT A TIME
# Does NOT load everything into memory at once

def count_up(n):
    """Generate numbers from 0 to n-1"""
    for i in range(n):
        yield i   # pause here, send value, resume on next()

g = count_up(5)
print(next(g))   # 0
print(next(g))   # 1
print(next(g))   # 2
# After all values are exhausted, raises StopIteration

# Loop over generator
for val in count_up(3):
    print(val)   # 0, 1, 2


# Real use case: process huge files line by line
def read_large_file(filepath):
    """Read file one line at a time — never loads entire file"""
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()

# Usage:
# for line in read_large_file("huge.csv"):
#     process(line)   # only one line in memory at a time!


# Generator for infinite sequences
def fibonacci():
    a, b = 0, 1
    while True:   # infinite!
        yield a
        a, b = b, a + b

fib = fibonacci()
for _ in range(8):
    print(next(fib), end=" ")   # 0 1 1 2 3 5 8 13
print()


# ── GENERATOR EXPRESSIONS ────────────────────────────────────
# Like list comprehension but LAZY (uses less memory)

# List comprehension — creates entire list in memory
lst = [x * 2 for x in range(1000000)]    # uses lots of memory

# Generator expression — lazy, uses almost no memory
gen = (x * 2 for x in range(1000000))   # parentheses not brackets

print(sum(gen))   # works fine, processes values one at a time


# ── CONTEXT MANAGERS ─────────────────────────────────────────
# The 'with' statement
# Guarantees cleanup even if an exception occurs

# Built-in example — file always closes
with open("test.txt", "w") as f:
    f.write("hello")
# file.close() is called automatically here

# Without 'with', you'd need try/finally:
# f = open("file.txt")
# try:
#     data = f.read()
# finally:
#     f.close()   # must always close


# ── WRITE YOUR OWN CONTEXT MANAGER (class-based) ────────────
class Timer:
    def __enter__(self):
        """Called at the start of 'with' block"""
        self.start = time.time()
        return self   # value bound to 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called at the end of 'with' block (even if exception)"""
        elapsed = time.time() - self.start
        print(f"Elapsed: {elapsed:.4f}s")
        return False  # False = don't suppress exceptions

with Timer() as t:
    time.sleep(0.1)
    print("doing work...")
# prints: Elapsed: 0.1001s


# ── WRITE YOUR OWN CONTEXT MANAGER (generator-based) ─────────
# Simpler way using @contextlib.contextmanager

@contextlib.contextmanager
def timer():
    start = time.time()
    try:
        yield   # execution of 'with' block happens here
    finally:
        print(f"Elapsed: {time.time() - start:.4f}s")

with timer():
    time.sleep(0.05)
    print("working...")


# Database connection context manager (common pattern)
@contextlib.contextmanager
def get_db_connection(url):
    import sqlite3
    conn = sqlite3.connect(url)
    try:
        yield conn          # provide connection to 'with' block
        conn.commit()       # commit if no exception
    except Exception:
        conn.rollback()     # rollback on exception
        raise
    finally:
        conn.close()        # always close connection

# Usage:
# with get_db_connection("mydb.db") as conn:
#     conn.execute("INSERT INTO users VALUES (?)", ("Chaman",))


# ── INTERVIEW SUMMARY ────────────────────────────────────────
"""
Q: What is a generator?
A: A function that uses 'yield' to produce values lazily, one at a time.
   Memory efficient — great for large datasets or infinite sequences.

Q: Generator vs list comprehension?
A: List comprehension creates all values in memory immediately.
   Generator expression is lazy — values are created on demand.

Q: What is a context manager?
A: An object that implements __enter__ and __exit__ (or uses
   @contextmanager). Used with 'with' statement to guarantee cleanup.

Q: Why use 'with open()' instead of just open()?
A: 'with' guarantees the file is closed even if an exception occurs.
   It's equivalent to a try/finally block.
"""
