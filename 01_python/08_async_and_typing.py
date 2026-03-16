"""
═══════════════════════════════════════════════════════════════════════════════
  ASYNC PYTHON, TYPE HINTS & ADVANCED PATTERNS
═══════════════════════════════════════════════════════════════════════════════

This file covers topics NOT in previous Python files:
1. Async Python (asyncio, async/await deep dive)
2. Type Hints & mypy
3. Dataclasses
4. Protocol & Abstract Base Classes
5. Metaclasses
6. Descriptors
7. Python Internals

"""

import asyncio
import aiohttp
from typing import TypeVar, Generic, Protocol, Optional, Union, Literal, TypedDict, Annotated
from dataclasses import dataclass, field, asdict, astuple
from abc import ABC, abstractmethod
import time

# ─── 1. ASYNC PYTHON ──────────────────────────────────────────────────────

"""
asyncio: Python's built-in async framework
Key concepts:
- Event loop: Schedules and runs coroutines
- Coroutine: Function defined with async def
- Task: Wraps coroutine so it can run concurrently
- Future: Represents eventual result of async operation
"""

# Basic async function
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Run a single coroutine
async def main():
    data = await fetch_data("https://api.github.com/users/octocat")
    print(data)

asyncio.run(main())  # Entry point

# ── CONCURRENT TASKS ─────────────────────────────────────────────────────

async def fetch_all_users(user_ids: list[int]) -> list[dict]:
    """Fetch multiple users concurrently (not sequentially!)"""

    async def fetch_one(uid: int) -> dict:
        # Simulate API call
        await asyncio.sleep(0.1)  # Non-blocking sleep
        return {"id": uid, "name": f"User {uid}"}

    # Run all tasks concurrently with gather
    results = await asyncio.gather(*[fetch_one(uid) for uid in user_ids])
    return list(results)

# Timing comparison:
# Sequential:  10 users × 0.1s = 1.0s
# Concurrent:  10 users = ~0.1s (all run at same time!)

# ── ASYNCIO.GATHER vs ASYNCIO.WAIT ────────────────────────────────────────

async def compare_gather_wait():
    async def task(n: int) -> int:
        await asyncio.sleep(n * 0.1)
        return n * n

    # gather: Get all results (or raises on first exception)
    results = await asyncio.gather(task(1), task(2), task(3))
    print(results)  # [1, 4, 9]

    # gather with return_exceptions=True (don't raise, collect errors)
    results = await asyncio.gather(
        task(1), task(2), task(3),
        return_exceptions=True  # Errors become part of results
    )

    # as_completed: Process results as they finish
    tasks = [asyncio.create_task(task(n)) for n in [3, 1, 2]]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"Got {result}")  # Prints in order of completion: 1, 4, 9

    # wait: More control (timeouts, first-completed, etc.)
    done, pending = await asyncio.wait(
        tasks,
        timeout=1.0,
        return_when=asyncio.FIRST_COMPLETED
    )

# ── ASYNCIO ERROR HANDLING ────────────────────────────────────────────────

async def robust_fetch(url: str) -> Optional[dict]:
    """Fetch with timeout and error handling"""
    try:
        async with asyncio.timeout(5.0):  # 5 second timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()  # Raise if 4xx/5xx
                    return await response.json()
    except asyncio.TimeoutError:
        print(f"Timeout fetching {url}")
        return None
    except aiohttp.ClientError as e:
        print(f"HTTP error: {e}")
        return None

# ── ASYNC CONTEXT MANAGERS ────────────────────────────────────────────────

from contextlib import asynccontextmanager

@asynccontextmanager
async def database_connection():
    """Async context manager for DB connections"""
    connection = await create_db_connection()
    try:
        yield connection
    finally:
        await connection.close()

async def use_db():
    async with database_connection() as db:
        result = await db.execute("SELECT * FROM users")
        return result

