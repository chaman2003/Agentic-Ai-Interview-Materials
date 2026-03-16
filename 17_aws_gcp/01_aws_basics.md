# AWS Basics for Python/Node.js Developers

AWS (Amazon Web Services) is the dominant cloud platform. As a developer, you won't
manage all services, but you need to understand the core building blocks and when to
use each one. This guide focuses on what you'll actually encounter in Python/Node.js
backend development.

---

## EC2 (Elastic Compute Cloud) - Virtual Servers

### What It Is
EC2 gives you a virtual machine (VM) running in AWS's data center. You pick the OS,
install whatever you want, and you have full root access. It's the closest thing to
having your own server in a rack, except AWS handles the physical hardware.

### Instance Types
AWS has hundreds of instance types grouped into families:

| Instance      | vCPUs | RAM   | Use Case                          |
|---------------|-------|-------|-----------------------------------|
| t3.micro      | 2     | 1 GB  | Free tier, dev/test environments  |
| t3.medium     | 2     | 4 GB  | Small web apps, low-traffic APIs  |
| t3.large      | 2     | 8 GB  | Medium web apps                   |
| c5.xlarge     | 4     | 8 GB  | Compute-intensive (ML inference)  |
| c5.4xlarge    | 16    | 32 GB | Heavy ML, batch processing        |
| r5.2xlarge    | 8     | 64 GB | Memory-intensive (large caches)   |
| p3.2xlarge    | 8     | 61 GB | GPU workloads (model training)    |

t3 = burstable general purpose (good default for web apps)
c5 = compute optimized (CPU-heavy tasks)
r5 = memory optimized (large in-memory datasets)
p3 = GPU instances (deep learning)

### Key Concepts

