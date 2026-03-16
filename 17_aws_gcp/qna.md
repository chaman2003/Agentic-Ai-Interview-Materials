# AWS / GCP Q&A

Common interview and practical questions for Python/Node.js developers working with AWS and GCP.

---

## Q1: EC2 vs Lambda vs ECS — when to use each?

**EC2** gives you a full virtual machine with complete control:
- Use when you need long-running processes (ML training, batch jobs > 15 min)
- Use when you need GPU access (deep learning, video encoding)
- Use when the app has complex system dependencies (custom C libraries, odd ports)
- Use when you want persistent in-memory state (Redis-like in-process caching)
- Cost: You pay 24/7 even if idle

**Lambda** runs functions on-demand without any server management:
- Use for event-driven, short-lived tasks (< 15 minutes per invocation)
- Use for webhooks (Stripe, GitHub, Slack callbacks)
- Use for scheduled jobs (cron: "delete old records every night")
- Use when traffic is unpredictable or very low (pay per request, zero idle cost)
- NOT for: large dependencies (250 MB limit), GPU, persistent connections, large files

**ECS (Fargate)** runs Docker containers without managing servers:
- Use for always-on HTTP services that scale with traffic
- Use when you want Docker locally → same container in production
- Use for medium-complexity apps that need more than Lambda allows
- Fargate removes the need to manage EC2 instances — just define your container
- Use when you have a Dockerfile and want a simple deployment target

Quick decision:
```
Short task triggered by event? → Lambda
Always-on web API in a container? → ECS Fargate (AWS) or Cloud Run (GCP)
Need GPU / full OS control / long job? → EC2
```

---

## Q2: What is S3 and what are common use cases?

S3 (Simple Storage Service) is AWS's object storage — an infinitely scalable system
for storing files (called objects) in containers called buckets.

- **Not a filesystem**: You access objects by their full key (path), no directories
- **Highly durable**: 99.999999999% (11 nines) — data replicated across 3+ AZs
- **Globally accessible**: any authorized app anywhere can read/write to it
- **Any file type, any size**: up to 5 TB per object

**Common use cases**:

1. **Static file hosting**: React/Vue/Angular SPAs — serve HTML/CSS/JS directly
2. **User file uploads**: PDFs, images, videos uploaded by users
3. **ML artifacts**: store model weights (.pkl, .pt), training datasets
4. **Document processing**: user uploads invoice PDF → S3 →
   triggers processing → results stored back in S3 or RDS
5. **Database backups**: nightly PostgreSQL dumps compressed and stored
6. **Application logs**: send log files to S3 for long-term archival
7. **Inter-service data transfer**: ECS task writes output to S3, another service reads it
8. **Data lake**: raw data files (JSON, CSV, Parquet) stored for BigQuery/Athena analysis

---

## Q3: What is a presigned URL? How do you generate one with boto3?

A presigned URL is a temporary, time-limited URL that grants access to a private S3
object without requiring the requester to have AWS credentials. The URL includes a
cryptographic signature that encodes the permissions and expiry time.

**Why it's useful**:
- Allow a user to download a file they're authorized to access without making the
  bucket public
- Allow a browser to upload directly to S3 (bypassing your server — no bandwidth cost
  on your server)
- Share a file temporarily (expires in 1 hour, 1 day, etc.)

**Generate a download URL with boto3**:
```python
import boto3

s3 = boto3.client('s3', region_name='us-east-1')

def generate_download_url(bucket: str, key: str, expires_in: int = 3600) -> str:
    """
    expires_in: seconds until the URL expires (max 7 days = 604800)
    """
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expires_in
    )
    return url

# Usage
url = generate_download_url('my-docs-bucket', 'invoices/2024/001.pdf', expires_in=300)
# User can now open this URL in their browser for the next 5 minutes
```

**Generate an upload URL (browser uploads directly to S3)**:
```python
def generate_upload_url(bucket: str, key: str, expires_in: int = 300) -> dict:
    """
    Returns URL and form fields. Client POSTs to the URL with the fields.
    The file never touches your server.
    """
    response = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        ExpiresIn=expires_in
    )
    # Response: {'url': 'https://bucket.s3.amazonaws.com', 'fields': {...}}
    return response
```

