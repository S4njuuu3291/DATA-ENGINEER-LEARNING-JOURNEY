# 01: EventBridge Basics (Managed Event Bus)

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐☆ Beginner-Intermediate  
> **Key Takeaway:** EventBridge replaces cron jobs with a managed, serverless event bus that routes events from AWS services (S3, DynamoDB) or custom applications to targets (Lambda, SQS, Step Functions).

---

## 🔥 The Problem: Fragile Cron Jobs

### Traditional Approach: Cron on EC2

**Scenario:** Run daily ETL job at 2 AM.

**Setup:**
```bash
# SSH into EC2
ssh ec2-user@my-ec2-instance

# Edit crontab
crontab -e

# Add cron job (2 AM daily)
0 2 * * * /home/ec2-user/etl_script.sh >> /var/log/etl.log 2>&1
```

**Problems:**

1. **Single Point of Failure**  
   EC2 instance crashes → cron job doesn't run → data pipeline broken

2. **Manual Maintenance**  
   - OS updates require reboot → cron service interrupted
   - Disk full → logs fill /var/log → script fails silently
   - Time zone issues (UTC vs local time)

3. **No Visibility**  
   - Did job run? Check logs manually
   - Job failed? No alert, no retry
   - How long did it take? Parse logs

4. **Scaling Issues**  
   Need to run on multiple regions → manually configure cron on 3 EC2 instances

5. **Cost**  
   EC2 runs 24/7 ($15/month) just to execute 1-minute job daily

---

## ✅ The Solution: Amazon EventBridge

### What is EventBridge?

> **EventBridge** is a **serverless event bus** that routes events from sources (AWS services, SaaS apps, custom code) to targets (Lambda, SQS, Step Functions, etc.).

**Key Characteristics:**

1. **Serverless:** No infrastructure to manage (no EC2, no cron daemon)
2. **Managed:** AWS handles scaling, retries, durability
3. **Event-Driven:** React to events (file uploaded, schedule triggered, API call)
4. **Multi-Target:** One event → multiple targets (fan-out pattern)
5. **Filtering:** Route events based on content (only .csv files, only failed orders)

---

### Core Concepts

#### 1. **Event Bus**

**Event Bus = Message highway** where events flow.

**Types:**
- **Default Event Bus:** Receives events from AWS services (S3, DynamoDB, EC2)
- **Custom Event Bus:** Your own bus for custom application events
- **Partner Event Buses:** SaaS providers (Datadog, Zendesk, Auth0)

**Example:** S3 sends "ObjectCreated" event to Default Event Bus.

---

#### 2. **Events**

**Event = JSON payload** describing something that happened.

**Example: S3 ObjectCreated event**
```json
{
  "version": "0",
  "id": "abc-123",
  "source": "aws.s3",
  "detail-type": "Object Created",
  "time": "2024-01-15T14:23:45Z",
  "region": "us-east-1",
  "detail": {
    "bucket": {
      "name": "data-lake"
    },
    "object": {
      "key": "bronze/orders/2024-01-15.csv",
      "size": 1048576
    }
  }
}
```

**Key Fields:**
- `source`: Where event came from (`aws.s3`, `aws.dynamodb`, `custom.app`)
- `detail-type`: Type of event (`Object Created`, `Table Updated`)
- `detail`: Custom payload (bucket name, file key, row count, etc.)

---

#### 3. **Rules**

**Rule = Filter + Trigger** that matches events and sends them to targets.

**Components:**
- **Event Pattern:** JSON filter (match events from source `aws.s3`)
- **Schedule Expression:** Cron or rate expression (`cron(0 2 * * ? *)`)
- **Target:** Where to send matched events (Lambda ARN, SQS queue ARN)

**Example Rule:**
```json
{
  "Name": "s3-csv-trigger",
  "EventPattern": {
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": {
        "name": ["data-lake"]
      },
      "object": {
        "key": [{
          "suffix": ".csv"
        }]
      }
    }
  },
  "Targets": [
    {
      "Arn": "arn:aws:lambda:us-east-1:123456789:function:csv-processor",
      "Id": "1"
    }
  ]
}
```

**Translation:** "When a `.csv` file is created in `data-lake` bucket, invoke `csv-processor` Lambda."

---

#### 4. **Targets**

**Target = Destination** for matched events.

