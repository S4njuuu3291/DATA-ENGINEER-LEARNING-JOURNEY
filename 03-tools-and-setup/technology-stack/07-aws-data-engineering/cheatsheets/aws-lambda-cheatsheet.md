# AWS Lambda Cheatsheet

Quick reference for Lambda creation, deployment, and troubleshooting.

---

## AWS CLI Essentials

### Create & Update Function

```bash
# Create Lambda function
aws lambda create-function \
  --function-name csv-validator \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/lambda-exec-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip

# Update code
aws lambda update-function-code \
  --function-name csv-validator \
  --zip-file fileb://function.zip

# Update configuration
aws lambda update-function-configuration \
  --function-name csv-validator \
  --memory-size 1024 \
  --timeout 60
```

### Invoke Function

```bash
# Invoke Lambda with payload
aws lambda invoke \
  --function-name csv-validator \
  --payload file://event_s3.json \
  response.json

# Invoke with JSON string
aws lambda invoke \
  --function-name csv-validator \
  --payload '{"message":"hello"}' \
  response.json
```

### List & Inspect

```bash
# List functions
aws lambda list-functions

# Get function configuration
aws lambda get-function-configuration --function-name csv-validator

# Tail logs (last 10 minutes)
aws logs filter-log-events \
  --log-group-name /aws/lambda/csv-validator \
  --start-time $(( $(date +%s) * 1000 - 600000 ))
```

---

## Lambda Layers

```bash
# Publish layer
aws lambda publish-layer-version \
  --layer-name pandas-layer \
  --zip-file fileb://pandas-layer.zip \
  --compatible-runtimes python3.11

# Attach layer
aws lambda update-function-configuration \
  --function-name csv-validator \
  --layers arn:aws:lambda:REGION:ACCOUNT:layer:pandas-layer:1
```

---

## IAM Role Basics

### Trust Policy

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

### Execution Policy (S3 + Logs)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
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

---

## Common Event Payloads

### S3 Object Created

```json
{
  "detail": {
    "bucket": {"name": "data-lake"},
    "object": {"key": "bronze/orders/2024-01-15.csv"}
  }
}
```

### EventBridge Schedule

```json
{
  "source": "aws.events",
  "detail-type": "Scheduled Event",
  "time": "2024-01-15T02:00:00Z"
}
```

---

## Error Handling

### Attach DLQ (SQS)

```bash
aws lambda update-function-configuration \
  --function-name csv-validator \
  --dead-letter-config TargetArn=arn:aws:sqs:REGION:ACCOUNT:csv-validator-dlq
```

### CloudWatch Alarm

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-high-errors \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=csv-validator
```

---

## Performance Tuning

- **Memory = CPU**: Increase memory to reduce runtime.
- **Sweet spot for pandas**: 1024 MB (1 GB).
- **Timeout**: Set slightly above observed duration (ex: 60 sec for 40 sec job).
- **Cold starts**: Reduce package size, use layers, lazy imports.

---

## Common Errors & Fixes

| Error | Cause | Fix |
|------|------|-----|
| `Task timed out` | Timeout too low | Increase timeout or optimize code |
| `MemoryError` | File too large | Increase memory or use Glue |
| `AccessDenied` | Missing IAM permissions | Add S3/Logs actions |
| `ModuleNotFoundError: pandas` | No layer/package | Add pandas layer |
| `TooManyRequestsException` | Concurrency limit hit | Reserve concurrency |

---

**Pro Tip:** Keep Lambda packages small. Use layers for heavy dependencies (pandas, numpy).
