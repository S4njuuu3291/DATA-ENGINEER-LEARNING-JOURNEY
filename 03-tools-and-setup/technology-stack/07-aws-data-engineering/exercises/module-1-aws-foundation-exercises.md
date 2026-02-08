# Module 1: AWS Foundation - Exercises

> **Total Exercises:** 14 (5 S3 + 5 IAM + 4 VPC)  
> **Estimated Time:** 5-6 hours  
> **Difficulty:** ⭐⭐ (All exercises)  
> **Requirements:** AWS account, AWS CLI configured, text editor

---

## Setup Checklist

Before starting exercises:

- [ ] AWS account created and active
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS credentials configured (`aws configure`)
- [ ] IAM user created (not using root)
- [ ] MFA enabled on IAM user
- [ ] Test credentials: `aws sts get-caller-identity`

---

## S3 EXERCISES

### Exercise 1: Create Bucket & Enable Versioning (15 min)

**Objective:** Create S3 bucket with versioning for data protection

**Steps:**
```bash
# 1. Create bucket with unique name (globally unique)
aws s3api create-bucket \
  --bucket my-data-lake-$(date +%s) \
  --region us-east-1

# 2. Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-data-lake-* \
  --versioning-configuration Status=Enabled

# 3. Upload test file
echo "test data v1" > test.txt
aws s3 cp test.txt s3://my-data-lake-*/test.txt

# 4. Overwrite file (creates new version)
echo "test data v2" > test.txt
aws s3 cp test.txt s3://my-data-lake-*/test.txt

# 5. List all versions
aws s3api list-object-versions \
  --bucket my-data-lake-*
```

**Deliverable:** Bucket with versioning enabled + 2 versions of test.txt

---

### Exercise 2: Storage Class Lifecycle Policy (20 min)

**Objective:** Implement storage class transitions for cost optimization

**Create policy file (lifecycle.json):**
```json
{
  "Rules": [
    {
      "Id": "TransitionOldData",
      "Filter": {"Prefix": ""},
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

**Apply policy:**
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-data-lake-* \
  --lifecycle-configuration file://lifecycle.json

# Verify
aws s3api get-bucket-lifecycle-configuration --bucket my-data-lake-*
```

**Deliverable:** Lifecycle policy applied (data auto-transitions to cheaper storage)

---

### Exercise 3: Bucket Policy & Public Access Block (15 min)

**Objective:** Secure bucket + prevent public exposure

**Create policy (bucket-policy.json):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-data-lake-*/*",
      "Condition": {
        "StringNotLike": {
          "aws:userid": "*:my-lambda-role"
        }
      }
    }
  ]
}
```

**Apply policy:**
```bash
aws s3api put-bucket-policy \
  --bucket my-data-lake-* \
  --policy file://bucket-policy.json

# Block all public access
aws s3api put-public-access-block \
  --bucket my-data-lake-* \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

**Deliverable:** Bucket is private + public access blocked

---

### Exercise 4: Medallion Folder Structure (20 min)

**Objective:** Create data lake folder structure (bronze/silver/gold)

**Create structure:**
```bash
# Create folders (prefixes)
aws s3api put-object --bucket my-data-lake-* --key bronze/
aws s3api put-object --bucket my-data-lake-* --key silver/
aws s3api put-object --bucket my-data-lake-* --key gold/

# Create source subfolders
aws s3api put-object --bucket my-data-lake-* --key bronze/ecommerce/2024-01-15/
aws s3api put-object --bucket my-data-lake-* --key bronze/api-logs/2024-01-15/

# Upload sample data
aws s3 cp orders.csv s3://my-data-lake-*/bronze/ecommerce/2024-01-15/orders.csv
aws s3 cp customers.csv s3://my-data-lake-*/bronze/ecommerce/2024-01-15/customers.csv

# Verify structure
aws s3 ls s3://my-data-lake-* --recursive
```

**Deliverable:** Bronze/Silver/Gold folders with sample data in bronze

---

### Exercise 5: Design Partitioning Scheme (20 min)

**Objective:** Plan S3 partitioning for analytics performance

**Create documentation (markdown):**
```
# Partitioning Strategy

Bronze Layer:
s3://lake/bronze/{source}/{year}/{month}/{day}/data.csv

Silver Layer:
s3://lake/silver/{entity}/year={YYYY}/month={MM}/day={DD}/data.parquet

Gold Layer:
s3://lake/gold/fact_{entity}/year={YYYY}/month={MM}/day={DD}/facts.parquet

Benefits:
- Bronze: Easy source identification, full history
- Silver: Hive-partitioned (Athena optimized)
- Gold: Optimized for analytical queries
- Cost: Query only partitions needed (scan less data)

Example Query:
SELECT * FROM gold_fact_orders 
WHERE year=2024 AND month=01 
→ Only scans gold/fact_orders/year=2024/month=01/ (fast!)
```

**Deliverable:** Documented partitioning strategy + example queries

---

## IAM EXERCISES

### Exercise 6: Create IAM User with S3 Policy (15 min)

**Objective:** Create data engineer user with limited S3 access

**Create user:**
```bash
# Create user
aws iam create-user --user-name john_data_engineer

