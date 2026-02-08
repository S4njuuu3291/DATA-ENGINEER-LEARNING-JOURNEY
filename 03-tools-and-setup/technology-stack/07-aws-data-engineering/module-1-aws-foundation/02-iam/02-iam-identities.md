# 02. IAM Identities: Users, Groups & Roles

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** Choose the right identity type (User vs Group vs Role) for the right use case

---

## The Three Identity Types

```
┌─────────────────────────────────────────┐
│         AWS Account (Root)              │
│  Has unrestricted access and unlimited  │
│   power. Almost never directly used.    │
└─────────────────────────────────────────┘
           ↓ Creates ↓
   ┌───────┬──────────┬────────┐
   ↓       ↓          ↓        ↓
 USERS  GROUPS    ROLES    POLICIES
```

---

## 1. IAM Users

### Definition & Purpose

**IAM User** = Identity for a person who needs long-term AWS access

```
Example: "john_data_engineer"
- Long-lived credentials (access key ID + secret)
- Used from: Laptop, CI/CD pipeline, terminal
- Lifetime: Months to years
- Rotation: Every 90 days (best practice)
```

### Creating an IAM User

```bash
aws iam create-user --user-name john_data_engineer

# Give passwords for console login
aws iam create-login-profile --user-name john_data_engineer 
  --password "TempPassword123!" --password-reset-required

# Or create access keys for API access
aws iam create-access-key --user-name john_data_engineer
```

### User Properties

```
Attributes:
- Username (unique within AWS account)
- Display name (optional)
- ARN: arn:aws:iam::123456789:user/john_data_engineer
- Creation date
- Access keys (0-2 per user, recommended 1 active)
- Console password (for AWS console login)
- MFA devices attached
```

### When to Use Users

✅ **Use Users for:**
- Individual people (permanent or long-term role)
- CI/CD pipelines (Jenkins, GitHub Actions)
- Local development (terminal access)
- Any scenario needing long-lived credentials

❌ **Do NOT use Users for:**
- AWS services (use Role instead)
- Temporary access (use Role with STS)
- Cross-account access (use Role with trust)

### User Limitations

```
Problems with always using users:
1. Credentials don't auto-expire (need manual rotation)
2. Hard to revoke team's access (remove each user individually)
3. Can't implement automatic expiry (3-month contractor)
4. Can't use with service principal (Lambda)
5. No "assume role" concept (temporary security)
```

---

## 2. IAM Groups

### Definition & Purpose

**IAM Group** = Collection of Users with same permissions

```
Example: "DataEngineering" group
- Contains: John, Sarah, Tom (3 users)
- All have: Same S3 + Glue permissions
- Management: Add/remove users from group
```

### How Groups Work

```
Without Groups (manual):
Policy attached to: John
Policy attached to: Sarah
Policy attached to: Tom

Problem: Update policy = attach to 3 people individually
         New engineer = attach policy manually
         Fire engineer = remove from 3 places

With Groups (automatic):
Group: "DataEngineering" has policy
  ├─ John (member)
  ├─ Sarah (member)
  └─ Tom (member)

Benefit: Update policy = update group once
         New engineer = add to group
         Fire engineer = remove from group
```

### Creating Groups

```bash
# Create group
aws iam create-group --group-name DataEngineering

# Add users to group
aws iam add-user-to-group --group-name DataEngineering 
  --user-name john_data_engineer
aws iam add-user-to-group --group-name DataEngineering 
  --user-name sarah_data_engineer

# Attach policy to group
aws iam attach-group-policy --group-name DataEngineering 
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### Common Groups (Best Practice)

```
Organization: Data Lake Company
Groups:

1. DataEngineersJunior
   - Members: Jake, Alex
   - Permissions: Read bronze/silver, write silver, run Glue jobs
   - Cannot: Delete anything, modify IAM

2. DataEngineersSenior
   - Members: Sarah, Tom
   - Permissions: Read/write all, debug jobs, create jobs
   - Cannot: Delete in production, modify IAM

3. DataArchitects
   - Members: Lisa
   - Permissions: Full access (except IAM)
   - Cannot: Modify IAM roles

4. AnalyticsEngineers
   - Members: Emma, Chris
   - Permissions: Read gold layer, query Athena, create views
   - Cannot: Modify underlying data, delete

