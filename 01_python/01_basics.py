# ============================================================
# PYTHON BASICS — Interview Essentials
# ============================================================

# ── VARIABLES & DATA TYPES ──────────────────────────────────
x = 5               # int
pi = 3.14           # float
name = "Chaman"     # str
is_active = True    # bool
nothing = None      # NoneType

print(type(x))      # <class 'int'>

# Everything in Python is an object
print(isinstance(x, int))   # True

# ── STRINGS ─────────────────────────────────────────────────
s = "  hello world  "
print(s.strip())            # "hello world"    remove whitespace
print(s.strip().upper())    # "HELLO WORLD"
print(s.strip().lower())    # "hello world"
print("hello".replace("l", "r"))  # "herro"
print("a,b,c".split(","))   # ['a', 'b', 'c']
print("hello".startswith("he"))   # True
print(len("hello"))         # 5
print("hello"[0])           # 'h'
print("hello"[-1])          # 'o'
print("hello"[1:4])         # 'ell'   slicing [start:end] end is exclusive

# f-strings (use these always)
age = 21
print(f"Name: {name}, Age: {age}")

# ── LISTS ────────────────────────────────────────────────────
lst = [1, 2, 3]
lst.append(4)           # [1, 2, 3, 4]
lst.pop()               # removes last → [1, 2, 3]
lst.pop(0)              # removes index 0 → [2, 3]
print(lst[0])           # 2
print(lst[-1])          # 3
print(len(lst))         # 2
lst.sort()              # sort in place
lst.reverse()           # reverse in place

# Loop
for x in [10, 20, 30]:
    print(x)

# ── DICTS ────────────────────────────────────────────────────
d = {"name": "Chaman", "age": 21}
print(d["name"])            # "Chaman"
print(d.get("city", "N/A")) # "N/A"  — safe get with default
d["city"] = "Bangalore"     # add/update key
d.update({"age": 22})       # update multiple keys
print(d.keys())             # dict_keys(["name","age","city"])
print(d.values())
print(d.items())            # dict_items([("name","Chaman"), ...])

# Loop over dict
for key, value in d.items():
    print(f"{key}: {value}")

# ── SETS ─────────────────────────────────────────────────────
s = {1, 2, 3, 2, 1}  # {1, 2, 3} — no duplicates
s.add(4)
s.remove(1)
print(2 in s)     # True — O(1) lookup (fast!)

# ── TUPLES ───────────────────────────────────────────────────
t = (1, 2, 3)     # immutable list — cannot change after creation
print(t[0])       # 1
# t[0] = 9        # ERROR — tuples are immutable
# Use tuples for fixed data: coordinates, RGB values, etc.

# ── CONTROL FLOW ─────────────────────────────────────────────
score = 85
if score >= 90:
    print("A")
elif score >= 75:
    print("B")
else:
    print("C")

# for + range
for i in range(5):          # 0,1,2,3,4
    print(i)

for i in range(1, 10, 2):  # 1,3,5,7,9
    print(i)

# while
count = 0
while count < 3:
    print(count)
    count += 1

# break and continue
for i in range(10):
    if i == 5:
        break       # stop loop
    if i % 2 == 0:
        continue    # skip even numbers
    print(i)        # prints 1, 3

# ── FUNCTIONS ────────────────────────────────────────────────
def greet(name):
    return f"Hello {name}"

# Default arguments
def greet_with_title(name, title="Mr"):
    return f"Hello {title}. {name}"

print(greet_with_title("Chaman"))           # Hello Mr. Chaman
print(greet_with_title("Priya", "Ms"))      # Hello Ms. Priya

# Multiple return values (returns a tuple)
def min_max(lst):
    return min(lst), max(lst)

low, high = min_max([3, 1, 4, 1, 5])
print(low, high)   # 1 5