**Frontend upload using the presigned POST**:
```javascript
const { url, fields } = await fetch('/api/get-upload-url').then(r => r.json());

const formData = new FormData();
Object.entries(fields).forEach(([key, value]) => formData.append(key, value));
formData.append('file', file);  // file must be last

await fetch(url, { method: 'POST', body: formData });
// File is now in S3 directly
```

---

## Q4: What is IAM? What is the principle of least privilege?

**IAM (Identity and Access Management)** is AWS's system for controlling who can
access what in your AWS account.

Core components:
- **Users**: Human or programmatic identities with permanent credentials
- **Groups**: Collections of users sharing the same permissions
- **Roles**: Assumed temporarily by AWS services (Lambda, EC2, ECS tasks) — no
  permanent credentials
- **Policies**: JSON documents defining allowed/denied actions on resources

**Principle of Least Privilege**: Grant only the minimum permissions required to
perform a specific task. Never give broader access "just in case."

Example of violating least privilege:
```json
{
  "Effect": "Allow",
  "Action": "s3:*",         // Too broad — can delete, list all buckets, change ACLs
  "Resource": "*"            // All buckets in the account
}
```

Correct application of least privilege:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",           // Only read
    "s3:PutObject"            // Only write
  ],
  "Resource": "arn:aws:s3:::my-specific-bucket/*"  // Only this bucket
}
```

**Why it matters**:
- If a Lambda function's credentials are stolen, the attacker can only do what that
  Lambda could do — not delete your entire S3 or spin up EC2 instances
- Limits blast radius of any security incident
- AWS will flag overly permissive policies in Security Hub / IAM Access Analyzer

**Practical rules**:
- Lambda functions: only give access to the specific S3 bucket, DynamoDB table, etc.
  they actually use
- Developers: use IAM users with MFA; never share root account credentials
- Never hardcode AWS access keys in code — use roles for services, IAM Identity
  Center for humans

---

## Q5: How would you deploy a FastAPI app on AWS ECS/Fargate?

**Step 1: Write a Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Create an ECR repository and push the image**
```bash
# Create repo
aws ecr create-repository --repository-name my-fastapi-app --region us-east-1

# Auth Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push
docker build -t my-fastapi-app .
docker tag my-fastapi-app:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest
```

**Step 3: Create a Task Definition**
Define CPU/memory, the container image, port mappings, environment variables,
secrets from Secrets Manager, and IAM task role.

```json
{
  "family": "my-fastapi-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "containerDefinitions": [{
    "name": "app",
    "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest",
    "portMappings": [{"containerPort": 8000}],
    "secrets": [
      {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:..."}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/my-fastapi-app",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```

**Step 4: Create an ECS Service with an Application Load Balancer**
- Create an ALB that listens on port 80/443
- Create a target group pointing to port 8000
- Create an ECS service with desired count 2, pointing to the task definition
- ECS automatically registers/deregisters containers with the target group

**Step 5: Set up CI/CD (GitHub Actions example)**
```yaml
- name: Deploy to ECS
  run: |
    aws ecs update-service \
      --cluster my-cluster \
      --service my-fastapi-service \
      --force-new-deployment
```

ECS will do a rolling deployment: bring up new tasks, wait for health checks,
then terminate old tasks.

---

## Q6: What is CloudWatch? How do you view Lambda logs?

**CloudWatch** is AWS's observability service:
- **Logs**: Collect and store log output from Lambda, ECS, EC2, etc.
- **Metrics**: Time-series data (CPU, request count, error rate, custom metrics)
- **Alarms**: Alert when a metric breaches a threshold
- **Dashboards**: Visualize metrics and logs in one place
- **Insights**: Query language for searching/aggregating logs

**How Lambda logs work**:
Every `print()` or `logging.*()` call in a Lambda function is automatically captured
and sent to CloudWatch Logs under the log group `/aws/lambda/your-function-name`.

**Viewing Lambda logs — 3 ways**:

1. **AWS Console**: CloudWatch → Log Groups → `/aws/lambda/function-name` → click a
   log stream (each log stream = one container execution instance)

2. **AWS CLI**:
```bash
# Live tail (like `tail -f`)
aws logs tail /aws/lambda/my-function --follow

# Filter for errors in the last hour
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-function \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)
```

3. **CloudWatch Insights (for complex queries)**:
```sql
fields @timestamp, @message, @requestId
| filter @message like /Exception/
| sort @timestamp desc
| limit 20
```

**Best practice** — use structured JSON logs:
```python
import json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        "action": "process_document",
        "doc_id": event.get("doc_id"),
        "status": "started"
    }))
