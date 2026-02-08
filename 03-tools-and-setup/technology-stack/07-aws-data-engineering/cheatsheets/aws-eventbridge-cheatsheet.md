# AWS EventBridge Cheatsheet

Quick reference for event rules, schedules, and pattern matching.

---

## AWS CLI Essentials

### Create Rule (Schedule)

```bash
aws events put-rule \
  --name daily-etl \
  --schedule-expression "cron(0 2 * * ? *)" \
  --description "Trigger ETL daily at 2 AM UTC"
```

### Create Rule (Event Pattern)

```bash
aws events put-rule \
  --name s3-csv-trigger \
  --event-pattern '{
    "source": ["aws.s3"],
    "detail-type": ["Object Created"],
    "detail": {
      "bucket": {"name": ["data-lake"]},
      "object": {"key": [{"suffix": ".csv"}]}
    }
  }'
```

### Add Targets

```bash
aws events put-targets \
  --rule s3-csv-trigger \
  --targets Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT:function:csv-validator
```

### Allow EventBridge to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name csv-validator \
  --statement-id allow-eventbridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:REGION:ACCOUNT:rule/s3-csv-trigger
```

---

## Schedule Reference

### Cron Examples

| Expression | When |
|------------|------|
| `cron(0 2 * * ? *)` | Daily at 02:00 UTC |
| `cron(0 */6 * * ? *)` | Every 6 hours |
| `cron(0 9 ? * MON-FRI *)` | Weekdays at 09:00 UTC |
| `cron(0 0 1 * ? *)` | First of month |

### Rate Examples

| Expression | When |
|------------|------|
| `rate(5 minutes)` | Every 5 minutes |
| `rate(1 hour)` | Every hour |
| `rate(1 day)` | Every 24 hours |

---

## Event Pattern Examples

### Prefix + Suffix Filter

```json
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "object": {
      "key": [{"prefix": "bronze/", "suffix": ".csv"}]
    }
  }
}
```

### File Size Filter (>1 MB)

```json
{
  "detail": {
    "object": {
      "size": [{"numeric": [">", 1048576]}]
    }
  }
}
```

### Multiple File Types (CSV or JSON)

```json
{
  "detail": {
    "object": {
      "key": [
        {"suffix": ".csv"},
        {"suffix": ".json"}
      ]
    }
  }
}
```

---

## Input Transformer

```json
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:REGION:ACCOUNT:function:csv-validator",
    "InputTransformer": {
      "InputPathsMap": {
        "bucket": "$.detail.bucket.name",
        "key": "$.detail.object.key"
      },
      "InputTemplate": "{\"bucket\": <bucket>, \"key\": <key>}"
    }
  }
]
```

---

## Fan-Out (Multiple Targets)

```bash
aws events put-targets \
  --rule s3-csv-trigger \
  --targets \
    Id=1,Arn=arn:aws:lambda:REGION:ACCOUNT:function:validate \
    Id=2,Arn=arn:aws:lambda:REGION:ACCOUNT:function:update-catalog \
    Id=3,Arn=arn:aws:sns:REGION:ACCOUNT:topic/notify
```

---

## DLQ for Targets

```json
[
  {
    "Id": "1",
    "Arn": "arn:aws:lambda:REGION:ACCOUNT:function:csv-validator",
    "DeadLetterConfig": {
      "Arn": "arn:aws:sqs:REGION:ACCOUNT:eventbridge-dlq"
    },
    "RetryPolicy": {
      "MaximumRetryAttempts": 2,
      "MaximumEventAge": 3600
    }
  }
]
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|------|------|-----|
| Rule not triggering | Missing permissions | Add `lambda:InvokeFunction` permission |
| Events ignored | Pattern mismatch | Check prefix/suffix and bucket name |
| Wrong schedule time | UTC confusion | Convert local time to UTC |
| Target fails | Missing IAM role | Add proper policy or DLQ |

---

**Pro Tip:** Always test event patterns with sample events using the EventBridge console before production.
