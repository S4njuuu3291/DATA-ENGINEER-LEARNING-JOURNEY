# 01. Why IAM Exists: The Security Foundation

> **Duration:** 45 minutes  
> **Difficulty:** ⭐ (Conceptual)  
> **Key Takeaway:** Without IAM, anybody with your AWS account can delete everything or steal your data

---

## The Problem: Who Gets Access to What?

### Scenario 1: The Disaster (2015, Real AWS Customer)

```
Company: CodeSpace (cloud development platform)
Problem: Attacker compromised AWS credentials
Result: Attacker accessed AWS account → deleted all customer databases
Damage: $10 million business destroyed in 30 minutes
Root cause: Root account credentials reused everywhere

What happened:
1. Hacker got access to root account password
2. Root account = complete control (delete anything)
3. Hacker deleted all databases (no backup)
4. Customer data destroyed
5. Company couldn't recover → bankruptcy

What should have happened:
- Root account should NEVER be used for daily work
- Data engineers should have DEV access (no DELETE)
- DBAs should have DELETE access (but not DELETE Glue jobs)
- CloudTrail should log all deletions
- MFA should protect root
- Backups should exist (cross-region)
```

### Scenario 2: The Insider Threat

```
Company: SaaS startup, 50 employees
Problem: Developer A leaves company (gets fired)
Issue: Developer A has S3 credentials for EVERYTHING
     - Production customer data
     - Backup systems
     - Root account key
     - Source code repositories

Risk: Developer A could:
- Download all customer PII (10 million customer records)
- Delete backups
- Expose trade secrets
- Demand ransom

Prevention: IAM would allow:
- Revoke Developer A's access instantly
- Developer A only had specific folder access
- CloudTrail logs show exactly what they accessed
- Customer data encrypted (can't read even if accessed)
```

### Scenario 3: The Accidental Mistake

```
Company: Data company, 5 data engineers
Problem: Data engineer runs script to delete old logs
Script mistake: `rm -rf /` instead of `rm -rf /old-logs/`
Result: Deletes EVERYTHING from S3 bucket
Damage: $2 million in downtime + recovery

What should have happened:
- Data engineer shouldn't have DELETE permission on production
- Production data should have:
  - Object Locking enabled (can't delete)
  - Versioning enabled (recover deleted files)
  - Backup bucket (cross-region)
```

---

## What is IAM? (Identity & Access Management)

**Official definition:** AWS Identity and Access Management controls who (identity) can do what (actions) on which resources (resources) under what conditions.

**Human-friendly definition:** IAM = The bouncer at the club

```
Bouncer (IAM) checks:
1. "Are you on the list?" (are you an authenticated user?)
2. "What can you do?" (what permissions do you have?)
3. "Can you prove it?" (can you provide credentials?)
4. "Are conditions met?" (time of day, IP address, etc.?)

✅ Yes to all → you enter (allowed access)
❌ No to any → you're blocked (denied access)
```

---

## Core Concepts

### 1. Identity (Who?)

**Types of identities:**

```
1️⃣ AWS Account
   - Root identity (dangerous, never use)
   - Has unlimited power
   - Should be locked with MFA

2️⃣ IAM User
   - Human (data engineer, analyst, DevOps)
   - Long-term credentials (access key + secret)
   - Can create multiple access keys

3️⃣ IAM Role
   - Service principal (Lambda, Glue, EC2)
   - Or cross-account human (contractor)
   - Temporary credentials (1 hour default)
   - Example: "GlueJobRole" = Lambda can assume this

4️⃣ MFA Device
   - Additional identity verification
   - Phone (authenticator app: Google Authenticator)
   - Hardware token (Yubikey)
   - Prevents password-only access
```

### 2. Principal (Proving You Are Who You Say)

**How authentication works:**

```
You claim: "I'm data engineer John"
AWS: "Prove it. Show me your credentials"

You provide:
- Access Key ID: "AKIAIOSFODNN7EXAMPLE"
- Secret Access Key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

AWS verifies: "Yes, these credentials match an IAM user named John"
Result: ✅ Authenticated (verified your identity)
```

### 3. Permission (What Can You Do?)

**After authentication, check authorization:**

```
John (IAM user) is authenticated ✅
Now what can John do?

Policy says:
- John can list S3 buckets (ListBucket) ✅
- John can read objects in /bronze/ (GetObject) ✅
- John can WRITE to /silver/ (PutObject) ✅
- John CANNOT delete anything (DeleteObject) ❌
- John CANNOT access Glue jobs (no Glue permissions) ❌

Result: John can only do what policy allows
```

### 4. Resource (What Can You Access?)

**Policies specify which resources:**

