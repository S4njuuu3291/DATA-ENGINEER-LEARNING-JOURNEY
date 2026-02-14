# 02: Catalog Objects & Metadata

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Glue Catalog is not just a table list. Each table has storage descriptors, partitions, SerDe, and properties that control how tools interpret data.

---

## 🧩 Core Objects in Glue Catalog

### 1) Database

**Database = logical grouping of tables**

Examples:
- `bronze`, `silver`, `gold` (by layer)
- `finance`, `marketing`, `sales` (by domain)
- `dev`, `prod` (by environment)

**Best practice:** Use database per environment (dev/prod), then per domain.

---

### 2) Table

A Glue table includes:
- Schema (columns + types)
- S3 location
- File format (CSV, Parquet, JSON)
- SerDe (how to parse file)
- Partition keys
- Table properties

**Example (simplified):**
```json
{
  "Name": "orders",
  "DatabaseName": "bronze",
  "StorageDescriptor": {
    "Location": "s3://data-lake/bronze/orders/",
    "Columns": [
      {"Name": "order_id", "Type": "string"},
      {"Name": "customer_id", "Type": "string"},
      {"Name": "amount", "Type": "double"}
    ],
    "SerdeInfo": {
      "SerializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
      "Parameters": {"separatorChar": ","}
    }
  },
  "PartitionKeys": [
    {"Name": "year", "Type": "string"},
    {"Name": "month", "Type": "string"},
    {"Name": "day", "Type": "string"}
  ]
}
```

---

### 3) Partition

Partition = metadata entry pointing to a specific sub-path in S3.

**Example partition keys:** `year=2024/month=01/day=15`

**Partition location:**
```
s3://data-lake/bronze/orders/year=2024/month=01/day=15/
```

Glue Catalog stores a separate entry for each partition, which allows:
- Partition pruning (Athena scans only necessary data)
- Faster queries
- Cost reduction

---

## 🧠 Storage Descriptor (The Critical Part)

Storage descriptor defines **how to read the files**.

Key fields:

| Field | Purpose | Example |
|------|---------|---------|
| **Location** | S3 path | `s3://data-lake/bronze/orders/` |
| **InputFormat** | Reader class | `TextInputFormat` |
| **OutputFormat** | Writer class | `HiveIgnoreKeyTextOutputFormat` |
| **Serde** | Parser | `LazySimpleSerDe` |
| **Columns** | Schema | `order_id: string, amount: double` |

**If any of these wrong:** Query fails or returns garbage.

---

## 🧾 File Formats & SerDe

### CSV (Text)

- InputFormat: `TextInputFormat`
- SerDe: `LazySimpleSerDe`
- Separator: `,`

### JSON

- InputFormat: `TextInputFormat`
- SerDe: `JsonSerDe` (org.openx.data.jsonserde.JsonSerDe)

### Parquet

- InputFormat: `ParquetInputFormat`
- SerDe: `ParquetHiveSerDe`

**Best practice:** Use Parquet for silver/gold (columnar + compressed).

---

## 📌 Table Properties (Underrated)

Table properties help with governance & discoverability:

Examples:
- `owner`: data-team
- `data_quality`: bronze
- `contains_pii`: true
- `update_frequency`: daily

**Example:**
```bash
aws glue update-table \
  --database-name bronze \
  --table-input '{
    "Name": "orders",
    "Parameters": {
      "owner": "data-team",
      "data_quality": "bronze",
      "update_frequency": "daily"
    }
  }'
```

---

## 🔄 Schema Evolution Basics

Common schema changes:

| Change | Safe? | Notes |
|--------|-------|------|
| Add column | ✅ Safe | Default values for old data = NULL |
| Reorder columns | ✅ Safe (Parquet) | Not safe for CSV if relying on column position |
| Change type (int → string) | ✅ Safe | Widening types is safer |
| Change type (string → int) | ❌ Risky | Old data might be invalid |
| Drop column | ❌ Risky | Downstream queries may fail |

**Rule:** Always append new columns, never drop without migration.

---

## 🧪 Hands-On Intuition Check

**Question:** Why does Glue Catalog store storage descriptor details (SerDe, InputFormat), not just schema?

<details>
<summary>Answer</summary>

Because schema alone is not enough to read the file. Athena/Glue needs:
- File format (CSV, JSON, Parquet)
- How to parse it (SerDe)
- InputFormat (reader class)

Without these details, query engines don't know how to interpret bytes into columns.
</details>

---

## 📋 Summary

| Object | Role |
|--------|------|
| **Database** | Logical grouping of tables |
| **Table** | Schema + storage descriptor |
| **Partition** | Path-specific metadata for pruning |
| **Storage Descriptor** | Defines how to read files |
| **Table Properties** | Governance and discoverability |

---

## ⏭️ Next Steps

Next: [Crawlers Basics](../02-crawlers/01-crawlers-how-they-work.md)
