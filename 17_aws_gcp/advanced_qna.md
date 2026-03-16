# Advanced AWS / GCP Q&A

Deep-dive questions for senior-level interviews and real production scenarios.

---

## Q1: What is a VPC? Key components (subnets, route tables, NAT gateway, internet gateway)?

A **VPC (Virtual Private Cloud)** is a logically isolated virtual network in AWS (or GCP).
It's your own private section of the cloud where you define IP ranges, subnets,
routing, and security.

Think of it as your own data center network, but in the cloud. Everything you create
in AWS — EC2, RDS, ECS, Lambda (when VPC-enabled) — lives inside a VPC.

### Key Components

**CIDR Block**: The IP address range for your entire VPC.
Example: `10.0.0.0/16` gives you 65,536 IP addresses (10.0.0.0 - 10.0.255.255).

**Subnets**: Sub-divisions of the VPC's IP range, tied to a specific Availability Zone.
```
VPC: 10.0.0.0/16 (us-east-1)
├── Subnet: 10.0.1.0/24  → us-east-1a  (public)   — 256 IPs
├── Subnet: 10.0.2.0/24  → us-east-1b  (public)   — 256 IPs
├── Subnet: 10.0.11.0/24 → us-east-1a  (private)  — 256 IPs
└── Subnet: 10.0.12.0/24 → us-east-1b  (private)  — 256 IPs
```

**Internet Gateway (IGW)**: Enables communication between the VPC and the public internet.
- Attach one IGW per VPC
- Route tables in public subnets send `0.0.0.0/0` traffic to the IGW
- Without an IGW, nothing in the VPC can reach the internet

**Route Tables**: Define where network traffic goes.
```
Public subnet route table:
Destination   Target
10.0.0.0/16   local          (stay inside VPC)
0.0.0.0/0     igw-abc123     (everything else → internet)

Private subnet route table:
Destination   Target
10.0.0.0/16   local          (stay inside VPC)
0.0.0.0/0     nat-gw-abc123  (everything else → NAT gateway)
```

**NAT Gateway**: Allows resources in private subnets to make outbound internet
connections (e.g., download packages, call external APIs) without being directly
reachable from the internet.
- Lives in a public subnet
- Has an Elastic IP
- Private subnet route tables send `0.0.0.0/0` to the NAT Gateway
- Cost: ~$0.045/hour + $0.045/GB data processed (significant at scale)

**Security Groups**: Stateful instance-level firewalls (covered in Q&A basics).

**NACLs (Network ACLs)**: Stateless subnet-level firewalls. Rules evaluated in order
by number. Less commonly used than security groups.

### Architecture Diagram
```
Internet
    ↓
Internet Gateway
    ↓
Public Subnet (10.0.1.0/24)
├── Load Balancer (public IP: 54.x.x.x)
└── NAT Gateway (outbound-only for private subnets)
    ↓
Private Subnet (10.0.11.0/24)
├── ECS Tasks (no public IP — only reachable via ALB)
├── EC2 instances
└── RDS database (most private — no route to internet at all)
```

**RDS Subnet Group**: RDS must be placed in a DB subnet group (2+ subnets in
different AZs). Always put RDS in private subnets.

---

## Q2: Public subnet vs private subnet — when to put things in each?

The rule: **if it doesn't need to be directly reachable from the internet, put it
in a private subnet.**

### Public Subnet
Resources here have public IP addresses and can receive inbound traffic from the internet.

Put here:
- **Load Balancers (ALB/NLB)**: The entry point for internet traffic
- **NAT Gateways**: Need a public IP to send traffic to internet on behalf of private resources
- **Bastion hosts**: Jump servers for SSHing into private instances (use AWS Systems Manager Session Manager instead for better security)
- **Static content servers** (if not behind CloudFront)

### Private Subnet
Resources here have only private IPs. They can initiate outbound connections via NAT
Gateway but cannot receive inbound connections from the internet.

Put here:
- **Application servers (ECS tasks, EC2)**: Accessed only via the ALB
- **Databases (RDS, ElastiCache)**: Should never be directly reachable from internet
- **Lambda functions** (when VPC-enabled): Needs VPC access to reach RDS/ElastiCache
- **Internal microservices**: Only communicate with each other, not the internet directly

### Security Principle
```
Internet user
    ↓ (only port 80/443)
ALB (public subnet) ← security group allows 80/443 from anywhere
    ↓ (only port 8000)
ECS Task (private subnet) ← security group allows 8000 only from ALB's security group
    ↓ (only port 5432)
RDS (private subnet) ← security group allows 5432 only from ECS's security group
```

Each layer only accepts traffic from the layer above it. Even if an attacker finds
a vulnerability in your API, they cannot directly reach RDS because it's in a private
subnet with no route from the internet.

### No-internet private subnet (for databases)
Some architectures use subnets with no NAT Gateway route — purely internal communication.
RDS doesn't need internet access, so its subnet can have no `0.0.0.0/0` route at all.

---

## Q3: What is a load balancer? ALB vs NLB vs CLB in AWS?

A **load balancer** distributes incoming traffic across multiple backend targets
(EC2 instances, ECS tasks, Lambda functions, IP addresses). It provides:
- **High availability**: if one target fails health checks, traffic routes to healthy ones
- **Scalability**: add/remove targets without changing DNS
- **TLS termination**: decrypts HTTPS at the load balancer, forwards plain HTTP internally
- **Single entry point**: one DNS name for your service regardless of how many instances

### ALB (Application Load Balancer) — Layer 7
Operates at the HTTP/HTTPS layer. Can inspect the request content and route based on it.

