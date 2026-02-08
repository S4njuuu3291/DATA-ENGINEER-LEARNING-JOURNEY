# 01: S3 + Lambda Integration (End-to-End Pipeline)

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Production data pipelines depend on clean integration between S3 triggers, Lambda execution roles, and VPC networking. The goal is reliable Bronze → Silver processing with idempotency and strong security.

---

## 🧭 Integration Overview

### Problem Statement

You have raw data landing in S3 (Bronze). You need to:

1. Validate schema
2. Clean bad rows
3. Convert CSV → Parquet
4. Write to Silver layer

**Requirements:**
- Auto-trigger on file upload
- Idempotent (no duplicates)
- Secure (IAM least privilege)
- Private networking (no public internet)
- Observable (CloudWatch logs + metrics)

---

## 🏗️ Architecture (Production Pattern)

```
S3 (bronze/)
   └─ ObjectCreated event
        ↓
EventBridge Rule (filter: prefix=bronze/, suffix=.csv)
        ↓
Lambda (csv-validator)
   ├─ Read CSV from S3 (bronze)
   ├─ Validate + clean
   ├─ Write Parquet to S3 (silver)
   ├─ Log results to CloudWatch
   └─ Send failure to DLQ (SQS)
```

**Optional Enhancements:**
- Glue Data Catalog update (Module 3)
- SNS alert for failure
- Metrics: rows processed, invalid row rate

---

## ✅ Step 1: S3 Event Trigger

### Option A: EventBridge (Recommended)

Enable EventBridge on S3 bucket:

```bash
aws s3api put-bucket-notification-configuration \
  --bucket data-lake \
  --notification-configuration '{"EventBridgeConfiguration": {}}'
```

Create rule to filter only CSV files in Bronze:

```bash
aws events put-rule \
  --name bronze-csv-trigger \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": {"name": ["data-lake"]},
      "object": {
        "key": [{"prefix": "bronze/", "suffix": ".csv"}]
      }
    }
  }'
```

Attach Lambda target:

```bash
aws events put-targets \
  --rule bronze-csv-trigger \
  --targets Id=1,Arn=arn:aws:lambda:us-east-1:123456789:function:csv-validator
```

Grant EventBridge permission to invoke Lambda:

```bash
aws lambda add-permission \
  --function-name csv-validator \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:123456789:rule/bronze-csv-trigger
```

---

### Option B: S3 Event Notifications (Simpler)

```bash
aws s3api put-bucket-notification-configuration \
  --bucket data-lake \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [
      {
        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789:function:csv-validator",
        "Events": ["s3:ObjectCreated:*"],
        "Filter": {
          "Key": {
            "FilterRules": [
              {"Name": "prefix", "Value": "bronze/"},
              {"Name": "suffix", "Value": ".csv"}
            ]
          }
        }
      }
    ]
  }'
```

**Recommendation:** Use EventBridge for complex filtering or fan-out.

---

## ✅ Step 2: Lambda Execution Role (IAM)

Lambda needs permissions for:
- Read from S3 (bronze)
- Write to S3 (silver)
- Write logs to CloudWatch

**Policy (least privilege):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadBronze",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::data-lake/bronze/*"
    },
    {
      "Sid": "WriteSilver",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::data-lake/silver/*"
    },
    {
      "Sid": "CloudWatchLogs",
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

**Trust Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

## ✅ Step 3: VPC Access (Private Networking)

If Lambda runs in **private subnet** (best practice), you must allow it to access S3.

**Option 1: NAT Gateway (expensive)**
- Lambda → NAT → Internet → S3
- Cost: $0.045/GB egress

**Option 2: S3 VPC Endpoint (recommended)**
- Lambda → VPC Endpoint → S3
- Cost: $0

**Create VPC Endpoint:**
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-123 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-456
```

---

## ✅ Step 4: Lambda Code (Bronze → Silver)

**Minimal CSV Validator (pandas):**

```python
import boto3
import pandas as pd
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse S3 event
    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']

    # Idempotency: output path
    output_key = key.replace('bronze/', 'silver/').replace('.csv', '.parquet')

    # Skip if already processed
    try:
        s3.head_object(Bucket=bucket, Key=output_key)
        print(f"Already processed: {output_key}")
        return {'status': 'duplicate'}
    except s3.exceptions.ClientError:
        pass

    # Read CSV
    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(obj['Body'])

    # Validate + clean
    required = ['order_id', 'customer_id', 'amount']
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.dropna(subset=['order_id', 'customer_id'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Write to silver
    df.to_parquet(f"s3://{bucket}/{output_key}", index=False)

    return {
        'status': 'success',
        'rows': len(df),
        'output': output_key
    }
```

**Note:** For small files (<100 MB). Larger files should move to Glue (Module 4).

---

## ✅ Step 5: Error Handling & DLQ

Configure DLQ for failed events (SQS):

```bash
aws sqs create-queue --queue-name csv-validator-dlq
```

Attach DLQ to Lambda:

```bash
aws lambda update-function-configuration \
  --function-name csv-validator \
  --dead-letter-config TargetArn=arn:aws:sqs:us-east-1:123456789:csv-validator-dlq
```

**Why:** If CSV is malformed (permanent error), it should go to DLQ, not retry forever.

---

## ✅ Step 6: Observability

**CloudWatch Logs:**
- Always log `bucket`, `key`, `rows_processed`
- Use structured JSON logging for queryability

**CloudWatch Metrics:**
- Errors > 5% triggers alarm
- Duration > 80% of timeout triggers alarm
- Custom metric: invalid row rate

---

## 🔒 Security Checklist

- [ ] Lambda execution role has **least privilege** (only bronze read + silver write)
- [ ] Bucket policy restricts write access to Lambda role
- [ ] No public access on bucket (BlockPublicAccess enabled)
- [ ] If in VPC, S3 access via **VPC Endpoint** (no public internet)
- [ ] Secrets stored in Secrets Manager (never hardcode)

---

## 🧪 Hands-On Intuition Check

**Question 1:** If Lambda processes the same CSV twice, how do you prevent duplicate silver output?

<details>
<summary>Answer</summary>

Use **idempotency**. The simplest: check if silver output already exists.

```python
try:
    s3.head_object(Bucket=bucket, Key=output_key)
    return {'status': 'duplicate'}
except:
    pass
```

If output exists, skip processing.
</details>

---

**Question 2:** Why should Lambda in private subnet use S3 VPC Endpoint instead of NAT?

<details>
<summary>Answer</summary>

**Cost & security:**
- NAT charges $0.045/GB (expensive)
- VPC Endpoint is free
- Endpoint traffic stays inside AWS network (more secure)
</details>

---

## 📋 Summary

| Step | Key Action |
|------|------------|
| **Trigger** | EventBridge rule filters bronze CSV files |
| **IAM Role** | Least privilege (S3 read bronze, write silver) |
| **Networking** | Use VPC Endpoint for private access |
| **Code** | Validate, clean, convert, write Parquet |
| **Idempotency** | Skip if output already exists |
| **Error Handling** | DLQ for failures + CloudWatch alarms |

---

## ⏭️ Next Steps

Now you can build a production-ready S3 → Lambda → S3 pipeline.

**Next:** [Module 2 Exercises](../../exercises/module-2-lambda-events-exercises.md) → Hands-on practice with real Lambda + EventBridge workflows.

---

**Pro Tip:** Always test with a small CSV first (10 rows) before running full pipeline. It saves time and AWS costs.
