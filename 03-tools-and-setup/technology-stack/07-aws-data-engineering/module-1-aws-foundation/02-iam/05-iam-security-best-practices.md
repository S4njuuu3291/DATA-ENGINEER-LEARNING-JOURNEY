# 05. IAM Security Best Practices

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** MFA, key rotation, and audit trails are your security net

---

## 1. MFA (Multi-Factor Authentication)

### What is MFA?

Two factors required:
1. Something you know (password)
2. Something you have (phone, hardware key)

### MFA Devices

**Authenticator App** (Free):
- Google Authenticator
- Authy
- Microsoft Authenticator
- Time-based codes (6 digits, change every 30s)

**Hardware Tokens** ($20-100):
- Yubikey
- AWS Hardware key fob
- More secure (can't be hacked remotely)

### Requiring MFA for Sensitive Operations

```json
{
  "Sid": "AllowDeleteWithMFA",
  "Effect": "Allow",
  "Action": ["s3:DeleteObject", "iam:DeleteUser"],
  "Resource": "*",
  "Condition": {
    "Bool": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

### Enabling MFA

```bash
# Create virtual MFA device
aws iam enable-mfa-device \
  --user-name john_doe \
  --serial-number arn:aws:iam::123456789:mfa/john_doe \
  --authentication-code1 123456 \
  --authentication-code2 654321

# Now MFA is required for sensitive operations
```

---

## 2. Access Key Rotation

### Why Rotate?

```
Timeline: Access key created Jan 1
- Day 1-30: Key used normally (safe)
- Day 31-60: Key seen in logs, configs (compromised?)
- Day 61-90: Key might be stolen, used by hacker (critical!)
- Day 91+: Key should be disabled (rotation best practice)
```

### Rotation Process

```bash
# Step 1: Create new access key
aws iam create-access-key --user-name john_doe
# Returns: AccessKeyId + SecretAccessKey

# Step 2: Update all applications/configs with new key
# (scripts, CI/CD, Lambda environment variables, etc.)

# Step 3: Test that new key works
aws s3 ls

# Step 4: Delete old access key
aws iam delete-access-key \
  --user-name john_doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Result: Old key invalid, new key active
```

### Rotation Policy

```
Best Practice:
- Rotate every 90 days
- Maximum 2 active keys during transition
- Automate if possible (Secrets Manager auto-rotation)
- Track rotation date (CloudTrail logs)
```

---

## 3. CloudTrail (Audit Logging)

### What is CloudTrail?

AWS audit log: "Who did what, when, from where?"

```
Example entry:
{
  "eventTime": "2024-02-08T14:30:00Z",
  "eventName": "DeleteObject",
  "userName": "john_doe",
  "sourceIPAddress": "203.0.113.45",
  "resourceName": "arn:aws:s3:::data-lake/sensitive/customer.csv",
  "errorCode": null
}

Reveals:
- John deleted customer data
- At 14:30 UTC
- From IP 203.0.113.45
- No errors (action succeeded)
```

### Enabling CloudTrail

```bash
# Create S3 bucket for logs
aws s3 mb s3://audit-logs-bucket

# Start CloudTrail (logs all API calls)
aws cloudtrail start-logging \
  --name my-trail \
  --s3-bucket-name audit-logs-bucket

# CloudTrail now logs ALL AWS API calls
```

### Investigating Incidents

```bash
# Find who deleted something
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=arn:aws:s3:::data-lake/sensitive/data.csv \
  --max-results 10

# Response:
# {
#   "Events": [
#     {
#       "EventName": "DeleteObject",
#       "EventTime": "2024-02-08T14:30:00Z",
#       "Username": "attacker_account",
#       "SourceIPAddress": "192.168.1.100"
#     }
#   ]
# }

# Action: Revoke attacker's access immediately
```

---

## 4. Root Account Security

### Root Account Dangers

Root account = Complete AWS control (can't be limited by IAM)

❌ **Why not?**
- One stolen password = entire account compromised
- No way to delegate (can't share safely)
- No audit trail (CloudTrail has limited logging for root)

✅ **What to do:**
- Create root account during AWS signup (only step)
- Enable MFA immediately
- Never use for daily work
- Create IAM users/roles for everything else
- Store root password in vault (locked, offline)

### Root MFA Setup

```bash
# Attach MFA device to root
# (Must use AWS console, not CLI)

# Step 1: Sign-out of all IAM users
# Step 2: Sign in as ROOT (email + password)
# Step 3: Enable MFA on root account
# Step 4: Save backup codes (offline, secure location)

Result:
- Root now requires MFA
- Even if password stolen, attacker needs phone
```

---

## 5. Resource Tagging for Governance

### What are Tags?

Key-value pairs on AWS resources for organization/security

```
Example tags:
- Environment: prod | dev | test
- Owner: john_doe | sarah_engineer
- CostCenter: DataEngineering | Analytics
- Retention: 90days | 1year | 7years
```

### Using Tags for Access Control

```json
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
```

**Result:** User can only access dev resources (prod protected by tags)

### Enforcement

```bash
# Tag ALL resources on creation
aws s3api put-bucket-tagging \
  --bucket my-bucket \
  --tagging 'TagSet=[
    {Key=Environment,Value=prod},
    {Key=Owner,Value=john_doe},
    {Key=Retention,Value=1year}
  ]'