**Features**:
- Path-based routing: `/api/*` → ECS service A, `/static/*` → S3
- Host-based routing: `api.example.com` → backend A, `admin.example.com` → backend B
- Header-based routing: route based on custom headers
- Native WebSocket support
- HTTP/2 support
- WAF integration (Web Application Firewall)
- Target types: EC2 instances, ECS tasks, Lambda, IP addresses

**Use for**: All HTTP/HTTPS services, microservices with multiple routes, REST APIs.

### NLB (Network Load Balancer) — Layer 4
Operates at the TCP/UDP layer. Extremely high performance.

**Features**:
- Handles millions of requests per second with ultra-low latency (~100 microseconds)
- Preserves source IP address (ALB replaces source IP with ALB's IP)
- Static IP addresses (one per AZ) — useful for firewall whitelisting
- TLS termination (added later; ALB is still preferred for TLS)
- TCP and UDP traffic

**Use for**: Real-time applications (gaming, trading), non-HTTP protocols (MQTT, custom TCP), when you need static IPs.

### CLB (Classic Load Balancer) — Legacy
Old generation, supports basic Layer 4 and Layer 7 load balancing. No new features added.
**Avoid**: Use ALB or NLB instead. Only reason to use CLB is if migrating legacy infrastructure.

### Comparison

| Factor               | ALB                         | NLB                         |
|----------------------|-----------------------------|-----------------------------|
| Protocol             | HTTP/HTTPS/WebSocket        | TCP/UDP/TLS                 |
| OSI Layer            | 7 (Application)             | 4 (Transport)               |
| Routing logic        | Rich (path, host, header)   | IP + port only              |
| Performance          | Very high                   | Extreme (millions of RPS)   |
| Latency              | ~1ms                        | ~100 microseconds           |
| Static IPs           | No (use Global Accelerator) | Yes (1 per AZ)              |
| Source IP            | X-Forwarded-For header      | Preserved natively          |
| WebSocket            | Yes                         | Yes (TCP passthrough)       |
| Lambda target        | Yes                         | No                          |
| Price                | $0.008/LCU-hour             | $0.006/NLCU-hour            |
| Best for             | Web APIs, microservices     | Gaming, financial, non-HTTP |

---

## Q4: How does auto-scaling work with EC2? What metrics trigger it?

### Architecture
```
Auto Scaling Group (ASG)
├── Launch Template (AMI, instance type, user data, security groups)
├── Min capacity: 2
├── Max capacity: 20
├── Desired capacity: 4 (current running count)
└── Scaling Policies (when to add/remove)

Linked to:
├── Application Load Balancer Target Group (registers/deregisters instances)
└── CloudWatch Alarms (triggers scaling actions)
```

### Scaling Policy Types

**1. Target Tracking (simplest, most common)**:
```
Policy: Keep average CPU utilization at 50%
- CPU rises to 75% → ASG calculates how many instances needed → adds them
- CPU drops to 25% → removes excess instances (after scale-in cooldown)
```

**2. Step Scaling** (more control):
```
Alarm: CPU > 60%
  → If between 60-75%: add 1 instance
  → If between 75-90%: add 2 instances
  → If > 90%: add 4 instances

Alarm: CPU < 40%
  → Remove 1 instance (after 10 min cooldown)
```

**3. Scheduled Scaling**:
```
Every weekday at 8 AM UTC: set desired = 10
Every weekday at 8 PM UTC: set desired = 2
```

### Common Metrics That Trigger Scaling

| Metric                  | Service         | When to Use                              |
|-------------------------|-----------------|------------------------------------------|
| CPU Utilization         | EC2             | CPU-bound apps (most common)             |
| Memory Utilization*     | EC2             | Memory-bound apps (*custom metric)       |
| ALB RequestCountPerTarget| EC2/ECS        | Traffic-based scaling                    |
| SQS Queue Depth         | EC2             | Worker pools processing queued jobs      |
| ECS CPU/Memory          | ECS             | Container CPU or memory pressure         |
| Custom metric           | Any             | Business metric (active users, DB load)  |

*Memory is not a default CloudWatch metric. You must install the CloudWatch agent
on EC2 to publish memory utilization.

### Warm-Up and Cooldown
- **Scale-out cooldown**: After adding an instance, wait N seconds before evaluating
  again (prevents over-provisioning during rapid traffic spikes)
- **Scale-in cooldown**: After removing an instance, wait N seconds (prevents
  oscillation)
- **Instance warm-up time**: Time for a new instance to be ready (user data script
  runs, app starts) — ASG doesn't count it in metrics until warm-up completes

### Lifecycle Hooks
Pause the instance during launch or termination to run custom scripts:
- **Launch hook**: Wait for app initialization before registering with ALB
- **Termination hook**: Drain in-flight requests, ship final logs before termination

```bash
aws autoscaling put-lifecycle-hook \
  --auto-scaling-group-name my-asg \
  --lifecycle-hook-name app-ready \
  --lifecycle-transition autoscaling:EC2_INSTANCE_LAUNCHING \
  --heartbeat-timeout 300
```

---

## Q5: Explain AWS Secrets Manager vs SSM Parameter Store

Both store secrets/configuration securely. Choosing depends on your needs:

### AWS Secrets Manager
Purpose-built for secrets that need **automatic rotation**.

**Features**:
- Automatic credential rotation (Lambda function runs on schedule, updates secret,
  and updates the database)
- Native rotation support for: RDS, Redshift, DocumentDB
- Cross-account access
- Versioning (AWSCURRENT, AWSPREVIOUS, AWSPENDING stages)
- Audit trail via CloudTrail
- JSON value storage (store username + password together)

**Cost**: $0.40/secret/month + $0.05 per 10,000 API calls

```python
import boto3, json

def get_db_credentials():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='prod/myapp/postgres')
    secret = json.loads(response['SecretString'])
    return {
        'host': secret['host'],
        'username': secret['username'],
        'password': secret['password'],
        'dbname': secret['dbname']
    }
```

### SSM Parameter Store
General-purpose configuration and secret storage.

**Features**:
- Hierarchical path structure: `/myapp/prod/db-password`
- SecureString type: KMS-encrypted values
- No automatic rotation
- Standard tier: free (up to 10,000 parameters)
- Advanced tier: $0.05/parameter/month (supports larger values, policies)
- Reference directly in ECS task definitions and CloudFormation

**Cost**: Free for standard tier (up to 4KB per parameter)

```python
import boto3

ssm = boto3.client('ssm', region_name='us-east-1')

# Get a single parameter
def get_param(name: str) -> str:
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

# Get all params with a prefix
def get_params_by_path(path: str) -> dict:
    response = ssm.get_parameters_by_path(
        Path=path,
        WithDecryption=True,
        Recursive=True
    )
    return {p['Name'].split('/')[-1]: p['Value'] for p in response['Parameters']}

# Usage
config = get_params_by_path('/myapp/prod/')
# Returns: {'db-password': '...', 'api-key': '...', 'jwt-secret': '...'}
```

### Decision Guide

| Need                                    | Use                    |
|-----------------------------------------|------------------------|
| DB password with auto-rotation          | Secrets Manager        |
| API key, JWT secret (no rotation)       | SSM Parameter Store    |
| Config values (non-secret)              | SSM Parameter Store    |
| Cross-account secret sharing            | Secrets Manager        |
| Budget-sensitive (many secrets)         | SSM Parameter Store    |
| Built-in RDS credential rotation        | Secrets Manager        |

**Tip**: Many teams use SSM for non-rotating secrets (cheaper) and Secrets Manager
only for database credentials that need rotation.

---

## Q6: How do you do zero-downtime deployments on ECS?

**Zero-downtime deployment** means new versions of your app are deployed without
any requests failing during the transition.

ECS achieves this through its rolling update mechanism:

### Rolling Update (ECS Service default)
```
Config:
- Minimum healthy percent: 100 (never go below 100% capacity)
- Maximum percent: 200 (allow up to 200% capacity during deploy)

Deploy sequence:
1. ECS launches new task (version 2) → now at 200% (2 old + 2 new for desired=2)
2. New task passes health check
3. ECS registers new task with ALB target group
4. ECS deregisters old task from ALB target group
5. Old task receives no more new requests; in-flight requests complete (connection draining)
6. Old task stops
7. Repeat until all old tasks replaced
```

### Configuring Health Checks for Zero-Downtime

**ALB health check** (critical — must be fast and accurate):
```json
{
  "healthCheckPath": "/health",
  "healthCheckIntervalSeconds": 10,
  "healthCheckTimeoutSeconds": 5,
  "healthyThresholdCount": 2,
  "unhealthyThresholdCount": 3
}
```

**Your health endpoint**:
```python
@app.get("/health")
async def health():
    # Check dependencies are reachable
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="unhealthy")
```

### Connection Draining (Deregistration Delay)
When ECS deregisters a task from the ALB, the ALB waits for in-flight connections
to complete before fully removing the target. Default: 300 seconds. Set to 30-60
seconds for APIs with short request times.

### Blue/Green Deployment with AWS CodeDeploy
More controlled than rolling update:
```
Blue environment (current): 100% traffic
Green environment (new version): 0% traffic

Step 1: Deploy new version to green (test it)
Step 2: Gradually shift traffic: 10% green, 90% blue
Step 3: Monitor metrics/errors
Step 4: Fully shift to green (100%)
Step 5: If issues detected → instantly roll back to blue
```

Configure in ECS service:
```json
{
  "deploymentController": {
    "type": "CODE_DEPLOY"
  }
}
```

### Graceful Shutdown in Application
Your app must handle SIGTERM gracefully (ECS sends SIGTERM before stopping):
```python
import signal, asyncio

@app.on_event("shutdown")
async def shutdown_event():
    # Wait for in-flight requests to complete
    await asyncio.sleep(5)
    # Close DB connections
    await db.disconnect()
    print("Graceful shutdown complete")
```

```javascript
// Node.js
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        mongoose.connection.close(false, () => {
            process.exit(0);
        });
    });
});
```

---

## Q7: What is ECR and how does the Docker push workflow work?

**ECR (Elastic Container Registry)** is AWS's managed Docker image registry. Like
Docker Hub, but private, integrated with IAM, and within your AWS account.

**Why use ECR instead of Docker Hub for production**:
- Images stay in your AWS account (no external dependency)
- IAM authentication — no separate credentials
- Vulnerability scanning (automatically scans for CVEs)
- Lifecycle policies: delete old images automatically
- Replication: replicate images to multiple regions
- Private: no accidental public image exposure

### Full Docker Build → Push → Deploy Workflow

```bash
# --- One-time setup ---

# 1. Create ECR repository
aws ecr create-repository \
  --repository-name my-fastapi-app \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true

# Output: repositoryUri: 123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app

# --- Every deployment ---

# 2. Authenticate Docker to ECR (token valid 12 hours)
aws ecr get-login-password --region us-east-1 | \
  docker login \
    --username AWS \
    --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com

# 3. Build the image (use git SHA as tag for traceability)
GIT_SHA=$(git rev-parse --short HEAD)
IMAGE_URI="123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:${GIT_SHA}"

docker build -t $IMAGE_URI .

# 4. Also tag as latest
docker tag $IMAGE_URI \
  123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest

# 5. Push both tags
docker push $IMAGE_URI
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-fastapi-app:latest

# 6. Update ECS task definition with new image URI and deploy
aws ecs register-task-definition \
  --family my-fastapi-app \
  --container-definitions "[{\"name\":\"app\",\"image\":\"$IMAGE_URI\",...}]"

aws ecs update-service \
  --cluster my-cluster \
  --service my-fastapi-service \
  --force-new-deployment
```

### GitHub Actions CI/CD Pipeline
```yaml
name: Deploy to ECS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
          aws-region: us-east-1

      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and Push
        run: |
          IMAGE_URI="123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:${{ github.sha }}"
          docker build -t $IMAGE_URI .
          docker push $IMAGE_URI
          echo "IMAGE_URI=$IMAGE_URI" >> $GITHUB_ENV

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster my-cluster \
            --service my-service \
            --force-new-deployment
```

### ECR Lifecycle Policy (auto-delete old images)
```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {"type": "expire"}
    },
    {
      "rulePriority": 2,
      "description": "Delete untagged images older than 1 day",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 1
      },
      "action": {"type": "expire"}
    }
  ]
}
```

---

## Q8: How do you reduce Lambda cold starts?

### Root Cause
Cold start = time to start a new container + initialize the runtime + run your
initialization code. The main contributors are:

1. **Package size**: Large deployment packages take longer to download and unpack
2. **Heavy imports**: Loading TensorFlow, Pandas at import time can take 2-5 seconds
3. **Connection setup**: Establishing DB connections, loading ML models

### Optimization Strategies

**1. Minimize package size**
```bash
# Check what's taking space in your deployment package
pip install pipdeptree
pipdeptree --warn silence | grep -v "  "

# Use Lambda Layers for heavy dependencies (shared across functions, cached)
# Instead of packaging numpy/pandas in every function, create a shared layer

# Exclude dev dependencies
pip install -r requirements.txt --no-dev -t package/

# Use .zip instead of Docker for simple functions (faster cold start)
```

**2. Move heavy initialization outside the handler**
```python
# BAD — reinitializes on every invocation
def lambda_handler(event, context):
    import boto3             # Import inside handler
    import pandas as pd      # Runs every invocation
    s3 = boto3.client('s3')  # Creates new client every invocation
    df = pd.DataFrame()
    ...

# GOOD — runs once per container (cold start only)
import boto3
import pandas as pd  # Imported at module level

s3 = boto3.client('s3')  # Created once per container

def lambda_handler(event, context):
    # s3 and pd are already ready — no initialization overhead
    df = pd.DataFrame()
    ...
```

**3. Conditional heavy imports** (if not always needed)
```python
def lambda_handler(event, context):
    if event.get('action') == 'ml_inference':
        # Only import ML libraries when needed for that specific path
        from transformers import pipeline
        model = get_cached_model()
        ...
    else:
        # Fast path — no ML imports
        return simple_response(event)
```

**4. Provisioned Concurrency** (most effective but costs money)
```bash
# Keep 5 Lambda containers always warm (no cold starts for up to 5 concurrent requests)
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod \
  --provisioned-concurrent-executions 5

# Cost: ~$0.000004646 per GB-second provisioned (even when idle)
# 5 containers × 1 GB × 3600 s/hr × 24 hr × 30 days ≈ $60/month
```

**5. Increase memory allocation** (counter-intuitive but works)
Lambda allocates CPU proportionally to memory. More memory = more CPU = faster init.
Test: 128 MB cold start 800ms vs 512 MB cold start 300ms. Higher memory may cost less
overall if it reduces duration more than it increases the memory cost.

**6. Use ARM64 (Graviton2)**
```python
# In SAM template
Architecture: arm64  # 20% cheaper, often faster cold starts for Python/Node
```

**7. Connection pooling with RDS Proxy**
DB connections are expensive to establish. RDS Proxy maintains a warm connection pool
so Lambda functions connect instantly.

**8. Keep functions warm with EventBridge ping**
```yaml
# EventBridge rule: invoke the function every 5 minutes (hacky but free)
Schedule: rate(5 minutes)
# In handler:
def lambda_handler(event, context):
    if event.get('source') == 'warmup':
        return {'status': 'warm'}
    # ... actual logic
```

---

## Q9: What is SQS? When would you use it in an ML pipeline?

### What is SQS
SQS (Simple Queue Service) is a managed message queue. Producers put messages in;
consumers poll and process them. Messages are retained until explicitly deleted after
successful processing.

**Key properties**:
- **Decoupling**: Producer and consumer don't need to be running simultaneously
- **Durability**: Messages stored redundantly across 3 AZs
- **At-least-once delivery**: Messages may be delivered more than once (consumers
  must handle duplicates or use FIFO queue)
- **Visibility timeout**: Message hidden from other consumers while one consumer
  processes it. If not deleted within timeout, reappears for retry.
- **Dead Letter Queue (DLQ)**: Messages that fail N times are sent to a DLQ for
  investigation

### SQS in an ML Document Processing Pipeline

**Architecture**:
```
S3 Upload (PDF/image)
    ↓ (S3 event notification)
Lambda (validator)
├── Check file type and size
├── Extract metadata
├── Send to SQS with priority routing:
│   ├── small files → fast-processing-queue
│   └── large files → batch-processing-queue
    ↓
ECS Worker Pool (polls SQS)
├── Worker 1: receives message, processes document (OCR + ML extraction)
├── Worker 2: processes another document simultaneously
└── Worker 3: ...
    ↓
S3 (output JSON) + RDS (job status + results)
    ↓
Lambda (notifier) → API response / webhook to client
```

**Why SQS in the middle**:
1. **Traffic spike handling**: 100 documents uploaded simultaneously → 100 SQS messages.
   Workers process at their own pace. No messages lost.
2. **Retry logic**: If an ECS task crashes mid-processing, the message visibility
   timeout expires and another worker picks it up
3. **Backpressure**: Workers don't get overwhelmed — they take one message at a time
4. **Scaling signal**: Queue depth triggers Auto Scaling (more messages = more workers)

**Auto-scaling workers based on SQS queue depth**:
```python
# CloudWatch alarm: ApproximateNumberOfMessagesVisible > 100
# → Trigger: add 2 ECS tasks
# CloudWatch alarm: ApproximateNumberOfMessagesVisible < 5
# → Trigger: remove ECS tasks (scale to minimum)
```

**SQS Consumer in Python (ECS worker)**:
```python
import boto3, json, time

sqs = boto3.client('sqs', region_name='us-east-1')
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789/ml-processing-queue'

def run_worker():
    print("Worker starting, polling queue...")
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,      # Long polling — reduces empty receives
            VisibilityTimeout=600    # 10 min to process before message reappears
        )

        messages = response.get('Messages', [])
        if not messages:
            continue

        message = messages[0]
        body = json.loads(message['Body'])
        receipt_handle = message['ReceiptHandle']

        try:
            print(f"Processing document: {body['doc_id']}")
            result = process_ml_pipeline(body['s3_key'], body['doc_id'])
            save_result(body['doc_id'], result)

            # Only delete after successful processing
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            print(f"Successfully processed {body['doc_id']}")

        except Exception as e:
            print(f"Failed to process {body['doc_id']}: {e}")
            # Don't delete — message will reappear after visibility timeout
            # After maxReceiveCount failures, moves to DLQ
```

---

## Q10: Blue-green deployment vs rolling deployment on AWS

### Rolling Deployment
Replace old instances/tasks gradually, a few at a time.

```
Initial state:  [v1] [v1] [v1] [v1]  — 4 instances, all v1

Step 1:         [v2] [v1] [v1] [v1]  — replaced 1
Step 2:         [v2] [v2] [v1] [v1]  — replaced 2
Step 3:         [v2] [v2] [v2] [v1]  — replaced 3
Final:          [v2] [v2] [v2] [v2]  — all v2
```

**Pros**:
- Simple — ECS does this by default
- Lower cost (no duplicate infrastructure)
- Gradual exposure — problems affect partial traffic first

**Cons**:
- During deployment, both v1 and v2 serve traffic → mixed versions in flight
- Rollback is slow (deploy v1 again via another rolling update)
- Cannot test new version in isolation before sending real traffic

### Blue-Green Deployment
Run two identical environments. Switch traffic all at once (or gradually).

```
Blue environment (v1):  [v1] [v1] [v1] [v1]  ← 100% traffic
Green environment (v2): [v2] [v2] [v2] [v2]  ← 0% traffic (deployed, tested)

Traffic switch:
Blue: 0% traffic
Green: 100% traffic

If issue:
Blue: 100% traffic (instant rollback — just change the pointer)
```

**Pros**:
- Instant rollback (change ALB listener rule back to blue target group)
- Test new version with real infrastructure before sending traffic
- No mixed versions in production at any point
- Can run smoke tests against green before switching

**Cons**:
- Double infrastructure cost during deployment window
- More complex setup (requires CodeDeploy or custom orchestration)

### Implementation with AWS

**ECS + CodeDeploy (Blue-Green)**:
```yaml
# appspec.yaml (CodeDeploy configuration)
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: app
          ContainerPort: 8000
Hooks:
  - BeforeAllowTraffic: ValidateLambdaFunction
  - AfterAllowTraffic: CleanupLambdaFunction
```

CodeDeploy deployment configurations:
- `CodeDeployDefault.ECSAllAtOnce`: switch 100% traffic immediately
- `CodeDeployDefault.ECSLinear10PercentEvery1Minute`: 10% per minute over 10 minutes
- `CodeDeployDefault.ECSCanary10Percent5Minutes`: 10% for 5 min, then 90%

### Canary Deployment (hybrid)
Route a small percentage of traffic to new version:
```
v1: 90% of traffic
v2: 10% of traffic (canary)

Monitor error rates, latency for 10 minutes
If metrics look good → gradually shift to 100% v2
If problems → shift 100% back to v1
```

Cloud Run supports this natively with traffic splitting:
```bash
gcloud run services update-traffic my-service \
  --to-revisions my-service-v2=10,my-service-v1=90
```

---

## Q11: How do you make S3 uploads directly from browser (avoiding server upload)?

The pattern is called **client-side direct upload with presigned URLs**. The browser
uploads directly to S3 — your server only generates the URL and stores the final S3 key.

**Why this matters**:
- No bandwidth cost on your server (files go browser → S3, not browser → server → S3)
- Server not the bottleneck for large file uploads
- Scalable to many concurrent uploads

### Flow
```
1. Browser → POST /api/get-upload-url → Your Server
   (sends: filename, file size, content type)

2. Your Server → generates presigned upload URL → returns to browser
   (validates user is authorized, picks S3 key)

3. Browser → PUT directly to S3 presigned URL
   (S3 receives file without going through your server)

4. Browser → POST /api/confirm-upload → Your Server
   (sends: S3 key, file metadata)

5. Your Server → saves file record to database
```

### Backend (Python/FastAPI)
```python
import boto3, uuid
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET = 'my-uploads-bucket'

class UploadRequest(BaseModel):
    filename: str
    content_type: str
    file_size_bytes: int

@app.post("/api/get-upload-url")
async def get_upload_url(
    req: UploadRequest,
    current_user = Depends(get_current_user)  # Auth check
):
    # Validate
    if req.file_size_bytes > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(400, "File too large")
    if req.content_type not in ['application/pdf', 'image/jpeg', 'image/png']:
        raise HTTPException(400, "Invalid file type")

    # Generate a unique S3 key
    s3_key = f"uploads/{current_user.id}/{uuid.uuid4()}/{req.filename}"

    # Generate presigned URL (valid for 5 minutes)
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET,
            'Key': s3_key,
            'ContentType': req.content_type
        },
        ExpiresIn=300
    )

    return {
        'upload_url': presigned_url,
        's3_key': s3_key
    }
```

### Frontend (React)
```javascript
async function uploadFile(file) {
    // Step 1: Get presigned URL from your API
    const { upload_url, s3_key } = await fetch('/api/get-upload-url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            filename: file.name,
            content_type: file.type,
            file_size_bytes: file.size
        })
    }).then(r => r.json());

    // Step 2: Upload directly to S3 (no server involved)
    const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
            'Content-Type': file.type
        }
    });

    if (!uploadResponse.ok) throw new Error('S3 upload failed');

    // Step 3: Tell your server the upload is complete
    await fetch('/api/confirm-upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ s3_key, filename: file.name })
    });
}
```

### S3 CORS Configuration (required for browser uploads)
```json
[{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["https://your-app.com"],
    "ExposeHeaders": ["ETag"]
}]
```

---

## Q12: What is CloudFront? How does cache invalidation work?

**CloudFront** is AWS's CDN (Content Delivery Network). It caches content at 450+
edge locations worldwide, so users fetch from the nearest edge server rather than
your origin (S3, ALB, EC2).

### How It Works
```
First request (cache miss):
User (Tokyo) → CloudFront Tokyo edge → Origin (us-east-1)
                                                ↓
                                    Fetches content, stores in edge cache
                                                ↓
User (Tokyo) ← Content served from Tokyo edge (cached)

Subsequent requests (cache hit):
User (Tokyo) → CloudFront Tokyo edge → Returns cached content immediately
               (no request to origin, ultra-low latency)
```

### Cache TTL (Time To Live)
CloudFront caches based on `Cache-Control` headers from your origin:
```
Cache-Control: max-age=86400          → Cache for 24 hours
Cache-Control: max-age=0, no-cache   → Don't cache
Cache-Control: max-age=31536000      → Cache for 1 year (for hashed assets)
```

**Strategy for static React apps**:
```
index.html:         Cache-Control: no-cache, no-store        (always fetch latest)
main.abc123.js:     Cache-Control: max-age=31536000          (immutable, content-hashed)
logo.png:           Cache-Control: max-age=86400              (cache 1 day)
```

Content-hashed filenames (Webpack/Vite output: `main.abc123.js`) mean the filename
changes when the file changes — old cache entries are never needed.

### Cache Invalidation
When you need to force CloudFront to fetch fresh content from origin:

**Via AWS Console**: CloudFront → Distribution → Invalidations → Create

**Via AWS CLI**:
```bash
# Invalidate specific files
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/index.html" "/static/main.js"

# Invalidate everything (use sparingly — 1000 paths free per month, then $0.005/path)
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"
```

Invalidation propagates to all edge locations within ~1-2 minutes.

**Cost**: First 1,000 invalidation paths per month: free. After that: $0.005 per path.
Wildcard `/*` counts as 1 path.

### Common CloudFront Patterns

**Pattern 1: S3 + CloudFront for React SPA**:
```bash
# Build React app
npm run build

# Sync to S3
aws s3 sync ./build s3://my-spa-bucket --delete

# Invalidate CloudFront cache for index.html
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/index.html"
# Note: content-hashed JS/CSS files don't need invalidation
```

**Pattern 2: API behind CloudFront (cache GET responses)**:
```
CloudFront cache behavior:
- Path: /api/static-data/*  → cache for 1 hour (rarely changes)
- Path: /api/user/*         → no cache (user-specific)
- Path: /*                  → no cache (default)
```

### Lambda@Edge
Run JavaScript functions at CloudFront edge locations to modify requests/responses:
- Add security headers (HSTS, CSP, X-Frame-Options)
- A/B testing (route 50% to different origin)
- URL rewrites and redirects
- Auth validation at edge (before hitting origin)

---

## Q13: Explain multi-region architecture for high availability

**High Availability (HA)** at the region level protects against entire AWS region
failures (rare but not impossible — us-east-1 has had major outages).

### Single Region HA (baseline)
Most apps start here:
```
us-east-1:
├── AZ a: ALB + ECS tasks + RDS primary
└── AZ b: ALB + ECS tasks + RDS standby (Multi-AZ)

Handles: single AZ failure (e.g., data center fire)
Does not handle: full region failure
```

### Multi-Region Active-Passive
One primary region handles all traffic. Standby region is ready to take over.

```
Primary (us-east-1):  → 100% traffic
                      ECS + RDS primary

Standby (us-west-2):  → 0% traffic (ready to receive)
                      ECS + RDS replica (read-only, receives replication from primary)

Failover:
1. RDS read replica in us-west-2 promoted to primary
2. Route 53 health check detects primary is down
3. DNS failover: Route 53 routes to us-west-2 (TTL-dependent, 60 sec default)
4. ECS in us-west-2 scales up to handle full traffic
```

**RPO (Recovery Point Objective)**: How much data you can afford to lose.
With async RDS replication, RPO = seconds to minutes of lag.

**RTO (Recovery Time Objective)**: How long to recover.
With DNS failover, RTO = 1-5 minutes.

### Multi-Region Active-Active
Both regions handle traffic simultaneously.

```
User (East Coast) → Route 53 geolocation → us-east-1
User (West Coast) → Route 53 geolocation → us-west-2

us-east-1:
├── ECS service
└── RDS regional cluster

us-west-2:
├── ECS service
└── RDS regional cluster

Aurora Global Database: synchronizes writes from both regions
```

**Challenges with Active-Active**:
- Write conflicts (if both regions accept writes to the same data)
- Higher latency for cross-region consistency
- Complex application logic (which region is authoritative for which user?)

**Aurora Global Database** is the managed solution: one primary region for writes,
secondary regions for reads. Failover promotes a secondary to primary in < 1 minute.

### Route 53 Routing Policies
- **Failover**: route to primary, if health check fails → secondary
- **Geolocation**: route based on user's geographic location
- **Latency-based**: route to region with lowest latency for that user
- **Weighted**: route X% to us-east-1, Y% to eu-west-1

### Multi-Region Considerations
- **Data residency**: GDPR requires EU user data stays in EU (mandate multi-region)
- **Latency**: users in Asia need an Asia-Pacific region
- **Cost**: ~2x infrastructure cost
- **Complexity**: secrets, configs, DB schemas must be synchronized
- **S3 Cross-Region Replication**: automatically replicate objects to another region

---

## Q14: How do you monitor costs on AWS? What are cost optimization strategies?

### Cost Monitoring Tools

**AWS Cost Explorer**:
- Visualize spending by service, region, account, tag
- Forecast future costs
- Identify cost anomalies
- Free to use

```bash
# Get last 30 days of costs by service
aws ce get-cost-and-usage \
  --time-period Start=2024-12-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

**AWS Budgets**:
- Set budget thresholds (monthly cost, usage, reservation coverage)
- Alert via email/SNS when approaching/exceeding budget

```bash
# Create a $100/month budget with 80% alert
aws budgets create-budget \
  --account-id 123456789 \
  --budget '{"BudgetName":"Monthly","BudgetLimit":{"Amount":"100","Unit":"USD"},"TimeUnit":"MONTHLY","BudgetType":"COST"}' \
  --notifications-with-subscribers '[{"Notification":{"NotificationType":"ACTUAL","ComparisonOperator":"GREATER_THAN","Threshold":80},"Subscribers":[{"SubscriptionType":"EMAIL","Address":"alerts@company.com"}]}]'
```

**Cost Allocation Tags**: Tag all resources with `project`, `environment`, `team`.
Then filter Cost Explorer by tag to see costs per project.

```bash
# Tag an EC2 instance
aws ec2 create-tags --resources i-1234567890 \
  --tags Key=Project,Value=myapp Key=Environment,Value=production Key=Team,Value=backend
```

### Cost Optimization Strategies

**1. Right-sizing EC2/ECS**:
```
AWS Compute Optimizer analyzes CloudWatch CPU/memory metrics and recommends:
"Your m5.2xlarge is only 15% utilized — downsize to m5.large (saves $200/month)"
```

**2. Reserved Instances / Savings Plans**:
- On-Demand: full price, no commitment
- Reserved Instances: commit to 1 or 3 years, save 30-70%
- Savings Plans: commit to $/hour of compute, flexible across instance types

Best for predictable baseline load (always-on EC2, RDS).

**3. Spot Instances** (for fault-tolerant workloads):
Up to 90% discount. AWS can reclaim with 2-minute notice.
Use for: ML training, batch processing, development environments.

```yaml
# ECS capacity provider mix: 70% spot, 30% on-demand
capacityProviderStrategy:
  - capacityProvider: FARGATE_SPOT
    weight: 7
    base: 0
  - capacityProvider: FARGATE
    weight: 3
    base: 1
```

**4. Scale to zero**:
- Turn off dev/staging environments at night (Lambda, EventBridge cron)
- Use Lambda or Cloud Run for services that aren't always active

**5. S3 cost optimization**:
- Enable Intelligent-Tiering for objects with unknown access patterns
- Lifecycle policies: move old objects to Glacier
- Delete incomplete multipart uploads

**6. Data transfer costs** (often overlooked):
- Inbound to AWS: free
- Outbound to internet: $0.09/GB (first 10 TB)
- Between AZs in same region: $0.01/GB each way
- Use VPC endpoints to avoid NAT Gateway charges for S3/DynamoDB traffic

**7. NAT Gateway reduction**:
NAT Gateway is $0.045/GB processed — can be expensive.
- Use VPC endpoints for S3 and DynamoDB (traffic doesn't go through NAT)
- Consider NAT instances for small workloads (cheaper but you manage them)

```bash
# Create S3 VPC endpoint — eliminates NAT Gateway charges for S3 traffic
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-abc123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-abc123
```

---

## Q15: What is IAM role chaining? When would you use it?

**Role chaining** is when a principal (user, service, or role) assumes one IAM role,
and then that role assumes another IAM role. You're chaining multiple `sts:AssumeRole`
calls.

```
Developer (IAM User)
    → assumes → Developer-Role (read-only access)
                    → assumes → Production-Admin-Role (full access to prod)
```

Or in a service context:
```
Lambda Function (execution role A)
    → assumes → Cross-Account-Role in Account B
                    → accesses → S3 bucket in Account B
```

### Use Cases

**1. Cross-account access** (most common):
Your application in Account A needs to access resources in Account B (e.g., a
shared data account, a security audit account):

```python
import boto3

def get_cross_account_client(role_arn: str, service: str, region: str):
    """Assume a role in another AWS account and return a service client."""
    sts = boto3.client('sts')

    assumed_role = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='cross-account-session',
        DurationSeconds=3600
    )

    credentials = assumed_role['Credentials']

    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

