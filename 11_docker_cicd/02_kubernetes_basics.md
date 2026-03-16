# Kubernetes Basics — Comprehensive Guide

---

## CORE CONCEPTS

### What is Kubernetes?
Kubernetes (K8s) is a container orchestration platform that automates deployment, scaling, and management of containerized applications. It groups containers into logical units for easy management and discovery.

**Why Kubernetes?**
- Self-healing: Restarts crashed containers, reschedules on failed nodes
- Auto-scaling: Scale up/down based on CPU/memory/custom metrics
- Service discovery and load balancing: Built-in DNS and load balancing
- Rolling updates and rollbacks: Zero-downtime deployments
- Configuration management: Secrets, ConfigMaps decoupled from images

---

## POD

The smallest deployable unit in Kubernetes. A Pod wraps one or more containers that share network, storage, and lifecycle.

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    app: my-app
    version: "1.0"
spec:
  containers:
  - name: app
    image: my-app:1.0
    ports:
    - containerPort: 3000
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    env:
    - name: NODE_ENV
      value: production
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secrets
          key: password
```

**Pod characteristics:**
- Ephemeral: Pods are disposable, not self-healing
- Shared network namespace: Containers in a Pod communicate via `localhost`
- Shared volumes: Containers can share storage volumes
- Never use bare Pods in production — use Deployments

---

## DEPLOYMENT

Manages a set of identical Pod replicas. Handles rolling updates and rollbacks.

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # max extra pods during update
      maxUnavailable: 0   # min pods always running
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: app
        image: my-app:2.0
        ports:
        - containerPort: 3000
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 15
          periodSeconds: 20
          failureThreshold: 3
```

---

## SERVICE

Stable network endpoint that routes traffic to a set of Pods. Provides load balancing and service discovery.

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app          # routes to pods with this label
  ports:
  - port: 80             # service port (external)
    targetPort: 3000     # container port
  type: ClusterIP        # internal only (default)
```

**Service Types:**
| Type | Accessibility | Use Case |
|------|--------------|----------|
| `ClusterIP` | Internal only | Default, inter-service communication |
| `NodePort` | External via node IP:port | Dev/testing |
| `LoadBalancer` | External via cloud LB | Production on cloud (AWS ELB, GCP LB) |
| `ExternalName` | DNS alias to external service | Point to external DB, SaaS |

---

## CONFIGMAP

Stores non-sensitive configuration data as key-value pairs.

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  NODE_ENV: production
  API_URL: https://api.example.com
  MAX_CONNECTIONS: "100"
  app.properties: |
    log.level=INFO
    feature.flag.dark-mode=true
```

**Using ConfigMap in a Pod:**
```yaml
spec:
  containers:
  - name: app
    env:
    - name: NODE_ENV
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: NODE_ENV
    envFrom:
    - configMapRef:
        name: app-config      # inject ALL keys as env vars
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config  # mount as files
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

---

## SECRET

Stores sensitive data (passwords, tokens, TLS certificates). Base64-encoded (not encrypted by default — use encryption at rest in production).

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secrets
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=   # base64 encoded: echo -n 'password123' | base64
  username: YWRtaW4=           # base64 encoded: admin
```

**Create from command line (easier):**
```bash
kubectl create secret generic db-secrets \
  --from-literal=password=password123 \
  --from-literal=username=admin

kubectl create secret tls tls-secret \
  --cert=tls.crt \
  --key=tls.key
```

---

## NAMESPACE

Virtual cluster within a Kubernetes cluster. Provides isolation between teams/environments.

```bash
# Create namespace
kubectl create namespace staging

# Or declaratively:
# apiVersion: v1
# kind: Namespace
# metadata:
#   name: staging

# Deploy to specific namespace
kubectl apply -f deployment.yaml -n staging

# Set default namespace for context
kubectl config set-context --current --namespace=production
```

**Common namespaces:**
- `default` — where resources go without a namespace specified
- `kube-system` — K8s internal components (DNS, scheduler)
- `kube-public` — public, readable by all users
- Your own: `development`, `staging`, `production`

