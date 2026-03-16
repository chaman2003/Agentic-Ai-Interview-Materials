# ============================================================
# PYTHON INTERMEDIATE — Interview Essentials
# ============================================================

# ── *ARGS AND **KWARGS ────────────────────────────────────────
# *args → any number of positional arguments → stored as tuple
def add_all(*args):
    return sum(args)

print(add_all(1, 2, 3, 4))   # 10

# **kwargs → any number of keyword arguments → stored as dict
def show_info(**kwargs):
    for key, val in kwargs.items():
        print(f"{key}: {val}")

show_info(name="Chaman", age=21, city="Bangalore")

# Both together
def combined(required, *args, **kwargs):
    print(required, args, kwargs)

combined("hello", 1, 2, x=10, y=20)

# ── LIST COMPREHENSIONS ──────────────────────────────────────
# Pattern: [expression for item in iterable if condition]

# Simple
squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]

# With condition
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]

# Replaces:
# result = []
# for x in range(10):
#     if x % 2 == 0:
#         result.append(x)

# ── DICT COMPREHENSIONS ──────────────────────────────────────
data = {"a": 1, "b": 2, "c": 3}
doubled = {k: v * 2 for k, v in data.items()}  # {'a': 2, 'b': 4, 'c': 6}

# ── LAMBDA ───────────────────────────────────────────────────
# Anonymous function — use for short, one-line functions
double = lambda x: x * 2
print(double(5))   # 10

add = lambda a, b: a + b
print(add(3, 4))   # 7

# ── MAP AND FILTER ────────────────────────────────────────────
nums = [1, 2, 3, 4, 5]

# map: apply function to every item
doubled = list(map(lambda x: x * 2, nums))   # [2, 4, 6, 8, 10]

# filter: keep items where function returns True
evens = list(filter(lambda x: x % 2 == 0, nums))  # [2, 4]

# ── ZIP ──────────────────────────────────────────────────────
names = ["Alice", "Bob", "Charlie"]
scores = [90, 85, 92]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Create dict from two lists
result = dict(zip(names, scores))  # {'Alice': 90, 'Bob': 85, 'Charlie': 92}

# ── ENUMERATE ────────────────────────────────────────────────
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")  # 0: apple, 1: banana, 2: cherry

# Start from 1
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")  # 1: apple, 2: banana, ...

# ── TRY / EXCEPT / FINALLY ───────────────────────────────────
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Cannot divide by zero!")
        return None
    except TypeError as e:
        print(f"Wrong type: {e}")
        return None
    else:
        # runs only if no exception
        print("Division successful")
        return result
    finally:
        # ALWAYS runs — use for cleanup
        print("divide() finished")

divide(10, 2)   # 5.0
divide(10, 0)   # error message

# ── CUSTOM EXCEPTIONS ─────────────────────────────────────────
class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

class AgeError(ValidationError):
    """Raised when age is invalid"""
    pass

def validate_age(age):
    if age < 0:
        raise AgeError(f"Age cannot be negative: {age}")
    if age > 150:
        raise AgeError(f"Age too large: {age}")
    return True

try:
    validate_age(-5)
except AgeError as e:
    print(f"Invalid age: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
