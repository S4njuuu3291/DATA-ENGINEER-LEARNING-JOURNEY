# 03. IAM Policy JSON: The Complete Guide

> **Duration:** 75 minutes  
> **Difficulty:** ⭐⭐⭐ (Advanced)  
> **Key Takeaway:** Policies follow a JSON structure: Effect → Action → Resource → Condition

---

## Policy Anatomy

Every IAM policy has this structure:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow" | "Deny",
      "Action": "aws-service:action",
      "Resource": "arn:aws:service:region:account:resource",
      "Condition": {
        "condition-operator": {
          "condition-key": "value"
        }
      }
    }
  ]
}
```

---

## 1. Effect (Allow or Deny?)

**Effect** = Is this action allowed or denied?

```json
{
  "Effect": "Allow"    ← Permission granted
}

{
  "Effect": "Deny"     ← Permission explicitly denied (overrides Allow)
}
```

**Logic:**
- Default = Deny (implicit deny)
- "Allow" statement = grant permission
- "Deny" statement = explicitly block (even if other policies allow)

**Example:**
```json
Statement 1: "Allow s3:GetObject"
Statement 2: "Deny s3:DeleteObject"

Result:
- GetObject: ✅ Allowed
- DeleteObject: ❌ Explicitly denied
```

---

## 2. Action (What Operations?)

**Action** = Which API operations are permitted?

```
Format: "service:operation"

Examples:
- s3:GetObject          ← Read S3 object
- s3:PutObject          ← Write S3 object
- s3:DeleteObject       ← Delete S3 object
- glue:CreateJob        ← Create Glue job
- glue:StartJobRun      ← Run existing Glue job
- iam:CreateUser        ← Create IAM user
- athena:StartQueryExecution ← Run Athena query
```

**Wildcards:**
```json
"Action": "s3:*"           ← All S3 actions
"Action": "s3:Get*"        ← All S3 GET actions
"Action": "*"              ← All AWS actions (dangerous!)
```

**Multiple actions:**
```json
"Action": [
  "s3:GetObject",
  "s3:ListBucket",
  "s3:PutObject"
]
```

---

## 3. Resource (On What?)

**Resource** = Which AWS resources can the action affect?

```
Format: Amazon Resource Name (ARN)
Standard: arn:partition:service:region:account:resource-type/resource-name
```

### ARN Examples

```
S3 Bucket:
arn:aws:s3:::my-bucket

S3 Object:
arn:aws:s3:::my-bucket/path/to/file.csv

