# Day 6: Output Modes - Bagaimana Streaming Menulis Hasil

## Real Problem: Hasil Berubah Seiring Waktu

**Batch thinking (simple):**
```python
result = df.groupBy("category").sum("amount")
result.write.parquet("output/")
# Write once, done ✓
```

**Streaming reality (complex):**
```
10:00 - Window [10:00-11:00] processing
  └─ Partial result: Electronics = $5,000

10:30 - More events arrive
  └─ Updated result: Electronics = $8,000

11:00 - Window closes
  └─ Final result: Electronics = $12,000

Question: Write output kapan? Bagaimana?
```

**Challenge:** Hasil terus berubah, output mode menentukan behavior.

---

## Three Output Modes: Fundamental Differences

### 1. Append Mode: Write-Once per Window

**Concept:** Output hanya ketika result FINAL (tidak akan berubah)

```
Window [10:00-11:00] with watermark 10 min:

10:30 - Partial sum = $5,000
  └─ Do NOT output (window belum final)

11:00 - Window closes
  └─ Do NOT output (waiting for late data)

11:10 - Watermark passes
  └─ Output: {window: [10:00-11:00], sum: $12,000} ✓
  └─ Guarantee: Value won't change

11:15 - Late event arrives (timestamp 10:45)
  └─ Dropped (watermark passed)
  └─ Output unchanged ✓
```

**Characteristics:**
- **Write once:** Each result written exactly once
- **Immutable:** Written results never updated
- **Delayed:** Wait for watermark before output
- **Use case:** Append-only sinks (files, logs, Kafka)

**Restrictions:**
- **MUST have watermark** (otherwise, kapan result "final"?)
- Tidak bisa tanpa aggregation watermark
- Tidak compatible dengan non-windowed aggregations

### 2. Update Mode: Rewrite Changed Results

**Concept:** Output setiap result berubah (continuous updates)

```
Window [10:00-11:00]:

10:15 - Events processed
  └─ Output: {window: [10:00-11:00], sum: $2,000}

10:30 - More events
  └─ Output: {window: [10:00-11:00], sum: $5,000}
  └─ Overwrites previous $2,000

11:00 - More events
  └─ Output: {window: [10:00-11:00], sum: $12,000}
  └─ Overwrites previous $5,000

11:10 - Watermark passes
  └─ Final: {window: [10:00-11:00], sum: $12,000}
```

**Characteristics:**
- **Multiple writes:** Same key written multiple times
- **Mutable:** Results updated as events arrive
- **Low latency:** Output immediately per micro-batch
- **Use case:** Dashboards, key-value stores, databases

**Requirements:**
- Sink must support **upserts** (update or insert)
- Key-based storage (overwrite by key)
- Examples: Redis, Cassandra, database tables

### 3. Complete Mode: Rewrite Entire Result Set

**Concept:** Output SEMUA results setiap micro-batch

```
Global aggregation (no windowing):

Batch 1:
  └─ Output: {Electronics: $5k, Clothing: $3k}

Batch 2 (new events):
  └─ Output: {Electronics: $8k, Clothing: $5k, Books: $1k}
  └─ Entire result table rewritten

Batch 3:
  └─ Output: {Electronics: $12k, Clothing: $7k, Books: $2k}
  └─ All categories again
```

**Characteristics:**
- **Full rewrite:** All results every time
- **Expensive:** Output size grows with state
- **Simple:** No partial updates, always complete picture
- **Use case:** Small result sets, real-time dashboards

**Restrictions:**
- Only untuk aggregations tanpa watermark
- Result set must fit in memory
- Impractical untuk large result sets

---

## Why Output Mode Choice Matters

### Use Case 1: Hourly Sales Report (Append)

**Requirement:** Immutable hourly summaries

```python
# Append mode
query = df \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(window("event_time", "1 hour")) \
    .agg(sum("amount")) \
    .writeStream \
    .outputMode("append") \
    .format("parquet") \
    .start("output/sales/")
```

