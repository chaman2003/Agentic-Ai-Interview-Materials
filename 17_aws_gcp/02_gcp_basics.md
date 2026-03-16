# GCP Basics for Python/Node.js Developers

GCP (Google Cloud Platform) is the third-largest cloud provider after AWS and Azure.
Its standout services are BigQuery (data analytics), Cloud Run (serverless containers),
and GKE (the best managed Kubernetes). For MERN stacks and Python APIs, Cloud Run is
the go-to deployment target.

---

## Cloud Run - Serverless Containers

### What It Is
Cloud Run runs stateless containers and automatically scales them. You provide a
container image, and GCP handles everything else — provisioning, load balancing,
TLS certificates, and scaling including scaling to zero when idle.

Key advantages over Lambda:
- Full Docker container (not limited to a runtime or package size)
- Easier local development (test the same container locally)
- No need to repackage on dependency changes — just rebuild the image
- HTTP-based by default (no API Gateway needed)

### Key Concepts

| Concept           | Explanation                                                               |
|-------------------|---------------------------------------------------------------------------|
| Service           | A deployed application (like an ECS service)                             |
| Revision          | An immutable snapshot of your service at a point in time                 |
| Traffic splitting | Route X% to revision A, Y% to revision B (for canary deploys)           |
| Concurrency       | Max simultaneous requests per container instance (default: 80)           |
| Min instances     | Keep N instances warm to avoid cold starts (costs money when idle)       |
| Max instances     | Hard ceiling on scale (prevents runaway costs)                           |

### Deploying a Node.js Express App

**Step 1: Write a Dockerfile**
```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
EXPOSE 8080

# Cloud Run expects the app to listen on PORT env variable
ENV PORT=8080
CMD ["node", "server.js"]
```

Your `server.js` must listen on `process.env.PORT`:
```javascript
const express = require('express');
const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.post('/api/users', async (req, res) => {
  // Your logic here
  res.json({ created: true });
});

app.listen(PORT, () => {
  console.log(JSON.stringify({ message: 'Server started', port: PORT }));
});
```

**Step 2: Build and Push the Image**
```bash
# Option A: Cloud Build (builds in GCP, no local Docker needed)
gcloud builds submit --tag gcr.io/PROJECT_ID/my-node-app

# Option B: Local build, push to GCR
docker build -t gcr.io/PROJECT_ID/my-node-app .
docker push gcr.io/PROJECT_ID/my-node-app

# Option C: Local build, push to Artifact Registry (newer, preferred over GCR)
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-node-app .
docker push us-central1-docker.pkg.dev/PROJECT_ID/my-repo/my-node-app
```

**Step 3: Deploy**
```bash
gcloud run deploy my-node-app \
  --image gcr.io/PROJECT_ID/my-node-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "NODE_ENV=production,LOG_LEVEL=info" \
  --set-secrets "DB_PASSWORD=db-password:latest"
```

**Step 4: Get the service URL**
```bash
gcloud run services describe my-node-app \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
# Output: https://my-node-app-abc123-uc.a.run.app
```

### Deploying a FastAPI App

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run sets PORT — uvicorn must use it
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
```

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/my-fastapi-app

gcloud run deploy my-fastapi-app \
  --image gcr.io/PROJECT_ID/my-fastapi-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2
```

### Environment Variables and Secrets

**Environment variables** (non-sensitive config):
```bash
# At deploy time
gcloud run deploy my-app \
  --set-env-vars "NODE_ENV=production,API_URL=https://api.example.com"

# Update later
gcloud run services update my-app \
  --update-env-vars "LOG_LEVEL=debug"
```

**Secrets** (sensitive values via Secret Manager):
```bash
# 1. Create a secret
echo -n "my-super-secret-password" | \
  gcloud secrets create db-password --data-file=-

# 2. Reference it in Cloud Run (injected as environment variable)
gcloud run deploy my-app \
  --set-secrets "DB_PASSWORD=db-password:latest"

# 3. Reference as a mounted file (better for large secrets like API keys)
gcloud run deploy my-app \
  --set-secrets "/secrets/config.json=app-config:latest"
```

Access in Node.js:
```javascript
const dbPassword = process.env.DB_PASSWORD;  // Injected at startup
```

### Auto-scaling Behavior
```
Traffic = 0 requests:   Scale to 0 (unless min-instances > 0)
Traffic spike arrives:  Scale from 0 to 1 instance (cold start ~1-3 seconds)
Traffic grows:          Scale up to max-instances
Traffic drops:          Scale down (instances are terminated after ~15 min idle)
```