```
Structured logs are queryable in CloudWatch Insights: `filter action = "process_document"`.

---

## Q7: What is the difference between ECS Fargate vs EC2 launch type?

Both run Docker containers in ECS, but they differ in how the underlying compute is managed:

**ECS Fargate (Serverless)**:
- AWS manages the underlying hosts — you never see or touch them
- Specify CPU and memory per task; you're billed exactly for what you request
- No cluster capacity to manage
- Slower scaling (new tasks take ~30-60 seconds to start cold)
- No GPU support
- Higher per-CPU cost but zero operational overhead
- Best for: most web APIs, microservices, teams that want simplicity

**EC2 Launch Type**:
- You manage a pool of EC2 instances that ECS places tasks onto
- Can use spot instances (up to 90% cheaper for fault-tolerant workloads)
- GPU support (p3, g4 instance families)
- Faster task startup (container already on warm host)
- You must right-size the cluster (not enough instances = tasks won't start)
- Best for: cost-optimized large-scale deployments, GPU workloads, latency-sensitive apps

**Cost comparison** (approximate, us-east-1):
- 1 vCPU + 2 GB RAM task on Fargate: ~$29/month running 24/7
- 1 vCPU + 2 GB RAM on t3.small EC2: ~$15/month

For production web apps with moderate traffic: Fargate (simplicity wins).
For ML inference at scale or cost-sensitive high-volume workloads: EC2 launch type.

---

## Q8: What is RDS? When would you use it over DynamoDB?

**RDS (Relational Database Service)** is AWS's managed relational database. You
choose PostgreSQL, MySQL, MariaDB, Oracle, or SQL Server, and AWS handles:
- Automated backups (point-in-time recovery up to 35 days)
- OS and database engine patching
- Multi-AZ failover (automatic switchover in < 1 minute)
- Read replicas for horizontal read scaling
- Storage auto-scaling

**Use RDS (PostgreSQL) when**:
- Your data is relational (users have orders, orders have items, items have categories)
- You need complex queries with JOINs, aggregations, subqueries
- Transactions matter: multiple related writes must all succeed or all fail (ACID)
- Your team knows SQL well
- Examples: e-commerce, fintech, ERP systems, user management, document metadata

**Use DynamoDB when**:
- You need single-digit millisecond latency at massive scale (millions of reads/sec)
- Access patterns are simple and known in advance (get item by ID, query by partition key)
- Your data is a flat key-value or simple document structure
- Serverless architecture — DynamoDB scales automatically with zero management
- Session storage, gaming leaderboards, shopping carts, user preferences

**The wrong choice is costly**:
- Building a complex relational app on DynamoDB without careful schema design leads to
  painful data modeling (no JOINs, limited query flexibility)
- Running RDS for a simple lookup service is over-engineered and more expensive

---

## Q9: Explain serverless. What are cold starts?

**Serverless** means you write code (or define containers) without provisioning,
managing, or paying for idle servers. The cloud provider:
- Allocates compute only when a request arrives
- Scales automatically (including to zero)
- Charges only for actual compute time

"Serverless" doesn't mean no servers — servers still exist. It means you don't
manage them and don't pay when they're idle.

Examples: AWS Lambda, GCP Cloud Run, Cloud Functions, Azure Functions.

**Cold Starts** occur when a serverless function is invoked but there is no warm
(pre-existing, idle) container to handle it. The platform must:
1. Allocate a new micro-VM or container
2. Download and unpack your code/image
3. Start the runtime (Python interpreter, Node.js V8 engine)
4. Execute any top-level initialization code (imports, connecting to DB, etc.)
5. Finally run your handler function

Cold start durations:
- Node.js Lambda: 100-500ms typical
- Python Lambda: 200-700ms typical
- Container-based (Cloud Run): 1-3 seconds (larger image = slower)

**Warm invocations**: After the first cold start, subsequent requests to the same
container are fast (no startup overhead). Containers stay warm for ~15 minutes of
inactivity.

**Mitigation strategies**:
```python
# Move heavy initialization OUTSIDE the handler (runs once per container, not per request)
import boto3
from transformers import pipeline  # Heavy import