# Access S3 in a different AWS account
s3_client = get_cross_account_client(
    'arn:aws:iam::999888777:role/DataAccessRole',
    's3',
    'us-east-1'
)
objects = s3_client.list_objects_v2(Bucket='shared-data-bucket')
```

**2. Privilege escalation with time limit**:
Developers have a base role with minimal permissions. When they need to perform a
sensitive operation (deploy to prod), they temporarily assume a higher-privilege role.
The session expires after 1 hour. This is logged in CloudTrail.

**3. Multi-account organization**:
Large organizations have hundreds of AWS accounts (per team, per environment).
A central CI/CD account assumes roles in each target account to deploy.

### Limitations
- Maximum session duration of chained role: 1 hour (cannot extend)
- Maximum role chain depth: not officially documented, but keep it short
- Each AssumeRole call is logged in CloudTrail (good for audit)

---

## Q16: How do you handle database migrations in a containerized app on ECS/Cloud Run?

Database migrations are changes to the database schema (adding tables, columns,
indexes) that must be applied before your new application code runs. In containers,
this is tricky because you need migrations to run exactly once, before the app starts.

### The Problem
```
Old code:    SELECT id, name FROM users
New code:    SELECT id, name, email FROM users  ← needs email column

Migration:   ALTER TABLE users ADD COLUMN email VARCHAR(255)