**Cold start mitigation**:
```bash
# Keep at least 1 instance warm (adds ~$15/month for 256Mi/1CPU)
gcloud run services update my-app --min-instances 1
```

### Max Concurrency
Each Cloud Run instance handles multiple concurrent requests (unlike Lambda which
handles one at a time by default). Setting `--concurrency 1` makes each instance
handle one request at a time (Lambda-like behavior). Default is 80.

For stateless HTTP APIs: use the default 80 (high throughput per instance).
For CPU-intensive work: set concurrency to 1 (avoid CPU contention).

### Cost Model
- **$0.00002400 per vCPU-second** (only while processing requests)
- **$0.00000250 per GB-second** (only while processing requests)
- **$0.40 per million requests**
- Free tier: 2 million requests/month, 360,000 vCPU-seconds, 180,000 GB-seconds

Example: 1 million requests, each taking 100ms with 512Mi / 1 CPU:
- Request cost: $0.40 / 2 (free tier covers first half) = ~$0.20
- Compute cost: 1M × 0.1s × $0.000024 = $2.40 total

---

## Cloud Storage (GCS) - Like AWS S3

### What It Is
Google Cloud Storage is GCP's object storage. API and concepts are nearly identical
to S3. Buckets, objects, ACLs, lifecycle rules — same mental model.

**Differences from S3**:
- Bucket names are globally unique (same as S3)
- URLs: `gs://bucket-name/object-key`
- Python library: `google-cloud-storage` instead of `boto3`
- Signed URLs: equivalent to S3 presigned URLs

### gsutil Commands
```bash
# List buckets
gsutil ls

# List objects in a bucket
gsutil ls gs://my-bucket/
gsutil ls gs://my-bucket/prefix/

# Copy files
gsutil cp localfile.txt gs://my-bucket/path/file.txt
gsutil cp gs://my-bucket/path/file.txt ./localfile.txt

# Sync a directory
gsutil -m rsync -r ./local-dir gs://my-bucket/remote-dir

# Make object public
gsutil acl ch -u AllUsers:R gs://my-bucket/public-file.html

# Remove object
gsutil rm gs://my-bucket/path/file.txt

# Get object metadata
gsutil stat gs://my-bucket/path/file.txt
```

### Python Code with google-cloud-storage

```python
from google.cloud import storage
from datetime import datetime, timedelta
import os

# Authenticates via:
# 1. GOOGLE_APPLICATION_CREDENTIALS environment variable (path to service account JSON)
# 2. gcloud auth application-default login (local dev)
# 3. Workload Identity / service account attached to Cloud Run/GCE (production)
client = storage.Client()
BUCKET_NAME = 'my-app-bucket'
bucket = client.bucket(BUCKET_NAME)


# --- Upload a file ---
def upload_file(local_path: str, gcs_key: str, content_type: str = None):
    blob = bucket.blob(gcs_key)
    blob.upload_from_filename(local_path, content_type=content_type)
    print(f"Uploaded {local_path} -> gs://{BUCKET_NAME}/{gcs_key}")


# --- Upload from bytes ---
def upload_bytes(data: bytes, gcs_key: str, content_type: str = 'application/octet-stream'):
    blob = bucket.blob(gcs_key)
    blob.upload_from_string(data, content_type=content_type)


# --- Download a file ---
def download_file(gcs_key: str, local_path: str):
    blob = bucket.blob(gcs_key)
    blob.download_to_filename(local_path)
    print(f"Downloaded gs://{BUCKET_NAME}/{gcs_key} -> {local_path}")


# --- Download to bytes ---
def download_bytes(gcs_key: str) -> bytes:
    blob = bucket.blob(gcs_key)
    return blob.download_as_bytes()


# --- Generate a signed URL (temporary access) ---
def generate_signed_url(gcs_key: str, expiration_minutes: int = 60) -> str:
    """
    Anyone with this URL can download the file without GCP credentials.
    Requires the service account to have the 'iam.serviceAccounts.signBlob' permission.
    """
    blob = bucket.blob(gcs_key)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )
    return url


# --- Generate signed URL for upload ---
def generate_signed_upload_url(gcs_key: str, expiration_minutes: int = 15) -> str:
    blob = bucket.blob(gcs_key)
    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="PUT",
        content_type="application/octet-stream"
    )
    return url


# --- List all blobs with a prefix ---
def list_blobs(prefix: str):
    blobs = client.list_blobs(BUCKET_NAME, prefix=prefix)
    for blob in blobs:
        print(f"{blob.name} ({blob.size} bytes, updated: {blob.updated})")
    return list(blobs)


# --- Delete a blob ---
def delete_blob(gcs_key: str):
    blob = bucket.blob(gcs_key)
    blob.delete()
    print(f"Deleted gs://{BUCKET_NAME}/{gcs_key}")


# --- Check if blob exists ---
def blob_exists(gcs_key: str) -> bool:
    blob = bucket.blob(gcs_key)
    return blob.exists()


# --- Copy between buckets ---
def copy_blob(src_key: str, dst_bucket_name: str, dst_key: str):
    src_blob = bucket.blob(src_key)
    dst_bucket = client.bucket(dst_bucket_name)
    bucket.copy_blob(src_blob, dst_bucket, dst_key)
```

