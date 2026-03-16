# ============================================================
# LOW LEVEL DESIGN (LLD) — Design Patterns in Python
# ============================================================
# LLD = designing classes, interfaces, relationships
# 8 most important patterns for interviews

# ── 1. SINGLETON ─────────────────────────────────────────────
# Only ONE instance ever exists
# Use for: DB connection pool, config manager, logger

class DatabaseConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_string: str = ""):
        if self._initialized:
            return   # don't re-initialize
        self.connection_string = connection_string
        self._initialized = True
        print(f"DB connected: {connection_string}")

# Test
db1 = DatabaseConnection("postgres://localhost/mydb")
db2 = DatabaseConnection("postgres://localhost/other")
print(db1 is db2)   # True — same object!
print(db1.connection_string)   # "postgres://localhost/mydb" — first init wins


# ── 2. FACTORY ────────────────────────────────────────────────
# A method/class that creates objects — caller doesn't know the exact class
# Use for: creating different processor types, different notification channels

from abc import ABC, abstractmethod

class DocumentProcessor(ABC):
    @abstractmethod
    def process(self, document: str) -> dict:
        pass

class OCRProcessor(DocumentProcessor):
    def process(self, document: str) -> dict:
        return {"type": "ocr", "text": f"OCR extracted: {document[:50]}"}

class PDFProcessor(DocumentProcessor):
    def process(self, document: str) -> dict:
        return {"type": "pdf", "text": f"PDF parsed: {document[:50]}"}

class WhisperProcessor(DocumentProcessor):
    def process(self, document: str) -> dict:
        return {"type": "audio", "text": f"Whisper transcribed: {document[:50]}"}

# Factory function
def create_processor(doc_type: str) -> DocumentProcessor:
    processors = {
        "image": OCRProcessor,
        "pdf":   PDFProcessor,
        "audio": WhisperProcessor,
    }
    cls = processors.get(doc_type)
    if not cls:
        raise ValueError(f"Unknown processor type: {doc_type}")
    return cls()

# Usage
processor = create_processor("pdf")
result    = processor.process("my document content")
# Client doesn't know if it's OCR, PDF, or Whisper — just calls .process()


# ── 3. OBSERVER ───────────────────────────────────────────────
# Objects subscribe to events. When an event happens, all subscribers are notified.
# Use for: event systems, real-time updates, Socket.IO is this pattern!

class EventEmitter:
    def __init__(self):
        self._subscribers: dict[str, list] = {}

    def on(self, event: str, callback):
        """Subscribe to an event."""
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)

    def emit(self, event: str, data=None):
        """Fire an event — notifies all subscribers."""
        for callback in self._subscribers.get(event, []):
            callback(data)

# Usage
emitter = EventEmitter()

# Subscribe
emitter.on("case_created",  lambda d: print(f"Email: New case {d['id']}"))
emitter.on("case_created",  lambda d: print(f"Slack: Case {d['id']} created"))
emitter.on("case_resolved", lambda d: print(f"DB: Closing case {d['id']}"))

# Trigger
emitter.emit("case_created",  {"id": "CASE-001", "title": "Smith vs Jones"})
# → "Email: New case CASE-001"
# → "Slack: Case CASE-001 created"


# ── 4. STRATEGY ────────────────────────────────────────────────
# Swap algorithms at runtime without changing the client code
# Use for: sorting algorithms, payment methods, file parsing strategies

class TextChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        pass

class FixedSizeChunking(TextChunkingStrategy):
    def __init__(self, size=500, overlap=50):
        self.size, self.overlap = size, overlap

    def chunk(self, text: str) -> list[str]:
        chunks, i = [], 0
        while i < len(text):
            chunks.append(text[i:i+self.size])
            i += self.size - self.overlap
        return chunks

class SentenceChunking(TextChunkingStrategy):
    def chunk(self, text: str) -> list[str]:
        sentences = text.split(". ")
        return [" ".join(sentences[i:i+5]) for i in range(0, len(sentences), 5)]

# Context class — uses whatever strategy is injected
class DocumentPipeline:
    def __init__(self, chunking_strategy: TextChunkingStrategy):
        self.chunking_strategy = chunking_strategy   # inject strategy

    def set_strategy(self, strategy: TextChunkingStrategy):
        self.chunking_strategy = strategy   # swap at runtime!

    def process(self, text: str) -> list[str]:
        return self.chunking_strategy.chunk(text)