---

## KUBECTL COMMANDS

```bash
# --- VIEWING RESOURCES ---
kubectl get pods                              # list pods in default namespace
kubectl get pods -n production               # specific namespace
kubectl get pods --all-namespaces            # all namespaces
kubectl get pods -o wide                     # more details (node, IP)
kubectl get pods -o yaml                     # full YAML output
kubectl get all                              # all resource types

kubectl get deployments
kubectl get services
kubectl get configmaps
kubectl get secrets
kubectl get nodes
kubectl get namespaces
kubectl get ingress
kubectl get pv                               # persistent volumes
kubectl get pvc                              # persistent volume claims
kubectl get hpa                              # horizontal pod autoscaler

# --- INSPECTING RESOURCES ---
kubectl describe pod <pod-name>              # detailed info + events
kubectl describe deployment my-app
kubectl describe node <node-name>

# --- APPLYING/DELETING ---
kubectl apply -f deployment.yaml             # create or update
kubectl apply -f ./k8s/                      # apply all YAML in directory
kubectl delete -f deployment.yaml
kubectl delete pod <pod-name>
kubectl delete deployment my-app

# --- LOGS ---
kubectl logs <pod-name>                      # current logs
kubectl logs <pod-name> -f                   # follow (stream) logs
kubectl logs <pod-name> --previous           # logs from crashed container
kubectl logs <pod-name> -c <container-name>  # specific container in pod
kubectl logs -l app=my-app                   # logs from all pods matching label

# --- EXECUTING COMMANDS ---
kubectl exec -it <pod-name> -- bash          # interactive shell
kubectl exec <pod-name> -- ls /app           # single command
kubectl exec -it <pod-name> -c <container> -- sh  # specific container

# --- PORT FORWARDING ---
kubectl port-forward pod/<pod-name> 8080:3000       # local:container
kubectl port-forward svc/<service-name> 8080:80     # forward through service

# --- SCALING ---
kubectl scale deployment my-app --replicas=5
kubectl autoscale deployment my-app --min=2 --max=10 --cpu-percent=70

# --- ROLLOUTS ---
kubectl rollout status deployment/my-app     # watch rollout
kubectl rollout history deployment/my-app    # revision history
kubectl rollout undo deployment/my-app       # rollback to previous
kubectl rollout undo deployment/my-app --to-revision=2  # specific revision
kubectl rollout pause deployment/my-app      # pause rolling update
kubectl rollout resume deployment/my-app     # resume

# --- DEBUGGING ---
kubectl get events --sort-by='.metadata.creationTimestamp'
kubectl top pods                             # CPU/memory usage (requires metrics-server)
kubectl top nodes

# --- CONFIG ---
kubectl config get-contexts
kubectl config use-context my-cluster
kubectl config set-context --current --namespace=production
```

---

## DEPLOYMENT STRATEGIES

### 1. Rolling Update (Default)
Gradually replaces old pods with new ones. Zero downtime.
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1         # allow 1 extra pod during update
    maxUnavailable: 0   # never go below desired replicas
```
**Trade-off:** Two versions run simultaneously during update. Ensure backward compatibility.

### 2. Recreate
Terminates all old pods, then starts new ones. Causes downtime.
```yaml
strategy:
  type: Recreate
```
**Use when:** Versions cannot coexist (DB schema breaking changes).

### 3. Blue-Green Deployment
Run two identical environments (blue=current, green=new). Switch traffic all at once.
```bash
# Deploy green version
kubectl apply -f deployment-green.yaml

# Wait for green to be ready
kubectl rollout status deployment/my-app-green

# Switch service selector from blue to green
kubectl patch service my-app-service -p '{"spec":{"selector":{"version":"green"}}}'