**Supported Targets:**
| Target | Use Case |
|--------|----------|
| **Lambda** | Process event (validate CSV, transform data) |
| **SQS Queue** | Buffer events (async processing, decouple services) |
| **SNS Topic** | Send notifications (email, Slack alert) |
| **Step Functions** | Orchestrate workflows (multi-step ETL pipeline) |
| **Kinesis Stream** | Real-time analytics (aggregate metrics) |
| **ECS Task** | Run containerized job (Docker-based processing) |
| **EventBus (another region/account)** | Cross-region/account routing |

**For Data Engineering:** 80% = **Lambda** (process files) + **Step Functions** (orchestrate pipelines).

---

## 📅 Schedule Expressions

### Cron Expressions

**Format:** `cron(minute hour day month day-of-week year)`

**Examples:**

| Expression | When It Runs | Use Case |
|------------|--------------|----------|
| `cron(0 2 * * ? *)` | **2 AM daily** | Daily ETL job |
| `cron(0 */6 * * ? *)` | **Every 6 hours** (0:00, 6:00, 12:00, 18:00) | Data sync |
| `cron(0 9 ? * MON-FRI *)` | **9 AM weekdays** | Business hours report |
| `cron(0 0 1 * ? *)` | **1st of month, midnight** | Monthly aggregation |
| `cron(0 12 * * ? *)` | **Noon daily** | Lunchtime data refresh |

**Note:** EventBridge uses **UTC time zone** (no daylight saving adjustments).

**Field details:**
- `minute`: 0-59
- `hour`: 0-23 (UTC!)
- `day`: 1-31
- `month`: 1-12 or JAN-DEC
- `day-of-week`: 1-7 or SUN-SAT (1 = Sunday)
- `year`: 1970-2199

**Special characters:**
- `*` = any value
- `?` = no specific value (use for day or day-of-week when other is specified)
- `/` = increments (`*/15` = every 15 minutes)

---

### Rate Expressions

**Format:** `rate(value unit)`

**Examples:**

| Expression | When It Runs | Use Case |
|------------|--------------|----------|
| `rate(5 minutes)` | **Every 5 minutes** | Real-time monitoring |
| `rate(1 hour)` | **Every hour** | Hourly data ingestion |
| `rate(1 day)` | **Every 24 hours** (from time of creation) | Daily backup |
| `rate(7 days)` | **Every week** | Weekly report |

**Difference from cron:**
- **Cron:** Fixed times (always 2 AM daily)
- **Rate:** Relative intervals (every 6 hours from now)

