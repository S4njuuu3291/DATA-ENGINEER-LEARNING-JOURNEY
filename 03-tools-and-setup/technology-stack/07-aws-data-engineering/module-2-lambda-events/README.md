# Module 2: AWS Lambda & Event-Driven Architecture

> **Duration:** 8 hours  
> **Level:** ⭐⭐⭐ Intermediate  
> **Prerequisites:** Module 1 (S3, IAM, VPC)  
> **Author:** Data Engineering Curriculum  
> **Last Updated:** February 8, 2026

---

## 📚 Module Overview

Modul ini mengajarkan **serverless compute & event-driven data processing**:

1. **Lambda Functions** → Serverless data processing (no infrastructure management)
2. **EventBridge** → Event routing & scheduling (cron jobs, S3 triggers)
3. **Integration Patterns** → Lambda + S3 + IAM + VPC (production-ready pipelines)

**Why Lambda?** Di dunia data engineering, **80% workload adalah batch processing yang berjalan sesekali** (hourly, daily). Running EC2 24/7 untuk workload seperti ini = **buang budget**. Lambda = pay per request, auto-scaling, zero maintenance.

**Industry Reality:**
- Validasi file CSV (5 detik execution) → $0.00001 per file
- EC2 t3.small 24/7 → $15/month untuk workload yang sama
- Lambda scales otomatis 0 → 1000 concurrent executions

---

## 🎯 Learning Objectives

Setelah menyelesaikan module ini, Anda akan bisa:

- ✅ Create Lambda functions untuk data validation & transformation
- ✅ Configure S3 event triggers untuk otomatis process file uploads
- ✅ Implement error handling patterns (retries, Dead Letter Queues, CloudWatch alarms)
- ✅ Optimize Lambda cost & performance (memory sizing, cold starts, concurrency)
- ✅ Design event-driven pipelines dengan EventBridge (schedules, pattern matching)
- ✅ Integrate Lambda dengan Module 1 services (IAM roles, S3 buckets, VPC endpoints)
- ✅ Debug Lambda functions menggunakan CloudWatch Logs & X-Ray

---

## 📖 Learning Path

### Recommended sequence (linear, dependent)

```
Week 2 (Days 1-3): Lambda Fundamentals
├─ Day 1: Why Lambda + serverless economics (60 min theory)
├─ Day 2: Data processing patterns + layers (60 min theory)
├─ Day 3: Error handling + DLQ + CloudWatch (60 min theory)
└─ Day 4: Performance optimization + cost analysis (60 min theory)
   └─ Subtotal: 4 hours theory + 1.5 hours exercises

Week 2 (Days 5-6): EventBridge & Orchestration
├─ Day 5: EventBridge basics + schedules (45 min theory)
├─ Day 6: Event patterns + fan-out (60 min theory)
└─ Subtotal: ~2 hours theory + 1 hour exercises

Week 2 (Day 7): Integration & Production Patterns
├─ Day 7: S3 + Lambda end-to-end pipeline (60 min theory)
└─ Subtotal: 1 hour theory + 1.5 hours exercises

Total: ~8 hours theory + 4 hours exercises = 12 hours
```

---

## 🗂️ Module Structure

### Part 1: Lambda Functions (4 topics, 240 min)

| Topic | File | Duration | Key Concepts |
|-------|------|----------|--------------|
| **Why Lambda?** | [01-why-lambda-exists.md](./01-lambda/01-why-lambda-exists.md) | 60 min | Cost comparison EC2 vs Lambda, serverless benefits, when NOT to use Lambda |
| **Data Processing** | [02-lambda-data-processing.md](./01-lambda/02-lambda-data-processing.md) | 60 min | Execution model, memory/CPU, timeout, Lambda Layers, idempotency |
| **Error Handling** | [03-lambda-error-handling.md](./01-lambda/03-lambda-error-handling.md) | 60 min | Retries, Dead Letter Queue, CloudWatch Logs/Metrics, error patterns |
| **Optimization** | [04-lambda-optimization.md](./01-lambda/04-lambda-optimization.md) | 60 min | Cost optimization, cold starts, VPC best practices, concurrency limits |

**Learning Outcomes:**
- Understand Lambda pricing model & when it saves money
- Write production-ready Lambda functions with proper error handling
- Optimize Lambda for cost & performance

---

### Part 2: EventBridge (2 topics, 105 min)

| Topic | File | Duration | Key Concepts |
|-------|------|----------|--------------|
| **EventBridge Basics** | [01-eventbridge-basics.md](./02-eventbridge/01-eventbridge-basics.md) | 45 min | Event bus, rules, targets, cron/rate expressions, vs traditional cron |
| **Event Patterns** | [02-eventbridge-patterns.md](./02-eventbridge/02-eventbridge-patterns.md) | 60 min | Fan-out, event filtering, cross-account, DLQ for targets |

**Learning Outcomes:**
- Schedule Lambda functions (hourly ETL, daily reports)
- Design event-driven architectures (S3 upload → Lambda → Glue)
- Filter events efficiently (only process `.csv` files from `/bronze/`)

---

### Part 3: Integration (1 topic, 60 min)