S3 Prefix (all files in folder):
arn:aws:s3:::my-bucket/processed/*

Glue Job:
arn:aws:glue:us-east-1:123456789:job/my-etl-job

IAM User:
arn:aws:iam::123456789:user/john_data_engineer

EC2 Instance:
arn:aws:ec2:us-east-1:123456789:instance/i-1234567890abcdef0
```

### Resource Wildcards

```json
{
  "Resource": [
    "arn:aws:s3:::my-bucket",
    "arn:aws:s3:::my-bucket/*"
  ]
}
// All objects in my-bucket

{
  "Resource": "arn:aws:s3:::my-bucket/bronze/*"
}
// Only objects in /bronze/ prefix

{
  "Resource": "*"
}
// All resources (dangerous - avoid!)
```

---

## 4. Condition (When/Where?)

**Condition** = Additional restrictions (optional)

```
Operators: StringEquals, StringLike, IpAddress, DateGreaterThan, etc.
Keys: aws:SourceIp, aws:CurrentTime, aws:username, s3:prefix, etc.
```

### Common Conditions

**IP Address Restriction:**
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*",
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": "203.0.113.0/24"
    }
  }
}
// Only allow from corporate network
```

**Time-Based Access:**
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*",
  "Condition": {
    "DateGreaterThan": {
      "aws:CurrentTime": "2024-02-08T00:00:00Z"
    },
    "DateLessThan": {
      "aws:CurrentTime": "2024-05-08T00:00:00Z"
    }
  }
}
// Only allow from Feb 8 to May 8
```

**Username-Based:**
```json
{
  "Effect": "Allow",
  "Action": "ec2:TerminateInstances",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:username": "john_data_engineer"
    }
  }
}
// Only john_data_engineer can terminate instances
```

---

## Real-World Policy Examples

### Example 1: Junior Data Engineer (Read-Only)

**Requirement:** Junior engineer can read bronze/silver data, cannot delete

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBuckets",
      "Effect": "Allow",
      "Action": "s3:ListAllMyBuckets",
      "Resource": "*"
    },
    {
      "Sid": "ListBronzeAndSilver",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": [
        "arn:aws:s3:::data-lake"
      ],
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "bronze/*",
            "silver/*"
          ]
        }
      }
    },
    {
      "Sid": "ReadBronzeAndSilver",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion"
      ],
      "Resource": [
        "arn:aws:s3:::data-lake/bronze/*",
        "arn:aws:s3:::data-lake/silver/*"
      ]
    }
  ]
}
```

### Example 2: Senior Data Engineer (Read/Write Development, Read-Only Production)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "FullAccessDevelopment",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::data-lake-dev",
        "arn:aws:s3:::data-lake-dev/*"
      ]
    },
    {
      "Sid": "ReadOnlyProduction",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::data-lake-prod",
        "arn:aws:s3:::data-lake-prod/*"
      ]
    },
    {
      "Sid": "GlueJobManagement",
      "Effect": "Allow",
      "Action": [
        "glue:CreateJob",
        "glue:UpdateJob",
        "glue:GetJob",
        "glue:ListJobs",
        "glue:StartJobRun",
        "glue:GetJobRun"
      ],
      "Resource": "arn:aws:glue:us-east-1:123456789:job/*"
    }
  ]
}
```

### Example 3: Contractor (Temporary, Limited Access)

**Requirements:**
- 90-day temporary access
- Read-only specific bucket
- Expires after date

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TimeLimitedAnalysisAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::analysis-bucket",
        "arn:aws:s3:::analysis-bucket/project-xyz/*"
      ],
      "Condition": {
        "DateLessThan": {
          "aws:CurrentTime": "2024-05-08T23:59:59Z"
        }
      }
    }
  ]
}
```

### Example 4: Lambda Function (Service Role)

**Requirements:** Lambda reads S3, writes Processing.logs, calls SNS on errors

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadS3Input",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::input-bucket/*"
    },
    {
      "Sid": "WriteProcessingLogs",
      "Effect": "Allow",
      "Action": "logs:CreateLogGroup,logs:CreateLogStream,logs:PutLogEvents",
      "Resource": "arn:aws:logs:us-east-1:123456789:log-group:/aws/lambda/*"
    },
    {
      "Sid": "SNSNotification",
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789:error-topic"
    }
  ]
}
```

---

## Policy Evaluation Logic

**How does AWS decide to Allow or Deny?**

```
1. Default: DENY (implicit deny - block everything)
                     ↓
2. Any DENY statement? → DENY (Deny overrides everything)
                     ↓
3. Any ALLOW statement matching? → ALLOW
                     ↓
4. No ALLOW found → DENY

Example:
User tries: s3:GetObject on bucket

Check all policies:
- Policy 1: "Allow s3:GetObject on /bronze/*" ✅ Matches
- Policy 2: "Deny s3:GetObject on /secret/*" (doesn't match resource)
- No other policies

Result: ✅ ALLOW (matched Allow, no Deny)
```

---

## Common Mistakes

### ❌ Mistake 1: Overly Broad Wildcard

```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

**Problem:** User can delete ANY S3 bucket (too permissive)

**Fix:**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket"],
  "Resource": [
    "arn:aws:s3:::my-bucket",
    "arn:aws:s3:::my-bucket/*"
  ]
}
```

### ❌ Mistake 2: Missing Bucket + Objects

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-bucket/*"
}
// Missing: Can't LIST bucket (s3:ListBucket)
```

**Fix:**
```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket"],
  "Resource": [
    "arn:aws:s3:::my-bucket",      ← Bucket itself
    "arn:aws:s3:::my-bucket/*"     ← Objects in bucket
  ]
}
```

### ❌ Mistake 3: Condition Typo

```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*",
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": "203.0.113.0/24"
    }
  }
}
// Typo: "aws:SourceIP" instead of "aws:SourceIp"
// Result: Condition ignored, access always allowed
```

---

## Best Practices

- [ ] Use specific resources (not `*`)
- [ ] Use specific actions (not `*`)
- [ ] Include bucket + object in S3 policies
- [ ] Use conditions for sensitive operations (IP, date, MFA)
- [ ] Test policy before applying (use Policy Simulator)
- [ ] Document Sid (Statement ID) for clarity
- [ ] Review quarterly (remove unused permissions)

---

## AWS Policy Simulator (Testing)

```bash
# Test if policy allows action
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789:user/john \
  --action-names s3:DeleteObject \
  --resource-arns arn:aws:s3:::my-bucket/sensitive/data.csv

# Response:
# {
#   "EvaluationResults": [
#     {
#       "EvalActionName": "s3:DeleteObject",
#       "EvalResourceName": "arn:aws:s3:::my-bucket/sensitive/data.csv",
#       "EvalDecision": "implicitDeny"
#       ← User CANNOT delete (implicit deny)
#     }
#   ]
# }
```

---

## Key Takeaways

1. **JSON structure matters** ← Must follow format
2. **Effect** = Allow or Deny
3. **Action** = Which operations (service:operation)
4. **Resource** = Which resources (ARN format)
5. **Condition** = Optional restrictions

---

## Next Up

**→ [04-iam-least-privilege.md](./04-iam-least-privilege.md)** covers enterprise patterns for least privilege