# Keep blue running for quick rollback
# When confident: delete blue
kubectl delete deployment my-app-blue
```

### 4. Canary Deployment
Route a small percentage of traffic to the new version. Gradually increase.
```yaml
# Run 9 replicas of stable (v1) and 1 of canary (v2)
# = ~10% traffic goes to v2
# stable-deployment.yaml
metadata:
  name: my-app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: my-app
      track: stable
  template:
    metadata:
      labels:
        app: my-app
        track: stable
    spec:
      containers:
      - image: my-app:v1

# canary-deployment.yaml
metadata:
  name: my-app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
      track: canary
  template:
    metadata:
      labels:
        app: my-app   # same selector as service
        track: canary
    spec:
      containers:
      - image: my-app:v2
```

---

## HORIZONTAL POD AUTOSCALER (HPA)

Automatically scales the number of Pod replicas based on observed metrics.

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70    # scale when avg CPU > 70%
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 200Mi
```

**Create via CLI:**
```bash
kubectl autoscale deployment my-app --min=2 --max=20 --cpu-percent=70
kubectl get hpa
```

**Requirements:** `metrics-server` must be installed in the cluster.

---

## RESOURCE LIMITS AND REQUESTS

```yaml
spec:
  containers:
  - name: app
    resources:
      requests:              # minimum guaranteed resources
        memory: "64Mi"
        cpu: "100m"          # 100 millicores = 0.1 CPU core
      limits:                # maximum allowed resources
        memory: "256Mi"
        cpu: "500m"          # 500 millicores = 0.5 CPU core
```

**requests** — used for scheduling decisions (K8s finds a node with enough free capacity)
**limits** — CPU throttled at limit; container killed (OOMKilled) if exceeds memory limit

**CPU units:** `1000m = 1 core`. `100m = 10% of one core`
**Memory units:** `Mi = mebibytes`, `Gi = gibibytes`

**Best practice:** Always set both requests and limits. Set requests = actual average usage. Set limits = 2x–3x requests.

---

## HEALTH CHECKS

### Liveness Probe
Detects if a container is stuck (deadlocked). Kubernetes restarts the container if it fails.

### Readiness Probe
Detects if a container is ready to receive traffic. K8s removes it from Service endpoints until it passes.

### Startup Probe
For slow-starting containers. Disables liveness/readiness until startup succeeds.

```yaml
containers:
- name: app
  livenessProbe:
    httpGet:
      path: /healthz
      port: 3000
    initialDelaySeconds: 15    # wait 15s before first check
    periodSeconds: 20          # check every 20s
    failureThreshold: 3        # fail 3 times = restart container
    timeoutSeconds: 5

  readinessProbe:
    httpGet:
      path: /ready
      port: 3000
    initialDelaySeconds: 5
    periodSeconds: 10
    successThreshold: 1
    failureThreshold: 3

  startupProbe:
    httpGet:
      path: /healthz
      port: 3000
    failureThreshold: 30       # allow 30 * 10s = 5 minutes to start
    periodSeconds: 10

# Other probe types:
  livenessProbe:
    exec:
      command: ["cat", "/tmp/healthy"]   # run command in container
  livenessProbe:
    tcpSocket:
      port: 3000               # check TCP connection
```

---

## PERSISTENT VOLUMES (PV, PVC, StorageClass)

### StorageClass — defines the type of storage
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs     # or gke.io/pd, etc.
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Delete                   # or Retain
allowVolumeExpansion: true
```

### PersistentVolume (PV) — actual storage resource (admin creates)
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce                   # only one node can mount read-write
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  awsElasticBlockStore:
    volumeID: vol-xxxxx
    fsType: ext4
```

### PersistentVolumeClaim (PVC) — request for storage (developer creates)
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: fast-ssd        # uses dynamic provisioning
```

**Access Modes:**
- `ReadWriteOnce (RWO)` — one node read-write (most common, e.g., EBS)
- `ReadOnlyMany (ROX)` — many nodes read-only
- `ReadWriteMany (RWX)` — many nodes read-write (NFS, EFS)

**Using PVC in a Pod:**
```yaml
spec:
  containers:
  - name: db
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-pvc
```

---

## INGRESS AND INGRESS CONTROLLER

### Ingress Controller
A reverse proxy (nginx, Traefik, AWS ALB) that implements the Ingress rules. Must be deployed separately.
```bash
# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

