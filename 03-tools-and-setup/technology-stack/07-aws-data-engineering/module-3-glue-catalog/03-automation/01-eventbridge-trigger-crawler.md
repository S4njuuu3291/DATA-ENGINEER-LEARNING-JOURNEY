# 01: EventBridge Trigger for Glue Crawler

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Crawlers should run only when new data arrives. Use EventBridge + Lambda to trigger crawlers automatically after S3 uploads.

---

## 🔥 Problem: Crawler Runs on Schedule Only

**Scenario:**
- Crawler runs every night at 2 AM
- New file arrives at 9 AM
- Metadata is stale until next day

**Impact:**
- Athena queries fail (table not updated)
- Downstream pipeline delayed

---

## ✅ Solution: Event-Driven Crawler

**Goal:** When file uploaded to `bronze/`, trigger crawler immediately.

**Architecture:**
```
S3 Upload (bronze/)
  → EventBridge Rule
    → Lambda (start crawler)
      → Glue Crawler Run
```

---

## Step 1: EventBridge Rule

**Filter only bronze CSV uploads:**

```bash
aws events put-rule \
  --name glue-crawler-trigger \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "object": {
        "key": [{"prefix": "bronze/", "suffix": ".csv"}]
      }
    }
  }'
```

---

## Step 2: Lambda Function (Start Crawler)

**Lambda code (Python):**
```python
import boto3

crawler_name = "bronze-orders-crawler"
client = boto3.client("glue")

def lambda_handler(event, context):
    try:
        client.start_crawler(Name=crawler_name)
        return {"status": "started", "crawler": crawler_name}
    except client.exceptions.CrawlerRunningException:
        return {"status": "already_running"}
```

**IAM permissions for Lambda:**
```json
{
  "Effect": "Allow",
  "Action": ["glue:StartCrawler"],
  "Resource": "*"
}
```

---

## Step 3: Add Lambda as Target

```bash
aws events put-targets \
  --rule glue-crawler-trigger \
  --targets Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT:function:start-crawler
```

Grant permission:
```bash
aws lambda add-permission \
  --function-name start-crawler \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:REGION:ACCOUNT:rule/glue-crawler-trigger
```

---

## 🧠 Best Practices

- **Debounce runs:** Crawler can't run twice in parallel. Catch `CrawlerRunningException`.
- **Scope events:** Only trigger on relevant prefix (bronze/). Avoid bucket root.
- **Monitor runs:** CloudWatch Logs + Glue Console
- **Cost control:** Trigger only on new partitions, not every file if too frequent

---

## 🧪 Hands-On Intuition Check

**Question:** Why not trigger crawler for every single file upload?

<details>
<summary>Answer</summary>

Because crawler scans the entire prefix each time. If you upload 100 files/day, you run crawler 100 times → expensive and slow.

Better: trigger only on significant batch uploads or use schedule + recrawl new folders.
</details>

---

## 📋 Summary

| Step | Action |
|------|--------|
| **EventBridge Rule** | Detect S3 uploads in bronze/ |
| **Lambda** | Start crawler programmatically |
| **IAM** | Lambda needs `glue:StartCrawler` permission |
| **Best Practice** | Avoid triggering on every file (cost control) |

---

## ⏭️ Next Steps

Next: [Module 3 Exercises](../../exercises/module-3-glue-catalog-exercises.md)