**Output:**
```
output/sales/
├── hour=2024-01-15-10/
│   └── part-00000.parquet  (written once at 11:10)
├── hour=2024-01-15-11/
│   └── part-00000.parquet  (written once at 12:10)
```

**Benefit:** 
- Files immutable (safe untuk downstream consumers)
- No overwrites (efficient storage)
- Historical data stable

### Use Case 2: Live Dashboard (Update)

**Requirement:** Real-time metrics yang terus update

```python
# Update mode
query = df \
    .withWatermark("event_time", "5 minutes") \
    .groupBy("category", window("event_time", "5 minutes")) \
    .agg(sum("amount"), count("*")) \
    .writeStream \
    .outputMode("update") \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://...") \
    .option("dbtable", "live_metrics") \
    .start()
```

**Database table:**
```
live_metrics:
category    | window_start | sum    | count
------------|--------------|--------|-------
Electronics | 10:00        | 5000   | 120    (updated 5x)
Clothing    | 10:00        | 3000   | 80     (updated 3x)
```

**Benefit:**
- Low latency (immediate updates)
- Dashboard shows current state
- No historical rewrites

### Use Case 3: Real-Time Leaderboard (Complete)

**Requirement:** Top 10 users saat ini

```python
# Complete mode (no windowing)
query = df \
    .groupBy("user_id") \
    .agg(sum("score").alias("total_score")) \
    .orderBy(desc("total_score")) \
    .limit(10) \
    .writeStream \
    .outputMode("complete") \
    .format("memory") \
    .queryName("leaderboard") \
    .start()
```

**Output (in-memory table):**
```
Every micro-batch:
user_id | total_score
--------|------------
user_A  | 15000       
user_B  | 12000       (entire top 10 rewritten)
user_C  | 11500       
...
```

**Benefit:**
- Always complete snapshot
- Simple query (SELECT * FROM leaderboard)
- No complex merge logic

---

## Idempotent Sinks: Mengapa Penting

### Problem: Non-Idempotent Append

**Scenario: File sink dengan at-least-once**

```
Batch 100: Process events, write file
  └─ output/part-00100.parquet created ✓

Crash before checkpoint ✗

Recovery: Reprocess batch 100
  └─ output/part-00100-retry.parquet created
  └─ Duplicate data! ✗

Result: Same events di 2 files
```

**Impact:** Downstream reads duplicate data → wrong totals

### Solution 1: Idempotent Writes (Key-Based)

**Database dengan primary key:**

```sql
-- Update mode dengan upsert
INSERT INTO metrics (window, category, sum)
VALUES ('10:00', 'Electronics', 5000)
ON CONFLICT (window, category) 
DO UPDATE SET sum = 5000;

-- Reprocess batch → same key overwritten
-- No duplicates ✓
```

**Idempotent = rerun produces same result**

### Solution 2: Exactly-Once File Sink

**Spark file sink dengan micro-batch ID:**

```
output/
├── _spark_metadata/
│   └── 0  (batch 0 committed)
│   └── 1  (batch 1 committed)
├── part-00000-batch-0.parquet
├── part-00001-batch-1.parquet

Recovery:
├─ Check _spark_metadata/
├─ Batch 100 not committed
└─ Rewrite batch 100, same filename
   (atomic rename ensures no duplicate)
```

**Spark handles deduplication internally untuk file sinks**

---

## Databases as Sinks: Trickiness

### Challenge 1: Transaction Boundaries

**Micro-batch processing:**

```
Batch N:
├─ 1000 events processed
├─ Write to database (1000 INSERTs)
└─ Crash before checkpoint ✗

Recovery:
├─ Reprocess batch N
└─ Another 1000 INSERTs
   Result: 2000 rows (duplicates) ✗
```

**Solution: Transactional writes dengan idempotent key**

```scala
df.foreachBatch { (batchDF, batchId) =>
  batchDF.write
    .mode("append")  // but with upsert semantics
    .jdbc(url, table, props)
  
  // Database transaction:
  // - All writes succeed or rollback
  // - Duplicate batchId → skip (idempotent)
}
```

### Challenge 2: Slow Writes Block Processing

**Problem:**