**AMI (Amazon Machine Image)**
A snapshot of an OS + software configuration. When you launch an EC2 instance, you
pick an AMI. Common choices:
- Amazon Linux 2023 (AWS's own Linux, good default)
- Ubuntu 22.04 LTS (familiar, large community)
- Your own custom AMI (pre-baked with your app installed)

**Security Groups**
Virtual firewalls that control inbound and outbound traffic. Each EC2 instance must
belong to at least one security group.

Typical inbound rules for a web server:
```
Type        Protocol  Port  Source
SSH         TCP       22    Your IP (0.0.0.0/0 is dangerous — only use for dev)
HTTP        TCP       80    0.0.0.0/0 (anywhere)
HTTPS       TCP       443   0.0.0.0/0 (anywhere)
Custom TCP  TCP       8000  0.0.0.0/0 (if running FastAPI/Node directly)
```

Outbound rules: usually allow all outbound (default).

**Key Pairs**
SSH authentication uses key pairs instead of passwords.
- AWS stores the public key on the instance
- You download the private key (.pem file) once — never again
- You use it to SSH in

**Elastic IP**
By default, EC2 instances get a new public IP every time they stop/start. An Elastic
IP is a static public IP that stays the same. Use it if you need a fixed IP address.

**User Data Script**
A shell script that runs automatically on first boot. Used for bootstrapping:

```bash
#!/bin/bash
# User data script — runs once at launch as root
yum update -y                          # Amazon Linux
yum install -y python3 git nginx

# Install Python dependencies
pip3 install fastapi uvicorn boto3

# Pull your app code
git clone https://github.com/yourorg/yourapp.git /home/ec2-user/app

# Start the app
cd /home/ec2-user/app
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### SSH Into an EC2 Instance

```bash
# chmod required — SSH will refuse to use a key that is too open
chmod 400 my-key.pem

# Amazon Linux or RHEL-based
ssh -i my-key.pem ec2-user@<PUBLIC_IP>

# Ubuntu-based
ssh -i my-key.pem ubuntu@<PUBLIC_IP>
```

### When to Use EC2 vs Lambda vs ECS

| Scenario                              | Best Choice |
|---------------------------------------|-------------|
| Long-running processes (>15 min)      | EC2 or ECS  |
| Need full OS control / custom deps    | EC2         |
| GPU workloads                         | EC2         |
| Simple API with unpredictable traffic | Lambda      |
| Containerized app                     | ECS Fargate |
| Always-on web server                  | ECS or EC2  |
| Scheduled jobs / cron                 | Lambda      |

---

## S3 (Simple Storage Service) - Object Storage

### What It Is
S3 stores files (called "objects") in containers called "buckets." It is not a
filesystem — you cannot mount it like a drive (well, you can, but it's slow and
not recommended). Think of it as a key-value store where the key is the file path
and the value is the file contents.

- **Durability**: 99.999999999% (11 nines) — AWS replicates your data across
  multiple availability zones
- **Availability**: 99.99%
- **Scale**: Unlimited storage, objects up to 5 TB each
- **Global**: Buckets are in a specific region, but accessible from anywhere

### Key Concepts

| Concept          | Explanation                                                            |
|------------------|------------------------------------------------------------------------|
| Bucket           | Top-level container. Name is globally unique across ALL AWS accounts   |
| Object           | A file + its metadata                                                  |
| Key              | The "path" of an object, e.g., `invoices/2024/jan/001.pdf`            |
| ACL              | Access control list — controls who can access an object                |
| Bucket Policy    | JSON policy attached to the bucket for fine-grained access control     |
| Presigned URL    | Temporary URL that grants time-limited access to a private object      |

### Use Cases
- **Static file hosting**: HTML, CSS, JS for SPAs
- **ML model storage**: store .pkl, .pt, .onnx model files
- **Document uploads**: users upload PDFs/images, you store in S3 for further processing
- **Backups**: database dumps, log archives
- **Data lake**: raw data files for analytics pipelines
- **Inter-service data transfer**: ECS task outputs a file to S3, another service reads it

### Python Examples with boto3

```python
import boto3
from botocore.exceptions import ClientError

# boto3 automatically uses credentials from:
# 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
# 2. ~/.aws/credentials file
# 3. IAM role attached to EC2/Lambda/ECS (preferred in production)

s3 = boto3.client('s3', region_name='us-east-1')
BUCKET = 'my-app-bucket'


# --- Upload a file ---
def upload_file(local_path: str, s3_key: str):
    """Upload a local file to S3."""
    s3.upload_file(local_path, BUCKET, s3_key)
    print(f"Uploaded {local_path} -> s3://{BUCKET}/{s3_key}")


# --- Upload from memory (BytesIO) ---
def upload_bytes(data: bytes, s3_key: str, content_type: str = 'application/octet-stream'):
    import io
    s3.upload_fileobj(
        io.BytesIO(data),
        BUCKET,
        s3_key,
        ExtraArgs={'ContentType': content_type}
    )


# --- Download a file ---
def download_file(s3_key: str, local_path: str):
    s3.download_file(BUCKET, s3_key, local_path)
    print(f"Downloaded s3://{BUCKET}/{s3_key} -> {local_path}")


# --- Generate a presigned URL (temporary access) ---
def generate_presigned_url(s3_key: str, expiration_seconds: int = 3600) -> str:
    """
    Generate a URL that expires after `expiration_seconds`.
    Anyone with this URL can download the file without AWS credentials.
    """
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': s3_key},
        ExpiresIn=expiration_seconds
    )
    return url


# --- Generate presigned URL for upload (browser can upload directly) ---
def generate_presigned_upload_url(s3_key: str, expiration_seconds: int = 300) -> dict:
    response = s3.generate_presigned_post(
        BUCKET,
        s3_key,
        ExpiresIn=expiration_seconds
    )
    # Returns {'url': ..., 'fields': {...}}
    # Client POSTs to response['url'] with response['fields'] as form data
    return response


# --- List objects in a prefix ---
def list_objects(prefix: str):
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix):
        for obj in page.get('Contents', []):
            print(f"{obj['Key']} ({obj['Size']} bytes)")


# --- Delete an object ---
def delete_object(s3_key: str):
    s3.delete_object(Bucket=BUCKET, Key=s3_key)
    print(f"Deleted s3://{BUCKET}/{s3_key}")


