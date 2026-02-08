# 04. IAM Least Privilege: Enterprise Patterns

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐⭐ (Advanced)  
> **Key Takeaway:** Start restrictive, add permissions only as needed

---

## Principle of Least Privilege (PLaP)

**Definition:** Grant minimum permissions necessary to accomplish task.

### The Security Mindset

❌ **Wrong Mindset:**
```
Admin: "Give them S3 access"
(Attaches: s3:*)
Result: User can delete production databases
```

✅ **Right Mindset:**
```
Question: "What specific actions need to complete job?"
Answer: "Read bronze/silver data, write silver data, run validation"
Policy: "s3:GetObject + s3:PutObject on specific prefixes only"
Result: User can do job safely
```

---

## The Onion Model: Layers of Restriction

```
Layer 1: Account-Level
  └─ Which AWS accounts can this role access?

Layer 2: Service-Level
  └─ Which services (S3, Glue, Lambda, etc.)?

Layer 3: Resource-Level
  └─ Which specific resources (buckets, jobs, databases)?

Layer 4: Action-Level
  └─ Which operations (Get, Put, Delete)?

Layer 5: Condition-Level
  └─ When/where/how (IP, date, MFA required)?

Block at ANY layer = access denied
```

### Real Example: Data Engineer Access

```
Account-Level:
└─ Only {prod, dev} accounts (no {billing, security})

Service-Level:
├─ S3 ✅
├─ Glue ✅
├─ Athena ✅
├─ IAM ❌ (can't create users)
└─ RDS ❌ (can't delete databases)

Resource-Level:
├─ S3 Buckets:
│  ├─ {data-lake-prod, data-lake-dev} ✅
│  └─ {backups, security-logs} ❌
├─ Glue Jobs:
│  ├─ {transformation-*, validation-*} ✅
│  └─ {backup-*, admin-*} ❌

Action-Level:
├─ S3:
│  ├─ GetObject ✅
│  ├─ PutObject ✅
│  └─ DeleteObject ❌
├─ Glue:
│  ├─ CreateJob ✅
│  ├─ StartJobRun ✅
│  └─ UpdateJobRole ❌

Condition-Level:
└─ Except: Must use MFA for DeleteObject
```

---

## Real-World Role Definitions

### Junior Data Engineer Role

**Permissions:**
```
S3:
- Read: bronze/silver/processed (GetObject, ListBucket)
- Write: silver/temp (PutObject, DeleteObject on /temp/ only)
- Cannot: Delete from bronze or production

Glue:
- View: All jobs (GetJob, ListJobs)
- Run: Only test jobs (StartJobRun on *-test-*)
- Create: Cannot create production jobs

Athena:
- QueryExecution: All queries
- ResultLocation: Only /temp/athena-results/

Cannot:
- Modify IAM
- Delete backup data
- Assume other roles
```

### Senior Data Engineer Role

**Permissions:**
```
S3:
- Read/Write/Delete: All bronze/silver (except /archive)
- Cannot: Delete archived data (6-year retention)

Glue:
- Full control: Create, update, run, debug jobs
- Cannot: Modify job roles/trust policies

Athena:
- Full access
- Can: Optimize queries, create views

Additional:
- AssumeRole: Can assume "DebugRole" for troubleshooting
- CloudWatch: Full read (debugging metrics)
- CloudTrail: Read (audit logs)

Cannot:
- Modify IAM
- Delete production data backups
- Access customer PII directly
```

### Data Architect Role

**Permissions:**
```
S3:
- Full control including deletions
- Can: Modify bucket policies, enable features

Glue + RDS + DMS + Lambda:
- Full control

IAM:
- Create/modify roles (but cannot modify own trust policy)
- Manage users in DataEngineering group
- Cannot: Modify root account, delete admins

Additional:
- CloudFormation: Full control (IaC)
- CloudTrail: Full control
- AWS Config: Full control

Restrictions:
- MFA required for sensitive operations (DELETE, IAM modify)
```

---

## Implementation: Step-by-Step

### Step 1: Define Roles (By job title)

```
Organization roles:
- JuniorDataEngineer
- SeniorDataEngineer
- DataArchitect
- AnalyticsEngineer
- DataQualityEngineer
```

### Step 2: Define Permissions Per Role

```
Create policy document for each role:
- juniorDataEngineer.json
- seniorDataEngineer.json
- dataArchitect.json
- etc.
```

