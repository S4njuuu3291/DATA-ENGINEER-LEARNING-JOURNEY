# 04: Lambda Optimization (Cost & Performance)

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate-Advanced  
> **Key Takeaway:** Right-sizing Lambda memory can reduce costs by 50%+ while improving performance. Understand cold starts, concurrency limits, and when to migrate to Glue/EMR.

---

## 💰 Cost Optimization

### The Memory-Cost-Performance Triangle

**Key Insight:** Memory allocation affects **three things**:

1. **CPU power** (more memory = more vCPU, proportional)
2. **Cost per second** (more memory = higher cost)
3. **Execution duration** (more CPU = faster execution = less time)

**The math:** Cost = Memory × Duration × Price  
- Doubling memory = 2x cost per second
- But might reduce duration by 2x → **same total cost, but faster!**

---

### Real Cost Experiment

**Scenario:** Process 20 MB CSV file (pandas)

| Memory | vCPU | Duration | GB-sec | Cost | Notes |
|--------|------|----------|--------|------|-------|
| 256 MB | 0.17 | 45 sec | 11.25 | $0.0002 | ❌ Slow, OOM risk |
| 512 MB | 0.33 | 22 sec | 11.0 | $0.00018 | Similar cost |
| 1024 MB | 0.6 | 12 sec | 12.0 | $0.0002 | **✅ Sweet spot** |
| 1792 MB | **1.0** | 8 sec | 14.0 | $0.00023 | 1 full vCPU |
| 3008 MB | 1.7 | 6 sec | 18.0 | $0.0003 | 50% more cost |
| 10240 MB | 6.0 | 5 sec | 50.0 | $0.00083 | ❌ 4x cost for 20% gain |

**Winner:** **1024 MB (1 GB)** → Good balance of cost & speed for pandas operations.

**Key Threshold:** 1792 MB = **1 full vCPU** (AWS guarantees at least 1 vCPU at this tier).  
- Below 1792 MB → fractional vCPU (shared with other Lambdas)
- Above 1792 MB → dedicated vCPU + extras

---

### How to Find Optimal Memory

**Method: Binary Search**

```bash
# Test different memory configs
for memory in 512 1024 1536 2048 3008; do
  aws lambda update-function-configuration \
    --function-name csv-processor \
    --memory-size $memory
  
  # Invoke and measure duration
  aws lambda invoke \
    --function-name csv-processor \
    --payload file://test_event.json \
    response.json
  
  # Check CloudWatch Logs for duration
  aws logs filter-log-events \
    --log-group-name /aws/lambda/csv-processor \
    --filter-pattern "REPORT RequestId" \
    --limit 1
done
```

**Analysis:**
```
512 MB:  Duration: 15000 ms, Max Memory Used: 480 MB
1024 MB: Duration: 8000 ms, Max Memory Used: 650 MB  ← Sweet spot
1536 MB: Duration: 6000 ms, Max Memory Used: 650 MB  ← Diminishing returns
2048 MB: Duration: 5500 ms, Max Memory Used: 650 MB  ← Waste (memory unused)
```

**Decision:** Use **1024 MB**. Higher memory doesn't proportionally reduce duration (law of diminishing returns).

---

### AWS Lambda Power Tuning Tool

**Automated optimization:** [github.com/alexcasalboni/aws-lambda-power-tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning)

**What it does:**
1. Tests Lambda with memory: 128, 256, 512, 1024, 1536, 2048, 3008 MB
2. Invokes each config 10 times (statistical average)
3. Generates cost vs performance chart

**Output:**
```
Recommended: 1024 MB
- Cost: $0.0002 per invocation
- Duration: 8.2 sec (avg)
- Savings vs 512 MB: 45% faster, 5% cheaper
```

**Deploy tool:**
```bash
# SAM deployment (one-time setup)
sam deploy --guided --template-file template.yml
```

---

## ❄️ Cold Start Optimization

### Understanding Cold Starts

**Cold start = Time to initialize execution environment**

```
Timeline of cold start:
├─ 0-200ms: Download deployment package (code + deps)
├─ 200-500ms: Initialize runtime (Python 3.11 interpreter)
├─ 500-2000ms: Load imports (import pandas, import boto3)
├─ 2000-2500ms: Initialize connections (DB, S3 client)
└─ 2500ms+: Run handler function
```

**Impact:**
- First invocation: 2.5 sec overhead
- Subsequent invocations (warm): 0 sec overhead (reuse container)