# This runs on cold start, once
s3_client = boto3.client('s3')
model = pipeline('text-classification')  # Loaded once

def lambda_handler(event, context):
    # This runs on every invocation but s3_client and model are already loaded
    text = event['text']
    result = model(text)  # Fast — model already in memory
    return result
```

Other strategies:
- Provisioned Concurrency: keep N Lambda containers pre-warmed (costs money)
- Reduce package size: less to download/unpack
- Use smaller base images for containers
- `--min-instances 1` in Cloud Run

---

## Q10: What is Cloud Run and how does it compare to AWS Lambda?

**Cloud Run** deploys any HTTP-handling container and auto-scales it, including to
zero. You bring a Docker image; GCP handles routing, TLS, scaling, and load balancing.

**AWS Lambda** runs individual functions. You bring code (not a container by default),
and AWS handles the runtime, scaling, and invocation.

| Factor               | Cloud Run                      | AWS Lambda                      |
|----------------------|--------------------------------|---------------------------------|
| Unit of deployment   | Docker container               | Function (zip/container)        |
| Max runtime          | 60 min per request             | 15 min per invocation           |
| Package size limit   | Full container (no limit)      | 250 MB (zip) or container       |
| Concurrency          | 80 requests/instance (default) | 1 per instance (default)        |
| Cold start           | 1-3 seconds (container startup)| 100ms - 3s (function init)      |
| HTTP trigger         | Built-in (no API Gateway)      | Needs API Gateway                |
| Local testing        | docker run (identical)          | SAM / LocalStack (approximation)|
| Supported languages  | Anything in Docker             | Python, Node, Go, Java, etc.    |
| Cost                 | Per vCPU-second                | Per GB-second                   |

**Cloud Run is simpler for HTTP services**: no need to configure API Gateway, no
Lambda-specific event formats, and the container you test locally is exactly what runs in production.

**Lambda is better for event-driven patterns**: native integration with S3 events,
SQS, DynamoDB Streams, Kinesis, EventBridge — no HTTP involved.

For a MERN backend: Cloud Run is the natural choice on GCP.
For an S3-triggered document processor: Lambda is the natural choice on AWS.

---

## Q11: How would you deploy a Node.js MERN backend on GCP Cloud Run?

```bash
# File structure
# mern-api/
#   server.js
#   package.json
#   Dockerfile
```

**server.js** (key: listen on PORT env var):
```javascript
const express = require('express');
const mongoose = require('mongoose');

const app = express();
app.use(express.json());

mongoose.connect(process.env.MONGODB_URI);

app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.use('/api/users', require('./routes/users'));

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

**Dockerfile**:
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
```

**Deploy commands**:
```bash
# Set project
gcloud config set project my-gcp-project

# Build the container in Cloud Build (no local Docker needed)
gcloud builds submit --tag gcr.io/my-gcp-project/mern-api

# Store secrets in Secret Manager
echo -n "mongodb+srv://user:pass@cluster.mongodb.net/mydb" | \
  gcloud secrets create mongodb-uri --data-file=-

echo -n "super-secret-jwt-key" | \
  gcloud secrets create jwt-secret --data-file=-

# Deploy to Cloud Run
gcloud run deploy mern-api \
  --image gcr.io/my-gcp-project/mern-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --min-instances 1 \
  --set-secrets "MONGODB_URI=mongodb-uri:latest,JWT_SECRET=jwt-secret:latest" \
  --set-env-vars "NODE_ENV=production"

# Output: Service URL: https://mern-api-abc123-uc.a.run.app
```

**For React frontend**: build with `npm run build` and deploy to Firebase Hosting
or GCS + Cloud Load Balancing (with CDN).

---

## Q12: What is GCS? How does it compare to S3?

**GCS (Google Cloud Storage)** is GCP's object storage — functionally equivalent to
AWS S3. Both store files (objects) in buckets, support lifecycle rules, versioning,
presigned/signed URLs, and fine-grained access control.

| Factor              | GCS                                | S3                                  |
|---------------------|------------------------------------|-------------------------------------|
| Bucket namespace    | Globally unique                    | Globally unique                     |
| URL scheme          | `gs://bucket/key`                  | `s3://bucket/key`                   |
| Python library      | `google-cloud-storage`             | `boto3`                             |
| Signed URLs         | Signed URLs (v4)                   | Presigned URLs                      |
| Consistency         | Strong read-after-write always     | Strong since 2020                   |
| Storage classes     | Standard, Nearline, Coldline, Archive | Standard, IA, Glacier, Deep Archive|
| Native analytics    | BigQuery direct table reads from GCS| Athena queries on S3               |
| CDN                 | Cloud CDN                          | CloudFront                          |