# --- Check if object exists ---
def object_exists(s3_key: str) -> bool:
    try:
        s3.head_object(Bucket=BUCKET, Key=s3_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise
```

### Lifecycle Rules
S3 can automatically manage your objects over time:
- Move objects to cheaper storage classes after N days
- Delete objects after N days (great for temp files, old logs)
- Clean up incomplete multipart uploads

Example use case: uploaded documents older than 1 year move to Glacier for cheap
archival, then delete after 7 years.

### Versioning
When enabled on a bucket, S3 keeps every version of every object. If you overwrite
or delete a file, the old version is preserved. Useful for:
- Audit trails
- Accidental deletion recovery
- Rolling back bad model versions

### S3 Storage Classes

| Class          | Use Case                      | Retrieval Time | Cost      |
|----------------|-------------------------------|----------------|-----------|
| Standard       | Frequent access               | Immediate      | Highest   |
| Standard-IA    | Infrequent access             | Immediate      | Lower     |
| Glacier Instant| Archive, rare access          | Milliseconds   | Much lower|
| Glacier Flexible| Long-term archive            | Minutes-hours  | Very low  |
| Deep Archive   | Compliance, rarely accessed   | 12 hours       | Cheapest  |

---

## Lambda - Serverless Functions

### What It Is
Lambda lets you run code without provisioning or managing servers. You upload a
function, define what triggers it, and AWS handles everything else: scaling,
availability, patching, runtime updates.

**Pay per invocation**: You pay only when your function actually runs (~$0.20 per
1 million requests + compute time). Idle time costs nothing.

### Key Concepts

| Concept              | Explanation                                                        |
|----------------------|--------------------------------------------------------------------|
| Handler              | The entry-point function AWS calls (e.g., `lambda_handler`)       |
| Event                | Input data passed to your function (dict in Python)               |
| Context              | Runtime info: remaining time, request ID, memory limit            |
| Layer                | Shared library packages (avoids packaging deps in every function) |
| Environment Variables| Key-value config injected at runtime                              |
| Execution Role       | IAM role that defines what AWS services this function can access  |

### Common Triggers
- **API Gateway**: HTTP request comes in → Lambda runs → returns HTTP response
- **S3 Event**: file uploaded to S3 → Lambda processes it
- **SQS**: message in queue → Lambda processes batch of messages
- **EventBridge (cron)**: scheduled trigger (like cron jobs)
- **SNS**: notification sent → Lambda reacts

### Python Lambda Handler

```python
import json
import boto3
import os

# This runs once per container (cold start), not per invocation
s3 = boto3.client('s3')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'my-table')

def lambda_handler(event, context):
    """
    Main entry point. AWS calls this function.

    event: dict containing trigger-specific data
    context: LambdaContext object with runtime info
    """
    # context.get_remaining_time_in_millis() — useful to avoid timeout
    # context.function_name — your function's name
    # context.request_id — unique ID for this invocation

    print(f"Event: {json.dumps(event)}")  # Goes to CloudWatch Logs

    # --- API Gateway event example ---
    if 'httpMethod' in event:
        method = event['httpMethod']
        path = event['path']
        body = json.loads(event.get('body') or '{}')
        query_params = event.get('queryStringParameters') or {}

        if method == 'POST' and path == '/process':
            result = process_document(body)
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'result': result})
            }

        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

    # --- S3 event example ---
    if 'Records' in event and event['Records'][0].get('eventSource') == 'aws:s3':
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            print(f"Processing s3://{bucket}/{key}")
            process_file(bucket, key)

    return {'statusCode': 200, 'body': 'OK'}


def process_document(body: dict):
    # Your business logic here
    return {"processed": True}


def process_file(bucket: str, key: str):
    # Download from S3, process, upload result
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read()
    # ... process ...
