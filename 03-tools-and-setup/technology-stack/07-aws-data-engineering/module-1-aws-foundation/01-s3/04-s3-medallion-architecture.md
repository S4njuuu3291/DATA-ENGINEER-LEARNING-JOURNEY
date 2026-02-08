# 04. S3 Medallion Architecture: Data Lake Design

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐ (Intermediate)  
> **Key Takeaway:** Medallion pattern (Bronze → Silver → Gold) is the industry standard for organizing data lakes

---

## The Problem: Unorganized S3 = Data Swamp

### Bad Example: Chaotic Bucket Structure

```
s3://my-company-datalake/
├─ orders.csv
├─ orders_v2.csv
├─ orders_final.csv
├─ orders_REAL_final.csv  ← Which one is correct?
├─ customer_data.json
├─ customer_data_backup.json
├─ processed_orders.csv
├─ processed_orders_from_john.csv
├─ 2024-01-15-analysis.csv
├─ analysis_v1.csv
├─ tmp_test_data/
├─ archive/
│  ├─ old_stuff.csv
│  └─ more_old_stuff/
└─ reports/
   ├─ weekly_report.xlsx
   └─ ...
```

**Problems:**
- ❌ Where's the "source of truth"?
- ❌ Which file is the latest?
- ❌ How do I trace data lineage?
- ❌ Why are there 4 versions of orders.csv?
- ❌ Can't automate processing (don't know folder structure)
- ❌ Difficult to implement governance/security
- ❌ Analytics team confused (which dataset to query?)

This is a "data swamp" - lots of data, no organization.

---

## The Solution: Medallion Architecture

**Medallion = 3-tier data organization: Bronze → Silver → Gold**

```
┌─────────────────────────────────────────┐
│  GOLD LAYER (Clean, Business-Ready)    │
│  ✅ Aggregated, validated, optimized    │
│  ✅ Facts & dimensions for BI           │
│  ✅ Ready for dashboards & reports      │
│  ✅ Governed, versioned schema          │
└─────────────────────────────────────────┘
                    ↑
                (Transformed)
                    ↑
┌─────────────────────────────────────────┐
│  SILVER LAYER (Cleansed, Integrated)    │
│  ✅ Deduplicated, validated             │
│  ✅ Joins across sources (Orders + Cust)│
│  ✅ Business rules applied              │
│  ✅ Quality checks passed               │
└─────────────────────────────────────────┘
                    ↑
                (Cleaned)
                    ↑
┌─────────────────────────────────────────┐
│  BRONZE LAYER (Raw, Immutable)          │
│  ✅ Exactly as arrived from source      │
│  ✅ Read-only (object locking)          │
│  ✅ Full history (versioning enabled)   │
│  ✅ Minimal validation                  │
└─────────────────────────────────────────┘
```

---

## Bronze Layer: Landing Zone

### Purpose

Raw data, exactly as received from sources. No transformations.

### Characteristics

```
s3://data-lake/bronze/
├─ source_name/
│  ├─ ecommerce/
│  │  ├─ 2024-01-15/
│  │  │  ├─ orders.csv
│  │  │  ├─ customers.csv
│  │  │  └─ products.csv
│  │  ├─ 2024-01-16/
│  │  │  ├─ orders.csv
│  │  │  ├─ customers.csv
│  │  │  └─ products.csv
│  │  └─ ...
│  │
│  ├─ api-logs/
│  │  ├─ 2024-01-15/
│  │  │  └─ requests.json.gz
│  │  └─ 2024-01-16/
│  │      └─ requests.json.gz
│  │
│  └─ kafka-events/
│     ├─ 2024-01-15/
│     │  └─ clickstream.parquet
│     └─ 2024-01-16/
│         └─ clickstream.parquet
```

### Bronze Properties

```
✅ Organization: By source, then by date (date partition)
✅ Format: As-is (CSV, JSON, Parquet, whatever arrived)
✅ Immutability: Object lock enabled (can't modify/delete)
✅ Validation: Minimal (schema check only)
✅ Retention: Keep forever (compliance archive)
✅ Access: Read-only (data engineers only)
✅ Storage class: Standard → Glacier (old data) via lifecycle
```

### Real Example: E-commerce Orders

**Source system:** ERP database (sends daily API export)