# ── ASYNC GENERATORS ─────────────────────────────────────────────────────

async def stream_messages(channel: str):
    """Async generator for streaming data"""
    while True:
        message = await redis_client.get_next_message(channel)
        if message is None:
            break
        yield message

async def process_stream():
    async for message in stream_messages("notifications"):
        print(f"Received: {message}")

# ── SEMAPHORES (rate limiting async) ─────────────────────────────────────

async def fetch_with_rate_limit(urls: list[str]) -> list[dict]:
    """Limit concurrent requests using Semaphore"""
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

    async def fetch_one(url: str) -> dict:
        async with semaphore:  # Acquires slot, releases when done
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()

    return await asyncio.gather(*[fetch_one(url) for url in urls])

# ── ASYNC QUEUE (producer-consumer) ──────────────────────────────────────

async def producer_consumer_example():
    queue = asyncio.Queue(maxsize=100)

    async def producer():
        for i in range(50):
            await queue.put(f"task_{i}")
            await asyncio.sleep(0.01)

        await queue.put(None)  # Sentinel to stop consumers

    async def consumer(name: str):
        while True:
            item = await queue.get()
            if item is None:
                await queue.put(None)  # Pass sentinel to next consumer
                break
            print(f"{name} processing {item}")
            await asyncio.sleep(0.05)  # Simulate work
            queue.task_done()

    # Run producer and 3 consumers concurrently
    await asyncio.gather(
        producer(),
        consumer("Worker-1"),
        consumer("Worker-2"),
        consumer("Worker-3")
    )

# ─── 2. TYPE HINTS & MYPY ─────────────────────────────────────────────────

"""
Type hints: Optional annotations that describe expected types
mypy: Static type checker for Python
Benefits: Catch bugs early, better IDE autocomplete, self-documenting code
"""

from typing import (
    Any, Dict, List, Set, Tuple, FrozenSet,
    Optional, Union, Literal, Final,
    Callable, Iterator, Generator, AsyncIterator,
    ClassVar, TypeVar, Generic, Protocol,
    TypedDict, NamedTuple, NewType,
    overload, cast, TYPE_CHECKING
)

# Basic type annotations
def greet(name: str) -> str:
    return f"Hello, {name}"

def calculate(a: int, b: float) -> float:
    return a + b

# Optional (either the type or None)
def find_user(user_id: int) -> Optional[dict]:  # dict | None
    return None  # Could return dict or None

# Union (one of several types)
def process(data: Union[str, bytes, list]) -> None:
    pass

# Python 3.10+ syntax
def process_new(data: str | bytes | list) -> None:
    pass

# Literal (specific values only)
Status = Literal["pending", "active", "inactive"]

def set_status(status: Status) -> None:
    pass

set_status("active")    # ✅ OK
# set_status("unknown")  # ❌ mypy error

# Final (value cannot be reassigned)
MAX_RETRIES: Final = 3

# TypedDict (typed dictionary)
class UserData(TypedDict):
    id: int
    name: str
    email: str
    age: Optional[int]

user: UserData = {"id": 1, "name": "Alice", "email": "alice@example.com"}
# user["invalid_key"]  # ❌ mypy error

# NamedTuple (typed tuple)
class Point(NamedTuple):
    x: float
    y: float
    z: float = 0.0  # Default value

origin = Point(0.0, 0.0)
print(origin.x)  # Access by name
print(origin[0])  # Access by index

# NewType (create distinct type)
UserId = NewType("UserId", int)
ProductId = NewType("ProductId", int)

def get_user(user_id: UserId) -> dict:
    return {}

uid = UserId(42)
pid = ProductId(42)
get_user(uid)   # ✅ OK
# get_user(pid)  # ❌ mypy error (ProductId is not UserId)
# get_user(42)   # ❌ mypy error (plain int is not UserId)

# TypeVar (generic types)
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

def first(items: list[T]) -> Optional[T]:
    return items[0] if items else None