```
Micro-batch latency:
├─ Processing: 2 seconds
├─ Database write: 8 seconds (slow!)
└─ Total: 10 seconds

Throughput: 1 batch / 10 sec
Impact: Backlog grows
```

**Solutions:**
- **Batching:** Write multiple rows per transaction
- **Async writes:** Write saat processing next batch
- **Connection pooling:** Reuse DB connections
- **Consider streaming database** (ClickHouse, TimescaleDB)

### Challenge 3: Schema Mismatches

**Problem:**

```
Streaming DataFrame schema:
├─ event_time: Timestamp
├─ category: String
├─ amount: Double

Database table:
├─ event_time: TIMESTAMP
├─ category: VARCHAR(50)  ← truncation risk
├─ amount: DECIMAL(10,2)  ← precision mismatch
```

**Impact:** Data loss, silent failures

**Prevention:**
- Explicit schema validation
- Test writes dengan edge cases
- Monitor write errors

---

## Files vs Databases: Trade-offs

### Files (Parquet, JSON, CSV)

**Pros:**
- **Scalable:** Parallel writes, unlimited storage
- **Immutable:** Append-only, safe untuk analytics
- **Cheap:** Object storage (S3) cost-effective
- **Batch-friendly:** Downstream batch processing easy

**Cons:**
- **No updates:** Cannot modify written files (append mode only)
- **Latency:** Output delayed (wait for watermark)
- **Query:** Tidak real-time queryable (need load ke database)

**Best for:**
- Data lake pipelines
- Historical archives
- Batch analytics

### Databases (PostgreSQL, MySQL, Cassandra)

**Pros:**
- **Queryable:** Immediate SQL access
- **Updates:** Support update mode (mutable results)
- **Transactions:** ACID guarantees
- **Real-time:** Low-latency dashboards

**Cons:**
- **Scalability:** Write throughput limited
- **Cost:** Higher operational cost
- **Complexity:** Transaction management, connection pooling
- **Backpressure:** Slow writes block pipeline

**Best for:**
- Real-time dashboards
- Operational metrics
- Interactive queries

### Hybrid Approach (Lambda Architecture)

```
Stream → ┬─→ Database (real-time, update mode)
         │   └─ Live dashboard, alerts
         │
         └─→ Files (batch, append mode)
             └─ Historical analytics, reprocessing
```

**Benefits:**
- Real-time AND batch analytics
- Files untuk accuracy (reprocessable)
- Database untuk speed (low latency)

---

## Rules for Choosing Output Modes

### Decision Tree:

**Question 1: Perlu update existing results?**
- NO → Append mode
- YES → Question 2

**Question 2: Result set size?**
- Small (<1M rows) → Complete mode
- Large → Update mode

**Question 3: Sink type?**
- Append-only (files, Kafka) → Append mode
- Key-value store → Update or Complete
- Memory table → Complete

### Mode Requirements:

**Append Mode:**
```
Requirements:
✓ Windowed aggregation ATAU non-aggregation
✓ Watermark defined (untuk aggregation)
✓ Sink supports append (files, Kafka, databases)

Restrictions:
✗ Tidak untuk non-windowed aggregations
✗ Tidak untuk complete result updates
```

**Update Mode:**
```
Requirements:
✓ Aggregation (windowed atau non-windowed)
✓ Sink supports upserts (databases, KV stores)

Restrictions:
✗ Tidak untuk append-only sinks (file overwrites expensive)
```

**Complete Mode:**
```
Requirements:
✓ Aggregation tanpa watermark
✓ Result set fit memory
✓ Sink dapat handle rewrites

Restrictions:
✗ Tidak scalable untuk large results
✗ High write amplification
```

---

## Common Mistakes When Writing Output

### Mistake 1: Append Mode Tanpa Watermark

```python
# BROKEN: Append mode, no watermark
df.groupBy("category").sum("amount") \
  .writeStream \
  .outputMode("append") \
  .start()

# Error: "Append mode requires watermark for aggregation"
```

**Fix:** Add watermark atau use update/complete mode