**Practical difference**: If your workload is on GCP (Cloud Run, BigQuery, Vertex AI),
use GCS. If your workload is on AWS (Lambda, ECS, SageMaker), use S3. They're
interchangeable from a conceptual standpoint.

```python
# GCS example
from google.cloud import storage
client = storage.Client()
bucket = client.bucket('my-bucket')
blob = bucket.blob('path/to/file.txt')
blob.upload_from_filename('/local/file.txt')

# S3 equivalent
import boto3
s3 = boto3.client('s3')
s3.upload_file('/local/file.txt', 'my-bucket', 'path/to/file.txt')
```

---

## Q13: What is BigQuery and when would you use it?

**BigQuery** is GCP's serverless, fully managed data warehouse. It stores data in a
columnar format and is designed for running analytical SQL queries on massive datasets
(billions of rows, terabytes of data) in seconds.

Unlike traditional databases (PostgreSQL, MySQL), BigQuery is:
- Not optimized for transactional writes (INSERT/UPDATE/DELETE are expensive)
- Optimized for scanning large amounts of data quickly (aggregations, analytics)
- Serverless — no cluster to provision or manage
- Billed per data scanned ($5/TB)

**When to use BigQuery**:
- Business intelligence: "Show me daily revenue by region over the last 2 years"
- Log analysis: "Find all requests that returned 500 errors last week"
- ML feature engineering: compute features from raw event logs
- Analytics dashboard backend (connected to Looker, Data Studio, Metabase)
- Ad-hoc data exploration of large datasets

**When NOT to use BigQuery**:
- Transactional data store for your app (use PostgreSQL/Cloud SQL)
- Low-latency lookups by primary key (use Firestore or Bigtable)
- Real-time writes with high throughput (use Pub/Sub + Dataflow)

**Example**:
```python
from google.cloud import bigquery
client = bigquery.Client()

# This query scans only the 2024 partition (if table is partitioned by date)
sql = """
    SELECT
        DATE(created_at) as date,
        COUNT(*) as total_orders,
        SUM(amount) as revenue
    FROM `my-project.ecommerce.orders`
    WHERE DATE(created_at) >= '2024-01-01'
    GROUP BY date
    ORDER BY date
"""
df = client.query(sql).to_dataframe()
print(df.head())
```

---

## Q14: How do you handle secrets in AWS (not hardcode credentials)?

**Never put secrets in code, environment variables (committed to git), or
unencrypted config files.** Here are the right approaches:

**Option 1: AWS Secrets Manager** (recommended for DB passwords, API keys)
```python
import boto3
import json

def get_secret(secret_name: str) -> dict:
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Fetch at startup (outside handler to cache the value)
db_config = get_secret('prod/myapp/database')
DB_PASSWORD = db_config['password']
```

Secrets Manager features: automatic rotation for RDS, versioning, audit trail in
CloudTrail, cross-account access.

**Option 2: SSM Parameter Store** (simpler, cheaper for non-rotating secrets)
```python
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')

def get_parameter(name: str) -> str:
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

JWT_SECRET = get_parameter('/myapp/prod/jwt-secret')
```

**Option 3: IAM Roles (for AWS-to-AWS access)**
If your Lambda needs to access S3, don't use access keys at all. Attach an IAM role
to Lambda that grants S3 access. boto3 picks up the role credentials automatically.

```python
# No credentials anywhere in this code — uses the Lambda's IAM role
s3 = boto3.client('s3')
s3.get_object(Bucket='my-bucket', Key='my-file.txt')  # Works automatically
```

**Option 4: In ECS Task Definitions (inject from Secrets Manager)**
```json
"secrets": [
  {
    "name": "DB_PASSWORD",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:123:secret:prod/db/password"
  }
]
```
The ECS agent fetches the secret at task startup and injects it as an environment
variable. Your app reads `os.environ['DB_PASSWORD']` — never sees the ARN.

---

## Q15: What are security groups in EC2?