5. Admins
   - Members: Admin
   - Permissions: Full AWS access
   - Requirement: MFA mandatory
```

### When to Use Groups

✅ **Use Groups for:**
- Multiple users with same role (all engineers, all analysts)
- Easy onboarding (add person to group = instant permissions)
- Easy offboarding (remove from group = instant access revoke)
- Consistent permission management

❌ **Do NOT use Groups for:**
- Services (use Roles instead)
- Temporary access (use Roles with STS instead)
- Complex permission logic (use Roles with conditions instead)

---

## 3. IAM Roles

### Definition & Purpose

**IAM Role** = Identity for temporary access (service or assumed by human)

```
Two main uses:

1️⃣ Service Role:
   - When: Lambda needs to read S3
   - How: Lambda "assumes" GlueJobRole, gets temporary credentials
   - Duration: 1 hour (auto-expires)

2️⃣ Assumed Role:
   - When: Contractor needs access for 3 months
   - How: Contractor assumes "ContractorRole", gets temp credentials
   - Duration: 1 hour per assumption, role expires after 3 months
```

### How Roles Work (Service Example)

**Scenario:** Lambda function needs to read S3 data

```
Architecture:
┌──────────────┐
│   Lambda     │
│  (Service)   │
└──────────────┘
      ↓ needs S3 access
      ↓ assumes role
      ↓
┌──────────────────────────┐
│  DataProcessingRole      │
│  (IAM Role)              │
│  - Trust: Lambda         │
│  - Permissions: S3:*     │
└──────────────────────────┘

Process:
1. Lambda needs to call S3
2. Lambda: "I need to assume DataProcessingRole"
3. IAM: "Are you trusted to assume this role?" (checks trust policy)
4. IAM: "Yes, Lambda is trusted"
5. IAM: Issues temporary credentials (1 hour)
6. Lambda: Uses credentials to access S3
7. After 1 hour: Credentials auto-expire (no cleanup needed)
```

### Trust Policy (Who Can Assume)

**Trust Policy** = "Who is allowed to assume this role?"

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

**Meaning:** Only AWS Lambda service can assume this role

### Permission Policy (What Can They Do)

**Permission Policy** = "What actions are allowed?"

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

**Meaning:** Role holder can read S3 objects in my-bucket

### Real-World Roles Example

```
Data Pipeline Architecture:

┌────────────────────────────────────────────┐
│  S3 Bucket (Bronze Data)                   │
│  └─ s3://data-lake/bronze/                 │
└────────────────────────────────────────────┘
                      ↓
┌────────────────────────────────────────────┐
│  Lambda (Trigger on S3 upload)             │
│  Assumes: "S3TriggerLambdaRole"            │
│  Permissions: Read bronze, run Glue jobs   │
└────────────────────────────────────────────┘
                      ↓
┌────────────────────────────────────────────┐
│  Glue Job (ETL Processing)                 │
│  Assumes: "GlueJobRole"                    │
│  Permissions: Read bronze, write silver    │
└────────────────────────────────────────────┘
                      ↓
┌────────────────────────────────────────────┐
│  S3 Bucket (Silver Data)                   │
│  └─ s3://data-lake/silver/                 │
└────────────────────────────────────────────┘
```

**Each step temporary:** Lambda expires after 1hr, Glue job expires after job ends completes

### When to Use Roles

✅ **Use Roles for:**
- Services (Lambda, Glue, EC2, RDS)
- Temporary access (contractors, time-limited)
- Cross-account access (one account accessing another)
- Any scenario needing auto-expiring credentials
- Reducing key rotation burden (no manual rotation needed!)

❌ **Do NOT use Roles for:**
- Permanent human access (use Users instead)
- Long-lived credentials (use Users instead)

---

## User vs Group vs Role: Decision Tree

```
Question: Who needs AWS access?

