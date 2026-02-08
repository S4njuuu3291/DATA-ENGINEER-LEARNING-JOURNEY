# 03. S3 Security: Versioning, Locking & Encryption

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** Data protection requires three layers: versioning (recovery), locking (compliance), encryption (privacy)

---

## The Problem: Data Is Vulnerable

### Scenario: What Can Go Wrong?

**Day 1: Tuesday 2:30 PM**
```
Analytics team pulls weekly report from S3
Problem: Last week's report is missing!
Question: When did it disappear?
Answer: Someone overwrote it by accident
Damage: Report needed for client presentation in 2 hours
$$$ Lost: $40K client contract (they demand Tuesday reports)
```

**Day 2: Wednesday 10 AM**
```
Security audit discovers: S3 bucket is publicly accessible!
Problem: Customer PII (emails, phone numbers) exposed for 6 months
Damage: GDPR fine $7,000/day × 180 days = $1.26 million
$$$ Lost: Regulatory fine + reputational damage
```

**Day 3: Thursday 3 PM**
```
Suspicious activity detected: Employee A downloads 50GB customer data
Problem: Is this legitimate use or data theft?
Question: Can we see who did what?
Answer: Bucket logging disabled × 3 months = no audit trail
$$$ Lost: Can't investigate, assume data compromised
```

**This three-file covers how to prevent all three scenarios.**

---

## Layer 1: Versioning (Protection Against Accidental Deletion/Overwrite)

### What is Versioning?

S3 keeps multiple versions of an object. Accidentally delete something? Restore the previous version.

### How It Works

```
Without Versioning:
┌──────────────────┐
│ report.csv       │ ← Only one version
│ (Jan 15, 1.0)    │
└──────────────────┘
      ↓ (overwrite)
┌──────────────────┐
│ report.csv       │ ← Old version lost forever
│ (Jan 16, 2.0)    │
└──────────────────┘

With Versioning:
┌──────────────────┐   ┌──────────────────┐
│ report.csv       │   │ report.csv       │
│ v2: Jan 16, 2.0  │   │ v1: Jan 15, 1.0  │
│ (CURRENT)        │   │ (DELETE=hidden)  │
└──────────────────┘   └──────────────────┘
      ↓ (restore)
┌──────────────────┐   ┌──────────────────┐
│ report.csv       │   │ report.csv       │
│ v1: Jan 15, 1.0  │   │ v2: Jan 16, 2.0  │
│ (CURRENT)        │   │ (DELETE=hidden)  │
└──────────────────┘   └──────────────────┘
```

### Enabling Versioning

**AWS CLI:**
```bash
aws s3api put-bucket-versioning \
  --bucket my-data-lake \
  --versioning-configuration Status=Enabled
```

**Cost Impact:**
- Each version stored = costs storage
- Example: 10 GB file, 12 versions = 120 GB storage cost
- Mitigation: Lifecycle policy to delete old versions

### Use Case: Data Recovery

**Scenario: Malicious SQL injection overwrites customer database backup**

```
Monday: Backup created (10 GB)
Tuesday: Backup overwritten by bad SQL query (0.1 GB of garbage)
Wednesday: Discover issue, restore from version 1

Result: Lost 1 day of transactions, but NOT entire year of data
```

### Limitations⚠️

- Versioning can't protect against accidental BUCKET deletion
- Versioning doesn't prevent unauthorized deletes (IAM or bucket policy can still allow DeleteObject)
- Storage cost increases with versions (need lifecycle policy)

---

## Layer 2: Object Locking (Protection Against Intentional Deletion)

### What is Object Locking (WORM)?

**WORM = Write Once, Read Many** - Once uploaded, object can't be modified or deleted until retention expires.

### How It Works

```
Without Lock:
┌──────────────┐
│ order.json   │ ← Can be deleted anytime
│ (v1)         │
└──────────────┘
      ↓ (DELETE)
Object deleted (GONE)

With Lock (365-day retention):
┌──────────────────────────────┐
│ order.json                   │
│ Locked until: Jan 15, 2026   │ ← Even root user can't delete
│ (v1)                         │
└──────────────────────────────┘
      ↓ (DELETE attempt)
ERROR: Retention applies (365 days remaining)
Object remains
```

### Two Modes of Object Locking