Security groups are **stateful virtual firewalls** attached to EC2 instances, RDS
databases, Lambda functions, and ECS tasks. They control what network traffic is
allowed in (inbound rules) and out (outbound rules).

**Key properties**:
- **Stateful**: If inbound traffic is allowed, the response is automatically allowed
  outbound (no need to configure return traffic)
- **Whitelist-only**: You only define what is ALLOWED; everything else is denied
- **Multiple security groups**: One resource can have multiple security groups
  (combined effect is the union of all rules)
- **Reference other security groups**: Instead of specifying an IP range, you can
  say "allow traffic from instances in security group sg-abc123" — this is the
  secure pattern for internal services

**Example security group for a web server**:
```
Inbound Rules:
Type        Protocol  Port Range  Source
HTTP        TCP       80          0.0.0.0/0, ::/0  (anyone on the internet)
HTTPS       TCP       443         0.0.0.0/0, ::/0  (anyone on the internet)
SSH         TCP       22          203.0.113.5/32    (only your office IP)

Outbound Rules:
Type        Protocol  Port Range  Destination
All traffic All       All         0.0.0.0/0          (allow all outbound)
```

**Example: RDS security group (only allow app servers to connect)**:
```
Inbound Rules:
Type         Protocol  Port  Source
PostgreSQL   TCP       5432  sg-app-servers   (reference to app's security group)
```
This is better than allowing a specific IP range because IP addresses change when
instances are replaced.

---

## Q16: What is auto-scaling? How does it work?

**Auto-scaling** automatically adjusts the number of compute resources (EC2 instances,
ECS tasks, Lambda concurrent executions) based on demand.

**AWS Auto Scaling components**:
- **Auto Scaling Group (ASG)**: Collection of EC2 instances treated as a unit
- **Launch Template**: Configuration blueprint for new instances (AMI, instance type,
  user data, security groups)
- **Scaling Policy**: When and how to scale

**Types of scaling policies**:

1. **Target Tracking** (simplest, recommended):
```
Maintain average CPU utilization = 60%.
If CPU > 60%, add instances.
If CPU < 60%, remove instances.
```

2. **Step Scaling**: Different actions based on how far the metric has breached the threshold.

3. **Scheduled Scaling**: Scale at specific times (e.g., scale up at 8 AM Monday-Friday,
   scale down at 8 PM).

4. **Predictive Scaling**: ML-based forecasting of traffic patterns.

**ECS Service Auto Scaling example**:
```bash
# Scale ECS service when average CPU > 70%
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-cluster/my-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-tracking-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleOutCooldown": 60,
    "ScaleInCooldown": 300
  }'
```

**Cloud Run auto-scaling**: Handled automatically. GCP adds more instances as
concurrent requests increase, scales to zero when idle.

---

## Q17: Explain S3 storage classes (Standard, Glacier, etc.)

S3 storage classes let you optimize cost by matching the storage price to your access
frequency. Data automatically tiered using lifecycle rules.

| Storage Class        | Use Case                        | Retrieval Time  | Min Days | Relative Cost |
|----------------------|---------------------------------|-----------------|----------|---------------|
| S3 Standard          | Frequently accessed (daily)     | Milliseconds    | None     | Highest       |
| S3 Intelligent-Tiering| Unknown/changing access pattern| Milliseconds    | None     | Standard + fee|
| S3 Standard-IA       | Infrequent access (monthly)     | Milliseconds    | 30 days  | Lower         |
| S3 One Zone-IA       | Infrequent, can tolerate loss   | Milliseconds    | 30 days  | Lower still   |
| S3 Glacier Instant   | Archive, millisecond access     | Milliseconds    | 90 days  | Much lower    |
| S3 Glacier Flexible  | Archive, flexible retrieval     | 1 min - 12 hrs  | 90 days  | Very low      |
| S3 Glacier Deep Archive| Long-term compliance archive  | 12 - 48 hours   | 180 days | Cheapest      |

**Lifecycle rule example** (documents older than 1 year go to Glacier, deleted at 7 years):
```json
{
  "Rules": [{
    "ID": "document-archival",
    "Status": "Enabled",
    "Filter": {"Prefix": "documents/"},
    "Transitions": [
      {"Days": 365, "StorageClass": "GLACIER"},
      {"Days": 730, "StorageClass": "DEEP_ARCHIVE"}
    ],
    "Expiration": {"Days": 2555}
  }]
}
```

