# 02: Classifiers & Recrawl Strategy

> **Duration:** 45 minutes  
> **Difficulty:** ⭐⭐⭐ Intermediate  
> **Key Takeaway:** Classifiers determine how crawlers interpret files, and recrawl policy controls cost and schema drift.

---

## 🧪 Classifiers

### Built-in Classifiers

Glue automatically detects:
- CSV
- JSON
- Parquet
- ORC
- Avro

**Priority:** If multiple formats found, Glue picks the first classifier match (order matters).

---

### Custom Classifiers

Use when:
- File format is non-standard
- Logs have custom delimiters
- JSON has special structure

**Example: Custom CSV classifier**

```bash
aws glue create-classifier \
  --grok-classifier 'Name=orders-log,Classification=csv,Groks=["%{TIMESTAMP_ISO8601:timestamp} %{WORD:level} %{GREEDYDATA:message}"]'
```

**Note:** Grok classifiers are more common for log data (ex: CloudWatch logs).

---

## 🔄 Recrawl Strategy

Recrawl policy controls how crawler handles existing tables:

| Policy | Behavior | Use Case |
|--------|----------|----------|
| **CRAWL_EVERYTHING** | Rescan all data | Small datasets, dev |
| **CRAWL_NEW_FOLDERS_ONLY** | Only new partitions | Large datasets, production |
| **CRAWL_EVENT_MODE** | Use S3 events | Event-driven updates |

---

### Example: Set Recrawl Policy

```bash
aws glue update-crawler \
  --name bronze-orders-crawler \
  --recrawl-policy RecrawlBehavior=CRAWL_NEW_FOLDERS_ONLY
```

**Best practice:** Use `CRAWL_NEW_FOLDERS_ONLY` in production to reduce cost.

---

## 🧭 Schema Change Policy

Controls what happens when schema changes:

| UpdateBehavior | Effect |
|---------------|--------|
| **UPDATE_IN_DATABASE** | Update schema in Glue table |
| **LOG** | Log schema changes only |

| DeleteBehavior | Effect |
|---------------|--------|
| **DEPRECATE_IN_DATABASE** | Mark columns/tables deprecated |
| **DELETE_FROM_DATABASE** | Remove from catalog (dangerous) |
| **LOG** | Log changes only |

**Best practice:**
- Use `UPDATE_IN_DATABASE` + `DEPRECATE_IN_DATABASE`
- Avoid delete in production (can break queries)

---

## 💰 Cost Control Tips

1. **Narrow prefixes** (avoid bucket root)
2. **Use recrawl new folders only**
3. **Schedule during low traffic** (night)
4. **Avoid mixing formats under same prefix**

---

## 🧪 Hands-On Intuition Check

**Question:** Why is `CRAWL_EVERYTHING` dangerous in production?

<details>
<summary>Answer</summary>

It rescans all data every run.

Impact:
- High cost (many objects scanned)
- Long runtime
- Higher chance of schema changes overwriting stable metadata

Better: `CRAWL_NEW_FOLDERS_ONLY`.
</details>

---

## 📋 Summary

| Concept | Key Insight |
|---------|-------------|
| **Classifiers** | Determine how Glue interprets files |
| **Recrawl Policy** | Control cost and schema drift |
| **Schema Change Policy** | Decide how updates/deletes are handled |

---

## ⏭️ Next Steps

Next: [EventBridge Trigger Crawler](../03-automation/01-eventbridge-trigger-crawler.md)
