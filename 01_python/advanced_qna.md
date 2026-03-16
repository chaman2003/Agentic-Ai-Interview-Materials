# Python — Advanced Q&A, Tricky Questions & Variations

---

## TRICKY OUTPUT QUESTIONS

**Q: What does this print?**
```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```
**A:** `[1, 2, 3, 4]`
Because lists are mutable and `b = a` makes both variables point to the SAME list in memory. To make a copy: `b = a.copy()` or `b = a[:]`.

---

**Q: What does this print?**
```python
def add_item(item, lst=[]):
    lst.append(item)
    return lst

print(add_item(1))
print(add_item(2))
print(add_item(3))
```
**A:** `[1]`, `[1, 2]`, `[1, 2, 3]`
**Classic trap.** Default mutable arguments are created ONCE when the function is defined and shared across all calls. Fix:
```python
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

---

**Q: What does this print?**
```python
x = 5
def foo():
    print(x)
    x = 10

foo()
```
**A:** `UnboundLocalError`
Because Python sees `x = 10` inside the function and treats `x` as a local variable for the ENTIRE function scope. But then `print(x)` runs before `x = 10`, so `x` is uninitialized. Fix: declare `global x` at the top of the function, or pass `x` as a parameter.

---

**Q: What does this print?**
```python
funcs = [lambda: i for i in range(3)]
print(funcs[0](), funcs[1](), funcs[2]())
```
**A:** `2 2 2`
**Classic closure trap.** All lambdas capture the SAME `i` variable (by reference, not by value). By the time they're called, the loop has finished and `i = 2`. Fix:
```python
funcs = [lambda i=i: i for i in range(3)]  # capture by default arg
```

---

**Q: What does this print?**
```python
print(0.1 + 0.2 == 0.3)
```
**A:** `False`
Floating point precision issue. `0.1 + 0.2 = 0.30000000000000004`. Fix:
```python
import math
math.isclose(0.1 + 0.2, 0.3)   # True
round(0.1 + 0.2, 10) == 0.3    # True
```

---

**Q: What does this print?**
```python
a = (1,)
b = (1)
print(type(a), type(b))
```
**A:** `<class 'tuple'> <class 'int'>`
A single-element tuple REQUIRES a trailing comma. `(1)` is just `1` in parentheses.

---

**Q: What does this print?**
```python
print(bool(0), bool(""), bool([]), bool({}), bool(None))
print(bool(1), bool("a"), bool([0]), bool({"k": False}))
```
**A:** `False False False False False` (all falsy)
`True True True True` (all truthy)
Falsy values: `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `None`, `False`

---

## SCOPE AND CLOSURES

**Q: Explain LEGB rule.**
A: Python looks up variables in this order:
1. **L**ocal — inside the current function
2. **E**nclosing — in any outer function (for closures)
3. **G**lobal — module-level variables
4. **B**uilt-in — Python built-ins (`len`, `range`, etc.)

---

**Q: What is `nonlocal` and when do you use it?**
A: `nonlocal` lets an inner function modify a variable in the enclosing function's scope. Without it, inner functions can READ outer variables but not WRITE to them.
```python
def counter():
    count = 0
    def increment():
        nonlocal count    # without this, count += 1 would fail
        count += 1
        return count
    return increment

c = counter()
print(c())  # 1
print(c())  # 2
```

---

**Q: Write a closure that makes a multiplier.**
```python
def make_multiplier(n):
    def multiply(x):
        return x * n   # n is captured from enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15
```

---

## MUTABILITY IN DEPTH

**Q: What happens when you pass a list to a function?**
A: Python is "pass by object reference." The function gets a reference to the same list — mutations INSIDE the function affect the original. But reassigning the variable inside the function doesn't affect the original.
```python
def mutate(lst):
    lst.append(99)     # MODIFIES original  ← shared reference
    lst = [1, 2, 3]   # REASSIGNS local var ← doesn't affect original

a = [10, 20]
mutate(a)
print(a)  # [10, 20, 99] — append happened, reassignment didn't
```

---

**Q: How do you make a true deep copy?**
```python
import copy

lst = [[1, 2], [3, 4]]
shallow = lst.copy()       # or lst[:]
deep    = copy.deepcopy(lst)

lst[0].append(99)
print(shallow[0])  # [1, 2, 99] — shallow copy shares nested objects
print(deep[0])     # [1, 2]     — deep copy is fully independent
```

---

## DECORATORS IN DEPTH

**Q: Write a timing decorator.**
```python
import functools, time

def timer(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start  = time.time()
        result = fn(*args, **kwargs)
        end    = time.time()
        print(f"{fn.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_fn():
    time.sleep(1)

slow_fn()  # slow_fn took 1.0012s
```

---

**Q: Write a retry decorator with max attempts.**
```python
import functools, time

def retry(max_attempts=3, delay=1):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise Exception(f"All {max_attempts} attempts failed")
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success"
```

---

**Q: Write a cache/memoize decorator.**
```python
import functools

def memoize(fn):
    cache = {}
    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

# Python has this built-in:
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_builtin(n):
    if n <= 1: return n
    return fib_builtin(n-1) + fib_builtin(n-2)
```

---

## GENERATORS IN DEPTH

**Q: What is the difference between a generator and a list comprehension?**
```python
# List comprehension — ALL values created immediately in memory
squares_list = [x**2 for x in range(1000000)]  # uses ~8MB

# Generator expression — lazy, one value at a time
squares_gen  = (x**2 for x in range(1000000))  # uses ~200 bytes

# Both support the same iteration:
for val in squares_gen:
    if val > 100: break
```

