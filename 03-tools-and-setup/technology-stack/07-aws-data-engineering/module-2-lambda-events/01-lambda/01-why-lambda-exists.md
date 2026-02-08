# 01: Why Lambda Exists (The Serverless Revolution)

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐☆ Beginner-Intermediate  
> **Key Takeaway:** Lambda solves the "idle resource" problem—pay only for compute you actually use, not for 24/7 infrastructure sitting idle.

---

## 🔥 The Problem: Wasting Money on Idle Resources

### Scenario: Data Engineer at E-Commerce Company

Anda punya **data validation job** yang berjalan setiap kali ada file uploaded ke S3:

**Requirements:**
- Process CSV files (customer orders, product catalog)
- Run validation: check schema, remove duplicates, standardize dates
- Average execution time: **5 seconds per file**
- Frequency: **100 files/day** (mostly during business hours 9 AM - 5 PM)

**Option 1: Traditional EC2**

```
EC2 t3.small (2 vCPU, 2 GB RAM)
├─ Runs 24/7 (always ready for next file)
├─ Actual usage: 100 files × 5 sec = 500 seconds/day = 8.3 minutes/day
├─ Idle time: 23 hours 51 minutes/day (99.4% idle)
└─ Cost: $15.18/month ($0.0208/hour × 730 hours)
```

**Waste:** Anda bayar untuk 730 hours/month, tapi cuma pakai **8.3 minutes/day × 30 = 4.2 hours/month**. That's **99.4% wasted budget**.

---

**Option 2: AWS Lambda (Serverless)**

```
Lambda function
├─ Runs ONLY when triggered (file upload event)
├─ Auto-scales: 1 file = 1 execution, 100 simultaneous files = 100 executions
├─ Memory: 512 MB, Duration: 5 sec/file
└─ Cost breakdown:
    ├─ Requests: 100 files/day × 30 days = 3,000 requests/month (FREE, under 1M limit)
    ├─ Compute: 3,000 × (512 MB / 1024) × 5 sec = 7,500 GB-seconds
    │   └─ 7,500 × $0.0000166667 = $0.125/month
    └─ Total: $0.13/month
```

**Savings:** $15.18 - $0.13 = **$15.05/month** (99.1% cheaper)

---

### The "Idle Server" Analogy

**Tradisional (EC2):**  
seperti sewa **mobil + driver 24/7** untuk commute 2 jam/hari.  
Total cost bulan ini? **$3,000** (driver standby 22 jam/hari).

**Serverless (Lambda):**  
seperti pakai **Uber/Grab** cuma waktu butuh.  
Total cost bulan ini? **$100** (bayar per trip, no idle time).

---

## ✅ The Solution: AWS Lambda

### What is Lambda?

> **AWS Lambda** adalah **serverless compute service** yang menjalankan kode Anda tanpa provisioning atau managing servers.

**Key Characteristics:**

1. **Event-Driven:** Lambda dijalankan oleh events (S3 upload, API call, schedule)
2. **Fully Managed:** AWS handles infrastructure (OS patches, scaling, high availability)
3. **Pay-Per-Use:** Charged per request & compute time (not uptime)
4. **Auto-Scaling:** Handles 1 request or 10,000 requests automatically
5. **Stateless:** Each execution independent (no persistent state between invocations)

---

### Lambda Fundamentals

#### 1. **Function**
Your code (Python, Node.js, Java, Go, .NET, Ruby, custom runtime).

Example (Python):
```python
def lambda_handler(event, context):
    """
    event: Input data (S3 event, API Gateway payload, manual invocation)
    context: Runtime information (request ID, memory limit, remaining time)
    """
    print(f"Processing event: {event}")
    
    # Your business logic here
    result = {
        'statusCode': 200,
        'body': 'File processed successfully'
    }
    
    return result
```

**Key Points:**
- **Handler:** Entry point (function name AWS calls)
- **Event:** Input payload (S3 notification, EventBridge schedule, etc.)
- **Context:** Metadata about execution (request ID, memory, time left)

---

#### 2. **Trigger (Event Source)**

What invokes your Lambda?

| Trigger Type | Example | Use Case |
|--------------|---------|----------|
| **S3** | File uploaded to `s3://data-lake/bronze/` | Process new data files |
| **EventBridge** | Cron schedule `0 2 * * ? *` (2 AM daily) | Daily ETL job |
| **API Gateway** | HTTP POST to `/validate` | Real-time API validation |
| **SQS** | Message added to queue | Async data processing |
| **DynamoDB Streams** | Row inserted/updated | Real-time data sync |

**For Data Engineering:** 80% of use cases = **S3 + EventBridge**.

---

#### 3. **Execution Role (IAM)**

Lambda needs permissions to access AWS services (recap from Module 1!).

**Example:** Lambda reads from S3, writes to CloudWatch Logs

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::data-lake/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

**Trust Policy** (who can assume this role):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

→ Ini adalah **Role-based access** dari Module 1 IAM section!

---

#### 4. **Configuration**

