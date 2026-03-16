# Python Q&A — Interview Ready

---

## BASICS

**Q: What is the difference between a list, tuple, set, and dict?**
A:
- **List** `[1,2,3]` — ordered, mutable, allows duplicates. Use when order matters and you'll modify it.
- **Tuple** `(1,2,3)` — ordered, **immutable**. Use for fixed data (coordinates, DB records).
- **Set** `{1,2,3}` — unordered, **no duplicates**, O(1) lookup. Use to remove duplicates or check membership.
- **Dict** `{"k":"v"}` — key-value pairs, O(1) access by key. Use when you need to look up by name.

**Q: What is the difference between `is` and `==`?**
A: `==` checks if values are equal. `is` checks if they are the same object in memory.
```python
a = [1, 2]
b = [1, 2]
print(a == b)   # True  — same values
print(a is b)   # False — different objects
```

**Q: What does `None` mean in Python?**
A: `None` is Python's null value — it represents "nothing" or "no value". It's the only instance of `NoneType`.

**Q: What is a mutable vs immutable type?**
A: Mutable can be changed after creation (list, dict, set). Immutable cannot (int, str, tuple, bool). Strings look mutable but every operation creates a new string.

---

## FUNCTIONS

**Q: What are *args and **kwargs?**
A:
- `*args` collects extra positional arguments into a **tuple**.
- `**kwargs` collects extra keyword arguments into a **dict**.
```python
def fn(*args, **kwargs):
    print(args)    # (1, 2, 3)
    print(kwargs)  # {'x': 10}

fn(1, 2, 3, x=10)
```

**Q: What is a lambda function?**
A: An anonymous one-line function. `lambda x: x * 2` is equivalent to:
```python
def double(x):
    return x * 2
```
Use for short operations passed to `map/filter/sort`.

**Q: What is the difference between `map()` and `filter()`?**
A: `map(fn, lst)` applies `fn` to every item and returns all results. `filter(fn, lst)` keeps only items where `fn` returns True.

---

## OOP

**Q: What is the difference between instance variables and class variables?**
A: Instance variables (`self.name`) belong to each individual object. Class variables (`Dog.count`) are shared across ALL instances.

**Q: What is `self` in Python?**
A: `self` refers to the current instance of the class. It's always the first parameter of any instance method. Python passes it automatically — you don't pass it when calling.

**Q: What is the difference between `__str__` and `__repr__`?**
A: `__str__` is for end users — `print(obj)` calls it. `__repr__` is for developers — used in debuggers and REPLs. `__repr__` should show how to recreate the object.

**Q: What is method overriding?**
A: When a child class defines a method with the same name as the parent class, the child's version runs. Use `super().method()` to also call the parent's version.

**Q: What is an abstract class?**
A: A class that cannot be instantiated and forces subclasses to implement specific methods. Use `from abc import ABC, abstractmethod`.

**Q: What is the Singleton pattern?**
A: Ensures only ONE instance of a class is ever created. Useful for config, database connections, loggers.

**Q: What is the Factory pattern?**
A: A function/method that creates objects without exposing the creation logic. Caller just says "give me a processor of type X", not "create a new OCRProcessor()".

---

## DECORATORS

**Q: What is a decorator?**
A: A function that takes a function and returns a new (wrapped) function. `@decorator` is syntactic sugar for `fn = decorator(fn)`. Used to add behavior (logging, auth, caching) without modifying the original function.

**Q: What does `functools.wraps` do?**
A: Preserves the original function's `__name__` and `__doc__`. Without it, all decorated functions appear as "wrapper" in stack traces and debuggers.