```
Policy: "Allow s3:GetObject on /processed/* "

What this means:
✅ Can read objects in: s3://lake/processed/...
✅ Can read: s3://lake/processed/orders.parquet
✅ Can read: s3://lake/processed/2024-01-15/orders.csv
❌ Cannot read: s3://lake/raw/orders.csv (different prefix)
❌ Cannot read: s3://lake/silver/orders.parquet (different prefix)
```

---

## Why IAM Matters: The Risk of No Access Control

### Without IAM (Everyone has root access)

```
AWS Account
└─ Root user
    ├─ Data Engineer Sarah: CAN delete everything
    ├─ Database Admin Tom: CAN delete everything
    ├─ Intern Jake: CAN delete everything
    ├─ DevOps Engineer Lisa: CAN delete everything
    └─ Contractor (3rd party): CAN delete everything

Problem:
- Any person could accidentally/intentionally delete production data
- Impossible to audit "who did what"
- If one password compromised → entire account compromised
- No way to revoke single person's access
- No separation of concerns
```

### With IAM (Least Privilege)

```
AWS Account
├─ Data Engineer Sarah: s3:GetObject + s3:PutObject (bronze/silver only)
├─ Database Admin Tom: RDS:DeleteDBInstance (with MFA requirement)
├─ Intern Jake: s3:GetObject (processed data only, read-only)
├─ DevOps Engineer Lisa: All EC2 + Lambda + IAM permissions
└─ Contractor: s3:GetObject (specific bucket only, 3-month duration)

Benefits:
- Sarah can read/write data, but NOT delete production
- Tom can delete test databases, but requires MFA (2-factor authentication)
- Jake has limited read access (can't break anything)
- Lisa has full permissions (she's trusted)
- Contractor access expires automatically (3 months)
- Audit trail: "Sarah accessed this object on Feb 8, 2:30 PM"
```

---

## Real-World Roles: Data Engineering

### Typical Data Engineering Organization

```
1. Data Engineer (Junior) - Jake
   ├─ Read: Bronze layer (raw data)
   ├─ Write: Silver layer (processed data)
   ├─ Can: Run data validation
   ├─ Cannot: Delete data (protection against mistakes)
   └─ Cannot: Access customer PII (separation of concerns)

2. Data Engineer (Senior) - Sarah
   ├─ Read/Write: Bronze + Silver layers
   ├─ Read: Gold layer (to understand final output)
   ├─ Can: Create/modify Glue jobs
   ├─ Can: Debug data issues
   ├─ Cannot: Delete data in production
   └─ Can: Delete in development/staging

3. Data Architect - Alex
   ├─ Full S3 access (all buckets, all layers)
   ├─ Can: Design data models
   ├─ Can: Create/update IAM roles
   ├─ Can: Modify bucket policies
   ├─ Can: Create/delete Glue resources
   └─ Requires: MFA for destructive actions

4. Analytics Engineer - Emma
   ├─ Read: Gold layer (analytics-ready data)
   ├─ Write: Athena query results to temp bucket
   ├─ Can: Query via Athena
   ├─ Can: Create views/tables
   ├─ Cannot: Modify Silver/Bronze data
   └─ Cannot: Create new Glue jobs

5. Contractor (3rd Party) - Chris
   ├─ Read: Specific processed dataset only
   ├─ Duration: 3 months (automatic expiry)
   ├─ Cannot: Access other data
   ├─ Cannot: Create resources
   └─ Cannot: Assume other roles
```

---

## Principle of Least Privilege (PLaP)

### Definition

"Grant the minimum permissions necessary to accomplish the task."

### Wrong: Overprivileged Access

```
Data engineer needs to read S3 data
Admin thinking: "Oh, just give them full S3 access"

Policy: "s3:*" (ALL S3 permissions)
Result:
- ✅ Can read data
- ❌ Can accidentally delete production data
- ❌ Can download entire customer database
- ❌ Can modify bucket policies (expose data)
- ❌ Can access confidential folders (legal, HR, finance)

Risk: One mistake → $1M disaster
```

### Right: Least Privilege

```
Data engineer needs to read S3 data
Admin thinking: "What's the minimum to accomplish goal?"

Policy: "s3:GetObject + s3:ListBucket" on "bronze/* + silver/*"
Result:
- ✅ Can read data (goal achieved)
- ❌ Cannot delete (safe)
- ❌ Cannot download entire bucket (safe)
- ❌ Cannot modify policies (safe)
- ❌ Cannot access other folders (safe)

Security benefit: Mistakes limited to safe operations
```

### The Security Equation

