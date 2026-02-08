# Module 1: AWS Foundation (S3, IAM & Networking)

> **Duration:** 10 hours  
> **Level:** ⭐⭐☆ Beginner-Intermediate  
> **Prerequisites:** Basic AWS account knowledge, familiarity with CLI  
> **Author:** Data Engineering Curriculum  
> **Last Updated:** February 8, 2026

---

## 📚 Module Overview

Modul ini mengajarkan **tiga pilar fundamental** AWS Data Engineering:

1. **S3 (Simple Storage Service)** → Where your data lives
2. **IAM (Identity & Access Management)** → Who can access what
3. **VPC (Virtual Private Cloud)** → How data moves securely

Tanpa memahami foundation ini, pipeline Anda akan **insecure**, **expensive**, dan **unmaintainable**.

---

## 🎯 Learning Objectives

Setelah menyelesaikan module ini, Anda akan bisa:

- ✅ Design S3 architecture menggunakan medallion pattern (bronze/silver/gold)
- ✅ Implement least privilege IAM policies untuk data engineering roles
- ✅ Explain trade-offs antara storage classes (Standard → Glacier)
- ✅ Configure private networking untuk data pipelines menggunakan VPC endpoints
- ✅ Audit permissions dan identify security gaps dalam existing policies
- ✅ Optimize S3 costs melalui versioning, lifecycle policies, dan storage classes
- ✅ Design secure data flow tanpa exposing data ke public internet

---

## 📖 Learning Path

### Recommended sequence (linear, dependent)

```
Week 1 (Days 1-3): S3 Fundamentals
├─ Day 1: Why S3 exists + ecosystem (45 min theory)
├─ Day 2: Storage classes + cost optimization (60 min theory)
├─ Day 3: Versioning + encryption + access control (45 min theory)
└─ Day 4: Medallion architecture deep-dive (45 min theory)
   └─ Subtotal: 4 hours theory + 2 hours exercises

Week 1 (Days 5-7): IAM Fundamentals
├─ Day 5: Why IAM matters + identities (45 min theory)
├─ Day 6: Policy JSON fundamentals (75 min theory - MOST COMPLEX)
├─ Day 7: Least privilege patterns (60 min theory)
└─ Day 8: Best practices + audit trail (45 min theory)
   └─ Subtotal: 4 hours theory + 2 hours exercises

Week 2 (Days 9-10): VPC & Networking
├─ Day 9: VPC concepts + S3 endpoints (45 min theory)
├─ Day 10: Private networking for pipelines (60 min theory)
└─ Day 11: Network security patterns (45 min theory)
   └─ Subtotal: 2.5 hours theory + 1.5 hours exercises
```

**Total Time Investment:** 10 hours (theory) + 5.5 hours (exercises & labs) = 15.5 hours

---

## 📂 Sub-Modules

### **Part 1: S3 (Simple Storage Service)** — ⏱️ 3-4 hours

**Why it matters:** S3 is the backbone of AWS data lakes. 90% of data engineering jobs involve S3.

| File | Duration | Topic |
|------|----------|-------|
| [01-why-s3-exists.md](./01-s3/01-why-s3-exists.md) | 45 min | Storage problems AWS solves |
| [02-s3-storage-classes.md](./01-s3/02-s3-storage-classes.md) | 60 min | Standard, IA, Glacier, Deep Archive (cost vs speed) |
| [03-s3-security-versions.md](./01-s3/03-s3-security-versions.md) | 45 min | Versioning, Object Locking, Encryption |
| [04-s3-medallion-architecture.md](./01-s3/04-s3-medallion-architecture.md) | 45 min | Data lake architecture (bronze/silver/gold) |

**Learning Outcome:** Design S3 data lake with proper partitioning, security, and cost optimization