```

### Cold Starts
When Lambda runs your function for the first time (or after a period of inactivity),
it needs to:
1. Start a new container (micro VM)
2. Download your deployment package
3. Initialize the Python/Node.js runtime
4. Import your modules and run top-level code

This "cold start" adds 100ms - 3 seconds of latency. Subsequent invocations on the
same warm container skip steps 1-4.

**Mitigation strategies**:
- Keep functions small (less to initialize)
- Move heavy imports inside the handler for rarely-used paths
- Use Provisioned Concurrency (pre-warm containers, costs money)
- Use Lambda SnapStart (for Java; Python equivalent not available yet)
- Ping the function every few minutes (hacky but works)

### Limitations
| Limit             | Value                    |
|-------------------|--------------------------|
| Max timeout       | 15 minutes               |
| Max memory        | 10,240 MB (10 GB)        |
| Deployment package| 250 MB (zipped: 50 MB)   |
| /tmp storage      | 10 GB (ephemeral)        |
| Concurrent execs  | 1,000 per region (soft)  |
| Payload size      | 6 MB (sync), 256 KB (SQS)|

### When to Use Lambda
- Webhooks (GitHub, Stripe, Twilio callbacks)
- Image/document processing triggered by S3 uploads
- Scheduled cleanup jobs (delete old records, send reminders)
- API backends with low or spiky traffic
- Glue code between services
- NOT for: long ML training, always-on websockets, very large dependencies

---

## RDS (Relational Database Service) - Managed Databases

### What It Is
RDS removes the operational burden of running a relational database. AWS handles:
- OS patching
- Database engine upgrades
- Automated backups (point-in-time recovery)
- Failover (Multi-AZ)
- Storage scaling

Supported engines: PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, and Aurora
(AWS's own high-performance MySQL/PostgreSQL-compatible engine).

### Key Concepts

| Concept          | Explanation                                                            |
|------------------|------------------------------------------------------------------------|
| Instance type    | CPU/RAM size (db.t3.micro for dev, db.r5.2xlarge for production)      |
| Storage type     | gp3 (general purpose SSD, good default), io1 (high IOPS)             |
| Multi-AZ         | Synchronous standby replica in another AZ; automatic failover <1 min  |
| Read Replica     | Asynchronous copy for read-scaling; can promote to primary            |
| Parameter Group  | Configuration settings for the DB engine                              |
| Subnet Group     | Which VPC subnets RDS can be placed in                               |

### Connection String

```python
# PostgreSQL via psycopg2
import psycopg2

conn = psycopg2.connect(
    host='mydb.abc123.us-east-1.rds.amazonaws.com',  # RDS endpoint
    port=5432,
    database='myapp',
    user='admin',
    password=os.environ['DB_PASSWORD']  # Never hardcode!
)

# SQLAlchemy connection string format:
DATABASE_URL = (
    "postgresql://admin:password@"
    "mydb.abc123.us-east-1.rds.amazonaws.com:5432/myapp"
)
```

### RDS vs DynamoDB vs MongoDB Atlas

| Factor              | RDS (PostgreSQL)          | DynamoDB              | MongoDB Atlas           |
|---------------------|---------------------------|-----------------------|-------------------------|
| Data model          | Relational (tables, SQL)  | Key-value / document  | Document (BSON)         |
| Schema              | Strict schema             | Flexible              | Flexible                |
| Query language      | SQL                       | PartiQL / API         | MQL (Mongo Query Lang)  |
| Scaling             | Vertical + read replicas  | Auto (serverless)     | Horizontal sharding     |
| Transactions        | Full ACID                 | Limited               | Multi-document ACID     |
| Best for            | Complex queries, joins    | Simple lookups, scale | JSON-heavy apps, MERN   |
| Cost model          | Pay for instance always   | Pay per request       | Pay for cluster         |

**Use RDS when**: you have relational data, need complex queries with joins,
transactions are important (financial data, inventory), team knows SQL well.

**Use DynamoDB when**: massive scale at low latency, simple key-based lookups,
serverless architecture, gaming leaderboards, session storage.

---

## ECS (Elastic Container Service) - Container Orchestration

### What It Is
ECS runs Docker containers in AWS without you managing Kubernetes. You describe
what containers to run, and ECS places and manages them. Think of it as AWS's
answer to "I want containers but not the complexity of K8s."

### Key Concepts

| Concept           | Explanation                                                              |
|-------------------|--------------------------------------------------------------------------|
| Cluster           | Logical grouping of tasks/services                                       |
| Task Definition   | Blueprint for your container (like docker-compose.yml for one service)  |
| Task              | A running instance of a task definition                                  |
| Service           | Ensures N tasks are always running; handles rolling deploys              |
| ECR               | Elastic Container Registry — AWS's Docker Hub                           |
| Fargate           | Serverless container execution (no EC2 to manage)                       |

### Fargate vs EC2 Launch Type

| Factor          | Fargate (Serverless)           | EC2 Launch Type               |
|-----------------|--------------------------------|-------------------------------|
| Server mgmt     | None — AWS handles it          | You manage EC2 instances      |
| Cost            | Higher per CPU/hour            | Lower per CPU/hour            |
| Scaling speed   | Slower (cold start)            | Faster (if instances ready)   |
| Max task size   | 16 vCPU, 120 GB RAM            | Up to host instance size      |
| GPU support     | No                             | Yes (p3/p4 instances)         |
| Best for        | Most web apps, APIs            | GPU ML, cost-optimized scale  |

### How to Deploy a FastAPI App on ECS Fargate

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

**Step 2: Build and Push to ECR**
```bash
# Create ECR repository (one-time)
aws ecr create-repository --repository-name my-fastapi-app

# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t my-fastapi-app .
docker tag my-fastapi-app:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest
```

**Step 3: Task Definition (JSON snippet)**
```json
{
  "family": "my-fastapi-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/myAppTaskRole",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest",
      "portMappings": [
        {"containerPort": 8000, "protocol": "tcp"}
      ],
      "environment": [
        {"name": "ENV", "value": "production"}
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-fastapi-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Step 4: Create ECS Service**
```bash
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-fastapi-service \
  --task-definition my-fastapi-app:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-abc,subnet-def],securityGroups=[sg-xyz],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:...,containerName=app,containerPort=8000"
```

---

## IAM (Identity and Access Management)

### What It Is
IAM controls authentication (who are you?) and authorization (what can you do?) for
all AWS services. Every API call to AWS goes through IAM.

### Key Concepts

| Concept        | Explanation                                                               |
|----------------|---------------------------------------------------------------------------|
| User           | A person or application with long-term credentials (access key + secret) |
| Group          | Collection of users that share the same permissions                       |
| Role           | Set of permissions that can be assumed temporarily by services or users   |
| Policy         | JSON document defining permissions (allow/deny actions on resources)     |
| Principal      | The entity making the request (user, role, service)                      |

### Principle of Least Privilege
Only grant the minimum permissions required to do the job. If a Lambda function only
reads from one S3 bucket, don't give it S3:*, give it only s3:GetObject on that
specific bucket.

This limits blast radius if credentials are compromised.

### Roles vs Users
- **IAM Users**: For humans logging into AWS Console or using CLI. Have permanent
  credentials. Should use MFA.
- **IAM Roles**: For AWS services (Lambda, EC2, ECS tasks). Temporary credentials
  are automatically rotated. You never handle access keys.

**Always prefer roles over hardcoded access keys for AWS services.**

### Example Policy: S3 Read-Only for a Specific Bucket

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::my-documents-bucket",
        "arn:aws:s3:::my-documents-bucket/*"
      ]
    }
  ]
}
```

### Instance Profiles (Roles for EC2)
An instance profile attaches an IAM role to an EC2 instance. All code running on
that instance can call AWS services using the role's permissions — no access keys
in the code or environment variables.

```python
# boto3 automatically picks up instance profile credentials
# No explicit credentials needed when running on EC2 with role attached
s3 = boto3.client('s3')  # Uses instance profile automatically
```

### Common Managed Policies
- `AmazonS3ReadOnlyAccess`: S3 read access to all buckets
- `AmazonDynamoDBFullAccess`: Full DynamoDB access
- `AmazonECSTaskExecutionRolePolicy`: Required for ECS to pull images and push logs
- `CloudWatchLogsFullAccess`: Full CloudWatch Logs access

---

## CloudWatch - Monitoring & Logs

### What It Is
CloudWatch is AWS's observability platform: logs, metrics, alarms, dashboards, and
traces all in one service.

### Key Concepts

| Concept      | Explanation                                                          |
|--------------|----------------------------------------------------------------------|
| Log Group    | Container for log streams (one per Lambda function, ECS service...) |
| Log Stream   | Sequence of log events from a single source (container, instance)   |
| Metric       | A time-series data point (CPU usage, request count, error rate)     |
| Alarm        | Triggers an action when a metric exceeds a threshold                |
| Dashboard    | Visual display of metrics and alarms                                |
| Insights     | SQL-like query language for analyzing logs                          |

### Viewing Lambda Logs
Every print() / console.log() in a Lambda function goes to CloudWatch automatically.

Navigation: CloudWatch → Log Groups → `/aws/lambda/your-function-name`

```python
# In Lambda — use structured JSON logging for easy querying
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        "message": "Processing document",
        "document_id": event.get("doc_id"),
        "request_id": context.aws_request_id,
        "function": context.function_name
    }))