```
Raw JSON from API:
{
  "order_id": "ORD-001",
  "customer_id": "CUST-123",
  "order_date": "2024-01-15T14:30:00Z",
  "status": "completed",
  "total": 99.99
}

Bronze storage:
s3://lake/bronze/ecommerce/2024-01-15/orders.json
↑ Stored exactly as received (no transformation)
```

### Why Bronze Exists

1. **Recovery:** Source system crashes? You have full backup in Bronze
2. **Audit trail:** "Show me all customer data as of Feb 1, 2024"
3. **Reprocessing:** "Rerun data quality on all 2023 data"
4. **Compliance:** "Prove you have unchanged source data" (audit trail)

---

## Silver Layer: Clean, Validated Data

### Purpose

Cleaned, deduplicated, validated data. Business-logic applied.

### Characteristics

```
s3://data-lake/silver/
├─ business_domain/
│  ├─ customers/
│  │  ├─ year=2024/month=01/day=15/customers.parquet
│  │  ├─ year=2024/month=01/day=16/customers.parquet
│  │  └─ ...
│  │
│  ├─ orders/
│  │  ├─ year=2024/month=01/day=15/orders.parquet
│  │  ├─ year=2024/month=01/day=16/orders.parquet
│  │  └─ ...
│  │
│  └─ order_items/
│     ├─ year=2024/month=01/day=15/order_items.parquet
│     └─ ...
```

### Silver Properties

```
✅ Organization: By business domain, then date/time partitions
✅ Format: Parquet (compressed, optimized for analytics)
✅ Schema: Explicit & documented (parquet schema)
✅ Validation: Quality checks applied
   - NULL checks
   - Foreign key relationships
   - Business rule constraints
✅ Deduplication: Removed duplicate records
✅ Cleansing: Fixed common data issues
   - Trimmed whitespace
   - Standardized date formats
   - Fixed case (upper/lower)
✅ Access: Read for analytics, write for pipelines
✅ Retention: Keep 2-3 years (cost optimization)
```

### Transformations Applied

```
Raw Order (Bronze):
{
  "order_id": "ORD-001",
  "customer_id": " CUST-123 ",        ← Extra spaces
  "order_date": "01/15/2024",         ← Non-standard format
  "status": "Completed",              ← Mixed case
  "total": " 99.99 "                  ← String with spaces
}

Silver Order (Cleaned):
{
  "order_id": "ORD-001",
  "customer_id": "CUST-123",          ← Trimmed
  "order_date": "2024-01-15",         ← ISO format
  "status": "COMPLETED",              ← Uppercase
  "total": 99.99,                     ← Numeric
  "inserted_at": "2024-01-15T12:00Z"  ← Processing timestamp
}
```

### Example Transformation Job

**ETL Job: Bronze Orders → Silver Orders**

```python
# Glue job reads from Bronze
bronze_orders = glueContext.create_dynamic_frame.from_options(
    format_options={"multiline": False},
    connection_type="s3",
    format="json",
    connection_options={
        "paths": ["s3://lake/bronze/ecommerce/2024-01-15/orders.json"],
        "recurse": True,
    },
    transformation_ctx="bronze_orders",
)

# Apply transformations
clean_orders = ApplyMapping.apply(
    frame=bronze_orders,
    mappings=[
        ("order_id", "string", "order_id", "string"),
        ("customer_id", "string", "customer_id", "string"),
        ("order_date", "string", "order_date", "date"),
        ("status", "string", "status", "string"),
        ("total", "string", "total", "double"),
    ],
    transformation_ctx="clean_orders",
)

# Write to Silver (Parquet, partitioned by date)
glueContext.write_dynamic_frame.from_options(
    frame=clean_orders,
    connection_type="s3",
    connection_options={
        "path": "s3://lake/silver/customers/year=2024/month=01/day=15/",
        "partitionKeys": [],
    },
    format="parquet",
    transformation_ctx="silver_orders",
)
```

---

## Gold Layer: Analytics-Ready Dimensions & Facts

### Purpose

Business-ready datasets. Optimized for analytics & BI tools.

### Characteristics