### Step 3: Create IAM Groups

```
aws iam create-group --group-name JuniorDataEngineers
aws iam create-group --group-name SeniorDataEngineers
aws iam create-group --group-name DataArchitects
```

### Step 4: Attach Policies to Groups

```bash
aws iam put-group-policy \
  --group-name JuniorDataEngineers \
  --policy-name DataEngineeringPolicy \
  --policy-document file://juniorDataEngineer.json
```

### Step 5: Add Users to Groups

```bash
aws iam add-user-to-group \
  --group-name JuniorDataEngineers \
  --user-name john_doe
```

---

## Delegation Pattern (Team Lead)

### Scenario

Data team lead (Sarah) manages junior engineers but isn't admin.

**What Sarah CAN do:**
- Add/remove people from DataEngineering group
- Reset passwords for team
- Create development resources

**What Sarah CANNOT do:**
- Modify role policies (need architect approval)
- Access production data directly
- Assume admin roles

**Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ManageDataEngineeringGroup",
      "Effect": "Allow",
      "Action": [
        "iam:AddUserToGroup",
        "iam:RemoveUserFromGroup",
        "iam:GetGroup"
      ],
      "Resource": "arn:aws:iam::*:group/DataEngineering"
    },
    {
      "Sid": "ResetTeamPasswords",
      "Effect": "Allow",
      "Action": "iam:CreateLoginProfile",
      "Resource": "arn:aws:iam::*:user/de-*"  ← Only team members
    },
    {
      "Sid": "ViewTeamActivity",
      "Effect": "Allow",
      "Action": "cloudtrail:LookupEvents",
      "Condition": {
        "StringLike": {
          "aws:username": "de-*"
        }
      }
    }
  ]
}
```

---

## Sensitive Operations: MFA Required

### Example: Require MFA for Deletions

```json
{
  "Sid": "AllowDeleteWithMFA",
  "Effect": "Allow",
  "Action": "s3:DeleteObject",
  "Resource": "arn:aws:s3:::data-lake/*",
  "Condition": {
    "Bool": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

**Behavior:**
- Without MFA: DeleteObject request → DENIED
- With MFA: DeleteObject request → ALLOWED

---

## Audit & Review Quarterly

### Quarterly Review Checklist

- [ ] Who has access they don't need anymore?
- [ ] Contractors with expired roles?
- [ ] Unused access keys?
- [ ] Permissions added that are unused?
- [ ] Any policy violations (overly permissive)?

### Automated Actions

```bash
# Find unused access keys (no activity > 90 days)
aws iam get-credential-report

# Find unused roles
aws accessanalyzer validate-policy --policy-document file://policy.json

# Find overly permissive policies
aws accessanalyzer list-findings
```

---

## Anti-Patterns: What NOT to Do

❌ **Don't: Give everyone root access**
```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

❌ **Don't: Hardcode credentials in code**
```python
aws_key = "AKIAIO..."  # NEVER DO THIS
s3 = boto3.client('s3', aws_access_key_id=aws_key)
```

❌ **Don't: Share IAM user credentials**
```
# WRONG: Multiple people using same user account
```

❌ **Don't: Trust all IP addresses**
```json
{
  "IpAddress": {
    "aws:SourceIp": "0.0.0.0/0"  // WRONG: Anyone
  }
}
```

✅ **Do: Use roles with auto-rotating credentials**
✅ **Do: Use Secrets Manager for runtime credentials**
✅ **Do: One user per person**
✅ **Do: Restrict IP to VPN/corporate network**

---

## Cost Impact of Least Privilege

```
Overpermissioned user:
- Cost: $1M+ (deleted production data → recovery costs)
- Risk: High (insider threat, hacking)
- Compliance: Fails audit (no access control)

Least privilege user:
- Cost: $0 (mistakes limited to non-destructive operations)
- Risk: Low (limited blast radius)
- Compliance: Passes audit (documented access control)

ROI: Tiny policy effort → massive risk reduction
```

---

## Key Takeaways

1. **Start restrictive** → Add only what's needed
2. **Use layers** → Account → Service → Resource → Action → Condition
3. **Group by role** → Manage via groups, not individual users
4. **Audit quarterly** → Remove unused permissions
5. **MFA for sensitive** → Delete, modifyIAM requires MFA

---

## Next Up

**→ [05-iam-security-best-practices.md](./05-iam-security-best-practices.md)** covers MFA, rotation, and CloudTrail