# Swap strategies without changing DocumentPipeline
pipeline = DocumentPipeline(FixedSizeChunking(size=200))
chunks   = pipeline.process("long document text here...")

pipeline.set_strategy(SentenceChunking())   # switch strategy
chunks = pipeline.process("same document")


# ── 5. DECORATOR PATTERN (not Python decorator syntax!) ───────
# Add behaviour to objects dynamically without modifying their class
# Python decorators (@) implement this concept

class TextProcessor(ABC):
    @abstractmethod
    def process(self, text: str) -> str:
        pass

class BaseTextProcessor(TextProcessor):
    def process(self, text: str) -> str:
        return text

class LowercaseDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).lower()   # adds lowercase behaviour

class StripDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).strip()   # adds strip behaviour

# Chain decorators
processor = StripDecorator(LowercaseDecorator(BaseTextProcessor()))
result    = processor.process("  HELLO WORLD  ")   # "hello world"


# ── 6. REPOSITORY PATTERN ─────────────────────────────────────
# Abstracts data access behind an interface
# Swap database implementations without changing business logic
# Use in: production APIs to separate business logic from DB queries

class CaseRepository(ABC):
    @abstractmethod
    def find_by_id(self, case_id: str) -> dict | None:
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> list[dict]:
        pass

    @abstractmethod
    def save(self, case: dict) -> dict:
        pass

class MongoDBCaseRepository(CaseRepository):
    def __init__(self, collection):
        self.collection = collection

    def find_by_id(self, case_id: str) -> dict | None:
        return self.collection.find_one({"_id": case_id})

    def find_by_status(self, status: str) -> list[dict]:
        return list(self.collection.find({"status": status}))

    def save(self, case: dict) -> dict:
        result = self.collection.insert_one(case)
        case["id"] = str(result.inserted_id)
        return case

class InMemoryCaseRepository(CaseRepository):
    """Use for testing — no real DB needed."""
    def __init__(self):
        self._store = {}

    def find_by_id(self, case_id: str) -> dict | None:
        return self._store.get(case_id)

    def find_by_status(self, status: str) -> list[dict]:
        return [c for c in self._store.values() if c["status"] == status]

    def save(self, case: dict) -> dict:
        self._store[case["id"]] = case
        return case

# Service uses repository — doesn't know which DB is underneath
class CaseService:
    def __init__(self, repo: CaseRepository):   # inject dependency
        self.repo = repo

    def create_case(self, title: str, amount: float) -> dict:
        case = {"id": "CASE-001", "title": title, "amount": amount, "status": "open"}
        return self.repo.save(case)

# Test with in-memory repo (no DB needed!)
test_service = CaseService(InMemoryCaseRepository())
# Production with MongoDB
# prod_service = CaseService(MongoDBCaseRepository(db.cases))


# ── 7. BUILDER PATTERN ────────────────────────────────────────
# Build complex objects step by step
# Use for: constructing complex queries, request objects, configurations

class QueryBuilder:
    def __init__(self, collection: str):
        self._collection = collection
        self._filters  = {}
        self._sort     = {}
        self._limit    = 100
        self._skip     = 0
        self._fields   = {}

    def where(self, field: str, value) -> "QueryBuilder":
        self._filters[field] = value
        return self   # return self for chaining!

    def sort_by(self, field: str, ascending: bool = True) -> "QueryBuilder":
        self._sort[field] = 1 if ascending else -1
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def skip(self, n: int) -> "QueryBuilder":
        self._skip = n
        return self

    def select(self, *fields) -> "QueryBuilder":
        self._fields = {f: 1 for f in fields}
        return self

    def build(self) -> dict:
        return {
            "collection": self._collection,
            "filter":     self._filters,
            "sort":       self._sort,
            "limit":      self._limit,
            "skip":       self._skip,
            "projection": self._fields,
        }

# Builder chaining — very readable
query = (QueryBuilder("cases")
    .where("status", "open")
    .where("client_id", "CLIENT-123")
    .sort_by("created_at", ascending=False)
    .limit(20)
    .skip(0)
    .select("title", "amount", "status")
    .build()
)
