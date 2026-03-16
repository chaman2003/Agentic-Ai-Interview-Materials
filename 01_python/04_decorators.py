# ============================================================
# PYTHON DECORATORS — Interview Essentials
# ============================================================

import functools
import time

# ── STEP 1: UNDERSTAND CLOSURES FIRST ────────────────────────
# Inner function "captures" the variable from the outer function
def make_multiplier(n):
    def multiply(x):       # inner function
        return x * n       # captures 'n' from outer scope
    return multiply        # return the function itself

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15


# ── STEP 2: BASIC DECORATOR ───────────────────────────────────
# A decorator = a function that takes a function and returns a new function

def logger(fn):
    def wrapper(*args, **kwargs):          # accept any arguments
        print(f"Calling {fn.__name__}...")
        result = fn(*args, **kwargs)       # call the original function
        print(f"Done.")
        return result
    return wrapper

# Manual way:
def greet(name):
    return f"Hello {name}"

greet = logger(greet)    # wrap it
print(greet("Chaman"))


# The @ syntax is just shorthand for the line above
@logger
def add(a, b):
    return a + b

print(add(3, 4))


# ── STEP 3: PRESERVE FUNCTION METADATA ───────────────────────
# Problem: after decorating, fn.__name__ shows "wrapper" not "greet"
# Fix: use functools.wraps

def better_logger(fn):
    @functools.wraps(fn)   # preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        print(f"Calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

@better_logger
def say_hello(name):
    """Say hello to someone"""
    return f"Hello {name}"

print(say_hello.__name__)   # say_hello  (not "wrapper")
print(say_hello.__doc__)    # "Say hello to someone"


# ── STEP 4: DECORATOR WITH ARGUMENTS ─────────────────────────
# Need 3 levels: outer function takes args, returns decorator, which returns wrapper

def retry(max_attempts):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3)
def unreliable_api_call():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success!"


# ── REAL-WORLD DECORATORS ────────────────────────────────────

# 1. Timer decorator
def timer(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print(f"{fn.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.1)
    return "done"

slow_function()


# 2. Validate input decorator
def require_positive(fn):
    @functools.wraps(fn)
    def wrapper(n):
        if n <= 0:
            raise ValueError(f"Expected positive number, got {n}")
        return fn(n)
    return wrapper

@require_positive
def square_root(n):
    return n ** 0.5

print(square_root(9))    # 3.0
# square_root(-4)        # ValueError


# 3. Cache decorator (memoization)
def memoize(fn):
    cache = {}
    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    return wrapper

@memoize
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(30))   # fast because of caching


# ── INTERVIEW SUMMARY ────────────────────────────────────────
"""
Q: What is a decorator?
A: A function that takes a function and returns a new (wrapped) function.
   Used to add behaviour without modifying the original function.
   @decorator is syntactic sugar for: fn = decorator(fn)

Q: What does functools.wraps do?
A: Preserves the original function's __name__, __doc__, etc.
   Without it, all decorated functions look like "wrapper" to debuggers.

Q: When do you use decorators?
A: Logging, authentication (@login_required), caching (@lru_cache),
   rate limiting, input validation, timing.
"""