### Storage Classes

| Class     | Use Case                           | Min Duration | Retrieval Cost |
|-----------|------------------------------------|--------------|----------------|
| Standard  | Frequently accessed data           | None         | None           |
| Nearline  | Once a month or less               | 30 days      | Small          |
| Coldline  | Once a quarter or less             | 90 days      | Small          |
| Archive   | Once a year or less (compliance)   | 365 days     | Small          |

Lifecycle rule example (JSON for bucket lifecycle config):
```json
{
  "rule": [
    {
      "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
      "condition": {"age": 30}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90}
    },
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    }
  ]
}
```

---

## BigQuery - Serverless Data Warehouse

### What It Is
BigQuery lets you run SQL queries on terabytes (or petabytes) of data without any
infrastructure setup. You create tables, load data, and query. Billing is based on
data scanned, not infrastructure.

It stores data in a columnar format, making aggregation queries extremely fast.

### Key Concepts

| Concept      | Explanation                                                             |
|--------------|-------------------------------------------------------------------------|
| Project      | GCP project that owns the dataset                                       |
| Dataset      | Container for tables (like a database schema)                           |
| Table        | Column-based data table                                                 |
| Job          | A query, load, or export operation                                      |
| Partitioning | Split table by date/column — queries only scan relevant partitions     |
| Clustering   | Sort data within partitions — faster filtered queries                  |
| View         | Named SQL query treated as a virtual table                             |

### Use Cases
- Analytics on large event/log datasets
- Business intelligence (connect to Looker, Data Studio)
- ML feature engineering (compute features from raw events)
- Log analysis (Cloud Run/GKE logs exported to BigQuery)
- Financial reporting across millions of transactions

### Python Query Example

```python
from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig
import pandas as pd

client = bigquery.Client(project='my-gcp-project')


# --- Run a simple query ---
def run_query(sql: str) -> list[dict]:
    query_job = client.query(sql)
    results = query_job.result()  # Waits for completion
    return [dict(row) for row in results]


# --- Query with parameters (safe, avoids SQL injection) ---
def get_user_events(user_id: str, start_date: str) -> list[dict]:
    sql = """
    SELECT
        event_type,
        COUNT(*) as event_count,
        MIN(created_at) as first_occurrence
    FROM `my-project.analytics.events`
    WHERE user_id = @user_id
      AND DATE(created_at) >= @start_date
    GROUP BY event_type
    ORDER BY event_count DESC
    """

    job_config = QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        ]
    )

    query_job = client.query(sql, job_config=job_config)
    return [dict(row) for row in query_job.result()]


# --- Load results into pandas ---
def query_to_dataframe(sql: str) -> pd.DataFrame:
    return client.query(sql).to_dataframe()


# --- Insert rows (streaming insert) ---
def insert_rows(table_id: str, rows: list[dict]):
    """
    table_id format: 'project.dataset.table'
    """
    errors = client.insert_rows_json(table_id, rows)
    if errors:
        raise Exception(f"BigQuery insert errors: {errors}")


# --- Load from GCS ---
def load_from_gcs(gcs_uri: str, table_id: str):
    """Load a CSV/JSON file from GCS into a BigQuery table."""
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,          # Auto-detect schema
        write_disposition="WRITE_APPEND"
    )
    load_job = client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
    load_job.result()
    print(f"Loaded {gcs_uri} into {table_id}")
```

### Cost Optimization
- **Use partition filters**: `WHERE DATE(created_at) = '2024-01-01'` scans only
  that partition instead of the entire table
- **SELECT specific columns**: BigQuery is columnar — `SELECT *` reads all columns
  even if you only use two
- **Use `bq --dry_run`**: Preview how many bytes a query will scan before running
- **Partition tables by date**: Essential for large tables

