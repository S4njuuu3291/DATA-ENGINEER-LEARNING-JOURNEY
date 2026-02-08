# 03: Lambda Error Handling & Monitoring

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate-Advanced  
> **Key Takeaway:** Production Lambda must handle failures gracefully—retries, Dead Letter Queues, CloudWatch alarms, and structured logging are non-negotiable.

---

## ⚠️ The Problem: Silent Failures

### Scenario: CSV Validation Lambda

**Code:**
```python
def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Process file
    df = pd.read_csv(f's3://{bucket}/{key}')
    df_cleaned = df.dropna()
    df_cleaned.to_parquet(f's3://{bucket}/silver/{key}')
```

**What happens when:**

1. **S3 file doesn't exist?**  
   → `NoSuchKey` exception → Lambda crashes → ❌ No output

2. **CSV has bad schema?**  
   → pandas raises `ParserError` → Lambda crashes → ❌ No output

3. **Out of memory?**  
   → Process killed → ❌ No output

4. **Network timeout to S3?**  
   → `ReadTimeoutError` → Lambda crashes → ❌ No output

**Current behavior:** Lambda fails silently. File sits in `bronze/` forever, never makes it to `silver/`.

**What you don't know:**
- Which files failed?
- Why did they fail?
- How many failures per hour?
- When did problem start?

**Production requirement:** You must know about failures **immediately** and have mechanisms to recover.

---

## 🔄 Retry Behavior

### Async vs Sync Invocations

**Synchronous (API Gateway, manual invoke):**
- Caller waits for response
- If Lambda fails → error returned to caller
- **No automatic retries** (caller decides to retry)

**Asynchronous (S3, EventBridge, SNS):**
- AWS queues request, returns immediately
- If Lambda fails → AWS **automatically retries 2 times**
- Retry intervals: 1 minute, then 2 minutes
- After 3 total attempts (1 original + 2 retries) → send to Dead Letter Queue (if configured)

**For data engineering:** 95% of triggers are **async** (S3 events, EventBridge schedules).

---

### Retry Example

**Scenario:** Lambda processes CSV, but file is corrupted.

```
Timeline:
00:00:00 - File uploaded to S3
00:00:01 - Lambda invoked (Attempt 1)
          ├─ Reads CSV
          ├─ pandas raises ParserError (bad CSV)
          └─ Lambda crashes (uncaught exception)

00:01:01 - AWS retries (Attempt 2, after 1 min)
          ├─ Same error (ParserError)
          └─ Lambda crashes again

00:03:01 - AWS retries (Attempt 3, after 2 min)
          ├─ Same error
          └─ Lambda crashes (final retry)

00:03:02 - Event sent to Dead Letter Queue (SQS/SNS)
          ├─ Original S3 event payload saved
          └─ Engineer alerted
```

**Key Insight:** Automatic retries are good for **transient errors** (network glitches), bad for **permanent errors** (bad data).

---

## 💀 Dead Letter Queue (DLQ)

### What is a DLQ?

**Dead Letter Queue = SQS queue or SNS topic that receives failed events after all retries exhausted.**

**Why you need it:**
- Know which files failed to process
- Investigate failure reasons
- Replay failed events after fixing code
- Alert engineers when failures spike

---

### Set Up DLQ

**Step 1: Create SQS queue**

```bash
aws sqs create-queue --queue-name lambda-failures-dlq

# Returns: QueueUrl: https://sqs.us-east-1.amazonaws.com/123456789/lambda-failures-dlq
```

**Step 2: Attach to Lambda**

```bash
aws lambda update-function-configuration \
  --function-name csv-processor \
  --dead-letter-config TargetArn=arn:aws:sqs:us-east-1:123456789:lambda-failures-dlq
```

**Step 3: Grant Lambda permission to write to SQS**

IAM policy for Lambda execution role:
```json
{
  "Effect": "Allow",
  "Action": "sqs:SendMessage",
  "Resource": "arn:aws:sqs:us-east-1:123456789:lambda-failures-dlq"
}
```