**When it hurts:**
- **Real-time APIs** (user waiting for response) → 2.5 sec delay unacceptable
- **ETL jobs** (batch processing) → 2.5 sec / 1000 sec execution = 0.25% overhead (acceptable)

---

### Mitigation Strategies

#### 1. **Reduce Package Size**

**Problem:** 200 MB deployment package takes 500ms to download.

**Solution:** Use Lambda Layers for heavy dependencies.

```
Before (no layers):
├─ lambda_function.py (10 KB)
└─ pandas/ (180 MB)
    Deployment: 180 MB (download: 500ms)

After (with layer):
├─ lambda_function.py (10 KB)
└─ [Layer: pandas-layer (cached)]
    Deployment: 10 KB (download: 5ms)
```

**Savings:** 495ms cold start reduction!

---

#### 2. **Lazy Imports (Load Only When Needed)**

**Problem:** Importing pandas always, even when not needed (JSON processing).

```python
# ❌ Bad: Always import pandas (cold start: +1.5 sec)
import pandas as pd

def lambda_handler(event, context):
    if event['format'] == 'csv':
        df = pd.read_csv(event['file'])
    else:
        return process_json(event['file'])  # Pandas not needed!
```

```python
# ✅ Good: Lazy import (cold start: +0 sec for JSON path)
def lambda_handler(event, context):
    if event['format'] == 'csv':
        import pandas as pd  # Import only if CSV
        df = pd.read_csv(event['file'])
    else:
        return process_json(event['file'])
```

**Trade-off:** If CSV is 99% of requests, upfront import better (pay 1.5 sec once, fast thereafter).

---

#### 3. **Provisioned Concurrency (Keep Warm)**

**What it is:** AWS keeps N containers **always warm** (pre-initialized, ready for requests).

**Enable:**
```bash
aws lambda put-provisioned-concurrency-config \
  --function-name csv-processor \
  --provisioned-concurrent-executions 2
```

**Effect:**
- 2 containers always running (no cold start for first 2 concurrent requests)
- Cold start eliminated!

**Cost:**
- **$0.000004167 per GB-second** (10x more expensive than on-demand)
- Example: 1024 MB function, 2 instances, 24/7
  - GB-hours = 1 GB × 2 instances × 730 hours/month = 1,460 GB-hours
  - Cost = 1,460 × 3600 sec × $0.000004167 = **$21.91/month** (vs $0.20 on-demand!)

**When to use:**
- ✅ **Latency-critical APIs** (user-facing, <100ms response required)
- ❌ **Batch ETL** (cold start 0.25% overhead, not worth $21.91/month)

**Rule:** If cold start >10% of total execution time → consider Provisioned Concurrency.

---

#### 4. **Warmup Cron (Poor Man's Provisioned Concurrency)**

**Pattern:** EventBridge schedule invokes Lambda every 5 min → keeps container warm.

```bash
# Create EventBridge rule (every 5 min)
aws events put-rule \
  --name lambda-warmup \
  --schedule-expression "rate(5 minutes)"

# Add Lambda as target
aws events put-targets \
  --rule lambda-warmup \
  --targets Id=1,Arn=arn:aws:lambda:us-east-1:123:function:csv-processor
```

**Lambda code (detect warmup event):**
```python
def lambda_handler(event, context):
    # Detect warmup ping (no actual work)
    if event.get('source') == 'aws.events' and event.get('detail-type') == 'Scheduled Event':
        print("Warmup ping, keeping container alive")
        return {'status': 'warm'}
    
    # Real work
    return process_csv(event)
```

**Cost:**
- 12 invocations/hour × 730 hours = 8,760 invocations/month
- Duration: 100ms per warmup
- Cost: 8,760 × 0.1 sec × (1024 MB / 1024) = 876 GB-sec = **$0.015/month**

**Comparison:**
- Warmup cron: $0.015/month
- Provisioned Concurrency: $21.91/month
- Savings: **99.9% cheaper!**

**Trade-off:** Warmup cron keeps 1 container warm (not guaranteed, AWS might recycle). Provisioned Concurrency keeps N containers guaranteed warm.

---

## 🚀 Concurrency Limits

### What is Concurrency?

**Concurrency = Number of Lambdas running simultaneously**

**Example:**
- 100 files uploaded to S3 in 1 second
- Each Lambda takes 5 seconds to process
- Concurrency needed: **100** (all files processed in parallel)