**Intelligent-Tiering** monitors access patterns and automatically moves objects
between frequent and infrequent access tiers. Best when you don't know the access pattern.

---

## Q18: What is a CDN? Name AWS and GCP CDN services.

A **CDN (Content Delivery Network)** is a globally distributed network of servers
(called "edge locations" or "points of presence") that cache content close to users.
Instead of all users fetching content from your origin server in us-east-1, a user
in Tokyo fetches it from an edge server in Tokyo — much lower latency.

**What gets cached at the edge**:
- Static assets: images, CSS, JavaScript, HTML
- API responses with caching headers set
- Video streams
- Large file downloads

**AWS CDN: Amazon CloudFront**
- 450+ edge locations globally
- Works with S3, EC2, ALB, Lambda@Edge (run code at the edge)
- Custom domain + HTTPS (via ACM certificate)
- Cache-Control headers control TTL
- Cache invalidation: `aws cloudfront create-invalidation --distribution-id E123 --paths "/*"`
- Price class: can restrict to certain regions to save cost

```bash
# Create CloudFront distribution for an S3 static site
aws cloudfront create-distribution \
  --origin-domain-name my-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

**GCP CDN: Cloud CDN**
- Works with Cloud Load Balancing (backend services, buckets)
- Enable with: `--enable-cdn` flag on a backend service
- Global Anycast routing

**Common pattern**:
```
User → CloudFront → S3 (static React app)
User → CloudFront → ALB → ECS (API, with cache headers for GET requests)
```

Cache-busting for deployments: use content-hashed filenames (Webpack does this
automatically: `main.abc123.js`) so new deploys don't require invalidation.

---

## Q19: How do you configure environment variables in Cloud Run?

**At deploy time via CLI**:
```bash
# Set env vars
gcloud run deploy my-app \
  --set-env-vars "NODE_ENV=production,LOG_LEVEL=info,REGION=us-central1"

# Update a single env var without redeploying
gcloud run services update my-app \
  --update-env-vars "LOG_LEVEL=debug"

# Remove an env var
gcloud run services update my-app \
  --remove-env-vars "OLD_VAR"
```

**Secrets (for sensitive values) via Secret Manager**:
```bash
# Create a secret
echo -n "my-db-password" | gcloud secrets create db-password --data-file=-

# Reference it in Cloud Run (injected as env var at startup)
gcloud run deploy my-app \
  --set-secrets "DB_PASSWORD=db-password:latest"

# Mount as file (for large secrets like service account JSON)
gcloud run deploy my-app \
  --set-secrets "/secrets/sa.json=service-account:latest"