```bash
# Check how much data a query will scan before running it
bq query --dry_run \
  "SELECT user_id FROM my_dataset.events WHERE DATE(created_at) = '2024-01-01'"
# Output: Query successfully validated. Assuming the tables are not modified,
# running this query will process 125 MB of data.
```

---

## Cloud SQL - Managed Relational Database

### What It Is
Cloud SQL is GCP's managed relational database service, supporting PostgreSQL, MySQL,
and SQL Server. Like AWS RDS, it handles backups, patching, failover, and replicas.

### Connecting to Cloud SQL

**Option A: Cloud SQL Auth Proxy (for local development)**
```bash
# Download the proxy binary
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.6.1/cloud-sql-proxy.linux.amd64

chmod +x cloud-sql-proxy

# Run the proxy (creates a local TCP socket)
./cloud-sql-proxy my-project:us-central1:my-postgres-instance

# Now connect to localhost:5432 as if it were local PostgreSQL
psql -h 127.0.0.1 -U postgres -d mydb
```

**Option B: Direct connection from Cloud Run (production)**
```bash
# Add Cloud SQL connection to Cloud Run service
gcloud run deploy my-app \
  --add-cloudsql-instances my-project:us-central1:my-postgres-instance \
  --set-env-vars "DB_HOST=/cloudsql/my-project:us-central1:my-postgres-instance"
```

```python
# Python (SQLAlchemy) via Unix socket (Cloud Run → Cloud SQL)
import os
from sqlalchemy import create_engine

# When running on Cloud Run with --add-cloudsql-instances
db_socket_dir = "/cloudsql"
connection_name = os.environ['CLOUD_SQL_CONNECTION_NAME']  # project:region:instance

engine = create_engine(
    "postgresql+pg8000://",
    creator=lambda: pg8000.connect(
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        database=os.environ['DB_NAME'],
        unix_sock=f"{db_socket_dir}/{connection_name}/.s.PGSQL.5432"
    )
)
```

**Option C: Private IP (production, inside VPC)**
```python
# Simpler — Cloud Run and Cloud SQL in same VPC
DATABASE_URL = (
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASS']}"
    f"@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
)
engine = create_engine(DATABASE_URL)
```

### High Availability
- Enable HA at instance creation: creates a standby replica in another zone
- Automatic failover in ~60 seconds if primary fails
- Read replicas available for read-heavy workloads

---

## GKE (Google Kubernetes Engine)

### What It Is
GKE is a managed Kubernetes service. Google created Kubernetes, so GKE has the best
Kubernetes experience. Autopilot mode handles node provisioning automatically.

### When to Use GKE
- You need Kubernetes-specific features (custom controllers, CRDs, advanced networking)
- Microservices at scale (dozens of services)
- You need more control than Cloud Run allows (init containers, sidecar containers)
- Team already knows Kubernetes

**For most web apps: use Cloud Run instead.**

### Key Concepts

| Concept      | Explanation                                                          |
|--------------|----------------------------------------------------------------------|
| Cluster      | Set of nodes (VMs) that run your workloads                          |
| Node Pool    | Group of nodes with the same machine type                           |
| Pod          | Smallest deployable unit; one or more containers                    |
| Deployment   | Manages replicas of a pod; handles rolling updates                  |
| Service      | Exposes pods via a stable DNS name and load balancing               |
| Ingress      | Routes external HTTP/HTTPS traffic to services                      |
| ConfigMap    | Key-value config injected into pods                                 |
| Secret       | Like ConfigMap but for sensitive data (base64 encoded in etcd)      |

### GKE Autopilot vs Standard
- **Autopilot**: You pay per pod (CPU/memory requested), GKE manages nodes
- **Standard**: You manage node pools; more control, more responsibility

```bash
# Create an Autopilot cluster
gcloud container clusters create-auto my-cluster \
  --region us-central1

# Connect kubectl to it
gcloud container clusters get-credentials my-cluster --region us-central1

# Deploy a container
kubectl apply -f deployment.yaml

# Expose it externally
kubectl expose deployment my-app --type=LoadBalancer --port=80 --target-port=8080
```

### Cloud Run vs GKE Decision Guide
```
Need to run a containerized HTTP service?
    |
    +--> Is your team already using Kubernetes? --> YES --> GKE
    |
    +--> Do you need custom Kubernetes controllers/CRDs? --> YES --> GKE
    |
    +--> Do you need sidecar containers (Istio, Envoy)? --> YES --> GKE
    |
    +--> Do you have >50 microservices? --> YES --> GKE
    |
    +--> Otherwise --> Cloud Run (simpler, cheaper, faster to deploy)
```

---

## Deployment Comparison Table

