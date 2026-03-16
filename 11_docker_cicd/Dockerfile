# ============================================================
# DOCKERFILE — Flask App — Interview Essentials
# ============================================================

# 1. Start from official Python image
#    -slim = smaller image (no dev tools, docs, etc.)
FROM python:3.11-slim

# 2. Set working directory inside the container
WORKDIR /app

# 3. Copy requirements FIRST (before code)
#    Why: Docker caches layers. If requirements don't change,
#    this layer is cached → pip install doesn't run again → faster builds
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your code
COPY . .

# 6. Expose port (documentation only — doesn't actually publish the port)
EXPOSE 5000

# 7. Run the application
CMD ["python", "app.py"]

# ── MULTI-STAGE BUILD (for smaller production images) ─────────
# Build stage: install everything
# FROM python:3.11 AS builder
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --user -r requirements.txt
#
# Final stage: only copy what you need
# FROM python:3.11-slim
# COPY --from=builder /root/.local /root/.local
# COPY . .
# CMD ["python", "app.py"]

# ── COMMON DOCKER COMMANDS ─────────────────────────────────────
# docker build -t myapp:latest .          → build image
# docker run -p 5000:5000 myapp           → run container
# docker run -d -p 5000:5000 --name myapp myapp  → run in background
# docker ps                               → list running containers
# docker logs myapp                       → view logs
# docker exec -it myapp bash              → shell into container
# docker stop myapp                       → stop container
# docker rm myapp                         → remove container
# docker images                           → list images
# docker rmi myapp                        → remove image
# docker push myrepo/myapp:latest         → push to Docker Hub