### Ingress Resource — routing rules
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod    # TLS via cert-manager
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /api/users
        pathType: Prefix
        backend:
          service:
            name: users-service
            port:
              number: 80
      - path: /api/orders
        pathType: Prefix
        backend:
          service:
            name: orders-service
            port:
              number: 80
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

**Ingress vs LoadBalancer Service:**
- `LoadBalancer` Service creates one cloud load balancer per service (expensive)
- `Ingress` uses a single load balancer with routing rules for many services (cheaper)

---

## HELM BASICS

Helm is the package manager for Kubernetes. A "chart" is a Helm package containing Kubernetes manifests.

### Core Concepts
- **Chart** — package of K8s manifests + templates
- **Release** — installed instance of a chart
- **Repository** — collection of charts
- **values.yaml** — default configuration for a chart

```bash
# --- HELM COMMANDS ---
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm search repo bitnami/postgresql
helm show values bitnami/postgresql      # see all configurable values

# Install a chart
helm install my-postgres bitnami/postgresql \
  --namespace database \
  --create-namespace \
  --set auth.postgresPassword=secret123 \
  --set primary.persistence.size=10Gi

# Install with custom values file
helm install my-app ./my-chart -f values-production.yaml

# List releases
helm list --all-namespaces
helm status my-postgres

# Upgrade a release
helm upgrade my-postgres bitnami/postgresql \
  --set auth.postgresPassword=newsecret

# Rollback
helm history my-postgres        # see revision history
helm rollback my-postgres 1     # rollback to revision 1

# Uninstall
helm uninstall my-postgres

# Template rendering (dry run, see generated YAML)
helm template my-app ./my-chart -f values-production.yaml
helm install my-app ./my-chart --dry-run --debug
```

### Custom Chart Structure
```
my-chart/
├── Chart.yaml          # chart metadata
├── values.yaml         # default values
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── _helpers.tpl    # template helpers/partials
└── charts/             # chart dependencies
```

### values.yaml
```yaml
replicaCount: 3

image:
  repository: my-app
  tag: "1.0.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

### templates/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-chart.fullname" . }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

---

## KUBERNETES vs DOCKER COMPOSE

| Feature | Docker Compose | Kubernetes |
|---------|---------------|-----------|
| **Purpose** | Local dev, simple multi-container apps | Production orchestration |
| **Scaling** | `docker-compose up --scale app=3` (manual) | HPA (automatic) |
| **Self-healing** | No (manual restart) | Yes (auto restarts, reschedules) |
| **Load balancing** | Basic (round-robin) | Service + Ingress |
| **Config management** | `.env` files | ConfigMaps + Secrets |
| **Rolling updates** | No | Yes (Deployments) |
| **Health checks** | `healthcheck:` (basic) | Liveness + Readiness + Startup probes |
| **Storage** | Named volumes | PV, PVC, StorageClass |
| **Networking** | Internal DNS by service name | CoreDNS, Services |
| **Complexity** | Simple, quick setup | Complex, steep learning curve |
| **Use case** | Local development | Production at scale |

**Migration path:** Docker Compose → K8s with `kompose convert` (converts compose file to K8s manifests)

---

## QUICK REFERENCE — Common Patterns

```bash
# Debug a failing pod
kubectl describe pod <pod-name>          # check Events section
kubectl logs <pod-name> --previous       # logs from crashed container
kubectl exec -it <pod-name> -- sh        # shell into running container

# Force restart all pods in a deployment
kubectl rollout restart deployment/my-app

# Update image in deployment (triggers rolling update)
kubectl set image deployment/my-app app=my-app:2.0

# Scale quickly
kubectl scale deployment my-app --replicas=0   # stop all pods
kubectl scale deployment my-app --replicas=3   # bring back

# View resource usage
kubectl top pods --sort-by=cpu
kubectl top nodes

# Drain a node (for maintenance)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node-name>            # re-enable scheduling
```