| Factor               | EC2           | Lambda         | ECS Fargate    | Cloud Run      | GKE            |
|----------------------|---------------|----------------|----------------|----------------|----------------|
| Server management    | Full          | None           | None           | None           | Node pools     |
| Container support    | Manual Docker | Limited        | Native Docker  | Native Docker  | Native Docker  |
| Max runtime          | Unlimited     | 15 min         | Unlimited      | 60 min (req)   | Unlimited      |
| Scale to zero        | No            | Yes            | No (by default)| Yes            | No             |
| Cold start           | No            | Yes            | Slow           | Yes            | No             |
| Min cost (idle)      | ~$8/mo (t3)   | $0             | ~$0 (scaled)   | $0             | ~$50/mo        |
| Concurrency model    | Threads/procs | 1 per instance | Configurable   | 80 per instance| Configurable   |
| Best for             | GPU, legacy   | Events, cron   | Always-on API  | HTTP services  | Microservices  |
| GCP equivalent       | Compute Engine| Cloud Functions| (none exact)   | Cloud Run      | GKE            |
| AWS equivalent       | EC2           | Lambda         | ECS Fargate    | (Fargate-like) | EKS            |

---

## Common GCP Architecture Patterns

### 1. MERN Stack on GCP
```
Browser
    ↓ HTTPS
Cloud Load Balancing + Cloud Armor (WAF, DDoS protection)
    ↓
Cloud Run (Node.js/Express API)
    ↓               ↓              ↓
Cloud SQL       Cloud Storage  Secret Manager
(PostgreSQL)    (file uploads)  (API keys, DB pass)
```

```bash
# Deploy the complete stack
gcloud run deploy mern-api \
  --image gcr.io/PROJECT_ID/mern-api \
  --platform managed \
  --region us-central1 \
  --add-cloudsql-instances PROJECT_ID:us-central1:mern-db \
  --set-secrets "DB_PASSWORD=db-password:latest,JWT_SECRET=jwt-secret:latest" \
  --set-env-vars "NODE_ENV=production,DB_NAME=merndb" \
  --min-instances 1 \
  --memory 512Mi
```

### 2. ML Pipeline on GCP
```
Data arrives → Cloud Storage (raw input)
                    ↓ (GCS notification)
               Cloud Pub/Sub (message queue)
                    ↓ (push subscription)
               Cloud Run (preprocessing: validate, resize, enqueue)
                    ↓
               Vertex AI (managed ML training/inference)
                    ↓
               Cloud Storage (model outputs, predictions)
                    ↓
               BigQuery (store predictions for analytics)
```

### 3. Serverless Data Pipeline
```
External data source → Cloud Scheduler (cron trigger)
                            ↓
                       Cloud Run Job (ETL script)
                            ↓
                       BigQuery (store results)
                            ↓
                       Looker Studio (dashboard)
```

---

## GCP CLI (gcloud) Quick Reference

```bash
# Auth
gcloud auth login
gcloud auth application-default login       # For local SDK usage
gcloud config set project PROJECT_ID

# Cloud Run
gcloud run services list --region us-central1
gcloud run services describe SERVICE_NAME --region us-central1
gcloud run services delete SERVICE_NAME --region us-central1
gcloud run deploy SERVICE_NAME --image IMAGE_URL --region us-central1

# Cloud Storage
gsutil mb -l us-central1 gs://my-new-bucket
gsutil cp ./file.txt gs://my-bucket/path/
gsutil rm gs://my-bucket/path/file.txt
gsutil ls -l gs://my-bucket/

# BigQuery
bq ls                                       # List datasets
bq query "SELECT COUNT(*) FROM dataset.table"
bq load --source_format=CSV dataset.table gs://bucket/file.csv schema.json

# Cloud SQL
gcloud sql instances list
gcloud sql connect my-instance --user=postgres

# Container Registry
gcloud container images list
gcloud container images delete gcr.io/PROJECT/IMAGE:TAG

# Logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json
gcloud beta run services logs read SERVICE_NAME --region us-central1 --tail=100

# Secrets
gcloud secrets create my-secret --replication-policy automatic
echo -n "secret-value" | gcloud secrets versions add my-secret --data-file=-
gcloud secrets versions access latest --secret my-secret
```

---

## Environment Setup for GCP Development

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Initialize
gcloud init

# Install Python SDK
pip install google-cloud-storage google-cloud-bigquery google-cloud-secret-manager

# Set credentials for local development
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
# OR use ADC (recommended):
gcloud auth application-default login

# Set default project and region
gcloud config set project my-project-id
gcloud config set run/region us-central1
```
