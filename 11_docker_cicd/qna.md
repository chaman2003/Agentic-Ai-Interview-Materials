# Docker + CI/CD + Kubernetes Q&A — Comprehensive

---

## DOCKER FUNDAMENTALS

**Q: What is Docker?**
A: A platform for running applications in isolated containers. A container is a lightweight, portable environment with everything the app needs (code, runtime, dependencies). "Works on my machine" problem is solved — runs the same everywhere because the container includes its own filesystem and dependencies.

**Q: What is the difference between a Docker image and a container?**
A: Image = blueprint (read-only, layered filesystem). Container = running instance of an image. Like class vs object. Build an image once, run many containers from it. Each container is an isolated process.

**Q: What is a Dockerfile?**
A: A text file with instructions to build a Docker image. Each instruction creates a new layer in the image.
- `FROM` — base image
- `WORKDIR` — set working directory
- `COPY` / `ADD` — copy files into image
- `RUN` — execute command during build
- `ENV` — set environment variable
- `EXPOSE` — document the port
- `CMD` / `ENTRYPOINT` — command to run on container start

**Q: CMD vs ENTRYPOINT?**
A:
- `CMD` — default command, easily overridden at runtime: `docker run myimage python other.py`
- `ENTRYPOINT` — fixed command, arguments are appended: `docker run myimage --verbose`
- Together: `ENTRYPOINT ["python"]` + `CMD ["app.py"]` → run `python app.py`, override CMD to change script

**Q: Why copy requirements.txt before the code?**
A: Docker caches each layer. If `requirements.txt` hasn't changed, the `pip install` layer is cached and doesn't re-run — much faster builds. If you copy all code first, any code change invalidates the pip cache.

**Q: What is a multi-stage build?**
A: Using multiple `FROM` statements in one Dockerfile to reduce final image size. Build artifacts are created in a "builder" stage, then only the binary/artifact is copied to the final slim image.
```dockerfile
# Stage 1: Build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (only ~50MB vs ~400MB)
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Q: What is .dockerignore?**
A: File that prevents files from being sent to the Docker build context (like `.gitignore`). Include: `node_modules`, `.git`, `*.log`, `.env`, `dist`. Reduces build time and prevents sensitive files from entering the image.

**Q: What is the difference between RUN, CMD, and ENTRYPOINT?**
A:
- `RUN` — executes during image BUILD, creates a new layer
- `CMD` — executes when CONTAINER starts, only the last CMD is used
- `ENTRYPOINT` — main container command, not overridden by `docker run` args (unlike CMD)

---

## DOCKER INTERNALS

**Q: How do Docker containers work under the hood?**
A: Containers are NOT virtual machines. They are Linux processes with isolation:
- **Namespaces** — isolate what the process can SEE (PID, network, filesystem, users, IPC)
- **cgroups** (control groups) — limit what resources the process can USE (CPU, memory, I/O)
- **Union filesystem (overlay2)** — layered filesystem, each image layer is read-only, container adds a read-write layer on top

**Q: What is a Docker layer?**
A: Each Dockerfile instruction creates an immutable layer. Layers are cached and shared between images. If `FROM node:18` is used by 10 images, the layer is stored once on disk. The final image is the union of all layers.

**Q: What is the Docker build context?**
A: The set of files sent to the Docker daemon when you run `docker build`. Everything in the current directory is sent. Use `.dockerignore` to exclude large or sensitive files.

**Q: Container vs Virtual Machine?**
A:
| | Container | VM |
|-|-----------|-----|
| Isolation | Process-level | Hardware-level |
| OS | Shares host kernel | Own guest OS |
| Boot time | Milliseconds | Minutes |
| Size | MB | GB |
| Performance | Near-native | Overhead from hypervisor |

**Q: What are Docker volumes?**
A: Mechanism for persisting container data beyond the container's lifecycle.
- **Named volumes**: `docker volume create mydata` — managed by Docker
- **Bind mounts**: Host directory mounted into container → used in development for live reload
- **tmpfs mounts**: In-memory, not persisted

**Q: What are Docker networks?**
A:
- `bridge` (default) — isolated network for containers on same host. Containers communicate by name in compose.
- `host` — container shares host network stack (no isolation, better performance)
- `none` — no networking
- `overlay` — multi-host networking for Docker Swarm/Kubernetes

---

## DOCKER COMPOSE

**Q: What is docker-compose?**
A: Tool to run multi-container applications with a single `docker-compose.yml` file. Define services, volumes, and networks. Start everything with `docker-compose up`.

**Q: How do containers communicate in docker-compose?**
A: Docker Compose creates a private network. Services reach each other by service name. If your app service and `db` service are in the same compose file, the DB URL is `postgresql://user:pass@db:5432/mydb`.