If you deploy the new code before running the migration → crash
If you run migration after deploying new code → crash during window
```

### Strategy 1: Init Container (recommended for ECS)
Run migrations as a separate task before deploying the new service.

```bash
# CI/CD pipeline:

# Step 1: Run migrations as a standalone ECS task
aws ecs run-task \
  --cluster my-cluster \
  --task-definition my-app-migrations:latest \
  --launch-type FARGATE \
  --overrides '{"containerOverrides":[{"name":"app","command":["python","manage.py","migrate"]}]}'

# Wait for migration task to complete
aws ecs wait tasks-stopped --cluster my-cluster --tasks $TASK_ARN

# Check exit code
EXIT_CODE=$(aws ecs describe-tasks --cluster my-cluster --tasks $TASK_ARN \
  --query 'tasks[0].containers[0].exitCode' --output text)
[ "$EXIT_CODE" -eq 0 ] || { echo "Migration failed!"; exit 1; }

# Step 2: Only if migration succeeded, deploy new app version
aws ecs update-service \
  --cluster my-cluster \
  --service my-service \
  --force-new-deployment
```

### Strategy 2: Startup Script in Entrypoint
Run migration as part of app startup. Only safe if your migration tool ensures
idempotency and handles concurrent runs safely.

```dockerfile
# Dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
#!/bin/bash
# entrypoint.sh