**Use cron when:** You care about exact time (2 AM sharp).  
**Use rate when:** You care about frequency (every hour, doesn't matter which minute).

---

## 🛠️ Creating EventBridge Rules

### Example 1: Daily ETL at 2 AM

**Step 1: Create rule**

```bash
aws events put-rule \
  --name daily-etl \
  --schedule-expression "cron(0 2 * * ? *)" \
  --description "Trigger ETL job daily at 2 AM UTC"
```

**Step 2: Add Lambda target**

```bash
aws events put-targets \
  --rule daily-etl \
  --targets \
    Id=1,Arn=arn:aws:lambda:us-east-1:123456789:function:etl-job
```

**Step 3: Grant EventBridge permission to invoke Lambda**

```bash
aws lambda add-permission \
  --function-name etl-job \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:123456789:rule/daily-etl
```

**Done!** Lambda runs daily at 2 AM UTC, fully managed.

---

### Example 2: Process CSV Files from S3

**Step 1: Enable EventBridge on S3 bucket**

```bash
aws s3api put-bucket-notification-configuration \
  --bucket data-lake \
  --notification-configuration '{
    "EventBridgeConfiguration": {}
  }'
```

**Step 2: Create event pattern rule**

```bash
aws events put-rule \
  --name s3-csv-processor \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": {
        "name": ["data-lake"]
      },
      "object": {
        "key": [{
          "suffix": ".csv"
        }]
      }
    }
  }'
```

**Step 3: Add Lambda target**

```bash
aws events put-targets \
  --rule s3-csv-processor \
  --targets \
    Id=1,Arn=arn:aws:lambda:us-east-1:123456789:function:csv-validator
```

**Done!** Every CSV uploaded to `data-lake` triggers `csv-validator` Lambda.

---

## 📊 EventBridge vs S3 Event Notifications

**You have two options for S3 triggers:**

| Feature | S3 Event Notifications | EventBridge |
|---------|------------------------|-------------|
| **Setup** | Configure on S3 bucket directly | Enable EventBridge on bucket + create rule |
| **Filtering** | Prefix/suffix only (`bronze/` or `.csv`) | Advanced (JSON pattern, size, metadata) |
| **Targets** | Lambda, SQS, SNS | 15+ targets (Lambda, SQS, SNS, Step Functions, etc.) |
| **Fan-out** | 1 event → 1 target | 1 event → multiple targets |
| **Event transformation** | No | Yes (input transformers) |
| **Cross-account** | Requires bucket policy | Native support |
| **Cost** | Free | Free (no EventBridge charges for S3 events) |

**When to use S3 Event Notifications:**
- ✅ Simple use case (1 S3 bucket → 1 Lambda)
- ✅ Basic filtering (prefix/suffix)

**When to use EventBridge:**
- ✅ Complex filtering (file size >10 MB, specific metadata)
- ✅ Multiple targets (1 file → 3 Lambdas: validate, catalog, notify)
- ✅ Cross-account routing (S3 in Account A → Lambda in Account B)

**Recommendation for Data Engineering:** **EventBridge** (more flexible, future-proof).

---

## 🎯 Hands-On Intuition Check

**Question 1:**  
You want to run a Lambda function every 6 hours. Which schedule expression?

<details>
<summary>Answer</summary>

**Two options:**

1. **Cron:** `cron(0 */6 * * ? *)` → Runs at 00:00, 06:00, 12:00, 18:00 UTC daily
2. **Rate:** `rate(6 hours)` → Runs every 6 hours from rule creation time

**Difference:**
- Cron: Fixed times (predictable, always at 6AM/12PM/6PM/12AM)
- Rate: Relative (if created at 2:35 PM, runs at 2:35, 8:35, 2:35, etc.)

**Best practice:** Use **cron** for predictable schedules (easier to reason about).
</details>

---

**Question 2:**  
Your EventBridge rule triggers at `cron(0 9 * * ? *)`. Users in New York (EST, UTC-5) complain job runs at 4 AM, not 9 AM. Why?

<details>
<summary>Answer</summary>

**EventBridge always uses UTC timezone.**

- `cron(0 9 * * ? *)` = 9 AM **UTC**
- 9 AM UTC = 4 AM EST (9 - 5 hours)

**Fix:** Adjust for timezone:
- Want 9 AM EST (UTC-5) → Set `cron(0 14 * * ? *)` (9 AM + 5 hours = 14:00 UTC)

**Note:** During daylight saving (EDT, UTC-4), this becomes 10 AM EDT. EventBridge doesn't auto-adjust for DST.

**Best practice:** Document timezone in rule description: "Runs at 9 AM EST (14:00 UTC)".
</details>

---

**Question 3:**  
You upload 100 CSV files to S3 simultaneously. EventBridge rule triggers Lambda for each. How many Lambdas run?

<details>
<summary>Answer</summary>

**100 Lambdas run concurrently** (one per event).

**EventBridge behavior:**
- Each S3 ObjectCreated event triggers rule independently
- 100 events → 100 Lambda invocations

**Potential issue:** Hit Lambda concurrency limit (1,000 account-wide). If other Lambdas using 920 concurrency → 80 of these Lambdas throttled.

**Solution:** Reserve concurrency for this Lambda (guarantee capacity).

```bash
aws lambda put-function-concurrency \
  --function-name csv-validator \
  --reserved-concurrent-executions 200
```
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **EventBridge** | Managed event bus (replaces cron, routes AWS service events to targets) |
| **Event Bus** | Highway where events flow (default, custom, partner) |
| **Rule** | Event pattern (filter) + target (where to send matched events) |
| **Schedule** | Cron (fixed times, UTC) or Rate (intervals) |
| **S3 Integration** | EventBridge more flexible than S3 Event Notifications (filtering, fan-out) |

---

## ⏭️ Next Steps

You now understand **EventBridge basics** (schedules, event routing).

**Next:** [02-eventbridge-patterns.md](./02-eventbridge-patterns.md) → Learn event-driven patterns (fan-out, filtering, cross-account).

---

**Pro Tip:** Always test cron expressions before production. Use [crontab.guru](https://crontab.guru/) to verify syntax (remember: EventBridge = UTC!).