---

**Q: What is `yield from`?**
```python
def chain(*iterables):
    for it in iterables:
        yield from it   # delegates to sub-generator

list(chain([1,2], [3,4], [5,6]))
# [1, 2, 3, 4, 5, 6]

# Equivalent to:
def chain_manual(*iterables):
    for it in iterables:
        for item in it:
            yield item
```

---

**Q: How do generators save memory? Real example.**
```python
# Reading a 10GB log file — DON'T load it all into memory
def read_large_file(filepath):
    with open(filepath) as f:
        for line in f:       # file object is itself a generator!
            yield line.strip()

# Process millions of records without memory issues
def find_errors(filepath):
    for line in read_large_file(filepath):
        if "ERROR" in line:
            yield line

# Only one line is in memory at a time
for error in find_errors("app.log"):
    print(error)
```

---

## OOP IN DEPTH

**Q: What is the MRO (Method Resolution Order)?**
A: In multiple inheritance, Python uses C3 linearization to decide which parent's method to call. You can see it with `ClassName.__mro__`.
```python
class A:
    def speak(self): return "A"

class B(A):
    def speak(self): return "B"

class C(A):
    def speak(self): return "C"

class D(B, C):   # Inherits from both
    pass

d = D()
print(d.speak())     # "B" — MRO: D → B → C → A
print(D.__mro__)     # (D, B, C, A, object)
```

---

**Q: Difference between `__new__` and `__init__`?**
A: `__new__` creates the object (allocates memory). `__init__` initializes it (sets attributes). `__new__` runs first, returns the new instance, then `__init__` receives it.
```python
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance   # always returns same object
```

---

**Q: What is `__slots__`?**
A: Restricts which attributes an object can have. Saves memory by avoiding the per-instance `__dict__`.
```python
class Point:
    __slots__ = ["x", "y"]   # only x and y allowed
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
# p.z = 3  → AttributeError! z not in __slots__
```

---

## ASYNC PYTHON

**Q: What is `asyncio` and when do you use it?**
A: `asyncio` enables concurrent I/O-bound tasks in a single thread using cooperative multitasking. Use for: multiple API calls, database queries, file I/O that you want to run concurrently.
```python
import asyncio, aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    return await asyncio.gather(*tasks)    # run all concurrently

# vs doing them sequentially — much faster for 10+ API calls
results = asyncio.run(fetch_all(["https://api.com/1", "https://api.com/2"]))
```

---

**Q: `threading` vs `multiprocessing` vs `asyncio` — when to use each?**

| Scenario | Tool | Why |
|----------|------|-----|
| Many API calls / DB queries | `asyncio` | I/O-bound, single thread, event loop |
| CPU-heavy (OCR, ML, encoding) | `multiprocessing` | Bypasses GIL, true parallel CPUs |
| Legacy blocking I/O libraries | `threading` | GIL released during I/O waits |
| GPU operations (PyTorch CUDA) | Threading OK | CUDA ops release GIL |

---

## TYPE HINTS

**Q: Write a fully type-annotated Python function.**
```python
from typing import Optional, Union, List, Dict, Tuple, Any

def process_user(
    user_id: int,
    name: str,
    tags: List[str],
    metadata: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    if not name:
        return False, "Name required"
    return True, f"Processed user {user_id}"

# Python 3.10+ shorthand:
def greet(name: str | None = None) -> str:   # | instead of Union
    return f"Hello {name}" if name else "Hello"
```

---

## COMMON INTERVIEW VARIATIONS

**Q: How would you flatten a nested list?**
```python
nested = [[1, 2], [3, [4, 5]], 6]

# Simple one level
flat = [item for sublist in nested for item in sublist]

# Recursive (any depth)
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

# One-liner with itertools
from itertools import chain
flat = list(chain.from_iterable([[1,2],[3,4],[5]]))
```

---

**Q: How do you merge two dicts?**
```python
a = {"x": 1, "y": 2}
b = {"y": 3, "z": 4}

# Python 3.9+
merged = a | b          # {"x":1, "y":3, "z":4} — b wins on conflict

# Python 3.5+
merged = {**a, **b}     # same result

# Old way
merged = a.copy()
merged.update(b)
```

---

**Q: How do you sort a list of dicts by a key?**
```python
users = [{"name": "Charlie", "age": 30}, {"name": "Alice", "age": 25}]

by_age  = sorted(users, key=lambda u: u["age"])
by_name = sorted(users, key=lambda u: u["name"])

# Multiple keys (sort by age, then by name)
multi = sorted(users, key=lambda u: (u["age"], u["name"]))

# In-place sort
users.sort(key=lambda u: u["age"], reverse=True)

# More readable with itemgetter
from operator import itemgetter
users.sort(key=itemgetter("age"))
```

---

**Q: What are common Python performance tips?**
A:
- Use `set` for membership tests: `x in my_set` is O(1) vs `x in my_list` is O(n)
- Use list comprehensions over for loops — faster, more Pythonic
- Use generators for large data — don't load everything into memory
- Use `join()` to concatenate strings: `"".join(lst)` vs `+` in a loop
- Use `collections.defaultdict` and `Counter` instead of manual counting
- Profile before optimizing: `cProfile`, `line_profiler`
- Use `__slots__` for memory optimization in large object counts
- `lru_cache` for expensive deterministic functions