| Topic | File | Duration | Key Concepts |
|-------|------|----------|--------------|
| **S3 + Lambda** | [01-s3-lambda-integration.md](./03-integration/01-s3-lambda-integration.md) | 60 min | S3 event notifications, IAM roles, VPC endpoints, Bronze→Silver ETL, idempotency |

**Learning Outcomes:**
- Build end-to-end data pipelines (file upload → validation → transformation)
- Apply Module 1 concepts (IAM roles dari Module 1, S3 buckets, VPC endpoints)

---

## 🎓 Prerequisites

**From Module 1 (MUST complete first):**
- ✅ S3 buckets & medallion architecture (bronze/silver/gold)
- ✅ IAM roles & policy JSON (Lambda execution role needs S3 permissions)
- ✅ VPC endpoints (private Lambda access to S3)

**Technical Skills:**
- Python basics (functions, try/except, imports)
- JSON syntax (event payloads, IAM policies)
- AWS CLI familiarity (aws lambda invoke, aws s3 cp)

**AWS Account:**
- Free Tier eligible account (Lambda free tier = 1M requests/month)
- IAM user dengan AdministratorAccess atau custom policy:
  - `lambda:CreateFunction`, `lambda:InvokeFunction`
  - `iam:CreateRole`, `iam:AttachRolePolicy`
  - `s3:PutBucketNotification`
  - `events:PutRule`, `events:PutTargets`

---

## 🧪 Hands-On Exercises

**File:** [Module 2 Exercises](../exercises/module-2-lambda-events-exercises.md)

**8 exercises total (~4 hours):**

**Lambda Exercises (4):**
1. Hello World Lambda (Python) - Basic function creation & testing
2. CSV Validation Lambda - Process orders.csv from S3 with pandera
3. Lambda with Layer - Share pandas dependency across functions
4. Error Handling - DLQ + CloudWatch alarms

**EventBridge Exercises (2):**
5. Schedule Lambda - Cron job every 5 minutes
6. S3 Event Pattern - Trigger only for `.csv` in `/bronze/`

**Integration Exercises (2):**
7. Bronze → Silver Pipeline - End-to-end ETL with validation
8. Fan-out Pattern - 1 S3 upload → 3 Lambda functions

---

## 📊 Assessment Checklist

Anda siap untuk Module 3 jika bisa:

- [ ] Explain kapan Lambda lebih murah daripada EC2 (give cost example)
- [ ] Create Lambda function yang process S3 file upload
- [ ] Write IAM policy untuk Lambda execution role (S3 + CloudWatch permissions)
- [ ] Configure Dead Letter Queue untuk failed Lambda invocations
- [ ] Set up EventBridge rule dengan cron expression (daily 2 AM)
- [ ] Implement idempotency pattern (handle duplicate S3 events)
- [ ] Debug Lambda failures menggunakan CloudWatch Logs
- [ ] Optimize Lambda memory allocation untuk cost/performance trade-off

---

## 💰 Cost Considerations

**Lambda Pricing (us-east-1, Feb 2026):**
- First 1M requests/month: **FREE**
- $0.20 per 1M requests after
- $0.0000166667 per GB-second

**Example workload:**
- 10,000 file uploads/day = 300K/month
- Each Lambda: 512 MB, 2 second execution
- Cost: **$0.00** (within free tier) + $1.67 for compute = **$1.67/month**

**Compare to EC2:**
- t3.small (2 vCPU, 2 GB) 24/7 = **$15.18/month**
- Savings: **~$13.50/month** (90% cheaper)

**When Lambda becomes expensive:**
- Constantly running (>20% uptime) → EC2 cheaper
- Large memory (>3 GB) + long runtime (>5 min) → Glue/EMR better
- Rule of thumb: If execution time <15 min & infrequent → Lambda wins

---

## 🔗 Study Materials

**Official AWS Docs:**
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [EventBridge User Guide](https://docs.aws.amazon.com/eventbridge/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

**Recommended Reading:**
- *Serverless Architectures on AWS* (book)
- AWS re:Invent sessions on Lambda optimization
- AWS Well-Architected: Serverless Lens

---

## ⏭️ What's Next?

**Module 3: AWS Glue Data Catalog** → Metadata management & schema evolution  
**Module 4: AWS Glue ETL** → Distributed transformations with PySpark  

---

## 🔗 Quick Links

- [Module 2 Exercises](../exercises/module-2-lambda-events-exercises.md)
- [Lambda Code Samples](../data/lambda-code/)
- [AWS Lambda Cheatsheet](../cheatsheets/aws-lambda-cheatsheet.md)
- [AWS EventBridge Cheatsheet](../cheatsheets/aws-eventbridge-cheatsheet.md)
- [Back to Module 1](../module-1-aws-foundation/README.md)
- [Back to Roadmap](../README.md)

---

## 💡 Pro Tips

1. **Start small:** Test Lambda locally first (no AWS charges while debugging)
2. **Use Layers:** Don't package pandas in every function (180 MB → 1 MB with layer)
3. **Monitor costs:** Set CloudWatch billing alarm at $5/month
4. **Version control:** Store Lambda code in Git, deploy via CI/CD
5. **Think events:** Design pipelines around events (file upload, schedule) not polling

---

**Ready? Start with [01-why-lambda-exists.md](./01-lambda/01-why-lambda-exists.md) →**