**Q: What is the difference between depends_on and health checks?**
A: `depends_on` only waits for the container to START, not for the service inside to be READY. Use `condition: service_healthy` with a `healthcheck` to wait for the DB to be actually ready:
```yaml
db:
  image: postgres
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 5s
    retries: 5

app:
  depends_on:
    db:
      condition: service_healthy
```

**Q: docker-compose up vs docker-compose up --build?**
A: `up` — starts containers, uses existing image if available. `up --build` — always rebuilds the image before starting.

---

## KUBERNETES

**Q: What is Kubernetes (K8s)?**
A: Container orchestration platform. Automates deployment, scaling, self-healing, and management of containerized apps across a cluster of machines.

**Q: Pod vs Deployment vs Service?**
A:
- **Pod** — smallest unit, wraps one or more containers. Ephemeral.
- **Deployment** — manages a set of identical Pods, handles rolling updates, restarts.
- **Service** — stable network endpoint (IP + DNS name) that load-balances to a set of Pods.

**Q: What is the difference between ClusterIP, NodePort, and LoadBalancer?**
A:
- `ClusterIP` — internal only, accessible within the cluster (default)
- `NodePort` — exposes on static port on every node's IP. External access via `NodeIP:NodePort`
- `LoadBalancer` — creates a cloud load balancer (AWS ELB, GCP LB). External traffic → LB → Service → Pods

**Q: What is an Ingress?**
A: An API object that manages external HTTP/HTTPS routing to services. One Ingress resource replaces many LoadBalancer services (cheaper). Requires an Ingress Controller (nginx, Traefik, etc.) to be installed.

**Q: What is the difference between liveness and readiness probes?**
A:
- **Liveness probe** — "Is the app alive?" Fails → container restarts. Use for deadlocked apps.
- **Readiness probe** — "Is the app ready for traffic?" Fails → removed from Service endpoints (no traffic). Use during startup and when temporarily unable to serve (e.g., loading data).

**Q: What is a ConfigMap vs Secret?**
A:
- **ConfigMap** — non-sensitive config data (env vars, config files)
- **Secret** — sensitive data (passwords, API keys, TLS certs). Base64 encoded, but NOT encrypted at rest by default. Enable etcd encryption in production.

**Q: What is HPA (Horizontal Pod Autoscaler)?**
A: K8s controller that automatically scales Pod replicas based on CPU/memory/custom metrics. Checks metrics every 15 seconds (default). Requires `metrics-server` to be installed.

**Q: What is a rolling update?**
A: Kubernetes gradually replaces old Pods with new ones, ensuring the app stays available throughout. `maxSurge` allows extra pods during update; `maxUnavailable` limits how many can be down.

**Q: How does blue-green deployment work in K8s?**
A: Deploy two Deployments (blue = current, green = new). Service selector points to blue. When green is ready, switch the selector: `kubectl patch service app -p '{"spec":{"selector":{"version":"green"}}}'`. Zero downtime. Instant rollback by switching selector back.

**Q: What is a Namespace?**
A: Virtual cluster within a K8s cluster. Provides resource isolation between teams or environments. Resources in different namespaces don't see each other by default (RBAC + NetworkPolicy).

**Q: What is a PersistentVolume (PV) and PersistentVolumeClaim (PVC)?**
A:
- **PV** — actual storage resource (provisioned by admin or dynamically)
- **PVC** — request for storage by a user/app. K8s binds the PVC to a matching PV.
- **StorageClass** — defines how PVs are dynamically provisioned (e.g., AWS gp3, GCP pd-ssd)

**Q: Kubernetes vs Docker Compose?**
A:
- Compose: Local dev, simple multi-container. No self-healing, no auto-scaling, no rolling updates.
- K8s: Production at scale. Self-healing, HPA, rolling updates, RBAC, multi-node.

---

## GITHUB ACTIONS / CI/CD

**Q: What is GitHub Actions?**
A: A CI/CD platform built into GitHub. Define workflows in `.github/workflows/*.yml`. Trigger on push, pull request, schedule, manual dispatch, etc.

**Q: What is CI vs CD?**
A:
- **CI** (Continuous Integration) — automatically run tests, linting, build on every push. Merge to main only when all checks pass.
- **CD** (Continuous Delivery) — automatically deploy to staging, manually approve for production.
- **CD** (Continuous Deployment) — automatically deploy to production when CI passes. No manual gate.