```
s3://data-lake/gold/
├─ fact_tables/
│  ├─ fact_orders/
│  │  ├─ year=2024/month=01/day=15/fact_orders.parquet
│  │  └─ ...
│  │
│  ├─ fact_order_items/
│  │  ├─ year=2024/month=01/day=15/fact_order_items.parquet
│  │  └─ ...
│  │
│  └─ fact_daily_sales/
│     ├─ year=2024/month=01/day=15/daily_sales.parquet
│     └─ ...
│
├─ dimension_tables/
│  ├─ dim_customer/
│  │  └─ dim_customer.parquet (slowly changing dimension)
│  │
│  ├─ dim_product/
│  │  └─ dim_product.parquet
│  │
│  └─ dim_date/
│     └─ dim_date.parquet
│
└─ metrics/
   ├─ daily_revenue/
   │  ├─ year=2024/month=01/day=15/revenue.parquet
   │  └─ ...
   │
   └─ customer_lifetime_value/
      └─ clv.parquet
```

### Gold Properties

```
✅ Modeling: Star schema (facts + dimensions)
✅ Granularity: Event-level (each order item) OR aggregated (daily sales)
✅ Format: Parquet (optimized columns, compressed)
✅ Partitioning: By date for time-series (querying last 30 days is fast)
✅ Statistics: Pre-calculated metrics (revenue, counts, etc.)
✅ Validation: Heavy validation (BI-team confidence)
✅ Slowly Changing Dimensions: Handle customer updates (SCD Type 2)
✅ Access: Read-only (Athena, Redshift, BI tools)
✅ Retention: Keep 5+ years (long-term analytics)
```

### Real Example: Daily Sales Metric

**Input:** Individual orders from Silver

```
Silver fact_orders:
order_id, customer_id, order_date, total
1, CUST-001, 2024-01-15, 100
2, CUST-002, 2024-01-15, 50
3, CUST-003, 2024-01-15, 75
4, CUST-001, 2024-01-15, 60
```

**Aggregated:** Gold daily sales metric

```
Gold daily_revenue:
date, total_orders, total_revenue, avg_order_value
2024-01-15, 4, 285, 71.25
```

**Benefits:**
- Dashboards query aggregated metric (fast)
- Instead of scanning 10 million orders
- Pre-calculated = ready for visualization

---

## Partitioning Strategy: The Secret Sauce

### Why Partition?

```
❌ Query all 1 billion orders to find Jan 2024 orders:
SELECT SUM(total) FROM gold.fact_orders
WHERE year=2024 AND month=01
→ Scans 1 billion rows, takes 30 seconds

✅ Query only Jan 2024 partition:
→ Scans 100 million rows, takes 3 seconds (10x faster)
→ Cost: 10x cheaper (charged per data scanned)
```

### Date Partitioning (Most Common)

```
s3://lake/silver/orders/
├─ year=2024/month=01/day=15/orders.parquet
├─ year=2024/month=01/day=16/orders.parquet
├─ year=2024/month=02/day=01/orders.parquet
└─ ...

Query: "Give me Jan 15 data"
→ Reads only: year=2024/month=01/day=15/orders.parquet
→ Ignores other dates
→ Fast & cheap
```

### Multi-Level Partitioning

```
s3://lake/silver/orders/
├─ region=NA/
│  ├─ year=2024/
│  │  ├─ month=01/
│  │  │  ├─ day=15/orders.parquet
│  │  │  ├─ day=16/orders.parquet
│  │  │  └─ ...
│  │  └─ ...
├─ region=EU/
│  ├─ year=2024/
│  │  ├─ month=01/
│  │  │  └─ ...
```

**Benefits:**
- Query "EU Jan 15 orders" = super fast
- Only reads matching partitions
- Can even delete old regions' old data

---

## Data Lineage & Traceability

### How to Track Data Flow

Every object should have metadata showing source:

```
Bronze:
s3://lake/bronze/ecommerce/2024-01-15/orders.json
  └─ Source: ecommerce API
  └─ Ingested: 2024-01-15 03:00 UTC
  └─ Record count: 50,000

Silver:
s3://lake/silver/customers/year=2024/month=01/day=15/orders.parquet
  └─ Source: bronze/ecommerce/...
  └─ Processed: 2024-01-15 04:00 UTC
  └─ Validations: ✅ No NULLs, ✅ Order ID unique
  └─ Record count: 49,998 (2 rejected as invalid)

Gold:
s3://lake/gold/fact_orders/year=2024/month=01/day=15/fact_orders.parquet
  └─ Source: silver/customers/...
  └─ Aggregated: 2024-01-15 05:00 UTC
  └─ Validations: ✅ Fact table constraints passed
  └─ Record count: 49,998
```

**Benefit:** If BI dashboard shows wrong number, can trace backwards:
- "That number came from Gold metric X"
- "Which came from Silver order data Y"
- "Which came from Bronze raw data Z"

