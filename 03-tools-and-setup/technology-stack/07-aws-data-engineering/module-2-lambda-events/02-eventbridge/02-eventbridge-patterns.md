# 02: EventBridge Event Patterns & Architecture

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate-Advanced  
> **Key Takeaway:** Event-driven architectures decouple services via EventBridge—one S3 upload can trigger validation, metadata extraction, and notifications simultaneously through fan-out patterns and precise event filtering.

---

## 🎯 Event Pattern Matching

### What is an Event Pattern?

**Event Pattern = JSON filter** that matches specific events.

**Structure:**
```json
{
  "source": ["aws.s3"],          # Match events from S3
  "detail-type": ["Object Created"],  # Match ObjectCreated events
  "detail": {                    # Match event payload details
    "bucket": {
      "name": ["data-lake"]      # Only from data-lake bucket
    },
    "object": {
      "key": [{
        "prefix": "bronze/"      # Only files in bronze/ folder
      }]
    }
  }
}
```

**How it works:**
- EventBridge compares **every incoming event** against this pattern
- If all fields match → event routed to targets
- If any field doesn't match → event ignored

---

### Filtering by Prefix/Suffix

**Use case:** Process only CSV files from `bronze/orders/` folder.

**Event Pattern:**
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["data-lake"]
    },
    "object": {
      "key": [{
        "prefix": "bronze/orders/",
        "suffix": ".csv"
      }]
    }
  }
}
```

**Matches:**
- ✅ `bronze/orders/2024-01-15.csv` (prefix ✓, suffix ✓)
- ✅ `bronze/orders/2024/monthly_report.csv` (prefix ✓, suffix ✓)

**Doesn't match:**
- ❌ `bronze/customers/2024-01-15.csv` (wrong prefix)
- ❌ `bronze/orders/2024-01-15.json` (wrong suffix)
- ❌ `silver/orders/2024-01-15.csv` (wrong prefix)

---

### Filtering by File Size

**Use case:** Process only files >1 MB (skip empty/tiny files).

**Event Pattern:**
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "object": {
      "size": [{ "numeric": [">", 1048576] }]
    }
  }
}
```

**Matches:**
- ✅ 5 MB file (5,242,880 bytes > 1,048,576)
- ✅ 1.1 MB file (1,153,434 bytes > 1,048,576)

**Doesn't match:**
- ❌ 500 KB file (512,000 bytes < 1,048,576)
- ❌ 0 byte file (empty)

---

### Combining Filters (AND Logic)

**Use case:** CSV files >10 MB from `bronze/orders/`.

**Event Pattern:**
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["data-lake"]
    },
    "object": {
      "key": [{
        "prefix": "bronze/orders/",
        "suffix": ".csv"
      }],
      "size": [{ "numeric": [">", 10485760] }]
    }
  }
}
```

**ALL conditions must match** (AND logic):
- ✅ `bronze/orders/big_file.csv` (15 MB) → All conditions met
- ❌ `bronze/orders/small.csv` (1 MB) → Size too small
- ❌ `bronze/customers/big_file.csv` (20 MB) → Wrong prefix

---

### Multiple Values (OR Logic)

**Use case:** Accept CSV **or** JSON files.

**Event Pattern:**
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "object": {
      "key": [{
        "suffix": ".csv"
      }, {
        "suffix": ".json"
      }]
    }
  }
}
```

**Matches either** (OR logic):
- ✅ `data.csv` (suffix = .csv)
- ✅ `data.json` (suffix = .json)
- ❌ `data.parquet` (neither .csv nor .json)

---

## 🌟 Fan-Out Pattern

### Problem: One Event, Multiple Actions

**Scenario:** When CSV uploaded to `bronze/`, you need to:

1. **Validate** data (Lambda: check schema, remove nulls)
2. **Update catalog** (Lambda: register table in Glue Data Catalog)
3. **Notify** engineers (SNS: send Slack alert)

**Traditional approach:** Chain functions.