result: Optional[int] = first([1, 2, 3])     # T = int
result2: Optional[str] = first(["a", "b"])    # T = str

# Generic class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> Optional[T]:
        return self._items[-1] if self._items else None

int_stack: Stack[int] = Stack()
int_stack.push(1)    # ✅ OK
# int_stack.push("x")  # ❌ mypy error

# ── PROTOCOL (Structural Subtyping / "Duck Typing") ──────────────────────

class Drawable(Protocol):
    """Anything with a draw() method"""
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Rectangle:
    def draw(self) -> None:
        print("Drawing rectangle")

def render(shape: Drawable) -> None:
    shape.draw()

render(Circle())     # ✅ Works! Circle has draw()
render(Rectangle())  # ✅ Works! Rectangle has draw()

# Unlike ABC, Circle/Rectangle don't inherit from Drawable
# Protocol uses structural typing ("if it walks like a duck...")

# ── CALLABLE TYPES ────────────────────────────────────────────────────────

from typing import Callable

def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

result = apply(lambda x, y: x + y, 3, 4)  # ✅ OK

# Type alias
Predicate = Callable[[int], bool]

def filter_evens(numbers: list[int], pred: Predicate) -> list[int]:
    return [n for n in numbers if pred(n)]

# ── OVERLOAD (function with multiple signatures) ──────────────────────────

@overload
def parse(value: str) -> str: ...
@overload
def parse(value: bytes) -> bytes: ...
@overload
def parse(value: int) -> int: ...

def parse(value):  # Actual implementation
    return value

# ─── 3. DATACLASSES ───────────────────────────────────────────────────────

@dataclass
class User:
    name: str
    email: str
    age: int = 0
    roles: list[str] = field(default_factory=list)  # Mutable default

    # Post-init processing
    def __post_init__(self):
        self.email = self.email.lower()

    # Computed property (not a real field)
    @property
    def is_adult(self) -> bool:
        return self.age >= 18

user = User(name="Alice", email="Alice@Example.com", age=25)
print(user.email)    # alice@example.com (lowercased in post_init)
print(user.is_adult) # True

# Conversion methods
user_dict = asdict(user)    # {'name': 'Alice', 'email': ...}
user_tuple = astuple(user)  # ('Alice', 'alice@example.com', ...)

# Frozen dataclass (immutable)
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 3.0  # ❌ FrozenInstanceError: cannot assign to field 'x'

# Ordered dataclass
@dataclass(order=True)
class SortableItem:
    priority: int
    name: str

items = [SortableItem(3, "C"), SortableItem(1, "A"), SortableItem(2, "B")]
print(sorted(items))  # Sorted by priority, then name

# ─── 4. METACLASSES ────────────────────────────────────────────────────────

"""
Metaclass: The class of a class
"A class is an instance of its metaclass"
Use cases: Singletons, ORMs, plugin systems
"""

class SingletonMeta(type):
    """Metaclass that enforces singleton pattern"""
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected"

db1 = Database()
db2 = Database()
print(db1 is db2)  # True

# Registry metaclass (auto-register subclasses)
class PluginMeta(type):
    registry: dict[str, type] = {}

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if bases:  # Don't register base class itself
            PluginMeta.registry[name] = cls

class Plugin(metaclass=PluginMeta):
    pass

class EmailPlugin(Plugin):
    pass

class SlackPlugin(Plugin):
    pass

print(PluginMeta.registry)  # {'EmailPlugin': ..., 'SlackPlugin': ...}

# ─── 5. DESCRIPTORS ────────────────────────────────────────────────────────

"""
Descriptors: Objects that define how attribute access works
Used by property, classmethod, staticmethod
"""

class Validator:
    """Descriptor that validates value on assignment"""
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if not (self.min_val <= value <= self.max_val):
            raise ValueError(
                f"{self.name} must be between {self.min_val} and {self.max_val}, got {value}"
            )
        obj.__dict__[self.name] = value