```python
df.withWatermark("event_time", "10 minutes") \
  .groupBy("category", window("event_time", "1 hour")) \
  .sum("amount") \
  .writeStream \
  .outputMode("append") \
  .start()
```

### Mistake 2: Complete Mode untuk Large State

```python
# BAD: Complete mode, millions of keys
df.groupBy("user_id").sum("amount") \
  .writeStream \
  .outputMode("complete") \
  .format("console") \
  .start()

# Problem: Rewrite millions of rows every micro-batch
# Result: High latency, OOM risk
```

**Fix:** Use update mode dengan windowing

### Mistake 3: Update Mode ke File Sink

```python
# INEFFICIENT: Update mode to files
df.withWatermark(...) \
  .groupBy(window(...)) \
  .agg(...) \
  .writeStream \
  .outputMode("update") \
  .format("parquet") \
  .start("output/")

# Problem: Rewrite files every update (expensive!)
```

**Fix:** Use append mode untuk files (wait for finality)

### Mistake 4: Database Writes Tanpa Error Handling

```python
# FRAGILE: No error handling
df.writeStream \
  .foreachBatch(lambda df, id: df.write.jdbc(...)) \
  .start()

# Problem: Database error → crash entire job
```

**Fix:** Implement retry logic, dead letter queue

```python
def write_with_retry(df, batch_id):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            df.write.jdbc(url, table, props)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                df.write.parquet(f"dlq/{batch_id}")
            time.sleep(2 ** attempt)

df.writeStream.foreachBatch(write_with_retry).start()
```

### Mistake 5: Tidak Monitor Write Latency

```python
# Missing: Write latency tracking
query = df.writeStream \
  .format("jdbc") \
  .start()

# Problem: Tidak tahu kalau writes lambat
```

**Fix:** Monitor query metrics

```python
# Check write latency
query.lastProgress["batchDuration"]  # Total batch time
query.lastProgress["numOutputRows"]   # Rows written

# Alert if latency > threshold
if query.lastProgress["batchDuration"] > 10000:  # 10 sec
    send_alert("Slow writes detected")
```

### Mistake 6: Duplicate Writes pada Non-Idempotent Sink

```python
# RISK: Append to non-idempotent sink
df.writeStream \
  .outputMode("append") \
  .format("kafka") \
  .option("topic", "output") \
  .start()

# Problem: Crash → reprocess → duplicate messages in Kafka
```

**Fix:** 
- Accept at-least-once untuk logs/events
- Atau add deduplication di consumer side
- Atau use transactional Kafka writes (complex)

---

## Checklist: Output Configuration

**Before production:**

**Output Mode:**
- [ ] Mode sesuai use case (append/update/complete)?
- [ ] Watermark configured (if append aggregation)?
- [ ] Result set size reasonable (if complete)?

**Sink Selection:**
- [ ] Sink supports chosen output mode?
- [ ] Idempotent writes possible (if critical)?
- [ ] Write latency acceptable?
- [ ] Error handling implemented?

**Monitoring:**
- [ ] Track write latency per batch
- [ ] Monitor output row counts
- [ ] Alert on write failures
- [ ] Validate output correctness

**Testing:**
- [ ] Test with duplicate batches (simulate crash)
- [ ] Verify no duplicate outputs
- [ ] Check late data handling
- [ ] Load test write throughput

---

## Key Takeaways

**Three Output Modes:**
- **Append:** Write once when final (files, immutable)
- **Update:** Overwrite on change (databases, dashboards)
- **Complete:** Rewrite all (small result sets)

**Mode Choice Matters:**
- Wrong mode → errors atau inefficiency
- Match mode dengan sink capabilities
- Consider latency vs completeness trade-off

**Idempotent Sinks Safer:**
- Key-based overwrites prevent duplicates
- Databases dengan upserts ideal
- Files dengan Spark metadata provide guarantees

**Databases Tricky:**
- Transaction boundaries critical
- Write latency can bottleneck pipeline
- Proper error handling essential

**Files vs Databases:**
- Files: scalable, immutable, batch-friendly
- Databases: real-time, queryable, update-capable
- Hybrid approach often best

---