**Governance Mode:**
- Can be overridden by user with special permission: `s3:BypassGovernanceRetention`
- Flexibility: Admin can delete if needed
- Use: Data governance (policy-enforced but flexible)

**Compliance Mode:**
- CANNOT be overridden (even root user can't disable)
- Immutable: Locked for full retention period
- Use: Regulatory compliance (HIPAA, SOC2, financial records)

### Real Scenario: Healthcare Compliance

```
HIPAA requirement: Medical records must be retained 6 years (2192 days)

Solution: Enable Object Locking (Compliance Mode)
- Mode: Compliance (can't override)
- Retention: 2192 days
- Applies to: All records uploaded

Result:
- Even if hacker deletes bucket → Object locks prevent deletion
- Even if administrator resigns → Records can't be deleted early
- Company passes compliance audit ✅
```

### Enabling Object Locking

⚠️ **Must enable at BUCKET CREATION** (can't add later)

```bash
# Create bucket WITH object locking enabled
aws s3api create-bucket \
  --bucket my-compliance-bucket \
  --object-lock-enabled-for-bucket \
  --region us-east-1

# Apply retention to object (365 days)
aws s3api put-object-retention \
  --bucket my-compliance-bucket \
  --key sensitive-data.csv \
  --retention Mode=COMPLIANCE,RetainUntilDate=2026-02-08T00:00:00Z
```

---

## Layer 3: Encryption (Protection Against Unauthorized Reading)

### What is Encryption?

Data stored as unreadable scrambled text. Only those with decryption key can read.

```
Plaintext (readable):
customer_email@gmail.com, phone: 555-1234

Encrypted (unreadable):
a7f3k9X2mQ8nR5pL1vW0X8kJ6yH3dF2bM9nZ4qT1sU7xV6cM2...

Need decryption key to reverse → Original readable content
```

### Three Encryption Approaches

#### Approach 1: SSE-S3 (Server-Side Encryption with S3-Managed Keys)

**Simplest option - AWS manages everything**

```
How it works:
1. Upload file to S3
2. AWS automatically encrypts using AWS-managed key
3. AWS automatically decrypts when you download
4. You don't manage keys

Cost: Included in S3 (no extra charge)
Complexity: Zero (default)
Control: Low (AWS manages keys)
Compliance: Medium (for most needs)
```

**Use case: Non-sensitive business data**

```bash
# Enable SSE-S3 (default for new buckets)
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration \
  '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

**Pros:** Simple, automatic, no key management  
**Cons:** Low control, key rotation managed by AWS (quarterly)

#### Approach 2: SSE-KMS (Server-Side Encryption with Key Management Service)

**More control - You manage encryption keys in KMS**

```
How it works:
1. Upload file to S3
2. S3 asks KMS: "Encrypt this with customer's key"
3. KMS encrypts data, stores in S3
4. On download: S3 asks KMS to decrypt
5. You (or admin) control who can decrypt

Cost: $1 per 10,000 requests (+ standard S3)
Complexity: Medium (manage KMS keys & policies)
Control: High (you control key access)
Compliance: High (audit trail, key rotation)
```

**Real scenario: GDPR compliance**

```
Requirement: Europeans' data encrypted separately from Americans'
Solution:
- Create KMS key for Europe (EU region)
- Create KMS key for US (US region)
- Encrypt EU customer data with EU key
- Encrypt US customer data with US key
- EU compliance officers can only decrypt EU keys
- Result: Data localization + role-based decryption

Audit Trail:
- CloudTrail logs: "John decrypted EU customer data on Feb 8, 2:30 PM"
- Compliance: Complete visibility into who accessed what
```

**Use case: Sensitive customer data, regulated industries**

```bash
# Create KMS key
aws kms create-key --description "Customer data encryption"

# Enable SSE-KMS on bucket
aws s3api put-bucket-encryption \
  --bucket my-sensitive-bucket \
  --server-side-encryption-configuration \
  '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789:key/12345678"
      }
    }]
  }'