# Create access key
aws iam create-access-key --user-name john_data_engineer

# Create policy (dataengineer-policy.json)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListDataLakeBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-data-lake-*"
    },
    {
      "Sid": "ReadBronzeSilver",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": [
        "arn:aws:s3:::my-data-lake-*/bronze/*",
        "arn:aws:s3:::my-data-lake-*/silver/*"
      ]
    },
    {
      "Sid": "WriteSilver",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-data-lake-*/silver/*"
    }
  ]
}

# Attach policy
aws iam put-user-policy \
  --user-name john_data_engineer \
  --policy-name S3DataEngineerPolicy \
  --policy-document file://dataengineer-policy.json

# Enable MFA
aws iam enable-mfa-device \
  --user-name john_data_engineer \
  --serial-number arn:aws:iam::ACCOUNT:mfa/john \
  --authentication-code1 123456 \
  --authentication-code2 654321
```

**Deliverable:** IAM user with S3 policy + MFA enabled

---

### Exercise 7:  Create Glue Job Execution Role (15 min)

**Objective:** Create role for Glue jobs with least privilege

**Create role:**
```bash
# Create trust policy (trust-policy.json)
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

# Create role
aws iam create-role \
  --role-name GlueJobExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# Create permission policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": [
        "arn:aws:s3:::my-data-lake-*/bronze/*",
        "arn:aws:s3:::my-data-lake-*/silver/*"
      ]
    },
    {
      "Sid": "GlueCatalogAccess",
      "Effect": "Allow",
      "Action": ["glue:GetDatabase", "glue:GetTable"],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": ["logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-east-1:*:log-group:/aws-glue/*"
    }
  ]
}

# Attach policy
aws iam put-role-policy \
  --role-name GlueJobExecutionRole \
  --policy-name GlueJobPolicy \
  --policy-document file://glue-policy.json
```

**Deliverable:** Glue execution role with minimal S3 + Glue permissions

---

### Exercise 8: Fix Overpermissive Policy (20 min)

**Objective:** Audit and reduce excessive permissions

**Given policy (overpermissive-policy.json):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

**Task:** Rewrite for junior data engineer

**Fixed policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadProcessedData",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::data-lake",
        "arn:aws:s3:::data-lake/processed/*"
      ]
    },
    {
      "Sid": "NoDeletePermission",
      "Effect": "Deny",
      "Action": ["s3:DeleteObject"],
      "Resource": "*"
    }
  ]
}
```

**Deliverable:** Corrected policy with least privilege justification

---

### Exercise 9: Cross-Account Role (20 min)

**Objective:** Create role for contractor to access your AWS

**Setup:**
```bash
# Contractor Account ID: 999888777666
# Your Account ID: 111222333444

# Create trust policy (allow contractor account)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::999888777666:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-contractor-id-12345"
        }
      }
    }
  ]
}

# Create role
aws iam create-role \
  --role-name ContractorAnalysisRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policy (read-only analysis data)
aws iam put-role-policy \
  --role-name ContractorAnalysisRole \
  --policy-name ContractorPolicy \
  --policy-document file://contractor-policy.json

# Output role ARN for contractor
aws iam get-role --role-name ContractorAnalysisRole --query Role.Arn
```

**Deliverable:** Cross-account role with temporary access capability

---

## VPC EXERCISES

### Exercise 10: Create VPC with Public/Private Subnets (20 min)

**Objective:** Build 3-tier VPC architecture

**Create VPC:**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create Internet Gateway
aws ec2 create-internet-gateway

# Attach gateway
aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-12345678 \
  --vpc-id vpc-12345678

# Public subnet  (us-east-1a)
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a

# Private subnet (us-east-1a)
aws ec2 create-subnet \
  --vpc-id vpc-12345678 \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1a

# Public route table
aws ec2 create-route-table --vpc-id vpc-12345678

# Add internet route
aws ec2 create-route \
  --route-table-id rtb-public \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-12345678

# Associate public route table
aws ec2 associate-route-table \
  --route-table-id rtb-public \
  --subnet-id subnet-public
```

**Deliverable:** VPC with public + private subnets, internet gateway

---

### Exercise 11: S3 VPC Endpoint Setup (15 min)

**Objective:** Create VPC endpoint for private S3 access

**Create endpoint:**
```bash
# Create S3 VPC endpoint (gateway type)
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-private-12345678

# Create endpoint policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-data-lake-*",
        "arn:aws:s3:::my-data-lake-*/*"
      ]
    }
  ]
}

# Apply policy
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-12345678 \
  --policy-document file://endpoint-policy.json

# Verify
aws ec2 describe-vpc-endpoints --vpc-endpoint-ids vpce-12345678
```

**Deliverable:** VPC endpoint for private S3 access + endpoint policy

---

### Exercise 12: Security Groups for Data Pipeline (15 min)

**Objective:** Configure layered security for Lambda → RDS

**Create security groups:**
```bash
# Lambda SG
aws ec2 create-security-group \
  --group-name lambda-sg \
  --description "Security group for Lambda" \
  --vpc-id vpc-12345678