---

### Inspect Failed Events

**Check DLQ for messages:**

```bash
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789/lambda-failures-dlq
```

**Response:**
```json
{
  "Messages": [
    {
      "Body": "{\"Records\": [{\"s3\": {\"bucket\": {\"name\": \"data-lake\"}, \"object\": {\"key\": \"bronze/orders/bad_file.csv\"}}}]}",
      "MessageId": "abc-123"
    }
  ]
}
```

**Now you know:** `bronze/orders/bad_file.csv` failed. Investigate why (check CloudWatch Logs for error).

---

### Replay Failed Events

After fixing Lambda code:

```bash
# Retrieve failed event from DLQ
aws sqs receive-message --queue-url <DLQ_URL>

# Save event payload to file
echo '<event_payload>' > failed_event.json

# Manually re-invoke Lambda with corrected code
aws lambda invoke \
  --function-name csv-processor \
  --payload file://failed_event.json \
  response.json
```

---

## 📝 CloudWatch Logs (Debugging)

### Structured Logging

**❌ Bad:**
```python
def lambda_handler(event, context):
    print("Processing file")  # No context!
    df = pd.read_csv('file.csv')
    print("Done")  # What file? How many rows?
```

**✅ Good:**
```python
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    logger.info(json.dumps({
        'event': 'file_processing_started',
        'bucket': bucket,
        'key': key,
        'request_id': context.request_id
    }))
    
    try:
        df = pd.read_csv(f's3://{bucket}/{key}')
        
        logger.info(json.dumps({
            'event': 'file_loaded',
            'rows': len(df),
            'columns': list(df.columns)
        }))
        
        # Process...
        
        logger.info(json.dumps({
            'event': 'file_processing_completed',
            'output_rows': len(df),
            'duration_ms': 1234
        }))
        
    except Exception as e:
        logger.error(json.dumps({
            'event': 'file_processing_failed',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'bucket': bucket,
            'key': key
        }))
        raise  # Re-raise to trigger retry/DLQ
```

**Benefits:**
- Structured JSON logs can be queried in CloudWatch Insights
- `request_id` links logs to specific invocation
- Error context includes file name (debugging easier)

---

### Query Logs with CloudWatch Insights

**Find all failures:**
```sql
fields @timestamp, @message
| filter @message like /file_processing_failed/
| sort @timestamp desc
| limit 20
```

**Find which files failed:**
```sql
fields @timestamp, bucket, key
| parse @message '{"event":"file_processing_failed",*"key":"*"*}' as prefix, filepath, suffix
| display @timestamp, filepath
| limit 50
```

**Count errors by type:**
```sql
fields error_type
| filter @message like /file_processing_failed/
| stats count() by error_type
```

---

## 📊 CloudWatch Metrics & Alarms

### Default Lambda Metrics

CloudWatch automatically tracks:

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Invocations** | Number of times Lambda executed | N/A (track volume) |
| **Errors** | Uncaught exceptions | >5% error rate |
| **Duration** | Execution time (ms) | >80% of timeout |
| **Throttles** | Invocations rejected (concurrency limit hit) | >1% |
| **DeadLetterErrors** | Failures to write to DLQ | >0 (critical!) |

---

### Create Alarm for Error Rate

**Goal:** Alert if error rate >5% over 5 minutes.

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-csv-processor-high-errors \
  --alarm-description "Alert if Lambda errors exceed 5%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=csv-processor \
  --alarm-actions arn:aws:sns:us-east-1:123456789:engineer-alerts
```

**What happens:**
1. Lambda errors exceed 5 in 5-minute window
2. Alarm state changes to `ALARM`
3. SNS topic `engineer-alerts` triggered
4. Engineer receives email/Slack notification

---

### Custom Metrics

Log custom business metrics:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    rows_processed = 1000
    rows_invalid = 50
    
    # Publish custom metric
    cloudwatch.put_metric_data(
        Namespace='DataPipeline',
        MetricData=[
            {
                'MetricName': 'RowsProcessed',
                'Value': rows_processed,
                'Unit': 'Count'
            },
            {
                'MetricName': 'InvalidRowRate',
                'Value': (rows_invalid / rows_processed) * 100,
                'Unit': 'Percent'
            }
        ]
    )
```