**Q: What does `needs` do in GitHub Actions?**
A: Creates a dependency between jobs. `needs: [test, lint]` means this job only runs if both `test` and `lint` succeed first. Creates a workflow graph.

**Q: What is a GitHub Actions secret?**
A: A sensitive value (API key, password, SSH key) stored in GitHub repository settings. Referenced as `${{ secrets.MY_SECRET }}` in workflows. Never visible in logs (masked).

**Q: What is a matrix strategy in GitHub Actions?**
A: Run the same job multiple times with different configurations:
```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    os: [ubuntu-latest, windows-latest]
```
Creates 6 parallel jobs.

**Q: What is a reusable workflow in GitHub Actions?**
A: A workflow file that can be called by other workflows. Avoids duplication across repos. Defined with `on: workflow_call:` and called with `uses: org/repo/.github/workflows/test.yml@main`.

**Q: What is a GitHub Actions artifact?**
A: Files generated during a workflow that you want to share between jobs or download later. Use `actions/upload-artifact` to upload, `actions/download-artifact` to download.

**Q: What are GitHub Actions environments?**
A: Named deployment targets (development, staging, production) with protection rules. Require manual approval, specific reviewers, or branch restrictions before deploying.

**Q: Explain a typical CI/CD pipeline for a containerized app.**
A:
1. **Code push** → triggers workflow
2. **Lint + Test** — unit tests, integration tests, code quality
3. **Build Docker image** — `docker build -t app:$SHA .`
4. **Push to registry** — ECR, Docker Hub, GCR
5. **Security scan** — Trivy or Snyk scan the image for CVEs
6. **Deploy to staging** — `kubectl set image deployment/app app=app:$SHA`
7. **E2E tests** — run against staging
8. **Manual approval** — human approves production deploy
9. **Deploy to production** — rolling update in K8s

**Q: What is a canary deployment in CI/CD?**
A: Deploy new version to a small subset of users/pods (1-5%). Monitor error rates and latency. Gradually increase to 100% if healthy, or rollback if not. Tools: Argo Rollouts, Flagger, or manual K8s approach.

**Q: What is GitOps?**
A: A CI/CD pattern where Git is the single source of truth for infrastructure and application state. All changes are made via Git commits/PRs. An operator (ArgoCD, Flux) watches the Git repo and syncs the cluster state to match.

---

## PYTHON CONCURRENCY (from existing content)

**Q: What is the GIL in Python?**
A: Global Interpreter Lock. Prevents multiple Python threads from executing simultaneously. Only one thread runs at a time. Implications:
- CPU-bound tasks (image processing, OCR) → use `multiprocessing` (separate processes, each with own GIL)
- I/O-bound tasks (API calls, DB queries) → use `asyncio` or `threading` (threads release GIL during I/O)

**Q: multiprocessing vs threading vs asyncio?**
A:
- `multiprocessing` — separate processes, bypass GIL → CPU-bound (OCR, image processing)
- `threading` — threads, GIL limits parallelism, good for I/O-bound tasks (simpler than asyncio)
- `asyncio` — single-threaded event loop, cooperative concurrency → I/O-bound (API calls, DB, websockets)

---

## TRICKY INTERVIEW SCENARIOS

**Q: Your Docker container keeps restarting. How do you debug?**
A:
1. `docker ps -a` — see exit code
2. `docker logs <container-id> --tail 50` — last 50 lines
3. `docker inspect <container-id>` — detailed config and state
4. Exit code 137 = OOM killed → increase memory limit
5. Exit code 1 = application error → check logs
6. Exit code 0 = app exited cleanly → check CMD

**Q: Your K8s pod is in CrashLoopBackOff. What do you do?**
A:
1. `kubectl describe pod <name>` — check Events section for error
2. `kubectl logs <name> --previous` — logs from crashed container
3. Check `restartCount` in describe output
4. Common causes: bad env vars, missing secrets, wrong CMD, port conflict, OOM
5. Temporarily add `sleep infinity` as command to keep it running for investigation

**Q: How do you zero-downtime deploy to Kubernetes?**
A:
1. Set `strategy.type: RollingUpdate` with `maxUnavailable: 0`
2. Set `readinessProbe` so K8s knows when new pods are ready
3. K8s won't send traffic to new pods until readiness passes
4. K8s won't remove old pods until new pods are ready
5. Result: zero downtime even during update

**Q: How do you manage secrets in CI/CD?**
A:
- GitHub: Repository secrets or environment secrets
- Production: HashiCorp Vault, AWS Secrets Manager, K8s Secrets (with etcd encryption)
- NEVER commit secrets to Git, even in private repos
- Rotate secrets regularly, use least-privilege access
