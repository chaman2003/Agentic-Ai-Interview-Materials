# Amazon — Self Introduction + Interview Prep (EXAMPLE)

---

## Self Introduction (2 minutes — say it 5 times out loud)

"Hi, I'm Jordan, a final-year Computer Science student from UC Berkeley with 3.9 GPA. My technical stack includes Python, JavaScript, Node.js, and Go, with strong expertise in AWS services, serverless architecture, and e-commerce systems. I'm proficient with databases like DynamoDB, RDS, and have built systems that handle high availability and fault tolerance.

I built a project called QuickCart—an e-commerce platform handling 50K+ concurrent users with real-time inventory management and 99.9% uptime. The system uses AWS Lambda for serverless compute, DynamoDB for database scalability, and CloudFront for global content delivery. I architected product recommendation engine using collaborative filtering that improved conversion by 25%. Currently, I'm interning at RetailTech, building backend services for inventory forecasting and customer personalization at scale. This experience directly aligns with Amazon's customer-obsessed philosophy and operational excellence. I'm excited to bring my full-stack e-commerce and AWS expertise to your team."

---

## QuickCart — Architecture Walkthrough

**What it is:** E-commerce platform handling 50K+ concurrent users — internship project (4 months).

**Why it's relevant to Amazon:** Amazon's core business is e-commerce at massive scale. I built a scalable commerce system from scratch.

**Core Components:**
1. User Authentication (JWT + OAuth)
2. Product Catalog (DynamoDB with GSI)
3. Shopping Cart (Redis cache + DynamoDB)
4. Order Processing (SQS queue + Lambda)
5. Payment Integration (Stripe API)
6. Inventory Management (Real-time sync)
7. Recommendation Engine (Collaborative filtering)
8. Notification System (SNS + SES)

**Technology Stack:**
- Backend: Node.js Express, Python FastAPI
- Cloud: AWS (Lambda, DynamoDB, S3, CloudFront, SQS, SNS)
- Frontend: React with Redux
- Caching: Redis
- Search: Elasticsearch
- Monitoring: CloudWatch, X-Ray

**Why 99.9% uptime with 50K concurrent users:**
"We used auto-scaling across multiple EC2 instances with an Application Load Balancer distributing traffic. DynamoDB provides automatic scaling based on demand. We implemented circuit breakers to handle service failures gracefully. Multi-region replication with Route 53 failover ensures no single point of failure. Caching with Redis reduced database load by 70%."

---

## RetailTech Internship

**Current work:**
- Building forecasting models for inventory optimization
- Designing personalization algorithms for product recommendations
- Implementing real-time price optimization logic
- Developing analytics dashboards for business metrics

**Key projects:**
- Demand forecasting system (ARIMA + ML models)
- A/B testing framework for personalization
- Real-time pricing engine (reduced overstock by 30%)

---

## Amazon-Specific Technical Questions

**Q: Design an e-commerce shopping cart system.**
"Use a combination of Redis for session carts (fast reads/writes) and DynamoDB for persistent storage (durability). When a user adds an item, update Redis immediately for performance. Periodically sync to DynamoDB for persistence. For checkout, use SQS to queue orders asynchronously. If a payment fails, remove from inventory. Include inventory validation before finalizing orders to prevent overselling."

**Q: What is eventual consistency and when is it acceptable?**
"Eventual consistency means replicas temporarily show different data but converge over time. It's acceptable for non-critical reads like product recommendations or view counts. It's NOT acceptable for inventory, payments, or account balances—these need strong consistency. Amazon chooses eventual consistency for catalog reads but strong consistency for financial transactions."

**Q: How would you handle inventory management at scale?**
"Use DynamoDB with conditional writes to prevent overselling. When an order comes in, use `UpdateItem` with a ConditionExpression: only decrement inventory if it's > 0. For distributed systems, implement optimistic locking to detect conflicts. Maintain a cache layer for hot items. Use event streaming (Kinesis) to sync inventory across regions."