**Create alarm:** Alert if `InvalidRowRate` >10% (data quality issue).

---

## 🚨 Error Patterns & Solutions

### Pattern 1: Transient Network Errors

**Error:**
```
ReadTimeoutError: Read timeout on endpoint URL: s3.amazonaws.com
```

**Cause:** Temporary S3 connectivity issue (network hiccup).

**Solution:** ✅ **Let automatic retries handle it** (likely succeeds on retry).

```python
from botocore.exceptions import ReadTimeoutError
import time

def lambda_handler(event, context):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            df = pd.read_csv('s3://bucket/file.csv')
            return process(df)
        except ReadTimeoutError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                continue
            else:
                raise  # Give up after 3 attempts
```

---

### Pattern 2: Permanent Data Errors

**Error:**
```
ParserError: Error tokenizing data. C error: Expected 5 fields, saw 8
```

**Cause:** CSV schema mismatch (file has 8 columns, code expects 5).

**Solution:** ❌ **Retrying won't help** (same error every time). Send to DLQ for manual inspection.

```python
from pandas.errors import ParserError

def lambda_handler(event, context):
    try:
        df = pd.read_csv('s3://bucket/file.csv')
        # Validate schema
        expected_cols = ['order_id', 'customer_id', 'amount', 'date', 'status']
        if list(df.columns) != expected_cols:
            raise ValueError(f"Schema mismatch: {df.columns} != {expected_cols}")
        
    except (ParserError, ValueError) as e:
        logger.error(f"Data error (won't retry): {e}")
        # Don't raise (no point retrying), send notification
        send_alert(f"Bad file: {key}, error: {e}")
        return {'status': 'failed', 'reason': str(e)}
```

---

### Pattern 3: Resource Exhaustion (Out of Memory)

**Error:**
```
MemoryError: Unable to allocate array with shape (10000000, 50) and data type float64
```

**Cause:** CSV too large for Lambda memory (10 GB max).

**Solution:** ❌ **Retrying won't help**. Process in chunks or use Glue.

```python
def lambda_handler(event, context):
    try:
        # Process in chunks
        chunks = pd.read_csv('s3://bucket/large_file.csv', chunksize=10000)
        
        for chunk in chunks:
            process_chunk(chunk)
            
    except MemoryError:
        logger.error("File too large for Lambda, routing to Glue job")
        trigger_glue_job(bucket, key)  # Offload to Glue (distributed processing)
        return {'status': 'routed_to_glue'}
```

---

### Pattern 4: Timeout (Execution Exceeds Limit)

**Error:**
```
Task timed out after 60.00 seconds
```

**Cause:** Lambda timeout set to 60 sec, but processing takes 90 sec.

**Solution:** ✅ Increase timeout OR ❌ optimize code.

```python
def lambda_handler(event, context):
    # Check remaining time
    remaining_ms = context.get_remaining_time_in_millis()
    
    if remaining_ms < 10000:  # <10 sec left
        logger.warning("Approaching timeout, aborting")
        # Save checkpoint for next invocation
        save_progress(df, checkpoint_key)
        raise TimeoutError("Need more time, saved checkpoint")
```

---

## 🔍 AWS X-Ray (Distributed Tracing)

### Enable X-Ray

**What X-Ray does:** Traces request through Lambda → S3 → DynamoDB → etc., shows where time is spent.

**Enable via CLI:**
```bash
aws lambda update-function-configuration \
  --function-name csv-processor \
  --tracing-config Mode=Active
```

**Add X-Ray SDK to code:**
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()  # Instrument boto3, requests, etc.

