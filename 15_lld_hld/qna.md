# LLD / HLD / System Design — Q&A

---

## SOLID PRINCIPLES

**Q: What are the SOLID principles?**
A:
- **S** — Single Responsibility: one class, one job
- **O** — Open/Closed: open for extension, closed for modification
- **L** — Liskov Substitution: child class can replace parent without breaking things
- **I** — Interface Segregation: many small interfaces > one large interface
- **D** — Dependency Inversion: depend on abstractions, not concrete classes

**Q: Give a real example of the Single Responsibility Principle.**
A: In an API project, separate: `UserValidator` (validates input), `UserRepository` (DB queries), `UserService` (business logic), `UserController` (HTTP handling). If email validation rules change, only `UserValidator` changes — nothing else.

**Q: What is Dependency Injection and why does it matter?**
A: Instead of a class creating its own dependencies (`self.db = MongoDB()`), they're passed in from outside. Benefits: easy to test (inject mock), easy to swap implementations, follows SOLID's Dependency Inversion Principle.

---

## DESIGN PATTERNS

**Q: What is the Singleton pattern and when do you use it?**
A: Only one instance of a class ever exists. Use for: DB connection pool, config manager, logger. In Python: override `__new__`. Warning: makes testing harder — prefer dependency injection where possible.

**Q: What is the Factory pattern?**
A: A function/class that creates objects. Callers ask "give me a processor for PDF" without knowing the class. Decouples object creation from usage.

**Q: What is the Observer pattern? Give a real example.**
A: Objects subscribe to events; when the event fires, all subscribers are notified. Real examples: Socket.IO (PRINTCHAKRA!), DOM events, message queues. Enables loose coupling.

**Q: What is the Repository pattern?**
A: Abstracts all data access behind an interface (`find_by_id`, `save`, `delete`). Business logic doesn't know if data comes from MongoDB, Postgres, or in-memory. Makes testing trivial.

**Q: When would you use Strategy pattern vs Inheritance?**
A: Use Strategy when the algorithm can change at runtime or you have many variants. Use Inheritance when the relationship is truly "is-a" and the algorithm is fixed. Strategy is more flexible and testable.

---

## HLD / SYSTEM DESIGN

**Q: How do you approach a system design question?**
A:
1. Clarify: who are the users? What's the scale?
2. Estimate: requests/sec, storage, bandwidth
3. Draw: client → API → services → DB
4. Design APIs: key endpoints with methods + status codes
5. Design data model: key tables/collections
6. Identify bottlenecks: where will it break at scale?
7. Scaling solutions: cache, queues, sharding, CDN

**Q: What is the CAP theorem?**
A: A distributed system can only guarantee 2 of: Consistency (all nodes same data), Availability (always responds), Partition Tolerance (works despite network splits). Since you always need P, you choose C or A. MongoDB = CP, Cassandra = AP.

**Q: When do you use a cache? What cache pattern do you use?**
A: Cache when: read-heavy, expensive queries, repeated data. Cache-aside pattern: check Redis → miss → query DB → store in cache → return. Set TTL based on how stale data can be.

**Q: How would you design a case management API at scale?**
A: See `02_hld_system_design.md`. Key points: load balancer + 3 API instances, MongoDB for flexible case documents, Redis for frequently-accessed case lists, S3 for document uploads (not API-proxied), message queue for notifications, Socket.IO for real-time status updates.

**Q: Why use a message queue instead of synchronous processing?**
A: Async queue decouples fast operations (create case) from slow ones (send email, process document). Benefits: API stays fast, workers can be scaled independently, if worker crashes the job stays in the queue. Use RabbitMQ, Celery, or AWS SQS.

**Q: What is the difference between horizontal and vertical scaling?**
A:
- **Vertical**: bigger server (more CPU/RAM). Simple but has limits and is a single point of failure.
- **Horizontal**: more servers behind a load balancer. Scales infinitely, resilient. Requires stateless APIs.

**Q: How do you make an API stateless?**
A: Don't store session data on the server between requests. Use JWT tokens (user carries their identity), Redis for shared session/cache (not server memory), object storage for files (not local disk). Stateless = any server can handle any request.
