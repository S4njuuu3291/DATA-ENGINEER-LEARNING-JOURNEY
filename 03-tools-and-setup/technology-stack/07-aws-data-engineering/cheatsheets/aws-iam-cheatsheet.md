# AWS IAM Cheatsheet

Quick reference for IAM operations and policy templates

---

## AWS CLI Commands

### User Management

```bash
# Create user
aws iam create-user --user-name john_doe

# Create access key
aws iam create-access-key --user-name john_doe

# Delete access key
aws iam delete-access-key \
  --user-name john_doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Create login profile (console access)
aws iam create-login-profile \
  --user-name john_doe \
  --password InitialPassword123!

# List users
aws iam list-users

# Delete user (must remove all policies first)
aws iam delete-user --user-name john_doe
```

### Group Management

```bash
# Create group
aws iam create-group --group-name DataEngineers

# Add user to group
aws iam add-user-to-group \
  --group-name DataEngineers \
  --user-name john_doe

# List group members
aws iam get-group --group-name DataEngineers

# Remove user from group
aws iam remove-user-from-group \
  --group-name DataEngineers \
  --user-name john_doe

# Delete group
aws iam delete-group --group-name DataEngineers
```

### Role Management

```bash
# Create role
aws iam create-role \
  --role-name GlueJobRole \
  --assume-role-policy-document file://trust-policy.json

# List roles
aws iam list-roles

# Get role
aws iam get-role --role-name GlueJobRole

# Delete role (must remove policies first)
aws iam delete-role --role-name GlueJobRole

# Attach policy to role
aws iam attach-role-policy \
  --role-name GlueJobRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Assume role (get temporary credentials)
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT:role/GlueJobRole \
  --role-session-name my-session
```

### Policy Management

```bash
# Create policy
aws iam create-policy \
  --policy-name MyS3Policy \
  --policy-document file://policy.json

# Attach policy to user
aws iam attach-user-policy \
  --user-name john_doe \
  --policy-arn arn:aws:iam::ACCOUNT:policy/MyS3Policy

# Attach policy to group
aws iam attach-group-policy \
  --group-name DataEngineers \
  --policy-arn arn:aws:iam::ACCOUNT:policy/MyS3Policy

# Inline policy to user
aws iam put-user-policy \
  --user-name john_doe \
  --policy-name InlinePolicy \
  --policy-document file://inline-policy.json

# List attached policies
aws iam list-attached-user-policies --user-name john_doe

# Get policy
aws iam get-user-policy --user-name john_doe --policy-name PolicyName

# Delete policy
aws iam delete-policy --policy-arn arn:aws:iam::ACCOUNT:policy/MyPolicy
```

### MFA

```bash
# Enable MFA on user
aws iam enable-mfa-device \
  --user-name john_doe \
  --serial-number arn:aws:iam::ACCOUNT:mfa/john_doe \
  --authentication-code1 123456 \
  --authentication-code2 654321

# Deactivate MFA
aws iam deactivate-mfa-device \
  --user-name john_doe \
  --serial-number arn:aws:iam::ACCOUNT:mfa/john_doe
```

---

## Policy Templates

### S3 Read-Only

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    },
    {
      "Sid": "GetObject",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

### S3 Read + Write Silver

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadBronzeSilver",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::data-lake/bronze/*",
        "arn:aws:s3:::data-lake/silver/*",
        "arn:aws:s3:::data-lake"
      ]
    },
    {
      "Sid": "WriteSilver",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::data-lake/silver/*"
    },
    {
      "Sid": "NoDelete",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "*"
    }
  ]
}
```

### Glue Job Execution Role Trust

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Lambda Execution Role Trust

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

### Cross-Account Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::CONTRACTOR-ACCOUNT:user/analyst"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-contractor-id"
        }
      }
    }
  ]
}
```

### Glue Job Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::data-lake/*"
    },
    {
      "Sid": "GlueCatalogAccess",
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:UpdatePartition",
        "glue:BatchCreatePartition"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### MFA Required for Delete

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDeleteWithMFA",
      "Effect": "Allow",
      "Action": "s3:DeleteObject",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    },
    {
      "Sid": "DenyDeleteWithoutMFA",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

---

## Policy Analysis

### ARN Format

```
arn:aws:service:region:account:resource-type/resource-name

Examples:
arn:aws:s3:::my-bucket                    (bucket)
arn:aws:s3:::my-bucket/*                  (all objects)
arn:aws:s3:::my-bucket/folder/*           (folder)
arn:aws:iam::123456789:user/john          (IAM user)
arn:aws:iam::123456789:role/GlueJob       (role)
arn:aws:iam::123456789:policy/MyPolicy    (policy)
```

### Common Actions

**S3:**
- `s3:GetObject` = Read
- `s3:PutObject` = Write
- `s3:DeleteObject` = Delete
- `s3:ListBucket` = List

**Glue:**
- `glue:CreateJob` = Create job
- `glue:StartJobRun` = Run job
- `glue:GetDatabase` = Access catalog
- `glue:UpdatePartition` = Update metadata

**Lambda:**
- `lambda:InvokeFunction` = Call function
- `lambda:CreateFunction` = Create function
- `lambda:UpdateFunctionCode` = Update code

**IAM:**
- `iam:CreateUser` = Create user
- `iam:AttachUserPolicy` = Assign policy
- `iam:ListUser` = List users

### Testing Policies

```bash
# Test if policy allows action
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789:user/john_doe \
  --action-names s3:DeleteObject \
  --resource-arns arn:aws:s3:::my-bucket/data.csv

# Look for "EvalDecision": "allowed" or "denied"
```

---

## Common Mistakes

❌ **Don't:**
- Use `"Action": "*"` (all permissions)
- Use `"Resource": "*"` (all resources)
- Share IAM user credentials (use roles instead)
- Keep access keys longer than 90 days
- Forget IAM policies (need both user policy + resource policy)

✅ **Do:**
- Specific actions (`s3:GetObject`)
- Specific resources (`arn:aws:s3:::bucket/prefix/*`)
- Use roles (temporary, auto-rotating)
- Rotate keys quarterly
- Test with IAM Policy Simulator

---

## Tagging for Access Control

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDevEnvironmentOnly",
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Environment": "dev"
        }
      }
    }
  ]
}
```

---

## Inline vs Managed Policies

| Type | Use Case | Limit |
|------|----------|-------|
| **Inline** | One-off specific permissions | Up to 2.5 KB |
| **Managed** | Reusable across users/roles | Up to 10 KB |
| **AWS Managed** | AWS-provided policies | Pre-built, read-only |

---

**Pro Tips:**
- 🔐 Always require MFA for sensitive operations
- 📋 Document policy changes (why + when)
- 🔄 Rotate keys every 90 days
- 📊 Monitor activity (CloudTrail)
- ✅ Use principle of least privilege (minimum permissions)
- 🧪 Test policies before production deployment