# RDS SG
aws ec2 create-security-group \
  --group-name rds-sg \
  --description "Security group for RDS" \
  --vpc-id vpc-12345678

# Allow Lambda outbound to RDS
aws ec2 authorize-security-group-egress \
  --group-id sg-lambda \
  --protocol tcp \
  --port 5432 \
  --source-group-id sg-rds

# Allow RDS inbound from Lambda
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds \
  --protocol tcp \
  --port 5432 \
  --source-group-id sg-lambda

# Verify
aws ec2 describe-security-groups --group-ids sg-lambda sg-rds
```

**Deliverable:** Security groups with least privilege rules

---

### Exercise 13: Design Network Diagram (20 min)

**Objective:** Documentation of network architecture

**Create diagram description (text format):**
```
Data Pipeline Network Architecture

┌──────────────────────────────────────────┐
│  INTERNET                                │
│  Users (office)                          │
└──────────────────────────────────────────┘
         ↓ (port 443)
┌──────────────────────────────────────────┐
│  PUBLIC SUBNET (us-east-1a)              │
│  ┌──────────────────────────────────────┐│
│  │ Bastion Host                         ││
│  │ - SG: Allow SSH from 203.0.113.0/24  ││
│  └──────────────────────────────────────┘│
│  ┌──────────────────────────────────────┐│
│  │ NAT Gateway (for outbound)           ││
│  └──────────────────────────────────────┘│
└──────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────┐
│ PRIVATE SUBNET (us-east-1a)              │
│ ┌──────────────────────────────────────┐ │
│ │ Lambda                               │ │
│ │ - SG: Allow HTTPS outbound (443)     │ │
│ │ - SG: Allow to RDS (5432)            │ │
│ │ - Assumes: GlueJobRole               │ │
│ └──────────────────────────────────────┘ │
│ ┌──────────────────────────────────────┐ │
│ │ S3 (VPC endpoint)                    │ │
│ │ - Private routing via endpoint       │ │
│ │ - No internet exposed                │ │
│ └──────────────────────────────────────┘ │
│ ┌──────────────────────────────────────┐ │
│ │ RDS Database                         │ │
│ │ - SG: Allow MySQL (3306) from Lambda │ │
│ │ - Not internet accessible            │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘

Key Features:
- Multi-tier security (DMZ + private + data)
- Private S3 access (via VPC endpoint)
- RDS protected (security group rules)
- No direct internet for data services
```

**Deliverable:** Network architecture documentation with security analysis

---

### Exercise 14: Test Network Connectivity (20 min)

**Objective:** Verify network security posture

**Create verification checklist:**
```bash
# 1. Verify VPC routing
aws ec2 describe-route-tables \
  --filters Name=vpc-id,Values=vpc-12345678

# Confirm:
# - Public subnet has route to IGW (0.0.0.0/0 → igw-*)
# - Private subnet has route to NAT (0.0.0.0/0 → nat-*)
# - S3 prefix list route exists (vpce-* for S3)

# 2. Check security groups
aws ec2 describe-security-groups \
  --filters Name=vpc-id,Values=vpc-12345678

# Confirm:
# - Lambda SG: Outbound 443 ✅, Inbound NONE ✅
# - RDS SG: Inbound 3306 from Lambda ✅
# - Bastion SG: Inbound 22 from office only ✅

# 3. Verify VPC endpoint
aws ec2 describe-vpc-endpoints \
  --filters Name=vpc-id,Values=vpc-12345678

# Confirm:
# - Service: com.amazonaws.us-east-1.s3 ✅
# - State: available ✅
# - Route table associations: private subnet ✅

# Document findings
echo "✅ VPC properly secured
✅ Routing tables configured correctly
✅ Security groups follow least privilege
✅ S3 VPC endpoint active
" > network-audit.txt
```

**Deliverable:** Network audit report + verification checklist

---

## Submission Checklist

- [ ] All 14 exercises completed
- [ ] AWS resources created (buckets, users, IAM roles, VPC)
- [ ] Documentation written (policies, architecture diagrams)
- [ ] Recommendations documented (optimizations, improvements)
- [ ] All code snippets tested
- [ ] Resource cleanup performed (optional based on cost)

---

## Time Estimate Breakdown

| Section | Exercises | Total Time |
|---------|-----------|-----------|
| S3 | 1-5 | 90 minutes |
| IAM | 6-9 | 70 minutes |
| VPC | 10-14 | 90 minutes |
| **Total** | **14** | **250 minutes (4+ hours)** |

---

## Next Steps

After completing exercises:

1. **Review:** Go back to theory files for concepts you struggled with
2. **Optimize:** Reduce costs (lifecycle policies, storage classes)
3. **Monitor:** Enable CloudTrail logging + CloudWatch monitoring
4. **Document:** Keep architecture diagrams updated
5. **Prepare:** Move to Module 2 (AWS Lambda)

---

**Congratulations on completing Module 1 exercises!** 🎉

