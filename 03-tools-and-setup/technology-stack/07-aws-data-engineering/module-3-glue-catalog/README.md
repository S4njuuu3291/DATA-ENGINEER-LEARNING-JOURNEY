# Module 3: AWS Glue Data Catalog & Crawlers

> **Duration:** 4 hours  
> **Level:** ⭐⭐⭐ Intermediate  
> **Prerequisites:** Module 1 (S3, IAM, VPC) + Module 2 (Lambda/EventBridge)  
> **Author:** Data Engineering Curriculum  
> **Last Updated:** February 10, 2026

---

## 📚 Module Overview

Module ini fokus pada **metadata management** untuk data lake:

1. **Glue Data Catalog** → Metastore untuk semua data di S3
2. **Crawlers** → Auto-discovery schema & partitions
3. **Automation** → Trigger crawler setelah file masuk (EventBridge + Lambda)

**Why it matters:** Data tanpa metadata = data yang tidak bisa di-query. Glue Catalog adalah fondasi untuk Athena, Glue, dan Redshift Spectrum.

---

## 🎯 Learning Objectives

Setelah menyelesaikan module ini, Anda akan bisa:

- ✅ Explain peran Glue Data Catalog sebagai Hive Metastore
- ✅ Create database, table, dan partitions di Glue Catalog
- ✅ Configure crawler dengan scope yang aman (prefix-based)
- ✅ Control schema drift dan recrawl behavior
- ✅ Apply partitioning conventions yang konsisten
- ✅ Automate crawler run via EventBridge/Lambda
- ✅ Troubleshoot crawler failures (IAM, format, prefix)

---

## 📖 Learning Path

```
Day 1: Catalog Fundamentals
├─ Why Glue Catalog exists (45 min)
└─ Catalog objects & metadata (45 min)

Day 2: Crawlers & Schema Drift
├─ Crawlers how they work (45 min)
└─ Classifiers + recrawl strategy (45 min)

Day 3: Automation & Practice
├─ EventBridge trigger crawler (45 min)
└─ Exercises (90 min)

Total: ~3.5-4 hours
```

---

## 🗂️ Module Structure

### Part 1: Catalog (2 topics)

| Topic | File | Duration | Key Concepts |
|------|------|----------|--------------|
| **Why Glue Catalog** | [01-why-glue-catalog-exists.md](./01-catalog/01-why-glue-catalog-exists.md) | 45 min | Metadata layer, Hive Metastore, Athena integration |
| **Catalog Objects** | [02-catalog-objects-and-metadata.md](./01-catalog/02-catalog-objects-and-metadata.md) | 45 min | Databases, tables, partitions, storage descriptors |

### Part 2: Crawlers (2 topics)

| Topic | File | Duration | Key Concepts |
|------|------|----------|--------------|
| **Crawler Basics** | [01-crawlers-how-they-work.md](./02-crawlers/01-crawlers-how-they-work.md) | 45 min | Crawler lifecycle, targets, outputs |
| **Classifiers + Recrawl** | [02-classifiers-and-recrawl.md](./02-crawlers/02-classifiers-and-recrawl.md) | 45 min | Custom classifiers, schema drift, cost control |

### Part 3: Automation (1 topic)

| Topic | File | Duration | Key Concepts |
|------|------|----------|--------------|
| **EventBridge Trigger** | [01-eventbridge-trigger-crawler.md](./03-automation/01-eventbridge-trigger-crawler.md) | 45 min | Trigger crawler on S3 events, Lambda wrapper |

---

## 🧪 Hands-On Exercises

**File:** [Module 3 Exercises](../exercises/module-3-glue-catalog-exercises.md)

**6 exercises total (~90 minutes):**

1. Create Glue database
2. Crawl Bronze data (orders.csv)
3. Verify table & partitions
4. Add new column (schema evolution)
5. Configure recrawl policy
6. Trigger crawler via EventBridge + Lambda

---

## 📊 Assessment Checklist

Anda siap untuk Module 4 jika bisa:

- [ ] Menjelaskan fungsi Glue Catalog dalam data lake
- [ ] Membuat database dan table di Glue
- [ ] Menjalankan crawler yang scoped (tidak scan seluruh bucket)
- [ ] Mengelola schema drift (add columns safely)
- [ ] Menggunakan partition layout yang konsisten
- [ ] Men-trigger crawler otomatis via EventBridge

---

## 🔗 Quick Links

- [Module 3 Exercises](../exercises/module-3-glue-catalog-exercises.md)
- [Glue Catalog Cheatsheet](../cheatsheets/aws-glue-catalog-cheatsheet.md)
- [Back to Module 2](../module-2-lambda-events/README.md)
- [Back to Roadmap](../README.md)

---

**Ready? Start with [01-why-glue-catalog-exists.md](./01-catalog/01-why-glue-catalog-exists.md) →**
