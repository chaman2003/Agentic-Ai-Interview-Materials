# ============================================================
# SOLID PRINCIPLES — With Python Examples
# ============================================================
# SOLID = 5 principles for writing maintainable OOP code

# ── S — Single Responsibility Principle ──────────────────────
# A class should have only ONE reason to change
# BAD: one class does everything
# GOOD: each class has one job

# BAD — handles data, validation, formatting, saving
class BadCaseManager:
    def create_case(self, title, amount, party_email):
        if not title:
            raise ValueError("Title required")     # validation
        if amount <= 0:
            raise ValueError("Amount must be positive")
        email_body = f"Dear party, your case {title} has been created"   # formatting
        print(f"Sending to {party_email}: {email_body}")                  # email sending
        # save to db...                                                  # persistence

# GOOD — each class has one responsibility
class CaseValidator:
    def validate(self, title: str, amount: float):
        if not title:    raise ValueError("Title required")
        if amount <= 0:  raise ValueError("Amount must be positive")

class EmailFormatter:
    def format_creation_email(self, case_title: str) -> str:
        return f"Dear party, your case '{case_title}' has been created."

class EmailSender:
    def send(self, to: str, body: str):
        print(f"Sending to {to}: {body}")

class CaseRepository:
    def save(self, case: dict) -> dict:
        return {**case, "id": 1}   # simulate save


# ── O — Open/Closed Principle ─────────────────────────────────
# Open for extension, closed for modification
# Add new behaviour by ADDING code, not CHANGING existing code

# BAD — every new processor type requires modifying this function
def process_document_bad(doc_type: str, content: str) -> str:
    if doc_type == "pdf":
        return f"PDF: {content}"
    elif doc_type == "image":
        return f"OCR: {content}"
    elif doc_type == "audio":      # had to modify existing code!
        return f"Audio: {content}"

# GOOD — add new processor by creating new class, not modifying existing
from abc import ABC, abstractmethod

class Processor(ABC):
    @abstractmethod
    def process(self, content: str) -> str: ...

class PDFProcessor(Processor):
    def process(self, content: str) -> str:
        return f"PDF: {content}"

class ImageProcessor(Processor):
    def process(self, content: str) -> str:
        return f"OCR: {content}"

class AudioProcessor(Processor):   # NEW: just add a class, no existing code changed
    def process(self, content: str) -> str:
        return f"Audio: {content}"


# ── L — Liskov Substitution Principle ─────────────────────────
# Subclasses should be substitutable for their parent class
# If you replace a parent with a child, everything should still work

# VIOLATION — Square breaks rectangle's contract
class Rectangle:
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h
    def set_width(self, w): self.w = w
    def set_height(self, h): self.h = h

class Square(Rectangle):
    def set_width(self, w):  self.w = self.h = w   # breaks parent behaviour!
    def set_height(self, h): self.w = self.h = h

def test_rectangle(r: Rectangle):
    r.set_width(5); r.set_height(10)
    assert r.area() == 50           # fails for Square! (25 instead of 50)

# FIX: Square and Rectangle shouldn't share a hierarchy — use separate classes


# ── I — Interface Segregation Principle ───────────────────────
# Don't force classes to implement methods they don't need
# Many specific interfaces > one large interface

# BAD — forces all processors to implement everything
class BadProcessor(ABC):
    @abstractmethod
    def extract_text(self): ...
    @abstractmethod
    def transcribe_audio(self): ...   # OCR processor doesn't need this!
    @abstractmethod
    def parse_tables(self): ...       # audio processor doesn't need this!

# GOOD — split into specific interfaces
class TextExtractable(ABC):
    @abstractmethod
    def extract_text(self, content: bytes) -> str: ...

class AudioTranscribable(ABC):
    @abstractmethod
    def transcribe(self, audio: bytes) -> str: ...

class TableParsable(ABC):
    @abstractmethod
    def parse_tables(self, content: bytes) -> list: ...

# Classes only implement what they need:
class OCRProcessor(TextExtractable, TableParsable):
    def extract_text(self, content): return "text from image"
    def parse_tables(self, content): return [["col1", "col2"]]
    # doesn't implement transcribe — doesn't need to!

class WhisperProcessor(AudioTranscribable):
    def transcribe(self, audio): return "transcribed text"


# ── D — Dependency Inversion Principle ───────────────────────
# Depend on abstractions (interfaces), not concrete implementations
# High-level modules shouldn't depend on low-level modules

# BAD — CaseService directly depends on concrete MongoDB
class BadCaseService:
    def __init__(self):
        import pymongo
        self.db = pymongo.MongoClient()["mydb"]["cases"]   # hard-coded!

    def get_case(self, id):
        return self.db.find_one({"_id": id})

# GOOD — depends on abstract interface, inject concrete at runtime
class CaseStore(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> dict | None: ...
    @abstractmethod
    def save(self, case: dict) -> dict: ...

class GoodCaseService:
    def __init__(self, store: CaseStore):   # inject dependency
        self.store = store

    def get_case(self, id: str):
        return self.store.get_by_id(id)

# Now you can swap implementations:
# GoodCaseService(MongoDBStore())         # production
# GoodCaseService(InMemoryStore())        # testing
# GoodCaseService(PostgresStore())        # future migration
