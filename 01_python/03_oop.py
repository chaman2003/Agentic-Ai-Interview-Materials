# ============================================================
# PYTHON OOP — Interview Essentials
# ============================================================

# ── BASIC CLASS ───────────────────────────────────────────────
class Dog:
    # Class variable — shared across ALL instances
    species = "Canis lupus familiaris"
    count = 0

    def __init__(self, name, breed):
        # Instance variables — unique to each object
        self.name = name
        self.breed = breed
        Dog.count += 1

    # __str__: what print(obj) shows — for users
    def __str__(self):
        return f"Dog: {self.name} ({self.breed})"

    # __repr__: developer-facing — for debugging
    def __repr__(self):
        return f"Dog(name='{self.name}', breed='{self.breed}')"

    # __eq__: how == works
    def __eq__(self, other):
        return self.name == other.name and self.breed == other.breed

    # Regular method (takes self)
    def bark(self):
        return f"{self.name} says: Woof!"

    # @property: access method like an attribute (no parentheses)
    @property
    def info(self):
        return f"{self.name} is a {self.breed}"

    # @classmethod: takes cls, not self — used for factory methods
    @classmethod
    def from_string(cls, dog_string):
        """Create a Dog from a string like 'Rex,Labrador'"""
        name, breed = dog_string.split(",")
        return cls(name.strip(), breed.strip())

    # @staticmethod: no self or cls — just a utility function
    @staticmethod
    def is_valid_name(name):
        return len(name) > 0 and name.isalpha()


d1 = Dog("Rex", "Labrador")
d2 = Dog("Max", "Poodle")
print(d1)           # Dog: Rex (Labrador)
print(repr(d1))     # Dog(name='Rex', breed='Labrador')
print(d1.bark())    # Rex says: Woof!
print(d1.info)      # Rex is a Labrador  ← no ()
print(Dog.count)    # 2
d3 = Dog.from_string("Buddy, Beagle")
print(d3)
print(Dog.is_valid_name("Rex"))  # True


# ── INHERITANCE ───────────────────────────────────────────────
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"


class Cat(Animal):
    def __init__(self, name, indoor):
        super().__init__(name)   # call parent __init__
        self.indoor = indoor

    # Method overriding — child's version runs instead of parent's
    def speak(self):
        return f"{self.name} says: Meow!"


class Dog2(Animal):
    def speak(self):
        return f"{self.name} says: Woof!"


cat = Cat("Whiskers", True)
dog = Dog2("Rex")
print(cat.speak())   # Whiskers says: Meow!
print(dog.speak())   # Rex says: Woof!

# isinstance — check if object is an instance of a class or subclass
print(isinstance(cat, Cat))     # True
print(isinstance(cat, Animal))  # True — Cat inherits from Animal
print(isinstance(cat, Dog2))    # False


# ── ABSTRACT CLASSES ─────────────────────────────────────────
from abc import ABC, abstractmethod

class Shape(ABC):
    """Blueprint — forces subclasses to implement area() and perimeter()"""

    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

    def describe(self):  # concrete method — subclasses inherit this
        return f"Area: {self.area()}, Perimeter: {self.perimeter()}"


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        import math
        return math.pi * self.radius ** 2

    def perimeter(self):
        import math
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


# Shape()  # ERROR: cannot instantiate abstract class
c = Circle(5)
print(c.describe())  # Area: 78.5..., Perimeter: 31.4...


# ── DESIGN PATTERNS ──────────────────────────────────────────

# 1. SINGLETON — only one instance ever exists
class Config:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)


config1 = Config()
config2 = Config()
config1.set("debug", True)
print(config2.get("debug"))   # True — same instance!
print(config1 is config2)     # True


# 2. FACTORY — function/method that creates objects without exposing logic
class OCRProcessor:
    def process(self, text):
        return f"OCR: {text}"

class WhisperProcessor:
    def process(self, audio):
        return f"Whisper: {audio}"

def create_processor(processor_type):
    """Factory function"""
    processors = {
        "ocr": OCRProcessor,
        "whisper": WhisperProcessor
    }
    cls = processors.get(processor_type)
    if not cls:
        raise ValueError(f"Unknown processor: {processor_type}")
    return cls()

p = create_processor("ocr")
print(p.process("hello world"))   # OCR: hello world


# 3. OBSERVER — objects subscribe to events and get notified
class EventEmitter:
    def __init__(self):
        self._listeners = {}

    def on(self, event, callback):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def emit(self, event, data=None):
        for cb in self._listeners.get(event, []):
            cb(data)


emitter = EventEmitter()
emitter.on("print_done", lambda data: print(f"Print complete: {data}"))
emitter.on("print_done", lambda data: print(f"Billing for: {data}"))
emitter.emit("print_done", "Document123")
# → Socket.IO in PRINTCHAKRA is exactly this pattern