class Player:
    health = Validator(0, 100)  # Descriptor instance
    mana = Validator(0, 200)

    def __init__(self, health, mana):
        self.health = health  # Calls Validator.__set__
        self.mana = mana

p = Player(50, 100)
print(p.health)  # Calls Validator.__get__ → 50

try:
    p.health = 200  # Calls Validator.__set__ → raises ValueError
except ValueError as e:
    print(e)  # health must be between 0 and 100, got 200

# ─── 6. PYTHON INTERNALS ───────────────────────────────────────────────────

"""
GIL (Global Interpreter Lock):
- CPython has a GIL that prevents true parallelism for CPU-bound tasks
- Only one thread executes Python bytecode at a time
- I/O-bound: Use threads or asyncio (GIL released during I/O)
- CPU-bound: Use multiprocessing or C extensions (bypass GIL)

Memory management:
- Reference counting: Objects freed when refcount = 0
- Garbage collector: Handles circular references
- Memory pools: Small objects reuse memory blocks

Internals:
- id(): Returns memory address of object
- sys.getrefcount(): Returns reference count
- gc.collect(): Force garbage collection
- dis.dis(): Disassemble function to bytecode
"""

import sys
import gc

# Reference counting
x = [1, 2, 3]
print(sys.getrefcount(x))  # 2 (x + temporary in getrefcount call)

y = x  # Another reference
print(sys.getrefcount(x))  # 3

del x  # Remove one reference
# y still holds reference, list not freed yet

# Circular reference (GC needed)
class CircularRef:
    def __init__(self):
        self.other = None

a = CircularRef()
b = CircularRef()
a.other = b  # a points to b
b.other = a  # b points to a (circular!)

del a, b  # Reference counts don't reach 0 due to circular ref
gc.collect()  # GC detects and frees the cycle

# Disassemble bytecode
import dis

def add(x, y):
    return x + y

dis.dis(add)
# 2           0 LOAD_FAST                0 (x)
#             2 LOAD_FAST                1 (y)
#             4 BINARY_OP               0 (+)
#             8 RETURN_VALUE

# ─── INTERVIEW SUMMARY ──────────────────────────────────────────────────

"""
ASYNC:
Q: What is asyncio?
A: Python framework for single-threaded concurrent code using coroutines.

Q: async def vs regular function?
A: async def creates coroutine. Must be awaited or run with asyncio.run().

Q: asyncio.gather vs asyncio.wait?
A: gather() for when you want all results together.
   wait() for more control (first-completed, timeouts).

Q: How to rate-limit async requests?
A: Use asyncio.Semaphore to limit concurrent operations.

Q: When to use asyncio vs threading vs multiprocessing?
A: asyncio:           I/O-bound, single-threaded, many concurrent operations
   threading:         I/O-bound, but using sync libraries
   multiprocessing:   CPU-bound tasks (bypasses GIL)

TYPE HINTS:
Q: What is Protocol?
A: Structural typing. Any class with matching methods satisfies the Protocol.
   "Duck typing with type annotations."

Q: TypeVar vs Generic?
A: TypeVar names the variable type. Generic[T] uses it in class definition.
   Both together enable type-safe containers like Stack[int].

Q: Optional[X] vs Union[X, None]?
A: They are identical. Optional[X] is just shorthand for Union[X, None].

DATACLASSES:
Q: dataclass vs NamedTuple?
A: dataclass: Mutable by default, supports inheritance, methods, post_init.
   NamedTuple: Immutable, tuple in memory, less overhead.

Q: field(default_factory=list)?
A: Avoids the mutable default argument pitfall.
   (Default args are shared across instances → bugs!)

GIL:
Q: Does Python have true multithreading?
A: Not for CPU-bound code (GIL prevents it).
   True parallelism: Use multiprocessing, concurrent.futures, or C extensions.
"""