**AWS Limits:**
- **Account-level default:** 1,000 concurrent executions (all Lambdas in region)
- **Per-function reserved concurrency:** Optional (guarantee capacity for critical functions)

---

### Throttling (Hitting Concurrency Limit)

**Scenario:** 1,500 files uploaded simultaneously, account limit = 1,000.

```
Result:
├─ First 1,000 files: Processed immediately
├─ Remaining 500 files: Throttled (rejected)
└─ CloudWatch Metric: Throttles = 500
```

**What happens to throttled events?**
- **Async invocations (S3, EventBridge):** AWS retries up to 6 hours
- **Sync invocations (API Gateway):** Error returned to caller (429 Too Many Requests)

---

### Reserve Concurrency for Critical Functions

**Problem:** `csv-processor` Lambda shares 1,000 concurrency limit with 50 other functions in account. During spike, other functions consume all capacity → `csv-processor` throttled.

**Solution:** Reserve 100 concurrency for `csv-processor`.

```bash
aws lambda put-function-concurrency \
  --function-name csv-processor \
  --reserved-concurrent-executions 100
```

**Effect:**
- `csv-processor` **guaranteed** 100 concurrent executions
- Other functions share remaining 900 concurrency
- `csv-processor` never throttled (up to 100 concurrent)

**Cost:** No additional charge (same per-invocation pricing).

---

### Monitor Concurrency

**CloudWatch Metric:** `ConcurrentExecutions`

**Query:**
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=csv-processor \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Maximum
```

**Alert if concurrency >80% of limit:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-high-concurrency \
  --metric-name ConcurrentExecutions \
  --threshold 800 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --period 60
```

---

## 🔌 VPC Lambda Best Practices

### Problem: VPC Lambda Slow Cold Starts

**Scenario:** Lambda in VPC needs to access RDS database.

**Old architecture (pre-2019):**
```
Lambda cold start in VPC:
├─ Create Elastic Network Interface (ENI) → 10-30 seconds!
├─ Attach to Lambda
└─ Connect to RDS
   Total cold start: 30+ seconds (unacceptable!)
```

**New architecture (post-2019 Hyperplane ENI):**
```
Lambda cold start in VPC:
├─ Reuse pre-warmed ENI pool → 0 seconds
├─ Connect to RDS → 100ms
└─ Total cold start: same as non-VPC Lambda!
```

**Good news:** VPC cold start penalty eliminated (AWS fixed it in 2019).

---

### VPC Lambda + S3 Access

**Problem:** Lambda in private subnet accessing S3 via NAT Gateway = expensive.

```
Bad (NAT Gateway):
Lambda → NAT ($0.045/GB) → Internet → S3
Cost: 100 GB/month = $4.50
```

**Solution:** Use S3 VPC Endpoint (Module 1 VPC knowledge!).

```
Good (VPC Endpoint):
Lambda → VPC Endpoint (free) → S3
Cost: $0.00
```

**Configuration:**
```bash
# Create S3 VPC endpoint (gateway type)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-456
```

**Lambda security group:** Allow outbound HTTPS (443) to S3 endpoint.

---

## 🎯 When to Switch from Lambda to Glue/EMR

### Lambda Limitations

| Limit | Value | Impact |
|-------|-------|--------|
| **Max memory** | 10 GB | Can't process datasets >5 GB in memory |
| **Max timeout** | 15 minutes | Can't run long jobs (Spark takes 2 hours) |
| **Ephemeral storage** | 512 MB - 10 GB | Can't download multi-GB files to /tmp |
| **Concurrency** | 1,000 (account) | Can't process 10,000 files simultaneously |

---

### Decision Matrix: Lambda vs Glue vs EMR

| Use Case | Lambda | Glue | EMR |
|----------|--------|------|-----|
| **File size** | <100 MB | 100 MB - 100 GB | >100 GB |
| **Execution time** | <15 min | 15 min - 2 hours | >2 hours |
| **Concurrency** | 1-1000 files | 1-100 files | 1-10 large datasets |
| **Cost** | $0.20 per 1M requests | $0.44/DPU-hour | $0.096/hour (EC2) |
| **Use Case** | File validation, lightweight ETL, event triggers | Medium ETL, Spark jobs, Catalog updates | Heavy ML, PB-scale data, long-running clusters |

**Example transitions:**

1. **CSV validation (10 MB files, <1 min)** → **Lambda** ($0.0002/file)
2. **Parquet aggregation (500 MB files, 10 min)** → **Glue** ($0.073/file)
3. **Join 2 TB datasets (2 hours)** → **EMR** ($19.20/job)

