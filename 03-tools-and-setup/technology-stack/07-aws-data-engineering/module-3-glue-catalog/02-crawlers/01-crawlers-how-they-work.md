# 01: Crawlers - How They Work

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Crawlers scan S3 data, infer schema, and update Glue Catalog. Their power is automation; their risk is cost and uncontrolled schema changes.

---

## 🤖 What is a Crawler?

> **Crawler = Glue job that scans data sources** (S3, JDBC, DynamoDB) and automatically creates/updates tables in Glue Catalog.

### What Crawlers Do

1. **Scan data** in S3 paths
2. **Infer schema** (columns, types)
3. **Detect partitions** from folder structure
4. **Create or update Glue tables**

---

## 🧩 Crawler Components

### 1) Data Store
Where to crawl:
- S3 bucket/prefix
- JDBC connection
- DynamoDB table

**Example:** `s3://data-lake/bronze/orders/`

---

### 2) IAM Role

Crawler needs permission to read S3 and write to Glue Catalog.

Minimal permissions:
- `s3:GetObject` on target prefix
- `glue:CreateTable`, `glue:UpdateTable`, `glue:GetDatabase`

---

### 3) Classifiers

Classifiers decide **file format**:
- Built-in: CSV, JSON, Parquet, Avro, ORC
- Custom: Regex-based for logs or proprietary format

Crawler runs classifiers in order (top priority first).

---

### 4) Output

Crawler updates Glue Catalog:
- Creates database (if configured)
- Creates new tables
- Updates schema for existing tables

---

## 🔄 Crawler Lifecycle

```
Crawler Run
  ├─ 1. Scan S3 paths
  ├─ 2. Classify file format
  ├─ 3. Infer schema
  ├─ 4. Detect partitions
  └─ 5. Create/update Glue tables
```

**Run modes:**
- On-demand
- Scheduled (cron/rate)
- Triggered by EventBridge/Lambda

---

## ✅ Example: Create Crawler (AWS CLI)

```bash
aws glue create-crawler \
  --name bronze-orders-crawler \
  --role GlueCrawlerRole \
  --database-name bronze \
  --targets S3Targets=[{Path="s3://data-lake/bronze/orders/"}] \
  --schema-change-policy UpdateBehavior=UPDATE_IN_DATABASE,DeleteBehavior=DEPRECATE_IN_DATABASE
```

**Key parameters:**
- `--database-name`: where tables will be created
- `--targets`: S3 prefix to scan
- `schema-change-policy`: what to do if schema changes

---

## ⚖️ Crawler vs Manual Table Creation

| Task | Crawler | Manual Table |
|------|---------|--------------|
| Schema discovery | ✅ Automatic | ❌ Manual |
| Partition discovery | ✅ Automatic | ❌ Manual |
| Schema stability | ❌ Can drift | ✅ Controlled |
| Cost | Moderate (scan) | Low (one-time) |
| Best for | Raw/bronze | Silver/Gold stable datasets |

**Best practice:**
- Use crawlers for **bronze layer** (raw, often messy)
- Use manual table definition for **silver/gold** (stable schema)

---

## 🧯 Common Failures

1. **Permission denied**  
   - Missing `s3:GetObject` or `glue:CreateTable`

2. **Wrong prefix**  
   - Crawler scans entire bucket (slow + expensive)

3. **Multiple formats**  
   - Mixing CSV + JSON under same prefix → wrong schema

4. **Schema drift**  
   - New columns added → crawler updates schema unexpectedly

---

## 🧪 Hands-On Intuition Check

**Question:** Why shouldn't you point a crawler at the bucket root?

<details>
<summary>Answer</summary>

Because crawler scans EVERYTHING under the prefix. Bucket root = entire data lake.

Risks:
- Long runtime (hours)
- High cost (many objects scanned)
- Confusing metadata (multiple unrelated datasets merged)

Best practice: point crawler to specific domain prefix (ex: `s3://data-lake/bronze/orders/`).
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Crawler** | Automates schema + partition discovery |
| **IAM Role** | Must read S3 + write Glue Catalog |
| **Classifier** | Detects file format |
| **Risk** | Schema drift + cost if prefix too wide |

---

## ⏭️ Next Steps

Next: [Classifiers & Recrawl Strategy](./02-classifiers-and-recrawl.md)
