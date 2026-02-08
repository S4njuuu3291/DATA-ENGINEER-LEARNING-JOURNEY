# 03. S3 VPC Integration & VPC Endpoints

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** VPC endpoints let private resources access S3 without internet

---

## The Problem: Private Access to S3

### Scenario

Lambda in private subnet needs to read S3:

```
WITHOUT VPC Endpoint:
Lambda (10.0.2.10) → needs S3
  ↓
No internet route (private subnet)
  ↓
Request fails (can't reach S3)
  ↓
ERROR: Unable to access S3

Solution: Add NAT gateway outbound? No!
-Too expensive ($0.045/hour + $0.045/GB)
- Slow (goes through internet)
- Unnecessary exposure
```

### Solution: S3 VPC Endpoint

```
WITH VPC Endpoint:
Lambda (10.0.2.10) → S3 VPC Endpoint (in VPC)
  ↓  (private AWS network)
  ↓
S3 Bucket (accessed privately)
  ↓
Response back to Lambda

Benefits:
✅ Private (never leaves AWS network)
✅ Free (no data egress charges)
✅ Fast (direct connection, low latency)
✅ Secure (no internet exposure)
```

---

## VPC Endpoint Types

### Gateway Endpoint (S3 & DynamoDB)

```
Characteristics:
- Free
- Automatic routing (no NAT needed)
- High performance
- Best for: S3, DynamoDB

How it works:
- Create: aws ec2 create-vpc-endpoint --vpc-endpoint-type Gateway
- It automatically adds route: "S3 traffic → VPC endpoint"
- Resources automatically use it
```

### Interface Endpoint (Other AWSServices)

```
Characteristics:
- Creates ENI (network interface) in VPC
- Accessed via private IP
- Works for: Athena, Glue, Secrets Manager, etc.
- Cost: $7/month per endpoint

When to use:
- Services without gateway endpoint (most AWS services)
- Need private access to service
```

---

## Creating S3 VPC Endpoint

### Step 1: Create Endpoint

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-12345678 rtb-87654321

# Returns:
# {
#   "VpcEndpoint": {
#     "VpcEndpointId": "vpce-12345678",
#     "State": "available",
#     "ServiceName": "com.amazonaws.us-east-1.s3"
#   }
# }
```

### Step 2: Verify Endpoint Policy (Optional)

```bash
# Default policy: All S3 actions allowed
# Can restrict to specific buckets/actions

aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-12345678 \
  --policy-document file://s3-endpoint-policy.json
```

### Example Endpoint Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::data-lake/*"
    }
  ]
}
```

**Meaning:** Only allow GetObject on data-lake bucket

---

## Cost Comparison: Internet vs VPC Endpoint

### Scenario: Glue Job Processes 100TB S3 Data/Month

**Using Internet (NAT Gateway):**
```
Egress charges: 100 TB × $0.02/GB = 100,000 GB × $0.02 = $2,000/month
NAT Gateway: $0.045/hour × 730 hours = $32.85/month
Total: ~$2,050/month
```

**Using VPC Endpoint:**
```
Data transfer: $0 (free within AWS network)
VPC Endpoint: $0 (gateway endpoint is free)
Total: $0/month

Savings: $2,050/month (entire cost eliminated!)
```

---

## Endpoint Policy vs IAM Policy

### IAM Policy (User-level)

```
WHO can do what:
"John can access S3"
```

### Endpoint Policy (Endpoint-level)

```
WHAT requests are allowed through endpoint:
"Only GetObject actions allowed through endpoint"
```

### Both Must Allow

```
Lambda role has: s3:*
Endpoint policy has: s3:GetObject only

Result:
- GetObject: ✅ Allowed (both allow)
- DeleteObject: ❌ Denied (endpoint policy doesn't allow)
- PutObject: ❌ Denied (endpoint policy doesn't allow)
```

---

## Architecture: Data Pipeline via VPC Endpoint

```
Bronze S3
  ↓ (private endpoint)
Lambda
  ↓ (calls Glue)
Glue Job
  ↓ (private endpoint)
Silver S3
  ↓ (private endpoint)
Athena
  ↓ (via Lambda, private)
Gold S3

All data movement: Private (via VPC endpoints)
Cost: Minimal ($0 for S3 transfers)
Security: Maximum (no internet exposure)
```

---

## Common Issues & Solutions

### Issue 1: Endpoint Not Routing Traffic

**Symptom:** Lambda still can't access S3

**Solution:**
```bash
# Check route table has endpoint route
aws ec2 describe-route-tables --route-table-ids rtb-12345678

# Should show:
# "Destination": "pl-12345678" (prefix list for S3)
# "Target": "vpce-12345678"

# If not: Endpoint not attached to route table
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-12345678 \
  --add-route-table-ids rtb-12345678
```

### Issue 2: Access Denied Through Endpoint

**Symptom:** GetObject works normally, fails through endpoint

**Cause:** Endpoint policy is too restrictive

**Solution:**
```bash
# Check endpoint policy
aws ec2 describe-vpc-endpoints --vpc-endpoint-ids vpce-12345678

# Modify policy to allow action
aws ec2 modify-vpc-endpoint \
  --vpc-endpoint-id vpce-12345678 \
  --policy-document file://permissive-policy.json
```

---

## Best Practices

- [ ] Use Gateway endpoints for S3 (free, automatic)
- [ ] Restrict endpoint policy (minimum permissions)
- [ ] Verify route table associations
- [ ] Test from private resource (Lambda, EC2)
- [ ] Monitor endpoint usage (CloudWatch metrics)
- [ ] Document endpoint configuration (why it exists)

---

## Key Takeaways

1. **VPC Endpoint** = Private access to AWS services
2. **Gateway Endpoint** = Free for S3/DynamoDB
3. **No internet needed** = Data stays in AWS network
4. **Cost savings** = Eliminate egress charges
5. **Security** = No exposure to internet threats

---

## Next Up

**→ [04-network-security-patterns.md](./04-network-security-patterns.md)** covers security groups and firewalling

