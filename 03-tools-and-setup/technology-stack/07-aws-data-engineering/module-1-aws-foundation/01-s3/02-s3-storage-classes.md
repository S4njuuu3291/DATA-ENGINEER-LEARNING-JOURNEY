# 02. S3 Storage Classes: Cost vs Speed Trade-off

> **Duration:** 60 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** Different access patterns require different storage classes. Choose wrong = waste thousands/year

---

## The Problem: Not All Data Is Equal

Imagine your company's S3 bucket with 10 TB data:

```
3 TB: Customer orders (accessed daily by analytics)
5 TB: Archived logs from 2019 (accessed 1x per year for compliance)
2 TB: Backup of backup (accessed never, only kept for disaster recovery)
```

**Naive approach:** Store everything in "standard" S3
- Cost: 10 TB × $0.023/month = $2,300/year
- Waste: Paying premium price for data nobody accesses

**Smart approach:** Use different storage classes
- Hot data (orders) → Standard (expensive but fast)
- Warm data (last year's logs) → Infrequent Access (cheaper)
- Cold data (backups) → Glacier (very cheap)
- Cost: ~$800/year (65% savings!)

---

## S3 Storage Classes Explained

### Overview Table

| Class | Cost/GB/Month | Speed | Min. Duration | Best For |
|-------|---|-------|---|---|
| **Standard** | $0.023 | Instant | None | Hot data (daily access) |
| **Standard-IA** | $0.0125 | Instant | 30 days | Warm data (monthly access) |
| **One Zone-IA** | $0.01 | Instant | 30 days | Warm + duplicate exists elsewhere |
| **Intelligent-Tiering** | $0.0125 | Automatic | None | Unknown access patterns |
| **Glacier Instant** | $0.004 | <1 sec | 90 days | Archive (quarterly access) |
| **Glacier Flexible** | $0.0036 | 1-12 hours | 90 days | Long-term archive (1x/year) |
| **Deep Archive** | $0.00099 | 12 hours | 180 days | Compliance archive (keep 7 years) |

---

## Storage Class Details

### 1. Standard (The Baseline)

**Use case:** Actively accessed data

```
Your bucket default. Don't overthink it.

Cost: $0.023 per GB per month
Minimum storage duration: None
Retrieval time: Milliseconds (instant)
Availability: 99.99%
```

**Real scenario:** E-commerce company

```
Production data:
- Daily orders: 5GB (need instant access for reports)
- Real-time analytics: 2GB (queried 24/7)

Store in: Standard
Cost: 7GB × $0.023 = $0.16/month = $1.92/year
```

**When to use:**
- ✅ Frequently accessed data (daily/hourly)
- ✅ Production databases & data lakes
- ✅ Active machine learning datasets
- ✅ Data feeding real-time dashboards

**When NOT to use:**
- ❌ Archives (use Glacier)
- ❌ Data accessed <1 month (use IA)

---

### 2. Standard-IA (Infrequent Access)

**Use case:** Data accessed occasionally (monthly)

```
Cost-optimized alternative to Standard for older data

Cost: $0.0125 per GB + $0.01 per GET
Minimum storage duration: 30 days (charge 30 days even if delete earlier)
Retrieval time: Milliseconds (instant, same as Standard)
Availability: 99.9%
```

**Key difference:** Minimum committed 30 days + retrieval charges

**Cost comparison for 1000 GB accessed 4x/year:**

```
Standard:
- 1000 GB × $0.023 × 12 = $276/year
- No retrieval charges
- Total: $276/year

Standard-IA:
- Storage: 1000 GB × $0.0125 × 12 = $150/year
- Retrieval: 4 accesses × 1000 GB × $0.01 = $40/year
- Total: $190/year (31% savings!)

Break-even: After 4 retrievals/year, IA is cheaper
```

**Real scenario:** Monthly compliance reports

```
Company: Financial services firm
Requirement: Monthly profit/loss report (accessed 12x/year)

Storage:
- Current month's raw data: 100GB Standard
- Previous 11 months: 1100GB Standard-IA
- Older archives: Glacier

Cost if all Standard: 1200 × $0.023 × 12 = $331/year
Cost with IA: 100×$0.023×12 + 1100×$0.0125×12 + 1100×12×$0.01 = $27 + $165 + $132 = $324/year
(Minimal savings here, but flexibility if access patterns change)
```

**When to use:**
- ✅ Data accessed 1-3x per month
- ✅ Backup data (rarely accessed but needed)
- ✅ Historical reports (monthly/quarterly)
- ✅ Minimum 30-day retention

**When NOT to use:**
- ❌ Data accessed daily (use Standard)
- ❌ Data retained <30 days (Standard actually cheaper)
- ❌ Large retrievals every day (retrieval charges add up)

---

### 3. One Zone-IA (Single AZ Infrequent Access)

**Use case:** Infrequent data in secondary regions/accounts

```
Like Standard-IA, but only 1 zone (not replicated across 3 zones)

Cost: $0.01 per GB (cheapest of the IA options)
Minimum storage duration: 30 days
Retrieval time: Milliseconds
Durability: 99.95% (vs 99.999999999% for Standard)
Risk: If entire AZ fails → data lost
```

**Key difference:** Single point of failure (entire AZ down = total data loss)

**Cost comparison:**

```
Standard-IA: $0.0125/GB
One Zone-IA: $0.01/GB
Difference: $0.0025/GB saved

For 1000 GB:
- Standard-IA: $150/year
- One Zone-IA: $120/year
- Savings: $30/year per 1000 GB
```

**When to use:**
- ✅ Backup that exists elsewhere (data redundancy elsewhere)
- ✅ Temporary staging data (not critical)
- ✅ Development/test data
- ✅ Data that's easy to regenerate

**When NOT to use:**
- ❌ Production data (risk of AZ failure)
- ❌ Compliance data (durability requirements)
- ❌ Your only copy

---

### 4. Intelligent-Tiering (The Lazy Choice)

**Use case:** Unknown access patterns → Let AWS decide

```
AWS monitors access patterns automatically
- Not accessed for 30 days → Move to Infrequent tier
- Not accessed for 90 days → Move to Archive
- Need it again → Back to Frequent automatically

Cost: $0.0125/GB (flexible tier) + monitoring fee
Minimum storage duration: None
Retrieval time: Automatic (or manual restore)
Automatic transitions: YES
```

**How it works:**

```
Month 1: Upload 100GB file
- Stored in Frequent tier ($0.023/GB)
- Cost: $2.30

Month 2-3: Nobody accesses it
- Day 30: Moved to Infrequent tier ($0.0125/GB)
- Cost: $1.25 (saved $1.05!)

Month 4-6: Still nobody touches
- Day 90: Moved to Archive tier ($0.004/GB)
- Cost: $0.40 (saved $0.85!)

Month 10: Business needs the file again
- Automatically: Moved back to Frequent
- Cost: Back to $2.30/month
```

**When to use:**
- ✅ Unpredictable access patterns
- ✅ Data might become hot or cold randomly
- ✅ Don't want to manage transitions manually
- ✅ Cost savings worth monitoring overhead

**When NOT to use:**
- ❌ You know access pattern already (use specific class)
- ❌ Frequent transitions (churn = overhead)
- ❌ Real-time predictable data (Standard simpler)

---

### 5. Glacier Instant Retrieval

**Use case:** Archive accessed 1-4x per year (quarterly)

```
Cheaper archival storage with instant retrieval

Cost: $0.004 per GB/month
Retrieval: <1 second (like Standard)
Minimum storage: 90 days
Retrieval charges: $0.03 per GB
Durability: 99.999999999%
```

**Cost comparison vs Standard-IA for quarterly access:**

```
Standard-IA (accessed 4x/year):
- Storage: $0.0125 × 12 = $0.15/month
- Retrieval: 4 × $0.01 = $0.04/month average
- Total: $0.19/month per GB

Glacier Instant (accessed 4x/year):
- Storage: $0.004 × 12 = $0.048/month
- Retrieval: 4 × $0.03 = $0.12/month average
- Total: $0.168/month per GB (12% cheaper)
```

**Real scenario:** Year-end audits

```
Company: Retail chain
Requirement: Keep 3 years of transaction logs
Access pattern: Full-year audit once per year (Jan 1st)

Jan-Dec Year 1: Access frequently (live analysis)
→ Store in Standard

Jan-Dec Year 2: Occasional reference
→ Move to Standard-IA

Jan-Dec Year 3: Archive (only accessed during annual audit)
→ Move to Glacier Instant (accessed Jan 1st every year)

Jan Year 4: Beyond retention → Delete
```

**When to use:**
- ✅ Archive accessed quarterly (3-4x/year)
- ✅ Backup files often needed
- ✅ Compliance: Must keep, but rarely access
- ✅ Cost sensitive with occasional access needs

---

### 6. Glacier Flexible Retrieval (Deep Glacier)

**Use case:** Archive accessed 1-2x per year (or less)

```
Cheapest mainstream storage

Cost: $0.0036 per GB/month
Retrieval: 3-5 hours (bulk), 1 hour (standard), 10 min (expedited)
Minimum storage: 90 days
Retrieval charges: $0, $0, $10-50 per TB (depends on speed)
```

**Key: Slower retrieval = Lower cost**

**Retrieval options:**

```
BULK retrieval (12 hour)
- Free retrieve (no charge for retrieval)
- Use when not in hurry
- Example: Annual compliance audit (bulk retrieve on Dec 31, get on Jan 1)

STANDARD retrieval (3-5 hours)
- $0.01 per GB
- Use when need it today
- Example: Customer requests data access (3-hour SLA)

EXPEDITED retrieval (10 minutes)
- $0.03 per GB
- Use for emergency access
- Example: Disaster recovery (emergency database restore)
```

**Cost comparison: 5-year archive**

```
Scenario: Store 500GB legal records, accessed 1x per year (bulk retrieval)

Standard (5 years):
- 500 GB × $0.023 × 12 × 5 = $6,900/year = $34,500 total

Glacier Flexible (5 years):
- Storage: 500 × $0.0036 × 12 × 5 = $108/year = $540 total
- Retrieval: 5 × 0 (bulk = free) = $0
- Total: $540 over 5 years (98.4% savings!)
```

**When to use:**
- ✅ Long-term legal/compliance archive (7+ years)
- ✅ Access is rare and not urgent (1x/year)
- ✅ Cost more important than speed
- ✅ Can afford to wait 3-5 hours for retrieval

**When NOT to use:**
- ❌ Need access within hours (use Glacier Instant)
- ❌ Frequent unpredictable access (use Standard-IA)
- ❌ Emergency data (recovery could take days)

---

### 7. Deep Archive (Most Extreme)

**Use case:** Compliance archives kept 7+ years

```
Absolute lowest cost option

Cost: $0.00099 per GB/month ($1 per 1000 GB!)
Retrieval: 12 hours (bulk)
Minimum storage: 180 days (6 months minimum)
Retrieval charges: FREE (bulk), but 12-hour wait
```

**Real scenario: SEC compliance (7-year record keeping)**

```
Company: Investment firm
Requirement: Keep 7 years of trading records (SEC mandate)
Size: 100 GB per year

Standard storage (7 years):
- 700 GB × $0.023 × 12 × 7 = $13,944

Deep Archive (7 years):
- 700 GB × $0.00099 × 12 × 7 = $58.32
- (Once every 7 years bulk retrieve: FREE)
- Total: $58.32 (99.6% savings!)
```

**When to use:**
- ✅ Compliance archives (must keep, never access)
- ✅ Immutable records (can't delete)
- ✅ Cost is only concern
- ✅ Can wait 12 hours if need to access

**When NOT to use:**
- ❌ Data needed within hours
- ❌ Minimum 180 days storage isn't acceptable
- ❌ Frequent access (even once per year = 12 hour wait)

---

## Lifecycle Policies: The Money-Saving Magic ✨

### What is a Lifecycle Policy?

Automatically move objects between storage classes based on age/rules

**Example policy:**

```
Rule: "Archive old data"
- If object older than 30 days → Move to Standard-IA
- If object older than 90 days → Move to Glacier Instant
- If object older than 365 days → Move to Deep Archive
- If object older than 2555 days (7 years) → Delete
```

**Benefits:**
- Automatic transitions (no manual work)
- Optimal cost (always in right class)
- Compliance-ready (auto-delete per retention policy)

**Real scenario: E-commerce data lake**

```
Bronze (raw data):
- Day 0-7: Standard (fast ETL processing)
- Day 8-90: Standard-IA (analytics team queries)
- Day 91+: Glacier Instant (archive for compliance)

Silver (processed data):
- Day 0-30: Standard (active use)
- Day 31+: Standard-IA (occasional reference)

Gold (analytics):
- Day 0: Standard (dashboards)
- Day 366: Delete (replaced by next year)
```

---

## Decision Tree: Which Storage Class?

```
┌─ Is data accessed daily/frequent?
│  ├─ YES → Use STANDARD
│  └─ NO ↓
│
├─ Is data accessed monthly (1-3x)?
│  ├─ YES → Use STANDARD-IA
│  └─ NO ↓
│
├─ Is data replicated elsewhere?
│  ├─ YES (backup scenario) → Use ONE ZONE-IA
│  └─ NO ↓
│
├─ Is access pattern unknown?
│  ├─ YES → Use INTELLIGENT-TIERING
│  └─ NO ↓
│
├─ Is data accessed quarterly (3-4x/year)?
│  ├─ YES → Use GLACIER INSTANT
│  └─ NO ↓
│
├─ Is data accessed annually (<2x/year)?
│  ├─ YES → Use GLACIER FLEXIBLE
│  └─ NO ↓
│
└─ Is data compliance archive (7+ years)?
   └─ YES → Use DEEP ARCHIVE
```

---

## Cost Optimization Checklist

- [ ] **Audit existing buckets:** What's actually stored? How often accessed?
- [ ] **Identify cold data:** >90 days without access? Move to cheaper tier
- [ ] **Set lifecycle policies:** Automatic transitions = no manual work
- [ ] **Delete unused data:** Old test data, temporary files
- [ ] **Consider Intelligent-Tiering:** If unsure about access patterns
- [ ] **Monitor costs:** CloudWatch metrics, AWS Billing dashboard

---

## Key Takeaways

1. **Storage classes exist for cost optimization** → Don't everything in Standard
2. **Access pattern determines class** → Hot data (Standard), Cold (Glacier), Unknown (Intelligent-Tiering)
3. **Lifecycle policies save money** → Automatic transitions + compliance
4. **Minimum storage duration matters** → Standard-IA = minimum 30 days
5. **Retrieval speed vs cost trade-off** → Instant (expensive) vs 12 hour (cheap)

---

## Hands-On Intuition Check ✓

After reading, you should know:

- [ ] Why Standard-IA shouldn't be accessed daily
- [ ] Cost-benefit of Glacier vs Standard for annual archival
- [ ] When One Zone-IA is acceptable
- [ ] How lifecycle policies reduce costs
- [ ] Why Deep Archive exists (compliance archives)

---

## Next Up

Ready to secure your data?

**→ [03-s3-security-versions.md](./03-s3-security-versions.md)** explains versioning, encryption, and access control

---

**Quick Reference: Cost Comparison (1000 GB, 1 year)**

| Class | Storage Cost | Access (4x/year) | Total | Use Case |
|-------|---|---|---|---|
| Standard | $276 | $0 | $276 | Daily access |
| Standard-IA | $150 | $40 | $190 | Monthly access |
| Glacier Instant | $48 | $120 | $168 | Quarterly archive |
| Glacier Flexible | $43 | $0 | $43 | Annual archive |
| Deep Archive | $12 | $0 | $12 | 7-year archive |