**Memory:** 128 MB - 10,240 MB (10 GB)  
- More memory = more CPU (proportional)
- Example: 512 MB = ~0.5 vCPU, 1024 MB = ~1 vCPU

**Timeout:** 1 second - 15 minutes (900 seconds)  
- Data validation: 30 sec sufficient
- Large file processing: 5-10 min
- If execution exceeds timeout → Lambda terminates

**Environment Variables:**  
Pass config without hardcoding in code
```python
import os
BUCKET_NAME = os.environ['BUCKET_NAME']  # Set in Lambda config
```

---

## 💰 Lambda Pricing Model

### How You're Charged

**Component 1: Requests**
- First **1 million requests/month = FREE**
- After that: **$0.20 per 1 million requests**

**Component 2: Compute Time (GB-seconds)**
- Formula: `(Memory in GB) × (Duration in seconds)`
- First **400,000 GB-seconds/month = FREE**
- After that: **$0.0000166667 per GB-second**

---

### Real Cost Examples

#### Example 1: CSV Validation (Small Job)

**Workload:**
- 10,000 file uploads/month
- Memory: 512 MB = 0.5 GB
- Duration: 2 seconds per file

**Cost Calculation:**
```
Requests: 10,000 (FREE, < 1M)

Compute:
GB-seconds = 10,000 × 0.5 GB × 2 sec = 10,000 GB-sec
Billable   = 10,000 - 400,000 (free tier) = 0 (still within free tier!)
Cost       = $0.00

Total: $0.00/month
```

---

#### Example 2: Daily ETL Job (Medium Job)

**Workload:**
- 30 executions/month (daily)
- Memory: 3,008 MB = 3 GB (higher for Pandas operations)
- Duration: 10 minutes = 600 seconds per execution

**Cost Calculation:**
```
Requests: 30 (FREE)

Compute:
GB-seconds = 30 × 3 GB × 600 sec = 54,000 GB-sec
Billable   = 54,000 - 400,000 (free tier) = 0 (still free!)
Cost       = $0.00

Total: $0.00/month
```

---

#### Example 3: High-Volume Processing (Exceeds Free Tier)

**Workload:**
- 2 million file uploads/month
- Memory: 1,024 MB = 1 GB
- Duration: 3 seconds per file

**Cost Calculation:**
```
Requests:
Free tier  = 1,000,000
Billable   = 2,000,000 - 1,000,000 = 1,000,000
Cost       = 1,000,000 × ($0.20 / 1,000,000) = $0.20

Compute:
GB-seconds = 2,000,000 × 1 GB × 3 sec = 6,000,000 GB-sec
Free tier  = 400,000
Billable   = 6,000,000 - 400,000 = 5,600,000
Cost       = 5,600,000 × $0.0000166667 = $93.33

Total: $0.20 + $93.33 = $93.53/month
```

**Compare to EC2:**
- c5.xlarge (4 vCPU, 8 GB) 24/7 = **$122.63/month**
- Lambda savings: $122.63 - $93.53 = **$29.10/month** (24% cheaper)

**Key Insight:** Even at high volume, Lambda competitive if workload is **bursty** (not constant).

---

## ⚖️ When to Use Lambda vs EC2

### Use Lambda When:

✅ **Infrequent execution** (hourly, daily, or event-driven)  
✅ **Short runtime** (<15 min, ideally <5 min)  
✅ **Variable load** (10 files today, 1000 tomorrow)  
✅ **Event-driven** (S3 upload, API call, schedule)  
✅ **No state** (stateless processing, no persistent connections)

**Example Use Cases:**
- File validation (CSV → check schema → write result)
- Image resizing (upload photo → resize → save thumbnails)
- Data enrichment (read JSON → call API → save enriched data)
- Scheduled reports (daily 2 AM → query DB → send email)

---

### Use EC2/ECS When:

❌ **Long-running** (>15 min execution, hours/days)  
❌ **Constant load** (24/7 processing, always busy)  
❌ **Stateful** (WebSockets, long-lived DB connections)  
❌ **Custom dependencies** (OS-level packages hard to bundle in Lambda)  
❌ **High memory/CPU** (>10 GB RAM, >6 vCPU → Glue/EMR better)

**Example Use Cases:**
- Spark job processing 100 GB data (use EMR)
- Real-time stream processing (Kinesis + Flink on EC2)
- Web application serving traffic 24/7 (EC2 + ALB)
- Database server (RDS, not Lambda)

---

## 🏗️ Real Data Engineering Scenario

### Bronze → Silver ETL Pipeline

**Requirements:**
1. **Bronze Layer:** Raw CSV files uploaded to `s3://data-lake/bronze/orders/`
2. **Validation:** Check schema, remove nulls, deduplicate
3. **Silver Layer:** Write cleaned Parquet to `s3://data-lake/silver/orders/`

**Architecture:**

```
S3 Upload Event
    ↓
┌──────────────────────┐
│   Lambda Function    │
│   (Validator)        │
│                      │
│  1. Read CSV from S3 │
│  2. Validate schema  │
│  3. Remove nulls     │
│  4. Write Parquet    │
└──────────────────────┘
    ↓
Silver Layer (Cleaned Data)
```

