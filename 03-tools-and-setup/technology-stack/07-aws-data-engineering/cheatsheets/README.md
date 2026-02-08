# Module 1-2 Cheatsheets

Quick reference guides for AWS Foundation and Serverless automation services.

---

## Available Cheatsheets

### 1. [S3 Cheatsheet](aws-s3-cheatsheet.md)
**Topic:** Simple Storage Service (S3)  
**Use for:**
- Upload/download files (AWS CLI, Boto3)
- Lifecycle policies (transition to IA, Glacier)
- Bucket policies and access control
- Storage class selection (cost optimization)
- Troubleshooting common S3 errors

**When to use:** Working on S3 exercises (1-5), medallion architecture setup, data lake operations.

---

### 2. [IAM Cheatsheet](aws-iam-cheatsheet.md)
**Topic:** Identity & Access Management (IAM)  
**Use for:**
- Create users, groups, roles (AWS CLI)
- Write IAM policy JSON (templates included)
- Least Privilege implementation
- Cross-account access setup
- MFA configuration

**When to use:** Working on IAM exercises (6-9), security configuration, policy debugging.

---

### 3. [VPC Cheatsheet](aws-vpc-cheatsheet.md)
**Topic:** Virtual Private Cloud (VPC)  
**Use for:**
- Create VPC, subnets, route tables
- Security group configuration
- NAT Gateway setup (private subnet internet)
- S3 VPC endpoints (cost savings)
- Network debugging (Flow Logs)

**When to use:** Working on VPC exercises (10-14), network architecture, troubleshooting connectivity.

---

### 4. [Lambda Cheatsheet](aws-lambda-cheatsheet.md)
**Topic:** AWS Lambda  
**Use for:**
- Create/update Lambda functions (AWS CLI)
- Invoke functions and debug with CloudWatch Logs
- Lambda Layers (pandas, pyarrow)
- Error handling (DLQ) and alarms

**When to use:** Working on Module 2 Lambda exercises (1-4), serverless ETL.

---

### 5. [EventBridge Cheatsheet](aws-eventbridge-cheatsheet.md)
**Topic:** Amazon EventBridge  
**Use for:**
- Schedule rules (cron/rate)
- Event patterns (prefix/suffix filters)
- Fan-out targets
- DLQ for failed targets

**When to use:** Working on Module 2 EventBridge exercises (5-8), event-driven pipelines.

---

## Quick Decision Guide

**Need to:**
- ✅ **Upload data to cloud?** → [S3 Cheatsheet](aws-s3-cheatsheet.md)
- ✅ **Control who accesses what?** → [IAM Cheatsheet](aws-iam-cheatsheet.md)
- ✅ **Secure network for data pipeline?** → [VPC Cheatsheet](aws-vpc-cheatsheet.md)
- ✅ **Automate data processing?** → [Lambda Cheatsheet](aws-lambda-cheatsheet.md)
- ✅ **Schedule or route events?** → [EventBridge Cheatsheet](aws-eventbridge-cheatsheet.md)

---

## Usage Tips

**During Theory:**
- Keep cheatsheet open while reading theory files
- Cross-reference commands mentioned in examples
- Try commands in AWS CLI as you read

**During Exercises:**
- Use cheatsheet for syntax lookup (don't memorize)
- Check "Common Issues" sections if stuck
- Refer to templates for policy/JSON structure

**After Module:**
- Keep cheatsheets for later reference
- Customize templates for your projects
- Add your own pro tips/lessons learned

---

## Cheatsheet Structure

Each cheatsheet follows this format:

1. **Commands Section**
   - AWS CLI commands with examples
   - Boto3 code snippets (where applicable)
   - Real-world usage scenarios

2. **Templates Section**
   - JSON templates (policies, configurations)
   - Copy-paste ready code
   - Annotated with explanations

3. **Reference Tables**
   - Quick lookup information
   - Cost comparisons
   - Decision matrices

4. **Common Issues**
   - Error messages you'll encounter
   - Solutions and debugging steps
   - Pro tips from experts

---

**Print-Friendly Format:**
All cheatsheets are plain Markdown—can be printed, saved as PDF, or opened in multiple tabs.

---

**Next:** Choose a cheatsheet based on which exercise you're working on, or browse all of them to get familiar with AWS syntax!

