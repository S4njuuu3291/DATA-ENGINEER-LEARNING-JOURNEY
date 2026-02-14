# AWS Data Engineering Learning Path

**Role:** Senior Data Architect  
**Objective:** Master AWS Data Engineering ecosystem secara modular, mendalam, dan berorientasi standar industri (bukan tutorial dasar)  
**Language:** Campuran Indonesian + English (technical terms)

---

## 🏛️ Industrial AWS Data Engineering Framework

### Aturan Main (Rules of Engagement)

1. **Modular:** Selesaikan satu modul sebelum lanjut ke modul berikutnya
2. **Enterprise Standard:** Fokus pada _Least Privilege_, _Infrastructure as Code (IaC)_, _Cost-Optimization_, dan _Security_
3. **Hands-on:** Setiap modul include konsep _Under-the-hood_, _Real-world scenarios_, dan _Micro-assignment_

---

## 🗺️ Learning Modules Roadmap

### **Module 1: AWS Foundation (S3, IAM & Networking)**
- **Duration:** 10 hours
- **Level:** ⭐⭐☆ Beginner-Intermediate
- **Status:** ✅ Completed
- **Requires:** AWS account, basic networking knowledge
- **Topics:**
  - **S3:** Storage Classes, Versioning, Object Locking, Medallion Architecture
  - **IAM:** Policy JSON, Role vs User, Least Privilege, Service-Linked Roles
  - **VPC:** S3 Endpoints & Private Networking

[📖 Start Module 1](./module-1-aws-foundation/README.md)

---

### **Module 2: Serverless Automation (AWS Lambda & EventBridge)**
- **Duration:** 8 hours
- **Level:** ⭐⭐⭐ Intermediate
- **Status:** ✅ Completed
- **Requires:** Module 1 complete
- **Topics:**
  - Serverless architecture, S3 triggers, EventBridge schedules
  - Lambda Layers, retries, DLQ, CloudWatch monitoring
  - Optimization (memory sizing, cold starts, concurrency)

[📖 Start Module 2](./module-2-lambda-events/README.md)

---

### **Module 3: Cataloging (Glue Data Catalog & Crawlers)**
- **Duration:** 4 hours
- **Level:** ⭐⭐⭐ Intermediate
- **Status:** ✅ Completed
- **Requires:** Module 1-2 complete
- **Topics:**
  - Glue Data Catalog fundamentals & metadata objects
  - Crawlers, classifiers, recrawl strategy
  - Event-driven automation for catalog updates

[📖 Start Module 3](./module-3-glue-catalog/README.md)

---

### **Module 4: ETL Engine (AWS Glue Jobs / Spark)**
- **Duration:** 8 hours
- **Level:** ⭐⭐⭐ Intermediate-Advanced
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1-3 complete
- **Topics:**
  - Dynamic Frames vs DataFrames
  - Job Bookmarks (Incremental processing)
  - Worker Types & distributed execution

---

### **Module 5: Serverless Analytics (Amazon Athena)**
- **Duration:** 5 hours
- **Level:** ⭐⭐⭐ Intermediate
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1, 3-4 complete
- **Topics:**
  - SQL query optimization
  - Partition Projection & Parquet/ORC
  - Workgroups & Query Result reuse

---

### **Module 6: Data Warehousing (Amazon Redshift Serverless)**
- **Duration:** 7 hours
- **Level:** ⭐⭐⭐⭐ Advanced
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1, 5 complete
- **Topics:**
  - RA3 Architecture & COPY command
  - DistKeys & SortKeys
  - Cost optimization strategies

---

### **Module 7: Modeling & Transformation (dbt on AWS)**
- **Duration:** 6 hours
- **Level:** ⭐⭐⭐⭐ Advanced
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1, 4-5 complete
- **Topics:**
  - dbt-athena & dbt-redshift
  - Snapshots, Tests, auto-doc

---

### **Module 8: Orchestration (Step Functions & MWAA)**
- **Duration:** 7 hours
- **Level:** ⭐⭐⭐⭐ Advanced
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1-7 complete
- **Topics:**
  - State Machines & Error Handling
  - Managed Airflow (MWAA)
  - Retry & escalation patterns

---

### **Module 9: Advanced (EventBridge, Streaming & Lake Formation)**
- **Duration:** 8 hours
- **Level:** ⭐⭐⭐⭐ Advanced (Enterprise)
- **Status:** 🔵 Coming Soon
- **Requires:** Module 1-8 complete
- **Topics:**
  - Kinesis Data Streams & Firehose
  - Lake Formation (Column-level security)
  - Event-driven architecture

---

## 📚 Learning Resources

### Quick References
- [AWS S3 Cheatsheet](./cheatsheets/aws-s3-cheatsheet.md)
- [AWS IAM Cheatsheet](./cheatsheets/aws-iam-cheatsheet.md)
- [AWS VPC Cheatsheet](./cheatsheets/aws-vpc-cheatsheet.md)
- [AWS Lambda Cheatsheet](./cheatsheets/aws-lambda-cheatsheet.md)
- [AWS EventBridge Cheatsheet](./cheatsheets/aws-eventbridge-cheatsheet.md)

### Sample Datasets
- [Raw Ecommerce Data](./data/raw/ecommerce/)
- [API Logs Archive](./data/raw/api-logs/)

---

## 🎯 How to Use This Path

### For Self-Learners
1. Read module README (overview + time estimate)
2. Work through theory files in order (follow the numbering)
3. Reference cheatsheets while practicing
4. Complete exercises at end of module
5. Move to next module

### For Instructors
- Each module is self-contained and can be taught independently
- Theory files designed for 45-75 min lectures
- Exercises range 15-45 min per problem
- Cheatsheets provided for reference during labs

### Prerequisites
- Basic understanding of cloud computing
- Familiarity with command-line interface
- Active AWS account (free tier eligible for modules 1-5)
- Python 3.8+ (for modules 2+)

---

## 💡 Key Principles

✅ **Real-world first:** Every concept tied to actual enterprise use cases  
✅ **Security by default:** Least privilege access in every example  
✅ **Cost awareness:** Trade-offs highlighted (performance vs cost vs complexity)  
✅ **Hands-on:** Theory → Practice → Reference flow  
✅ **Modular:** Start anywhere, progress independently  

---

## 📈 Progress Tracking

Use this checklist to track your progress:

- [ ] Module 1: AWS Foundation (S3, IAM, VPC)
- [ ] Module 2: AWS Lambda
- [ ] Module 3: Glue Data Catalog
- [ ] Module 4: Glue ETL Jobs
- [ ] Module 5: Amazon Athena
- [ ] Module 6: Amazon Redshift
- [ ] Module 7: dbt on AWS
- [ ] Module 8: Step Functions & MWAA
- [ ] Module 9: Advanced (Streaming, Lake Formation)

---

## 🔗 Additional Resources

### AWS Official Documentation
- [S3 User Guide](https://docs.aws.amazon.com/s3/)
- [IAM Documentation](https://docs.aws.amazon.com/iam/)
- [VPC User Guide](https://docs.aws.amazon.com/vpc/)

### Community
- AWS Forums: data-engineering tag
- r/aws subreddit
- LinkedIn AWS Communities

---

**Last Updated:** February 8, 2026  
**Maintainer:** Data Engineering Curriculum  
**Version:** 1.0-beta

