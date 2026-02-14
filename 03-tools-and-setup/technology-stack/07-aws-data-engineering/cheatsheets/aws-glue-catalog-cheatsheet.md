# AWS Glue Data Catalog Cheatsheet

Quick reference for Glue Data Catalog databases, tables, crawlers, and partitions.

---

## Glue Catalog Basics (CLI)

### Create Database

```bash
aws glue create-database \
  --database-input '{"Name":"bronze","Description":"Raw data layer"}'
```

### List Databases

```bash
aws glue get-databases
```

### Create Table (Manual)

```bash
aws glue create-table \
  --database-name bronze \
  --table-input file://table_input.json
```

### Get Table

```bash
aws glue get-table --database-name bronze --name orders
```

---

## Crawlers

### Create Crawler

```bash
aws glue create-crawler \
  --name bronze-orders-crawler \
  --role GlueCrawlerRole \
  --database-name bronze \
  --targets S3Targets=[{Path="s3://data-lake/bronze/orders/"}] \
  --schema-change-policy UpdateBehavior=UPDATE_IN_DATABASE,DeleteBehavior=DEPRECATE_IN_DATABASE
```

### Start Crawler

```bash
aws glue start-crawler --name bronze-orders-crawler
```

### Get Crawler

```bash
aws glue get-crawler --name bronze-orders-crawler
```

### Update Recrawl Policy

```bash
aws glue update-crawler \
  --name bronze-orders-crawler \
  --recrawl-policy RecrawlBehavior=CRAWL_NEW_FOLDERS_ONLY
```

---

## Partitions

### List Partitions

```bash
aws glue get-partitions \
  --database-name bronze \
  --table-name orders
```

### Add Partition (Manual)

```bash
aws glue create-partition \
  --database-name bronze \
  --table-name orders \
  --partition-input file://partition_input.json
```

---

## Schema Evolution

### Add Column (Update Table)

```bash
aws glue update-table \
  --database-name bronze \
  --table-input file://table_input.json
```

**Best practice:** Append columns only (avoid removing or changing types).

---

## IAM Permissions (Minimal)

### Crawler Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::data-lake",
        "arn:aws:s3:::data-lake/bronze/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:CreateTable",
        "glue:UpdateTable",
        "glue:GetDatabase",
        "glue:GetTable",
        "glue:GetPartitions"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|------|------|-----|
| `AccessDeniedException` | Missing IAM permissions | Add `s3:GetObject`, `glue:*` |
| `EntityNotFoundException` | Database/table not found | Verify database name and table name |
| Crawler creates multiple tables | Mixed formats in prefix | Separate prefixes per dataset |
| No partitions discovered | Wrong folder layout | Use `year=2024/month=01/day=15` format |

---

## Pro Tips

- Use crawlers for **bronze**, manual tables for **silver/gold**.
- Avoid crawling bucket root (expensive + noisy).
- Use `CRAWL_NEW_FOLDERS_ONLY` in production.
- Tag tables with `owner`, `data_quality`, `update_frequency`.

---

**Next:** Use this cheatsheet while doing Module 3 exercises.