**Q: Can decorators take arguments?**
A: Yes, but you need 3 levels: outer function (takes args) → decorator function (takes fn) → wrapper function (takes fn's args).

---

## GENERATORS

**Q: What is a generator?**
A: A function that uses `yield` instead of `return`. It produces values lazily — one at a time. Pauses execution at each `yield` and resumes on the next `next()` call.

**Q: Why use generators instead of lists?**
A: Memory efficiency. A list creates all values in memory upfront. A generator creates values on demand. Critical for processing large files or infinite sequences.

**Q: What is the difference between a generator function and a generator expression?**
A: Generator function uses `def` + `yield`. Generator expression uses parentheses `(x for x in ...)` — like list comprehension but lazy.

---

## CONTEXT MANAGERS

**Q: Why use `with open()` instead of `open()`?**
A: The `with` statement guarantees `file.close()` is called even if an exception occurs. Otherwise you need `try/finally` manually.

**Q: What are `__enter__` and `__exit__`?**
A: `__enter__` runs at the start of the `with` block (returns the value for `as`). `__exit__` runs at the end, even if an exception occurred. It receives exception info as arguments.

---

## COLLECTIONS

**Q: When would you use `defaultdict` over a regular dict?**
A: When you need to group data and don't want to check if a key exists first. `defaultdict(list)` auto-creates an empty list for new keys.

**Q: What is `Counter`?**
A: A dict subclass that counts hashable objects. `Counter("hello")` → `{'l': 2, 'h': 1, 'e': 1, 'o': 1}`. `.most_common(n)` returns the n most frequent items.

**Q: Why use `deque` instead of a list for a queue?**
A: List's `pop(0)` is O(n) because it shifts all elements left. `deque.popleft()` is O(1) — it's a doubly-linked list internally.

---

## EXCEPTIONS

**Q: What is the difference between `except Exception` and `except`:?**
A: `except Exception` catches most exceptions (not system-exiting ones like `SystemExit`, `KeyboardInterrupt`). Bare `except:` catches everything including those — generally bad practice.

**Q: What does `finally` do?**
A: Runs always — whether an exception occurred or not. Use for cleanup (closing connections, releasing locks).

**Q: How do you create a custom exception?**
A: Inherit from `Exception`. Optionally override `__init__` to add extra attributes.
```python
class AppError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code
```

---

## ASYNC / ASYNCIO

**Q: What is asyncio?**
A: Python's built-in async framework. Uses coroutines and an event loop to handle many I/O-bound tasks concurrently — without threads. Perfect for APIs, DB calls, file I/O.

**Q: async def vs regular def?**
A: `async def` defines a coroutine. Calling it returns a coroutine object (not the result). Must be `await`ed inside another `async def` or run via `asyncio.run()`.

**Q: What does `await` do?**
A: Suspends the current coroutine and lets the event loop run other tasks while waiting for the result. Other work can proceed — no blocking.
```python
async def main():
    result = await fetch_data()  # Suspends here, event loop does other work
    return result
```

**Q: asyncio.gather() vs asyncio.wait()?**
A:
- `gather(*coros)`: Runs all coroutines concurrently, returns results in order. Cancels all if any raises (by default).
- `wait(coros, return_when=...)`: More control — `FIRST_COMPLETED`, `FIRST_EXCEPTION`, `ALL_COMPLETED`. Returns sets (done, pending).
```python
# gather — simple parallel execution
results = await asyncio.gather(fetch_user(), fetch_posts(), fetch_comments())

# wait — stop at first success
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
```

**Q: What is asyncio.Semaphore?**
A: Limits concurrent coroutines. Like a connection pool — only N can run at once.
```python
sem = asyncio.Semaphore(10)

async def fetch(url):
    async with sem:
        return await http.get(url)
```

**Q: What is asyncio.Queue?**
A: Async producer-consumer queue. `await queue.put(item)` and `await queue.get()` are non-blocking.
Use for rate limiting, worker pools, streaming data pipelines.

**Q: What is the difference between CPU-bound and I/O-bound?**
A: I/O-bound: Spends time waiting for network/disk → asyncio is perfect.
   CPU-bound: Spends time computing → needs threading or multiprocessing. asyncio won't help (GIL).

**Q: How to run blocking code in asyncio?**
A: Use `loop.run_in_executor()` to run blocking code in a thread pool without blocking the event loop.
```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_function, args)
```

**Q: What is asyncio.create_task()?**
A: Schedules a coroutine to run concurrently. Unlike `await`, it doesn't pause the current coroutine.
```python
task = asyncio.create_task(background_job())
await other_work()  # Background job runs while this runs
await task          # Wait for it when you need the result
```

---

## TYPE HINTS

**Q: Why use type hints?**
A: Documentation in code, IDE autocompletion, static analysis (mypy, pyright), catch bugs before runtime. All valid Python still — hints are not enforced at runtime.

**Q: What is TypeVar?**
A: A type placeholder for generics. Lets you say "input and output are the same type" without fixing which type.
```python
T = TypeVar('T')

def first(lst: list[T]) -> T:
    return lst[0]
```

**Q: What is Protocol?**
A: Structural typing (duck typing with type safety). An object satisfies a Protocol if it has the required methods — no need to inherit.
```python
class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None: print("O")  # Satisfies Drawable without inheriting

def render(obj: Drawable) -> None:
    obj.draw()
```

**Q: TypedDict vs dataclass vs NamedTuple?**
A:
- `TypedDict`: Typed dict for JSON-like data. Still a real dict at runtime. Use for API responses.
- `dataclass`: Auto-generates `__init__`, `__repr__`, etc. Mutable by default. Use for model objects.
- `NamedTuple`: Immutable, tuple-backed. Efficient. Use for immutable records.
```python
class UserDict(TypedDict):    # dict at runtime
    name: str
    age: int

@dataclass
class UserClass:              # class at runtime
    name: str
    age: int

class UserTuple(NamedTuple):  # tuple at runtime
    name: str
    age: int
```

**Q: What is Optional vs Union?**
A: `Optional[X]` = `Union[X, None]`. Means the value can be X or None.
```python
def find_user(id: int) -> Optional[User]:  # Can return User or None
    ...
```

**Q: What is `Literal`?**
A: Restricts a value to specific literal values.
```python
def set_role(role: Literal["admin", "user", "guest"]) -> None: ...
```

**Q: What is `NewType`?**
A: Creates a distinct type alias for documentation and type safety without runtime overhead.
```python
UserId = NewType('UserId', int)
user_id = UserId(42)  # int at runtime, UserId in type checker
```

---

## DATACLASSES & ADVANCED OOP

**Q: What is a dataclass?**
A: Decorator that auto-generates `__init__`, `__repr__`, `__eq__` from class annotations. Less boilerplate than manual class.
```python
@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"

p = Point(1.0, 2.0)  # __init__ auto-generated
```

**Q: Dataclass frozen=True?**
A: Makes instances immutable (raises FrozenInstanceError on assignment). Also enables hashing (can be used in sets/dicts).

**Q: Dataclass post_init?**
A: `__post_init__` runs after the auto-generated `__init__`. Use for validation or computed fields.
```python
@dataclass
class Circle:
    radius: float

    def __post_init__(self):
        if self.radius <= 0:
            raise ValueError("Radius must be positive")
        self.area: float = 3.14 * self.radius ** 2
```

**Q: What is a metaclass?**
A: A class whose instances are classes. Controls class creation. `type` is the default metaclass.
Use cases: enforce singleton, register plugins, auto-add methods.
```python
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    pass
```

**Q: What is a descriptor?**
A: Object that defines `__get__`, `__set__`, `__delete__`. Used to add validation or computed behavior to attribute access.
```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")
        obj.__dict__[self.name] = value

class Product:
    price = Positive()
    quantity = Positive()
```

---

## PERFORMANCE & BEST PRACTICES

**Q: What is list comprehension vs generator expression?**
A: List compehension `[x for x in ...]` builds entire list in memory. Generator expression `(x for x in ...)` yields one item at a time. Use generators for large data.

**Q: What is `__slots__`?**
A: Restricts instance attributes to a fixed set. Saves memory (no `__dict__` per instance). Speeds up attribute access.
```python
class Point:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y
```

**Q: What is memoization in Python?**
A: Cache function results to avoid recomputation. Use `@functools.lru_cache(maxsize=128)` or `@functools.cache` (unbounded).
```python
@functools.lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Q: GIL — Global Interpreter Lock?**
A: CPython mutex that prevents multiple threads from executing Python bytecode simultaneously. Means threading doesn't give CPU parallelism. Use `multiprocessing` for CPU-bound parallel work, `asyncio` or `threading` for I/O-bound.

**Q: Difference between threading and multiprocessing?**
A: Threading: Shared memory, GIL limits CPU parallelism, good for I/O-bound.
   Multiprocessing: Separate memory per process, true CPU parallelism, good for CPU-bound. Higher overhead.

---

## COMMON TRICKY QUESTIONS

**Q: Mutable default argument trap?**
A: Default mutable arguments are shared across all calls — a Python gotcha:
```python
# BAD
def add_item(item, lst=[]):   # Same list reused every call!
    lst.append(item)
    return lst

# GOOD
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

**Q: What is the LEGB rule?**
A: Variable lookup order: Local → Enclosing → Global → Built-in. Python looks up names in this order.

**Q: What is `__all__`?**
A: List of public names exported when `from module import *` is used. Doesn't restrict direct imports.

**Q: Difference between `del` and removing from a collection?**
A: `del x` removes name binding (or item). If nothing else refers to the object, it gets garbage collected.
   `list.remove(x)` removes first occurrence by value. `del list[i]` removes by index.

**Q: What is `__init__.py`?**
A: Makes a directory a Python package. Can be empty or contain package initialization code. Python 3 supports implicit namespace packages without it.