# Compliance: AWS Config can enforce tagging rules
```

---

## 6. Password Policies

### Enforcing Strong Passwords

```bash
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --expire-passwords \
  --max-password-age 90

# Result:
# - Passwords must be 14+ chars
# - Must include symbols, numbers, upper, lower
# - Auto-expire every 90 days
# - Users can change own password
```

---

## 7. Permission Boundaries

### What are Permission Boundaries?

Maximum permissions an IAM user/role can have (even if policy allows more)

```
Example:
Policy says: "Allow s3:*" (all S3 permissions)
But Boundary says: "Allow only s3:Get*" (read-only)

Result: User can only GET (read), not DELETE
```

### Use Case: Delegating Admin Powers Safely

```
Scenario:
- Team lead Sarah needs to grant permissions to team
- But shouldn't be able to create admin users
- Solution: Permission boundary

Sarah's permissions:
- Can: Create users, attach policies
- But: Only within boundary
- Boundary: "Maximum s3:*, glue:*, athena:* (no IAM)"

Result:
- Sarah can help team
- Cannot create super-admin users
- Team lead empowerment without risk
```

---

## 8. Monitoring & Alerting

### CloudWatch Alarms for Suspicious Activity

```bash
# Alert if root account used
aws cloudwatch put-metric-alarm \
  --alarm-name "RootAccountUsage" \
  --alarm-description "Alert if root account used" \
  --metric-name RootAccountUsage

# Alert if access key created
aws cloudwatch put-metric-alarm \
  --alarm-name "UnauthorizedAPICallsAttempts" \
  --alarm-description "Alert on suspicious API calls"

# Alert if policies modified
aws cloudwatch put-metric-alarm \
  --alarm-name "IAMPolicyChanges" \
  --alarm-description "Alert on IAM changes"
```

### AWS Security Hub (Centralized Monitoring)

Aggregates findings from:
- CloudTrail (API logging)
- Config (compliance)
- GuardDuty (threat detection)
- IAM Access Analyzer (overpermissive policies)

---

## 9. Access Analyzer (Finding Overpermissive Policies)

### What It Does

Scans all IAM policies, identifies risks

```bash
aws accessanalyzer validate-policy \
  --policy-document file://policy.json \
  --policy-type IDENTITY_POLICY

# Returns:
# {
#   "findings": [
#     {
#       "message": "s3:* is overly permissive",
#       "locations": [{"path": [0, "Action"]}]
#     }
#   ]
# }
```

**Finding:** Policy too permissive → recommendations to reduce scope

---

## Security Checklist

- [ ] **Root account:** MFA enabled IMMEDIATELY after signup
- [ ] **Root account:** Strong password, stored offline
- [ ] **All IAM users:** MFA enabled (especially admins)
- [ ] **Access keys:** Rotate every 90 days
- [ ] **CloudTrail:** Enabled on all regions, logs to secure S3
- [ ] **Least privilege:** All policies reviewed quarterly
- [ ] **Tags:** All resources tagged (Environment, Owner, Retention)
- [ ] **Password policy:** Enforced (14+ chars, rotate 90 days)
- [ ] **Monitoring:** CloudWatch alarms for root/IAM changes
- [ ] **Access Analyzer:** Scan policies quarterly

---

## Cost of Security

```
Effort: ~4 hours setup + 1 hour/month maintenance
Cost: $0 (CloudTrail $2/month)
Benefit: Prevent $1M+ breaches

ROI: Infinite (prevention beats recovery)
```

---

## Key Takeaways

1. **MFA** = Prevent password-only compromise
2. **Rotation** = Limit damage window if key stolen
3. **CloudTrail** = Audit trail (who/what/when/where)
4. **Root protection** = Account-level security
5. **Monitoring** = Early detection of anomalies

---

**Final Checklist Before Moving to Next Module:**

- [ ] All IAM files read (01-05)
- [ ] CLI commands understood (not memorized)
- [ ] Policy JSON structure clear
- [ ] Least privilege concept internalized
- [ ] Ready for VPC & networking

---

## Next: VPC & Networking

**→ [03-vpc/](../03-vpc/)** covers private networks and S3 VPC endpoints