---

### When to Migrate

**Scenario 1: Lambda timing out (>15 min)**

```python
# Lambda code (timing out after 15 min)
def lambda_handler(event, context):
    df = pd.read_csv('s3://bucket/huge_file.csv')  # 5 GB
    df_agg = df.groupby('category').sum()  # Takes 20 min!
    # ❌ Timeout after 15 min
```

**Solution:** Migrate to Glue (distributed Spark processing).

```python
# Glue PySpark code (runs on cluster, no timeout)
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
df = spark.read.csv('s3://bucket/huge_file.csv')
df_agg = df.groupBy('category').sum()  # Distributed, finishes in 5 min
df_agg.write.parquet('s3://bucket/output/')
```

---

**Scenario 2: Lambda OOM (Out of Memory)**

```python
# Lambda code (10 GB memory, still OOM)
def lambda_handler(event, context):
    df = pd.read_parquet('s3://bucket/10GB_file.parquet')  # ❌ Crash
```

**Solution:** Glue/EMR (100+ GB memory available).

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
Your Lambda uses 512 MB memory, duration 20 sec, cost $0.0002. You increase to 1024 MB, duration drops to 12 sec. New cost?

<details>
<summary>Answer</summary>

**Calculation:**

512 MB:
- GB-sec = 0.5 GB × 20 sec = 10 GB-sec
- Cost = 10 × $0.0000166667 = $0.000166

1024 MB:
- GB-sec = 1 GB × 12 sec = 12 GB-sec
- Cost = 12 × $0.0000166667 = $0.0002

**Answer:** $0.0002 (20% more expensive but 40% faster).

**Decision:** Depends on priority:
- If cost-sensitive → stay at 512 MB
- If speed-sensitive → use 1024 MB
</details>

---

**Question 2:**  
Your Lambda has 3-second cold start (import pandas). You get 1,000 invocations/day, mostly clustered (200 files uploaded at 9 AM). Is Provisioned Concurrency worth $22/month?

<details>
<summary>Answer</summary>

**NO.**

**Analysis:**
- Cold start: 3 sec
- Typical execution: 10 sec
- Overhead: 3 / 13 = 23% (tolerable for batch ETL)
- 1,000 invocations/day = cold start hits ~100 times (900 reuse warm containers)
- Wasted time: 100 × 3 sec = 300 sec/day = 9,000 sec/month

**Cost comparison:**
- Wasted compute (cold starts): 9,000 sec × 1 GB = 9,000 GB-sec = $0.15/month
- Provisioned Concurrency (eliminate cold starts): $22/month

**Verdict:** Not worth it. Save $21.85/month, accept 3-sec cold start.

**Alternative:** Use warmup cron ($0.015/month) if warm container is important.
</details>

---

**Question 3:**  
Your Lambda processes 100 GB CSV file. It times out after 15 min. What should you do?

<details>
<summary>Answer</summary>

**Lambda is not the right tool.**

**Issues:**
1. 100 GB doesn't fit in memory (max 10 GB)
2. Even if chunked, processing >15 min → timeout

**Solution:** Migrate to **AWS Glue**.

**Glue advantages:**
- Distributed processing (Spark, handles TB-scale data)
- No timeout limit (jobs can run hours)
- Auto-scaling (10 DPU → 100 DPU as needed)

**Cost:**
- Lambda (would fail): N/A
- Glue (20 DPU, 30 min): 20 × 0.5 hour × $0.44 = **$4.40/job**
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Memory Optimization** | More memory = more CPU = faster execution. Find sweet spot (1024 MB for pandas). |
| **Cold Start** | Reduce package size (Layers), lazy imports, warmup cron ($0.015/month vs Provisioned Concurrency $22/month). |
| **Concurrency** | Reserve capacity for critical functions, monitor for throttles. |
| **VPC Lambda** | Use VPC endpoints for S3 access (avoid NAT costs). |
| **Lambda Limits** | 10 GB memory, 15 min timeout → migrate to Glue/EMR for larger workloads. |

---

## ⏭️ Next Steps

You now understand **how to optimize Lambda** (cost, cold starts, concurrency).

**Next:** [EventBridge Basics](../02-eventbridge/01-eventbridge-basics.md) → Learn event-driven architecture (schedules, S3 triggers, event routing).

---

**Pro Tip:** Run AWS Lambda Power Tuning tool before production. It finds optimal memory config automatically (saves hours of manual testing).
