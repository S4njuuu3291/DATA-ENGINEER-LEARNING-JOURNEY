# Module 3 Exercises: Glue Data Catalog & Crawlers

Hands-on labs untuk membangun metadata layer yang rapi dan production-ready.

> **Estimated Total Time:** 90-120 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Prerequisites:** Module 1 + 2

---

## 🧰 Setup Checklist

- [ ] AWS CLI configured
- [ ] S3 bucket available (data lake)
- [ ] Sample data uploaded (orders.csv in bronze)
- [ ] IAM permission: `glue:*`, `s3:*`, `iam:*`, `logs:*`

---

## ✅ Exercise 1: Create Glue Database (10 min)

**Goal:** Create database `bronze` in Glue Catalog.

```bash
aws glue create-database \
  --database-input '{"Name":"bronze","Description":"Raw data layer"}'
```

**Deliverable:** Database `bronze` appears in Glue Console.

---

## ✅ Exercise 2: Create Crawler for Bronze Orders (20 min)

**Goal:** Crawl `s3://<bucket>/bronze/orders/` and create table.

```bash
aws glue create-crawler \
  --name bronze-orders-crawler \
  --role GlueCrawlerRole \
  --database-name bronze \
  --targets S3Targets=[{Path="s3://<bucket>/bronze/orders/"}] \
  --schema-change-policy UpdateBehavior=UPDATE_IN_DATABASE,DeleteBehavior=DEPRECATE_IN_DATABASE
```

Run crawler:
```bash
aws glue start-crawler --name bronze-orders-crawler
```

**Deliverable:** Table `orders` created under database `bronze`.

---

## ✅ Exercise 3: Verify Partitions (15 min)

**Goal:** Confirm partitions discovered from folder structure.

```bash
aws glue get-partitions \
  --database-name bronze \
  --table-name orders
```

**Deliverable:** Partitions listed (year/month/day).

---

## ✅ Exercise 4: Schema Evolution (15 min)

**Goal:** Add new column `currency` to CSV and update catalog.

Steps:
1. Add column to CSV and upload new file to bronze.
2. Run crawler again.

```bash
aws glue start-crawler --name bronze-orders-crawler
```

**Deliverable:** Table schema updated with `currency` column.

---

## ✅ Exercise 5: Recrawl Policy (10 min)

**Goal:** Reduce cost by crawling only new folders.

```bash
aws glue update-crawler \
  --name bronze-orders-crawler \
  --recrawl-policy RecrawlBehavior=CRAWL_NEW_FOLDERS_ONLY
```

**Deliverable:** Recrawl policy set to new folders only.

---

## ✅ Exercise 6: EventBridge Trigger Crawler (20 min)

**Goal:** Trigger crawler automatically when new file arrives.

Steps:
1. Create EventBridge rule (bronze CSV uploads)
2. Create Lambda `start-crawler` with `glue:StartCrawler` permission
3. Add Lambda as EventBridge target

**Deliverable:** Upload new CSV → crawler starts automatically.

---

## ✅ Completion Checklist

- [ ] Glue database created
- [ ] Crawler runs successfully
- [ ] Table + partitions visible
- [ ] Schema evolution handled
- [ ] Recrawl policy optimized
- [ ] Event-driven crawler trigger works

---

**Next:** Module 4 (Glue ETL Jobs)