```python
# ❌ Bad: Tight coupling
def lambda_handler(event, context):
    validate_csv(event)      # Step 1
    update_catalog(event)    # Step 2 (if Step 1 fails, Step 2 never runs)
    send_notification(event) # Step 3 (if Step 2 fails, Step 3 never runs)
```

**Problems:**
- **Tight coupling:** All logic in 1 Lambda (hard to maintain)
- **Single point of failure:** If validation crashes, catalog never updated
- **Can't scale independently:** Can't allocate more memory to validation without affecting catalog update

---

### Solution: Fan-Out with EventBridge

**Architecture:**

```
S3 Upload (bronze/orders.csv)
    ↓
EventBridge Rule (1 event)
    ↓
┌────────────┬──────────────┬─────────────────┐
↓            ↓              ↓                 ↓
Lambda       Lambda         Lambda            SNS Topic
(Validate)   (Catalog)      (Quality Check)   (Slack Alert)

All triggered SIMULTANEOUSLY (parallel processing)
```

**EventBridge Rule:**
```bash
aws events put-rule \
  --name s3-csv-fanout \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "object": {
        "key": [{"suffix": ".csv"}]
      }
    }
  }'

# Add 4 targets to same rule
aws events put-targets \
  --rule s3-csv-fanout \
  --targets \
    Id=1,Arn=arn:aws:lambda:us-east-1:123:function:validate-csv \
    Id=2,Arn=arn:aws:lambda:us-east-1:123:function:update-catalog \
    Id=3,Arn=arn:aws:lambda:us-east-1:123:function:quality-check \
    Id=4,Arn=arn:aws:sns:us-east-1:123:topic/data-alerts
```

**Benefits:**
- ✅ **Loose coupling:** Each Lambda independent (update one without affecting others)
- ✅ **Parallel execution:** All 4 targets triggered simultaneously (faster than sequential)
- ✅ **Fault isolation:** If validation fails, catalog update still runs
- ✅ **Independent scaling:** Allocate 2 GB to validation, 512 MB to catalog update

---

### Real Example: Data Pipeline Fan-Out

**Event Pattern Rule:**
```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["data-lake"]
    },
    "object": {
      "key": [{
        "prefix": "bronze/"
      }]
    }
  }
}
```

**Targets:**

| Target | Purpose | Memory | Duration |
|--------|---------|--------|----------|
| `validate-csv` | Schema validation (pandas) | 1024 MB | 5 sec |
| `update-glue-catalog` | Register Glue table | 512 MB | 2 sec |
| `calculate-stats` | Count rows, detect duplicates | 512 MB | 3 sec |
| `sns-topic` | Slack notification "File uploaded" | N/A | <1 sec |

**Cost per event:**
- Validate: 1 GB × 5 sec = 5 GB-sec = $0.00008
- Catalog: 0.5 GB × 2 sec = 1 GB-sec = $0.000017
- Stats: 0.5 GB × 3 sec = 1.5 GB-sec = $0.000025
- SNS: $0.0000005 (per message)
- **Total:** $0.00012 per file upload (basically free!)

---

## 🔀 Event Transformation (Input Transformers)

### Problem: Event Payload Too Large or Wrong Format

**S3 Event Payload (simplified):**
```json
{
  "version": "0",
  "source": "aws.s3",
  "detail": {
    "bucket": {"name": "data-lake"},
    "object": {
      "key": "bronze/orders/2024-01-15.csv",
      "size": 1048576,
      "etag": "abc123def456"
    }
  }
}
```

**Lambda expects simpler input:**
```json
{
  "bucket": "data-lake",
  "key": "bronze/orders/2024-01-15.csv"
}
```

**Solution:** Use **Input Transformer** to extract only needed fields.

---

### Configure Input Transformer

**CLI:**
```bash
aws events put-targets \
  --rule s3-csv-processor \
  --targets file://target.json
```