# Upload file (automatically encrypted with KMS key)
aws s3 cp sensitive-data.csv s3://my-sensitive-bucket/
```

**Pros:** High control, audit trail, key rotation, role-based access  
**Cons:** Extra cost, more complex management

#### Approach 3: Client-Side Encryption (Encrypt Before Uploading)

**Maximum control - You encrypt before sending to AWS**

```
How it works:
1. On your computer, encrypt file with YOUR key
2. Upload encrypted file to S3
3. S3 stores encrypted blob (can't read it)
4. Download file, unencrypt on your computer
5. AWS never sees plaintext

Cost: Free (no AWS encryption fees)
Complexity: High (manage key, encryption library)
Control: Maximum (complete key control)
Compliance: Highest (AWS can't decrypt even if hacked)
```

**Use case: Top-secret data (government contracts, crypto keys)**

```python
# Python example with AWS Encryption SDK
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_kms as kms

# Encrypt locally before upload
client_side_encrypted_data = my_encryption_library.encrypt(
    plaintext_data,
    my_encryption_key
)

# Upload encrypted blob
s3.put_object(
    Bucket='my-bucket',
    Key='encrypted-secret.bin',
    Body=client_side_encrypted_data  # Already encrypted
)

# AWS can't decrypt even if breached (they don't have key)
```

**Pros:** Maximum security, AWS never sees plaintext  
**Cons:** You manage keys, encryption/decryption overhead

### Encryption Comparison Table

| Method | Cost | Control | Complexity | Compliance | Use Case |
|--------|------|---------|-----------|-----------|----------|
| **SSE-S3** | Free | Low | Minimal | Good | Public datasets, logs |
| **SSE-KMS** | $0.03/10k req | High | Medium | Excellent | Customer data, GDPR |
| **Client-Side** | Free | Maximum | High | Maximum | Secrets, crypto keys |
| **No Encryption** | Free | None | Minimal | Poor | ❌ Never use |

---

## Access Control: Who Can Read/Write?

### Default Behavior

```
When you create S3 bucket:
- PRIVATE by default ✅ (only AWS account owner can access)
- Requires IAM policy or bucket policy to grant access
- Requires S3 credentials (never public unless you explicitly allow)
```

### Blocking Public Access (Easiest)

```bash
# Prevent accidental public bucket exposure
aws s3api put-public-access-block \
  --bucket my-bucket \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

Result:
- Even if bucket policy says "public" → Still blocked
- Safety net against misconfiguration
```

### IAM Policies (Role-Based Access)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789:role/DataEngineer"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/processed/*"
      ]
    }
  ]
}
```

**Meaning:** DataEngineer role can read (`GetObject`) objects in `processed/` folder only

---

## Security Best Practices Checklist

- [ ] **Enable versioning** on all production buckets (recovery protection)
- [ ] **Enable Object Locking** for compliance data (immutability)
- [ ] **Enable encryption** (SSE-KMS for sensitive, SSE-S3 for others)
- [ ] **Block public access** (all 4 options enabled)
- [ ] **Enable logging** (who accessed what, when)
- [ ] **Enable MFA Delete** (require MFA to permanently delete)
- [ ] **Set lifecycle policy** (delete old versions, move to cheaper storage)
- [ ] **Use IAM policies** (principle of least privilege)

---

## Cost Impact Summary

| Feature | Monthly Cost (1000 GB) | Benefit |
|---------|---|---|
| Versioning (10 versions) | +10 GB storage × $0.023 = +$0.23 | Recovery protection |
| Object Locking | SKU per object (~$0.001 × objects) | Compliance immutability |
| SSE-S3 | Included | Encryption at rest |
| SSE-KMS | $0.03 per 10k requests | Key control + audit |
| Logging | ~10 GB/month = $0.23 | Audit trail |
| MFA Delete | Free | Extra deletion protection |

**Total: ~$0.50/month for all protections on 1000 GB = 0.05% overhead**

---

## Key Takeaways

1. **Versioning** = Recovery from accidents (user deleted file? Restore)
2. **Object Locking** = Compliance immutability (can't delete for 7 years)
3. **Encryption** = Privacy (choose S3-managed, KMS-managed, or client-side)
4. **Access Control** = Who can read/write (IAM policies + public access block)
5. **Logging** = Audit trail (who did what, when)

---

## Hands-On Intuition Check ✓

After reading, you should know:

- [ ] Why versioning doesn't prevent bucket deletion
- [ ] When Object Locking (WORM) is required
- [ ] Difference between SSE-S3 and SSE-KMS
- [ ] Why "no encryption" is never acceptable
- [ ] Cost-benefit of security features vs overhead

---

## Next Up

Ready to design your data lake architecture?

**→ [04-s3-medallion-architecture.md](./04-s3-medallion-architecture.md)** explains how to organize data for production pipelines