---

## Storage Classes by Layer

### Cost Optimization Across Layers

```
Bronze (Raw, keep forever):
- First 30 days: Standard (data might be reprocessed)
- After 30 days: Glacier (rarely accessed, archive)
- After 2 years: Deep Archive (compliance only)
- Retention: 7+ years (legal hold)
- Expected cost: $0.05/month per 1000 GB

Silver (Cleansed, keep 2-3 years):
- First 3 months: Standard (analytics team queries)
- After 3 months: Standard-IA or Glacier
- After 3 years: Delete (regenerate if needed)
- Expected cost: $0.20/month per 1000 GB

Gold (Ready for BI, keep 5+ years):
- Always Standard (dashboards query real-time)
- After 5 years: Standard-IA (historical analysis)
- Expected cost: $0.60/month per 1000 GB
```

---

## Medallion Architecture Decision Tree

```
Question: Where should my dataset go?

├─ Is it raw data, exactly as arrived from source?
│  └─ YES → BRONZE ✅
│     └─ Immutable, versioned, archived
│
├─ Has it been cleaned & validated?
│  └─ YES → SILVER ✅
│     └─ Deduplicated, quality checked, standard format
│
├─ Is it ready for dashboards & BI tools?
│  └─ YES → GOLD ✅
│     └─ Star schema, aggregated, optimized
│
└─ Is it temporary (test data, exploration)?
   └─ YES → Create separate "sandbox" folder (outside medallion)
      └─ Ephemeral, no governance needed
```

---

## Real Enterprise Example: 3-Tier Pipeline

**Scenario:** Retail company, 5 data sources, 10 analysts

```
Daily Pipeline:

1️⃣ INGESTION (Bronze)
   └─ Lambda function: Pull from ERP, API, data warehouse
   └─ Store in: s3://lake/bronze/ecommerce/YYYY/MM/DD/orders.json
   └─ Storage class: Standard
   └─ Versioning: ON (enable recovery)

2️⃣ TRANSFORMATION (Bronze → Silver)
   └─ Glue job runs 02:00 AM (after ingestion complete)
   └─ Reads: bronze/ecommerce/YYYY/MM/DD/orders.json
   └─ Cleans: remove dupes, fix dates, validate FKs
   └─ Writes: silver/customers/year=YYYY/month=MM/day=DD/orders.parquet
   └─ Storage class: Standard (analysts query daily)

3️⃣ AGGREGATION (Silver → Gold)
   └─ dbt job runs 03:00 AM
   └─ Reads: silver/customers/...orders.parquet
   └─ Aggregates: daily revenue, top products, customer cohorts
   └─ Writes: gold/fact_tables/daily_sales.parquet
   └─ Storage class: Standard (dashboards run real-time)

4️⃣ COST OPTIMIZATION (Lifecycle)
   └─ Bronze: Move to Glacier after 30 days
   └─ Silver: Delete after 3 years (re-create if needed)
   └─ Gold: Keep 5 years, then Standard-IA

Result:
✅ Data engineers see raw data (Bronze debugging)
✅ Analytics see clean data (Silver queries)
✅ Business see ready metrics (Gold dashboards)
✅ Cost optimized (right storage class per layer)
✅ Traceable (can see lineage Bronze → Silver → Gold)
```

---

## Key Takeaways

1. **Bronze = Landing zone** (raw, immutable, forever)
2. **Silver = Clean & validated** (business logic applied, 2-3 year retention)
3. **Gold = Analytics-ready** (facts, dimensions, optimized for BI)
4. **Partitioning = Speed & Cost** (query only what you need)
5. **Lineage = Traceability** (know where every number came from)

---

## Hands-On Intuition Check ✓

After reading, you should know:

- [ ] Why Bronze data should be immutable
- [ ] What transformations happen in Silver layer
- [ ] Difference between fact & dimension tables (Gold)
- [ ] How partitioning speeds up queries
- [ ] Cost benefits of medallion architecture

---

## Next Phase

Ready to secure access to this data architecture?

**→ Next module: [02-iam/](../02-iam/)** explains how to grant permissions (who accesses which layer)

---

## References

- **Medallion Architecture (Databricks):** Industry standard pattern
- **Star Schema (Kimball):** Gold layer modeling approach
- **Slowly Changing Dimensions:** Type 1 (overwrite), Type 2 (versioning)