**target.json:**
```json
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123:function:csv-processor",
    "InputTransformer": {
      "InputPathsMap": {
        "bucket": "$.detail.bucket.name",
        "key": "$.detail.object.key",
        "size": "$.detail.object.size"
      },
      "InputTemplate": "{\"bucket\": <bucket>, \"key\": <key>, \"size\": <size>}"
    }
  }
]
```

**Result:** Lambda receives:
```json
{
  "bucket": "data-lake",
  "key": "bronze/orders/2024-01-15.csv",
  "size": 1048576
}
```

**Benefits:**
- ✅ Smaller payload (faster Lambda invocation)
- ✅ Lambda code simpler (no need to navigate nested JSON)
- ✅ Hide sensitive fields (exclude etag, version)

---

## 🌐 Cross-Account Event Routing

### Use Case: Data Lake in Account A, Processing in Account B

**Scenario:**
- **Account A (123456789):** S3 bucket `data-lake` (central data storage)
- **Account B (987654321):** Lambda `process-data` (data team's processing function)

**Requirement:** When file uploaded to Account A's S3, trigger Account B's Lambda.

---

### Architecture

```
Account A (S3)
    ↓
Default Event Bus (Account A)
    ↓
EventBridge Rule → Send to Account B Event Bus
    ↓
Custom Event Bus (Account B)
    ↓
EventBridge Rule → Lambda (Account B)
```

---

### Setup

**Step 1: Account B - Create Custom Event Bus**

```bash
# In Account B
aws events create-event-bus --name data-intake
```

**Step 2: Account B - Grant Account A Permission**

```bash
# In Account B
aws events put-permission \
  --event-bus-name data-intake \
  --statement-id allow-account-a \
  --action events:PutEvents \
  --principal 123456789  # Account A
```

**Step 3: Account A - Create Rule to Forward Events**

```bash
# In Account A
aws events put-rule \
  --name forward-s3-events \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"]
  }'

aws events put-targets \
  --rule forward-s3-events \
  --targets \
    Id=1,Arn=arn:aws:events:us-east-1:987654321:event-bus/data-intake
```

**Step 4: Account B - Create Rule to Invoke Lambda**

```bash
# In Account B
aws events put-rule \
  --event-bus-name data-intake \
  --name trigger-lambda \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"]
  }'

aws events put-targets \
  --rule trigger-lambda \
  --event-bus-name data-intake \
  --targets \
    Id=1,Arn=arn:aws:lambda:us-east-1:987654321:function:process-data
```

**Done!** S3 upload in Account A → Lambda execution in Account B.

---

## 🚨 Dead Letter Queue for Targets

### Problem: Target Fails to Receive Event

**Scenario:** Lambda execution role missing permissions → EventBridge can't invoke Lambda.

**What happens without DLQ:**
- EventBridge retries event 24 hours (185 times!)
- After 24 hours → event **discarded** (lost forever)
- You never know which events failed

---

### Solution: Configure DLQ for Target

**Step 1: Create SQS DLQ**

```bash
aws sqs create-queue --queue-name eventbridge-target-dlq
```

**Step 2: Attach DLQ to Target**

```bash
aws events put-targets \
  --rule s3-csv-processor \
  --targets file://target-with-dlq.json
```

**target-with-dlq.json:**
```json
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:us-east-1:123:function:csv-processor",
    "DeadLetterConfig": {
      "Arn": "arn:aws:sqs:us-east-1:123:eventbridge-target-dlq"
    },
    "RetryPolicy": {
      "MaximumRetryAttempts": 2,
      "MaximumEventAge": 3600
    }
  }
]
```

**Configuration:**
- `MaximumRetryAttempts`: 2 retries (total 3 attempts)
- `MaximumEventAge`: 3600 sec (1 hour) → discard event older than 1 hour
- `DeadLetterConfig`: Send failed events to SQS queue

**What happens now:**
1. Event sent to Lambda → fails (permission denied)
2. Retry #1 after 1 min → fails
3. Retry #2 after 2 min → fails
4. Event sent to DLQ (not lost!)

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
Event pattern filters for `"prefix": "bronze/"` and `"suffix": ".csv"`. Does `bronze/subfolder/data.csv` match?

<details>
<summary>Answer</summary>

**Yes.**

**Explanation:**
- `"prefix": "bronze/"` → Matches any key starting with `bronze/`
- `bronze/subfolder/data.csv` starts with `bronze/` ✓
- Ends with `.csv` ✓

**Pattern matches:**
- `bronze/data.csv` ✓
- `bronze/2024/01/data.csv` ✓
- `bronze/orders/nested/deep/file.csv` ✓

**Prefix matching is NOT exact folder match** (it's string prefix).

**Want exact folder?** Use prefix `bronze/` + additional validation in Lambda.
</details>

---

**Question 2:**  
One S3 upload triggers 3 Lambda functions via fan-out. Lambda #2 fails. Do Lambda #1 and #3 still run?

<details>
<summary>Answer</summary>

**Yes, #1 and #3 still run.**

**EventBridge behavior:**
- Each target is invoked **independently**
- Failure in one target doesn't affect others
- #1 succeeds, #2 fails, #3 succeeds

**Failed invocation (#2):**
- EventBridge retries (according to RetryPolicy)
- After retries exhausted → sent to DLQ (if configured)
- CloudWatch metric `FailedInvocations` incremented

**Best practice:** Configure DLQ for each target to capture failures.
</details>

---

**Question 3:**  
You want Account B's Lambda to process files from Account A's S3. Can you skip the custom event bus and directly add Account B Lambda as target in Account A's rule?

<details>
<summary>Answer</summary>

**No, cross-account Lambda targets require custom event bus.**

**Why:**
- EventBridge can only invoke Lambdas **in the same account** directly
- Cross-account requires: Account A → Custom Event Bus (Account B) → Lambda (Account B)

**Alternative (simpler):** Use **S3 Event Notifications** (not EventBridge) with cross-account Lambda permission.

```bash
# In Account B: Grant S3 permission to invoke Lambda
aws lambda add-permission \
  --function-name process-data \
  --principal s3.amazonaws.com \
  --source-account 123456789 \
  --source-arn arn:aws:s3:::data-lake \
  --action lambda:InvokeFunction
```

**Then configure S3 notification directly** (no EventBridge needed).

**Trade-off:** S3 notifications simpler for cross-account, but less flexible (no advanced filtering, no fan-out).
</details>

---

## 📋 Production Patterns Summary

| Pattern | Use Case | Configuration |
|---------|----------|---------------|
| **Prefix/Suffix Filter** | Process only CSV from `bronze/orders/` | `"prefix": "bronze/orders/", "suffix": ".csv"` |
| **Size Filter** | Skip files <1 MB | `"size": [{"numeric": [">", 1048576]}]` |
| **Fan-Out** | 1 event → 3 Lambdas (validate, catalog, notify) | 1 rule + 3 targets |
| **Input Transformer** | Extract only needed fields | `InputPathsMap` + `InputTemplate` |
| **Cross-Account** | S3 (Account A) → Lambda (Account B) | Custom event bus + permissions |
| **DLQ for Targets** | Capture failed Lambda invocations | `DeadLetterConfig` on target |

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Event Patterns** | JSON filter (source, detail-type, prefix, suffix, size) |
| **Fan-Out** | 1 event → multiple targets (parallel processing, loose coupling) |
| **Input Transformer** | Extract/reshape event payload for Lambda |
| **Cross-Account** | Requires custom event bus + permissions |
| **Target DLQ** | Capture failed invocations (don't lose events) |

---

## ⏭️ Next Steps

You now understand **EventBridge patterns** (filtering, fan-out, cross-account).

**Next:** [S3 + Lambda Integration](../03-integration/01-s3-lambda-integration.md) → Build end-to-end data pipeline (Bronze → Silver ETL).

---

**Pro Tip:** Always configure DLQ for targets. Failed events without DLQ = lost data (especially in production).