echo "Running database migrations..."
python manage.py migrate --noinput   # Django
# OR: alembic upgrade head           # SQLAlchemy
# OR: npx prisma migrate deploy      # Prisma (Node.js)

if [ $? -ne 0 ]; then
  echo "Migration failed! Exiting."
  exit 1
fi

echo "Starting application..."
exec "$@"   # Run the CMD (uvicorn, node, etc.)
```

**Risk**: If you run 3 ECS tasks simultaneously, all 3 run migrations concurrently.
Good migration tools (Alembic, Flyway) use a lock table to prevent this.

### Strategy 3: Cloud Run Jobs (GCP)
Cloud Run Jobs are designed exactly for this use case:
```bash
# Create a job for migrations
gcloud run jobs create migrate-db \
  --image gcr.io/PROJECT/my-app \
  --command python \
  --args "manage.py,migrate"

# Run before deploying new revision
gcloud run jobs execute migrate-db --wait

# Then deploy
gcloud run deploy my-app --image gcr.io/PROJECT/my-app:new-version
```

### Backward-Compatible Migrations (best practice)
Write migrations that the old code can still run against. Deploy in phases:

**Phase 1 (migration only)**:
```sql
-- ADD new column, but make it nullable (old code ignores it)
ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL;
```

**Phase 2 (deploy new code)**:
```python
# New code uses email column
# Old code still works (column is nullable, old code doesn't reference it)
```

**Phase 3 (cleanup, later)**:
```sql
-- After confirming new code works, add constraints
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

This pattern avoids downtime even during migrations.

### Tools
| Language  | Migration Tool     | Notes                                     |
|-----------|--------------------|-------------------------------------------|
| Python    | Alembic            | SQLAlchemy-based, explicit versioning     |
| Python    | Django migrations  | Built-in to Django, automatic             |
| Node.js   | Prisma Migrate     | Type-safe, generates SQL from schema      |
| Node.js   | Knex.js migrations | Explicit SQL files                        |
| Any       | Flyway             | Java-based but works with any SQL DB      |
| Any       | Liquibase          | XML/YAML/SQL format, comprehensive        |