**Code (Python):**
```python
import boto3
import pandas as pd
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    print(f"Processing file: s3://{bucket}/{key}")
    
    try:
        # Read CSV from S3
        obj = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(obj['Body'])
        
        # Validate: Check required columns
        required_cols = ['order_id', 'customer_id', 'amount']
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Clean: Remove nulls in critical columns
        df = df.dropna(subset=['order_id', 'customer_id'])
        
        # Deduplicate
        df = df.drop_duplicates(subset=['order_id'])
        
        # Write to Silver layer (Parquet)
        silver_key = key.replace('bronze/', 'silver/').replace('.csv', '.parquet')
        df.to_parquet(f's3://{bucket}/{silver_key}', index=False)
        
        print(f"✅ Success: Processed {len(df)} rows → {silver_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Processed {len(df)} rows')
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise  # Re-raise to trigger retry/DLQ
```

**Execution:**
- File uploaded: `s3://data-lake/bronze/orders/2024-01-15.csv` (10 MB, 50K rows)
- Lambda triggered automatically
- Processing time: 8 seconds
- Output: `s3://data-lake/silver/orders/2024-01-15.parquet` (3 MB)

**Cost:**
- 1 execution × 1024 MB × 8 sec = 8 GB-sec
- Cost: $0.0001 (basically free)

---

## 🚫 When Lambda is NOT the Answer

### Anti-Pattern 1: Processing Large Datasets

**Bad:**
```python
# Lambda trying to process 50 GB Parquet file
df = pd.read_parquet('s3://data-lake/raw/huge_file.parquet')  # ❌ Out of memory!
```

**Why it fails:**
- Max memory: 10 GB (Lambda limit)
- Large datasets don't fit in memory
- Even if they fit, processing >15 min → timeout

**Better Alternative:** AWS Glue (PySpark, distributed processing)

---

### Anti-Pattern 2: Long-Running Jobs

**Bad:**
```python
# Lambda running ML training
for epoch in range(100):  # Takes 3 hours
    model.train()  # ❌ Timeout after 15 min!
```

**Better Alternative:** SageMaker, EC2 with GPU

---

### Anti-Pattern 3: Stateful Processing

**Bad:**
```python
# Lambda maintaining WebSocket connection
connection = websocket.connect()  # ❌ Connection lost between invocations
```

**Better Alternative:** ECS/Fargate (long-lived containers)

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
You have a job that runs **every 5 minutes, 24/7**, processing streaming data (always busy).  
**Should you use Lambda?**

<details>
<summary>Answer</summary>

**No.** Lambda is charged per invocation + compute time. Running every 5 min = 8,640 invocations/month. If each execution is long (>1 min), you're essentially paying for **continuous compute**—same as EC2, but with Lambda overhead.

**Better:** ECS/Fargate or EC2 with auto-scaling.

**Rule:** If uptime >20%, EC2 likely cheaper.
</details>

---

**Question 2:**  
You process **100 files/day**, each takes **10 seconds** to validate. Files arrive randomly (8 AM - 6 PM).  
**Lambda or EC2?**

<details>
<summary>Answer</summary>

**Lambda.** 

Calculation:
- 100 files × 10 sec = 1,000 sec/day = 16.7 min/day
- Uptime: 16.7 min / 1440 min = **1.2%**
- Lambda cost: ~$0.01/month (within free tier)
- EC2 t3.small cost: ~$15/month

**Lambda wins:** 99%+ savings.
</details>

---

**Question 3:**  
Your Lambda processes a 5 GB CSV file. Execution fails with "Out of memory" error. What's wrong?

<details>
<summary>Answer</summary>

**Problem:** Lambda max memory = 10 GB. A 5 GB CSV, when loaded into pandas DataFrame, can expand to 10-15 GB in memory (due to indexing, data types).

**Solutions:**
1. **Increase Lambda memory to 10 GB** (might still fail)
2. **Use chunked processing:** `pd.read_csv(chunksize=10000)`
3. **Better:** Use AWS Glue (distributed, handles TB-scale data)

**Lambda is NOT for big data processing.** Use for small-to-medium files (<100 MB raw data).
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Problem** | EC2 24/7 = 99% idle time, 100% cost |
| **Solution** | Lambda = pay per use, auto-scale, zero idle cost |
| **Pricing** | Requests + compute time (GB-seconds) |
| **Sweet Spot** | Infrequent (<20% uptime), event-driven, <15 min runtime |
| **Avoid** | Large data (>1 GB in memory), long jobs (>15 min), stateful workloads |
| **Data Engineering** | File validation, lightweight ETL, event triggers |

---

## ⏭️ Next Steps

You now understand **WHY** Lambda exists and when to use it.

**Next:** [02-lambda-data-processing.md](./02-lambda-data-processing.md) → Learn HOW to build production-ready Lambda functions (execution model, layers, idempotency).

---

**Pro Tip:** Before building Lambda, ask: "Is this job <15 min? Infrequent? Event-driven?" If yes → Lambda. If no → Glue/EC2.