```

**In code**:
```javascript
// Node.js
const dbPassword = process.env.DB_PASSWORD;     // Injected by Cloud Run
const nodeEnv = process.env.NODE_ENV;           // 'production'
```

```python
# Python
import os
db_password = os.environ['DB_PASSWORD']         # Injected by Cloud Run
node_env = os.getenv('NODE_ENV', 'development') # With default
```

**Via Cloud Console**: Cloud Run → Service → Edit & Deploy New Revision → Variables & Secrets tab.

**Via Terraform** (infrastructure as code):
```hcl
resource "google_cloud_run_service" "my_app" {
  template {
    spec {
      containers {
        env {
          name  = "NODE_ENV"
          value = "production"
        }
        env {
          name = "DB_PASSWORD"
          value_from {
            secret_key_ref {
              name = "db-password"
              key  = "latest"
            }
          }
        }
      }
    }
  }
}
```

---

## Q20: What is the difference between vertical and horizontal scaling?

**Vertical Scaling (Scale Up/Down)**:
Increase the resources (CPU, RAM) of a single machine.

- EC2: Change from t3.medium to c5.xlarge (more CPU/RAM)
- RDS: Upgrade from db.t3.small to db.r5.large
- Cloud Run: Increase `--cpu 1` to `--cpu 4` and `--memory 512Mi` to `--memory 2Gi`

Pros:
- Simple — no application changes needed
- No distributed systems complexity

Cons:
- Hard limit — you can only get so large (max ~192 vCPUs on a single AWS instance)
- Single point of failure
- Requires downtime (usually a restart)
- Expensive at the top end

**Horizontal Scaling (Scale Out/In)**:
Add more instances of the same machine/container and distribute traffic among them.

- EC2 Auto Scaling Group: add more t3.medium instances behind a load balancer
- ECS: increase desired count from 2 to 10 tasks
- Cloud Run: GCP adds more container instances automatically
- Lambda: runs thousands of concurrent instances automatically

Pros:
- Near-infinite scale
- High availability — one instance failing doesn't take down the service
- Can scale down to save costs
- Rolling deployments possible (update instances one at a time)

Cons:
- Application must be stateless (no in-memory state that can't be lost)
- Need a load balancer
- More complex: session management, database connections, distributed tracing

**Rule of thumb**:
- Databases: vertical scaling is common (though read replicas are horizontal)
- Web/API servers: always horizontal (stateless containers behind a load balancer)
- Serverless (Lambda, Cloud Run): horizontal scaling is automatic and invisible

**The 12-Factor App** principle: build stateless services that can be horizontally
scaled. Store state in external services (RDS, Redis, S3) not in the application process.

---

## Q21: How does API Gateway work with Lambda?

**API Gateway** is AWS's managed HTTP API layer. It receives HTTP requests, invokes
Lambda, and returns the Lambda response as an HTTP response.

Without API Gateway, Lambda has no public HTTP endpoint. API Gateway provides:
- HTTPS endpoint (automatic TLS)
- Request routing (GET /users, POST /orders)
- Request/response transformation
- Authentication (AWS Cognito, Lambda authorizers, API keys)
- Rate limiting and throttling
- Request validation
- Stage management (dev, staging, prod)

```
Browser: GET https://abc123.execute-api.us-east-1.amazonaws.com/prod/users
              ↓
         API Gateway (routes to Lambda based on path/method)
              ↓
         Lambda Function (receives event with path, method, headers, body)
              ↓
         Returns: {"statusCode": 200, "body": "[...]"}
              ↓
         API Gateway → HTTP 200 response to browser
```

**Lambda event format for API Gateway**:
```python
def lambda_handler(event, context):
    method = event['httpMethod']          # GET, POST, etc.
    path = event['path']                  # /users
    params = event['queryStringParameters']  # {'page': '1'}
    headers = event['headers']
    body = event['body']                  # JSON string (not dict!)

    import json
    data = json.loads(body) if body else {}

    # Must return this exact structure
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'users': []})
    }
```

**HTTP API vs REST API in API Gateway**:
- HTTP API: simpler, cheaper ($1/million vs $3.5/million), lower latency
- REST API: more features (caching, request transformation, usage plans)
- For most use cases: HTTP API is sufficient

---

## Q22: What is SQS and when would you use it?

**SQS (Simple Queue Service)** is a managed message queue. Producers send messages;
consumers poll and process them.

**When to use it**:
- Decouple services: instead of Service A directly calling Service B (tight coupling),
  A puts a message in SQS and B processes it when ready
- Handle traffic spikes: if uploads spike to 1000/second but your processor handles
  100/second, SQS buffers the excess
- Retry failed work: if processing fails, the message returns to the queue
- Fan-out with SNS → SQS: one event consumed by multiple independent processors

**Classic use case — document processing pipeline**:
```
User uploads PDF → S3
S3 triggers Lambda → validates file, puts message in SQS
SQS → ECS Worker polls queue → processes PDF → stores result in S3/RDS
```

```python
import boto3
import json

sqs = boto3.client('sqs', region_name='us-east-1')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/document-processing-queue'

# Producer: enqueue a document for processing
def enqueue_document(doc_id: str, s3_key: str):
    message = {
        'doc_id': doc_id,
        's3_key': s3_key,
        'created_at': '2024-01-15T10:30:00Z'
    }
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message)
    )

# Consumer (runs in ECS worker): poll and process
def process_queue():
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,     # Batch up to 10
            WaitTimeSeconds=20,         # Long polling — wait up to 20s for messages
            VisibilityTimeout=300       # Hide message for 5 min during processing
        )

        for message in response.get('Messages', []):
            body = json.loads(message['Body'])

            try:
                process_document(body['doc_id'], body['s3_key'])
                # Delete only after successful processing
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
            except Exception as e:
                print(f"Failed to process {body['doc_id']}: {e}")
                # Message remains in queue and reappears after VisibilityTimeout
```
