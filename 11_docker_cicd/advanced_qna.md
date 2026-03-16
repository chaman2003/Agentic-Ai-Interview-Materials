# Docker + CI/CD — Advanced Q&A & Production Patterns

---

## DOCKER INTERNALS

**Q: What are Docker layers and how does caching work?**
A: Each instruction in a Dockerfile creates an immutable layer. Docker caches layers — if a layer and everything before it haven't changed, the cached layer is reused. Once a layer changes, ALL subsequent layers are rebuilt.

```dockerfile
# BAD — copies entire . first → any code change invalidates pip install layer
FROM python:3.11-slim
COPY . /app                     # INVALIDATES next layer on ANY code change
RUN pip install -r requirements.txt

# GOOD — copy requirements first, install, THEN copy code
FROM python:3.11-slim
COPY requirements.txt .         # only invalidates on requirements change
RUN pip install -r requirements.txt   # cached unless requirements changed
COPY . /app                     # code changes don't force reinstall
```

---

**Q: What is a multi-stage build?**
A: Use multiple `FROM` statements. Build in an environment with all the tools, then copy just the final output to a clean runtime image. Makes the final image MUCH smaller.
```dockerfile
# Stage 1: Build (includes all build tools — large)
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build               # creates /app/dist

# Stage 2: Runtime (only what's needed to run — small)
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Final image is just nginx + built files, not Node.js + node_modules
```

---

**Q: What is the difference between COPY and ADD in Dockerfile?**
A:
- `COPY` — simple file copy. Preferred.
- `ADD` — like COPY but also handles: URLs (download from web), tar files (auto-extract). Only use ADD when you specifically need those features.

**Q: What is the difference between CMD and ENTRYPOINT?**
A:
- `CMD` — default command. Can be overridden by docker run arguments.
- `ENTRYPOINT` — always runs. Arguments from CMD (or docker run) are appended to it.
```dockerfile
# CMD — can override: docker run image python other_script.py
CMD ["python", "app.py"]

# ENTRYPOINT — always runs python: docker run image other_script.py → python other_script.py
ENTRYPOINT ["python"]
CMD ["app.py"]   # default arg to ENTRYPOINT
```

---

## DOCKER NETWORKING

**Q: How do containers communicate in docker-compose?**
A: Docker compose creates a default network. Each service is reachable by its SERVICE NAME as a hostname.
```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb   # 'db' is the hostname!
  db:
    image: postgres:15
```
`app` can reach `db` at hostname `db`. They're on the same virtual network.

**Q: What are the Docker network types?**
A:
- `bridge` (default) — containers on the same bridge can communicate by name
- `host` — container shares host network stack (no isolation)
- `none` — no networking
- `overlay` — multi-host networking (Docker Swarm)

---

## VOLUMES AND PERSISTENCE

**Q: How do you persist data in Docker?**
A: Container filesystem is ephemeral (lost on restart). Persist with:
1. **Named volumes** — Docker manages storage
2. **Bind mounts** — map a host directory into the container

```yaml
services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data   # named volume — persists between restarts

  app:
    volumes:
      - ./src:/app/src   # bind mount — host ./src maps to container /app/src (dev hot-reload)

volumes:
  postgres_data:   # declare the named volume
```

---

## GITHUB ACTIONS ADVANCED

**Q: What are GitHub Actions secrets and how do you use them?**
A: Encrypted environment variables stored in GitHub repo settings → never in code.
```yaml
jobs:
  deploy:
    steps:
      - name: Deploy to server
        env:
          SSH_KEY:    ${{ secrets.SSH_PRIVATE_KEY }}
          SERVER_IP:  ${{ secrets.SERVER_IP }}
        run: |
          echo "$SSH_KEY" > key.pem
          chmod 600 key.pem
          ssh -i key.pem user@$SERVER_IP "cd /app && docker-compose pull && docker-compose up -d"
```

**Q: What is a GitHub Actions matrix?**
A: Run the same job with different parameters — e.g., test across multiple Python versions:
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    os: [ubuntu-latest, windows-latest]

steps:
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
```

---

**Q: What is the difference between `on: push` and `on: pull_request`?**
A:
- `on: push` — triggers on every push to any/specified branch
- `on: pull_request` — triggers when a PR is opened/updated. RUNS IN THE CONTEXT of the PR, can see changes before merge.
```yaml
on:
  push:
    branches: [main]          # run on push to main (e.g., deploy)
  pull_request:
    branches: [main]          # run on PR against main (e.g., test)
```

---

## PRODUCTION DEPLOYMENT PATTERNS

**Q: What is a rolling deployment vs blue-green deployment?**

| Strategy | How It Works | Downtime | Rollback |
|---------|-------------|----------|---------|
| Rolling | Replace instances one by one | None | Slow (roll forward/backward) |
| Blue-Green | Run old (blue) + new (green) simultaneously, switch traffic | None | Instant (flip traffic back) |
| Canary | Send 5% of traffic to new version, gradually increase | None | Easy (reduce canary %) |

**Q: What is an EC2 instance type and how do you pick one?**
A:
- `t3.micro` — burstable, cheap. Good for dev/stage.
- `c5.large` — compute-optimized. Good for CPU-heavy tasks (OCR, ML inference).
- `r5.large` — memory-optimized. Good for databases, caches.
- `p3.2xlarge` — GPU instance. Good for deep learning training (like PRINTCHAKRA's Whisper GPU).

---

**Q: What is a Docker health check?**
A: Docker periodically runs a command to test if your container is healthy. Compose `depends_on: condition: service_healthy` waits for the health check to pass.
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```
```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy   # wait for DB health check before starting app
  db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
```