├─ Is it a person (human)?
│  ├─ YES
│  │  ├─ Is access permanent/long-term?
│  │  │  ├─ YES → Create IAM USER
│  │  │  └─ NO → Create temporary (STS AssumeRole)
│  │  │
│  │  └─ Multiple people with same permissions?
│  │     └─ YES → Create GROUP, add users to group
│  │
│  └─ NO (it's a service/process)
│     └─ Create IAM ROLE with trust policy
│
└─ Example routing:
   - Data engineer (person, permanent) → USER + added to GROUP
   - Lambda function (service) → ROLE with Lambda trust
   - Contractor (person, 3 months) → ROLE (temporary)
```

---

## Roles for Cross-Account Access

### Scenario

Your company (Account A) uses AWS consultant (Account B)

```
Account A (Your Company):
- Has production data in S3
- Wants consultant to analyze data
- Can't share account password (insecure)

Account B (Consultant Company):
- Has IAM user "analyst" who needs access
- Can't access Account A directly
```

### Solution: Cross-Account Role

**Step 1:** Account A creates role "ConsultantAnalysisRole"

```json
Trust Policy (Account A):
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::CONSULTANT-ACCOUNT-ID:user/analyst"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

Permission Policy:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/analysis-data/*"
    }
  ]
}
```

**Step 2:** Consultant (Account B) assumes role

```bash
# Consultant in Account B
aws sts assume-role \
  --role-arn "arn:aws:iam::ACCOUNT-A-ID:role/ConsultantAnalysisRole" \
  --role-session-name "analysis-session"

# Returns temporary credentials valid for 1 hour
{
  "Credentials": {
    "AccessKeyId": "ASIAJ...",
    "SecretAccessKey": "...",
    "SessionToken": "...",
    "Expiration": "2024-02-08T13:00:00Z"
  }
}
```

**Step 3:** Consultant uses credentials

```bash
# Use temporary credentials to access Account A data
aws s3 cp s3://my-bucket/analysis-data/ . --recursive
```

**Benefits:**
- ✅ Consultant doesn't have Account A password
- ✅ Access auto-expires (1 hour per session)
- ✅ Company can revoke by removing trust relationship
- ✅ Consultant's company (Account B) controls their credential
- ✅ Audit trail shows consultant access

---

## Service-Linked Roles (Auto-Created)

### What are SLRs?

**Service-Linked Role** = AWS-managed role automatically created when service is used

```
Example: When you create AWS Glue job:
- AWS automatically creates: "AWSGlueServiceRole"
- You don't manually create it
- It has permissions to read/write S3, Glue Catalog
- You just use it (it's pre-configured)

Advantage: Less IAM management (AWS handles it)
Disadvantage: Less control (fewer customization options)
```

### Common SLRs

| Service | Auto-Created Role | Permissions |
|---------|-------------------|------------|
| **Lambda** | (None, use custom role) | You define |
| **Glue** | AWSGlueServiceRole | S3, Glue Catalog, Logs |
| **RDS** | rds-monitoring-role | CloudWatch monitoring |
| **DMS** | dms-vpc-management-role | VPC access for migrations |

---

## Comparison Table: User vs Group vs Role

| Aspect | User | Group | Role |
|--------|------|-------|------|
| **Use for** | Individual person | Multiple users | Service/assumed access |
| **Credential type** | Long-term | None (inherits user creds) | Temporary (STS) |
| **Lifetime** | Months-years | N/A | 1 hour (auto-expires) |
| **Credential rotation** | Manual (90 days) | N/A | Automatic |
| **Revocation** | Remove user | Remove from group | Remove trust policy |
| **Management** | Individual | By group | By trust relationship |
| **Best for** | Permanent staff | Team permissions | Services + contractors |

---

## Best Practices

- [ ] Create Groups for common roles (DataEngineers, Analysts, etc.)
- [ ] Use one IAM user per person (not shared)
- [ ] Use Roles for all services (Lambda, Glue, EC2)
- [ ] Implement least privilege (minimum permissions)
- [ ] Rotate access keys every 90 days
- [ ] Use temporary credentials (STS) for contractors
- [ ] Enable MFA for privileged operations
- [ ] Use CloudTrail to audit identity usage

---

## Key Takeaways

1. **Users** = Long-term individual access (people)
2. **Groups** = Simplify user management (team permissions)
3. **Roles** = Temporary access (services, contractors)
4. **Trust Policies** = Who can assume role (service principal check)
5. **Permission Policies** = What actions allowed (resource-level control)

---

## Next Up

**→ [03-iam-policy-json.md](./03-iam-policy-json.md)** dives into how to write permission policies