**Exercises:** [S3 Exercises →](../exercises/module-1-aws-foundation-exercises.md#s3-exercises)

---

### **Part 2: IAM (Identity & Access Management)** — ⏱️ 3-4 hours

**Why it matters:** Security breaches cost millions. 99% traced to bad IAM policies.

| File | Duration | Topic |
|------|----------|-------|
| [01-why-iam-exists.md](./02-iam/01-why-iam-exists.md) | 45 min | Security fundamentals |
| [02-iam-identities.md](./02-iam/02-iam-identities.md) | 60 min | Users, Groups, Roles (when to use each) |
| [03-iam-policy-json.md](./02-iam/03-iam-policy-json.md) | 75 min | Policy anatomy (Effect, Action, Resource, Condition) |
| [04-iam-least-privilege.md](./02-iam/04-iam-least-privilege.md) | 60 min | Enterprise patterns (start restrictive, add as needed) |
| [05-iam-security-best-practices.md](./02-iam/05-iam-security-best-practices.md) | 45 min | MFA, rotation, audit trails (CloudTrail) |

**Learning Outcome:** Write least-privilege policies, audit permissions, understand security trade-offs

**Exercises:** [IAM Exercises →](../exercises/module-1-aws-foundation-exercises.md#iam-exercises)

---

### **Part 3: VPC (Virtual Private Cloud)** — ⏱️ 2-3 hours

**Why it matters:** Private networks prevent unauthorized access. Data stays within your infrastructure.

| File | Duration | Topic |
|------|----------|-------|
| [01-why-vpc-exists.md](./03-vpc/01-why-vpc-exists.md) | 45 min | Network isolation fundamentals |
| [02-vpc-subnets-basics.md](./03-vpc/02-vpc-subnets-basics.md) | 60 min | Subnets, public vs private, routing |
| [03-s3-vpc-integration.md](./03-vpc/03-s3-vpc-integration.md) | 45 min | VPC endpoints (private S3 access, cost savings) |
| [04-network-security-patterns.md](./03-vpc/04-network-security-patterns.md) | 45 min | Security groups, NACLs, pipeline patterns |

**Learning Outcome:** Design private data pipeline (no internet exposure), optimize data transfer costs

**Exercises:** [VPC Exercises →](../exercises/module-1-aws-foundation-exercises.md#vpc-exercises)

---

## 🔗 Dependencies Between Sub-Modules

```
S3 (independent, read this first)
    ↓
IAM (depends on S3 understanding - you'll write S3 policies)
    ↓
VPC (depends on both - integrates S3 with private networking)
```

**Can you skip S3?**  
❌ No. IAM policies must reference S3 resources.

**Can you skip IAM?**  
❌ No. Every AWS action requires identity & permissions.

**Can you skip VPC?**  
⚠️ Mostly (modules 2-5 work without VPC). VPC essential for **production security**.

---

## 📊 Real-World Scenario

**Imagine:** You're building a data pipeline for an e-commerce company.

**Week 1:** Raw customer order data lands in **S3 raw bucket** every day
```
s3://ecommerce-lake/raw/orders/2024-01-15/orders.csv
```

**Who needs access?**
- ✅ Data engineer (read raw, write processed)
- ✅ Analytics team (read processed, can't touch raw)
- ❌ Finance team (only read final aggregations)
- ❌ Marketing team (can't see customer emails)

**How do we enforce this?**
1. **S3 structure:** Separate folders per data sensitivity
2. **IAM policies:** Role-based permissions (data eng ≠ analysts ≠ finance)
3. **VPC endpoints:** Data never touches public internet

**This module teaches exactly that.**

---

## 🛠️ Prerequisites & Setup

### Required
- [ ] AWS Account (free tier eligible)
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] Basic understanding of CLI commands

### Recommended
- [ ] VS Code with AWS Toolkit extension
- [ ] Some experience with JSON (for IAM policies)
- [ ] Comfort with networking concepts (CIDR, subnets)

### How to Check Your Setup
```bash
# Check AWS CLI
aws --version

# Check credentials
aws sts get-caller-identity

# Check account ID
aws iam get-user
```

---

## 📚 Study Materials Available

### **Theory Files** (📖 Reading material)
- 13 markdown files covering all topics
- Each 45-75 minutes to read
- Includes code examples, diagrams, real scenarios

### **Exercise Files** (✏️ Hands-on practice)
- 14 total exercises (5 S3 + 5 IAM + 4 VPC)
- Estimated 15-45 min per exercise
- Guided solutions included

### **Cheatsheets** (⚡ Quick reference)
- AWS S3 CLI/Boto3 commands
- IAM policy templates
- VPC command reference
- Use while practicing

### **Sample Data** (📊 Real datasets)
- E-commerce transaction logs
- API request logs
- Schemas for medallion pattern examples

---

## ✅ How to Complete This Module

### Option A: Self-Paced (Recommended)
1. Read theory files in order (follow numbering)
2. After each part (S3/IAM/VPC), do exercises
3. Reference cheatsheet while practicing
4. Complete all 14 exercises
5. Move to Module 2 when comfortable

**Estimated time:** 15-20 hours

### Option B: Instructor-Led (Classroom)
1. Instructor lectures theory file (45-75 min per topic)
2. Students follow along with code examples
3. In-class exercises (30 min labs)
4. Homework: additional exercises

**Estimated time:** 15 hours in class + 5 hours homework

### Option C: Accelerated (Skip theory, jump to practice)
1. Skim theory file introductions only
2. Reference cheatsheet
3. Complete all exercises
4. Look up details as needed

**Estimated time:** 8-10 hours

---

## 📋 Completion Checklist

- [ ] Read all S3 theory files (01-04)
- [ ] Complete S3 exercises (5 exercises)
- [ ] Read all IAM theory files (01-05)
- [ ] Complete IAM exercises (5 exercises)
- [ ] Read all VPC theory files (01-04)
- [ ] Complete VPC exercises (4 exercises)
- [ ] Pass module assessment (quiz)
- [ ] Ready for Module 2

---

## 🎓 Assessment

**Module 1 Assessment:** After completing all exercises, test your knowledge:

- [ ] Explain why S3 storage classes matter (cost vs latency)
- [ ] Write IAM policy from verbal requirement
- [ ] Design VPC architecture for 3-tier pipeline
- [ ] Audit existing S3 bucket for security issues
- [ ] Optimize S3 costs for 365-day data retention

---

## 🚀 What Comes Next?

After mastering AWS Foundation, you can proceed to:

**Module 2: AWS Lambda** → Automate data workflows with serverless functions  
**Module 3: Glue Data Catalog** → Manage metadata & schema evolution  
**Module 4: Glue ETL** → Build distributed data transformations  

---

## 🔗 Quick Links

- [Module 1 Exercises](../exercises/module-1-aws-foundation-exercises.md)
- [Sample Data & Schemas](../data/README.md)
- [AWS S3 Cheatsheet](../cheatsheets/aws-s3-cheatsheet.md)
- [AWS IAM Cheatsheet](../cheatsheets/aws-iam-cheatsheet.md)
- [AWS VPC Cheatsheet](../cheatsheets/aws-vpc-cheatsheet.md)
- [Back to Roadmap](../README.md)

---

## 💡 Pro Tips

1. **Take notes:** Module is dense. Hand-write key concepts.
2. **Do exercises immediately:** Don't finish theory then do exercises days later.
3. **Experiment:** Change policy conditions, see what breaks.
4. **Reference cheatsheet:** Don't memorize AWS CLI syntax.
5. **AWS Security Best Practices:** Read official [AWS Whitepapers](https://aws.amazon.com/whitepapers/) after module.

---

**Ready? Start with [01-why-s3-exists.md](./01-s3/01-why-s3-exists.md) →**