@xray_recorder.capture('process_csv')
def process_csv(bucket, key):
    df = pd.read_csv(f's3://{bucket}/{key}')
    # X-Ray automatically traces S3 GetObject call
    return df
```

**View in Console:**
```
Service Map:
Lambda (csv-processor)
  → S3 (GetObject) → 120ms
  → DynamoDB (PutItem) → 45ms
  → S3 (PutObject) → 230ms
Total: 395ms
```

**Insight:** Most time spent writing to S3 (230ms) → optimize by using S3 multipart upload.

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
Lambda processes S3 file, but fails with `ParserError` (bad CSV). AWS retries 2 times. Will it succeed?

<details>
<summary>Answer</summary>

**No.** Retrying the same bad CSV will produce the same `ParserError` every time.

**What should happen:**
1. Don't retry (waste of resources)
2. Send event to DLQ
3. Log error details (which file, what error)
4. Alert engineer to inspect file

**Best practice:** Catch `ParserError`, log it, send to DLQ without retrying.
</details>

---

**Question 2:**  
Your Lambda fails occasionally with `ReadTimeoutError` (S3 network issue). Should you disable automatic retries?

<details>
<summary>Answer</summary>

**No!** Network errors are **transient**—likely to succeed on retry.

**Automatic retries (2 attempts) will fix:**
- Temporary S3 outage
- Network congestion
- Rate limiting (throttling)

**Keep retries enabled.** Add exponential backoff in code for robustness.
</details>

---

**Question 3:**  
How do you know if Lambda is failing silently (no errors visible)?

<details>
<summary>Answer</summary>

**Check CloudWatch Metrics:**
1. `Errors` metric >0 → uncaught exceptions
2. `DeadLetterErrors` >0 → failures to write to DLQ (critical!)
3. `Throttles` >0 → executions rejected (concurrency limit)

**Set up alarms:**
- Alert if `Errors` >5 in 5 minutes
- Alert if `DeadLetterErrors` >0 (immediate action required)

**Check CloudWatch Logs:**
- Filter logs for keyword: "ERROR", "Exception", "failed"
- No logs at all? → Lambda not being invoked (check trigger config)
</details>

---

## 📋 Production Checklist

Before deploying Lambda to production:

- [ ] **Dead Letter Queue configured** (SQS queue attached)
- [ ] **CloudWatch alarm for errors** (alert if >5% error rate)
- [ ] **Structured logging** (JSON format, includes `request_id`, file name)
- [ ] **Retry logic for transient errors** (network timeouts, throttling)
- [ ] **Graceful handling of permanent errors** (bad data → log + DLQ, don't retry)
- [ ] **Timeout set appropriately** (not default 3 sec, not max 15 min unless needed)
- [ ] **X-Ray tracing enabled** (optional, but helps debug performance issues)
- [ ] **Custom metrics published** (data quality: invalid row rate, rows processed)
- [ ] **IAM permissions least privilege** (only necessary S3/DynamoDB access)
- [ ] **Environment variables for config** (no hardcoded bucket names)

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Retries** | Async invocations auto-retry 2x (good for transient errors, bad for permanent errors) |
| **DLQ** | Captures failed events after retries exhausted (critical for debugging) |
| **CloudWatch Logs** | Structured JSON logging enables querying (find errors, count by type) |
| **CloudWatch Metrics** | Track errors, duration, throttles (set alarms for >5% error rate) |
| **Error Patterns** | Transient (retry) vs Permanent (log + DLQ, don't retry) |
| **X-Ray** | Distributed tracing shows where time is spent (S3 call slow? optimize there) |

---

## ⏭️ Next Steps

You now know **how to handle failures** in Lambda (retries, DLQ, monitoring).

**Next:** [04-lambda-optimization.md](./04-lambda-optimization.md) → Optimize cost & performance (memory sizing, cold starts, concurrency).

---

**Pro Tip:** Always configure DLQ. Silent failures are worse than visible failures—at least with DLQ you know something went wrong.
