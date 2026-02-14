# 01: Why Glue Data Catalog Exists

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Data tanpa metadata = data yang tidak bisa ditemukan, tidak bisa di-query, dan tidak bisa di-govern. Glue Catalog adalah pusat metadata untuk seluruh data lake.

---

## 🔥 The Problem: Data Without Metadata

### Scenario: Data Lake Tanpa Catalog

Anda punya S3 data lake:
```
s3://data-lake/bronze/orders/2024-01-15/orders.csv
s3://data-lake/bronze/customers/2024-01-15/customers.csv
```

**Masalah utama:**
- **Athena tidak tahu** schema file tersebut (kolom, tipe data)
- **Glue Jobs tidak tahu** struktur data
- **Tidak ada discoverability** (data engineer lain tidak tahu isi data)
- **Tidak ada governance** (tidak tahu siapa owner, kualitas data)

**Tanpa metadata:** Query jadi manual dan fragile.

---

## ✅ The Solution: Glue Data Catalog

### What is Glue Data Catalog?

> **AWS Glue Data Catalog** adalah **managed metadata store** yang kompatibel dengan **Apache Hive Metastore**.

**Fungsi utama:**
1. **Registry metadata** (schema, partitions, format, location)
2. **Central reference** untuk Athena, Glue, Redshift Spectrum, EMR
3. **Governance foundation** (data ownership, access control, tagging)

---

### Glue Catalog vs Hive Metastore

| Feature | Hive Metastore (On-prem) | Glue Data Catalog |
|---------|---------------------------|------------------|
| **Management** | Self-managed | Fully managed (serverless) |
| **Scalability** | Manual tuning | Auto-scale |
| **Availability** | Depends on infra | Multi-AZ built-in |
| **Integration** | Hadoop ecosystem | Athena, Glue, Redshift Spectrum |
| **Cost** | Infrastructure + ops | Pay per request (very low) |

**Insight:** Glue Catalog = Hive Metastore as-a-Service.

---

## 🧠 What Metadata Lives in Glue Catalog?

Glue Catalog stores:

- **Database:** logical grouping of tables (ex: `bronze`, `silver`, `gold`)
- **Table:** schema definition (columns + types)
- **Partition:** metadata for each partition (ex: `year=2024/month=01/day=15`)
- **Location:** S3 path for data
- **Format:** CSV, JSON, Parquet, ORC
- **SerDe:** serialization/deserialization library
- **Properties:** custom metadata (owner, description, quality tags)

**Example Table Entry:**
```json
{
  "Name": "orders",
  "DatabaseName": "bronze",
  "StorageDescriptor": {
    "Location": "s3://data-lake/bronze/orders/",
    "InputFormat": "org.apache.hadoop.mapred.TextInputFormat",
    "OutputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
    "SerdeInfo": {
      "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
      "Parameters": {"separatorChar": ","}
    },
    "Columns": [
      {"Name": "order_id", "Type": "string"},
      {"Name": "customer_id", "Type": "string"},
      {"Name": "amount", "Type": "double"}
    ]
  },
  "PartitionKeys": [
    {"Name": "year", "Type": "string"},
    {"Name": "month", "Type": "string"},
    {"Name": "day", "Type": "string"}
  ]
}
```

---

## 📊 Why Catalog is Essential for Athena

**Without Glue Catalog:**
```sql
-- Athena can't query because no schema
SELECT * FROM s3://data-lake/bronze/orders/;  -- ❌ Not valid
```

**With Glue Catalog:**
```sql
-- Athena uses Glue Catalog metadata
SELECT * FROM bronze.orders WHERE year='2024' AND month='01';
```

**Benefit:** Athena doesn't need manual schema definition per query.

---

## 🧭 Metadata Enables Governance

**Why governance matters:**
- Who owns the table?
- Is the data reliable?
- Which pipelines depend on it?

**Glue Catalog supports:**
- **Tags:** `owner=data-team`, `quality=bronze` 
- **Descriptions:** human-readable context
- **Column comments:** clarify meaning
- **Integration with Lake Formation** (Module 9)

---

## 💰 Cost Model (Cheap but Non-Zero)

Glue Catalog pricing is **per request** (not per GB).  
This means **metadata operations are cheap**, but excessive crawler scans can create unnecessary requests.

**Example:**
- 100 tables, 1,000 partitions
- 1 crawler run/day
- Cost: **~$1-2/month**

**Main cost risk:** Crawlers scanning huge buckets unnecessarily.

---

## 🎯 Real Use Case: E-Commerce Data Lake

**S3 layout:**
```
bronze/orders/2024/01/15/orders.csv
silver/orders/year=2024/month=01/day=15/orders.parquet
```

**Glue Catalog:**
- `bronze.orders` table → CSV schema
- `silver.orders` table → Parquet schema
- Partitions: year/month/day

**Pipeline:**
1. Upload CSV to bronze
2. Crawler updates metadata
3. Athena queries metadata
4. Glue ETL uses metadata for transformations

**Without Catalog:**
- You manually define schema for each query
- Hard to discover partitions
- Inconsistent data formats

---

## ⚠️ Common Pitfalls

1. **No Catalog = No Query**  
   Athena/Glue require schema definition. Without catalog, every query is manual.

2. **Wrong partition layout**  
   If S3 folders are inconsistent, partitions won't load correctly.

3. **Crawler scope too wide**  
   Crawling entire bucket → slow + expensive.

4. **Schema drift**  
   Adding columns without proper handling leads to query failures.

---

## 🧪 Hands-On Intuition Check

**Question:** Why is Glue Catalog required if I can query CSV directly in Athena?

<details>
<summary>Answer</summary>

Athena can query CSV directly **only if you define schema manually** in each query or create an external table.

Glue Catalog provides:
- Persistent schema definitions
- Partition discovery
- Central metadata store for all tools

So, Glue Catalog = reusable metadata layer (saves time, prevents errors).
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Problem** | Data lake without metadata is invisible and unusable |
| **Solution** | Glue Data Catalog = managed Hive Metastore |
| **Value** | Enables Athena, Glue, Redshift Spectrum to query data consistently |
| **Cost** | Cheap per request, crawler scans drive cost |

---

## ⏭️ Next Steps

Next: [Catalog Objects & Metadata](./02-catalog-objects-and-metadata.md)