```

### CloudWatch Insights Query Examples
```sql
-- Find all errors in the last hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Average Lambda duration
fields @duration
| stats avg(@duration), max(@duration), min(@duration) by bin(5m)

-- Find slow requests (>2 seconds)
fields @timestamp, @requestId, @duration
| filter @duration > 2000
| sort @duration desc
```

### Alarms
```bash
# Create alarm: trigger if Lambda errors > 5 in 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "LambdaHighErrors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=my-function \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:alert-topic
```

### Structured Logging Best Practice
Always log JSON in production. It enables powerful querying in CloudWatch Insights
and can be shipped to Elasticsearch/Datadog easily.

```python
import json, time, logging

class JSONLogger:
    def __init__(self, service_name: str):
        self.service = service_name
        self.logger = logging.getLogger()

    def info(self, message: str, **kwargs):
        self.logger.info(json.dumps({
            "level": "INFO",
            "service": self.service,
            "message": message,
            "timestamp": time.time(),
            **kwargs
        }))

    def error(self, message: str, **kwargs):
        self.logger.error(json.dumps({
            "level": "ERROR",
            "service": self.service,
            "message": message,
            "timestamp": time.time(),
            **kwargs
        }))
```

---

## Common Architecture Patterns

### 1. Static Website
```
User → CloudFront (CDN) → S3 (HTML/CSS/JS)
         ↓ (API calls)
     API Gateway → Lambda → DynamoDB
```
- S3 hosts the built React/Vue/Angular app
- CloudFront caches it at edge locations worldwide for low latency
- No server needed for the frontend

### 2. Traditional API Backend
```
User → Load Balancer (ALB)
           ↓
       ECS Service (FastAPI/Express containers)
           ↓                    ↓
       RDS (PostgreSQL)    S3 (file uploads)
```
- ALB distributes traffic across multiple container instances
- ECS service maintains desired count and handles rolling updates
- RDS for relational data, S3 for binary files

### 3. Serverless API
```
User → API Gateway → Lambda → DynamoDB
                   → Lambda → S3
```
- No servers, pay per request
- Good for unpredictable or low traffic
- DynamoDB is the natural pair with Lambda (both serverless, both auto-scale)

### 4. ML Processing Pipeline
```
S3 (input file uploaded)
    ↓ (S3 event notification)
Lambda (lightweight: validate, enqueue)
    ↓
SQS (message queue — buffer)
    ↓ (ECS trigger or polling)
ECS Task (GPU instance: run ML model)
    ↓
S3 (output results)
    ↓
RDS or DynamoDB (store metadata/results)
```
- SQS decouples the upload event from heavy processing
- If the ML job fails, message returns to queue and retries
- Multiple ECS tasks can process in parallel

### 5. Document Processing Pipeline
```
User uploads PDF → S3
S3 event → SQS message
SQS → ECS Worker pool
         - Extract text (OCR / pdfplumber)
         - Run field extraction (ML model or LLM)
         - Write structured JSON back to S3
         - Store results in RDS
Frontend polls RDS → returns extracted data to user
```

---

## Quick Reference: AWS CLI Commands

```bash
# S3
aws s3 ls s3://my-bucket/
aws s3 cp file.txt s3://my-bucket/path/file.txt
aws s3 sync ./local-dir s3://my-bucket/remote-dir
aws s3 rm s3://my-bucket/path/file.txt

# EC2
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"
aws ec2 start-instances --instance-ids i-1234567890abcdef0
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Lambda
aws lambda list-functions
aws lambda invoke --function-name my-function --payload '{"key":"value"}' output.json
aws lambda update-function-code --function-name my-function --zip-file fileb://function.zip

# ECS
aws ecs list-clusters
aws ecs describe-services --cluster my-cluster --services my-service
aws ecs update-service --cluster my-cluster --service my-service --force-new-deployment

# Logs
aws logs tail /aws/lambda/my-function --follow
aws logs filter-log-events --log-group-name /ecs/my-app --filter-pattern "ERROR"
```