```
Least Privilege = Reduced Risk + Reduced Blast Radius
                ↓
            If someone's account compromised:
            - Insider threat: Limited what they can do
            - Hacker: Limited lateral movement
            - Mistake: Limited blast radius
```

---

## Identity Types: User vs Role

### IAM User (For Humans)

```
Properties:
✅ Long-term credentials (access key ID + secret)
✅ Used by: Individual people (data engineers)
✅ Lifetime: Typically years (until they leave company)
✅ Credential rotation: Every 90 days (best practice)

When to use:
- People who need permanent access to AWS
- Need to access from laptop, terminal
- Need to create long-lived API keys

When NOT to use:
- Services (use Role instead)
- Temporary access (use Role instead)
- One-time access (use temporary credentials)
```

### IAM Role (For Services + Assumed Access)

```
Properties:
✅ Temporary credentials (issued at access time)
✅ Used by: Services (Lambda, Glue, EC2)
✅ Lifetime: Short-term (1 hour default)
✅ Trust relationship: Who can assume role?

When to use:
- Lambda needs to read S3
- Glue job needs to write to S3
- EC2 instance needs to access RDS
- Cross-account access (one AWS account accesses another)
- Temporary contractor access

When NOT to use:
- Humans needing permanent access (use User instead)
```

---

## Key IAM Features for Data Engineers

### 1. Temporary Credentials (STS)

```
Normally: Access key = valid until you manually rotate
Problem: If key compromised → attacker has permanent access

Solution: Temporary credentials
- Token issued for 1 hour
- Auto-expires (no manual cleanup)
- Perfect for services + contractors

Example: Lambda function
- Lambda assumes "GlueJobRole"
- AWS issues temporary credentials (valid 1 hour)
- Lambda uses credentials to access S3
- After 1 hour → credentials invalid (automatic security)
```

### 2. MFA (Multi-Factor Authentication)

```
Normally: Password = only factor
Problem: If password compromised → access lost

Solution: MFA
- Password (something you know)
- + Code from phone (something you have)
- Both required to access

Protection: Even if password compromised, attacker needs physical phone

Example:
1. Data architect tries to delete production database
2. AWS asks: "Confirm with MFA" (phone beeps)
3. Architect enters 6-digit code (4-digit code from phone)
4. Now deletion allowed

This prevents accidental/malicious deletions
```

### 3. Cross-Account Access

```
Scenario: Your company (Account A) uses contractor (Account B)

Without cross-account:
- Contractor shares your AWS password (insecure!)
- Can't revoke access quickly
- Can't audit activity separately

With cross-account:
- Contractor has IAM user in their account (Account B)
- Account B trusts Account A
- Contractor assumes role in Account A (temporary access)
- Can revoke by removing trust relationship
- Activity tracked (CloudTrail shows contractor access)

Example:
1. Contractor assumes "DataAccessRole" in your account
2. AWS issues temporary credentials (valid 1 hour)
3. Contractor accesses your S3 data
4. After 1 hour, credentials expire (automatic!)
5. You can revoke access anytime
```

---

## IAM Best Practices Checklist

- [ ] **Never use root account** (except account creation)
- [ ] **Enable MFA on root** (if you ever use it)
- [ ] **Create IAM users for humans** (one per person)
- [ ] **Create IAM roles for services** (Lambda, Glue, EC2)
- [ ] **Apply least privilege** (minimum permissions needed)
- [ ] **Enable CloudTrail** (audit who did what)
- [ ] **Rotate access keys** (every 90 days)
- [ ] **Use temporary credentials** (STS > long-term keys)
- [ ] **Enable MFA for sensitive actions** (delete, disable MFA)
- [ ] **Review permissions quarterly** (remove unused access)

---

## Key Takeaways

1. **IAM is about who can do what** ✅ Prevention mechanism
2. **Least privilege = reduced risk** ✅ Minimum permissions
3. **Users for humans, Roles for services** ✅ Different use cases
4. **Temporary credentials > long-term** ✅ Security by default
5. **MFA = protection against password theft** ✅ Extra security layer

---

## Hands-On Intuition Check ✓

After reading, you should understand:

- [ ] Why root account is dangerous
- [ ] Difference between User and Role
- [ ] Principle of Least Privilege
- [ ] Why MFA matters
- [ ] How temporary credentials work

---

## Next Up

Ready to understand HOW policies work?

**→ [02-iam-identities.md](./02-iam-identities.md)** dives deep into Users, Groups, and Roles

---

**Key Statistics to Remember:**
- 99% of breaches trace back to weak IAM policies
- Average time to detect compromise: 287 days (CloudTrail would reduce to <1 day)
- Cost of data breach: $4 million average (preventable with IAM)

