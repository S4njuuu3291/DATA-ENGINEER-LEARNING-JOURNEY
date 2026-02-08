# Day 7: Kafka + Spark Streaming - Industry Standard Pattern

## Mengapa Kafka + Spark?

**Problem tanpa Kafka:**

```
Data Sources → Spark Streaming
├─ Database CDC
├─ IoT sensors  
├─ Application logs
├─ Click streams
└─ Each source: different protocol, retry logic, buffering

Spark must handle:
├─ Connection management untuk each source
├─ Backpressure dari slow processing
├─ Replay capability jika failure
└─ Coupling between producer & consumer
```

**Solution dengan Kafka:**

```
Data Sources → Kafka → Spark Streaming
├─ All sources write to Kafka (unified interface)
├─ Kafka buffers data (decoupling)
├─ Spark reads at own pace (backpressure handled)
└─ Replay from any offset (failure recovery)
```

**Key benefit:** Kafka = buffer layer yang reliable antara producers & consumers.

---

## Kafka as Source: Mental Model

### Kafka Basics (Simplified)

```
Topic: "transactions"
├─ Partition 0: [msg0, msg1, msg2, msg3, ...]
├─ Partition 1: [msg0, msg1, msg2, ...]
└─ Partition 2: [msg0, msg1, msg2, ...]

Each message:
├─ Offset: Sequential ID (0, 1, 2, ...)
├─ Key: Determines partition (hash-based)
├─ Value: Actual data (JSON, Avro, etc.)
└─ Timestamp: Event time (optional)
```

**Kafka guarantees:**
- Messages dalam partition **ordered** (FIFO)
- Messages **persisted** (replicated across brokers)
- Messages **retained** (configurable, e.g., 7 days)
- Consumers **track offset** (position dalam log)

### Spark Reading from Kafka

```
Spark Streaming reads Kafka like "table":

Micro-batch 1:
├─ Read: partition 0, offsets 0-99
├─ Read: partition 1, offsets 0-150
└─ Read: partition 2, offsets 0-80

Micro-batch 2:
├─ Read: partition 0, offsets 100-199
├─ Read: partition 1, offsets 151-300
└─ Read: partition 2, offsets 81-160

Progress tracked: {p0: 199, p1: 300, p2: 160}
```

**Spark treats Kafka as unbounded table yang terus bertambah rows.**

---

## Offsets: Progress Tracking Mechanism

### Kafka Offset = Position dalam Stream

```
Partition 0 log:
[0] [1] [2] [3] [4] [5] [6] [7] [8] [9] ...
 ↑           ↑                   ↑
start    consumer A          consumer B

Consumer A offset: 3 (next read: message 3)
Consumer B offset: 8 (next read: message 8)
```

**Offset = bookmark:** "I've read up to message N"

### Spark Manages Offsets Internally

**Traditional Kafka consumer:**
```python
# Manual offset management
consumer.subscribe(["topic"])
while True:
    records = consumer.poll()
    process(records)
    consumer.commit()  # Save offset to Kafka
```

**Spark Structured Streaming:**
```python
# Spark handles offsets automatically
df = spark.readStream \
    .format("kafka") \
    .option("subscribe", "topic") \
    .load()

# Offsets saved to checkpoint, NOT Kafka consumer groups
```

**Key difference:** Spark doesn't use Kafka consumer groups - manages offsets dalam checkpoint.

---

## How Spark Tracks Progress with Kafka

### Checkpoint Stores Kafka Offsets

```
Checkpoint structure:
/checkpoint/my-query/
├─ offsets/
│   ├─ 0  → {"topic": {"0": 100, "1": 150, "2": 80}}
│   ├─ 1  → {"topic": {"0": 200, "1": 300, "2": 160}}
│   └─ 2  → {"topic": {"0": 300, "1": 450, "2": 240}}
```

**Per micro-batch:**
- Read offsets dari checkpoint (start position)
- Read messages from Kafka
- Process events
- Save new offsets ke checkpoint (end position)

### Exactly-Once Semantics

**Guarantee:**

```
Micro-batch N:
├─ Read: offsets [100-200]
├─ Process: aggregate, transform
├─ Update state
└─ Checkpoint: save offsets + state atomically

Crash before checkpoint ✗
Recovery:
├─ Load checkpoint: offsets [0-100]
├─ Reprocess: offsets [100-200] again
└─ Idempotent state update → same result
```

**Exactly-once achieved through:**
1. Atomic checkpoint (offsets + state together)
2. Idempotent processing (replay produces same state)
3. Kafka replay capability (re-read same messages)

---

## Failure Scenarios dengan Kafka

### Scenario 1: Spark Job Crash

```
Before crash:
├─ Last checkpoint: partition 0 offset 500
├─ Processing: offsets 501-600
└─ Crash! ✗

After restart:
├─ Load checkpoint: offset 500
├─ Seek Kafka to offset 501
├─ Reprocess: offsets 501-600
└─ Continue: offset 601+

Result: No data loss, no duplicates (dalam state)
```

**Kafka retention critical:** Messages must still exist untuk replay.

### Scenario 2: Kafka Broker Failure

```
Spark processing normally...
Kafka broker crash ✗

Spark behavior:
├─ Retry read dari Kafka (automatic)
├─ Kafka fails over to replica
├─ Spark continues reading
└─ Transparent recovery (no Spark restart needed)

Kafka replication ensures durability
```

### Scenario 3: Offset Outside Retention

```
Job stopped: 7 days
Kafka retention: 7 days
Restart attempt:

Checkpoint offset: 1000
Kafka earliest available: 5000 (older messages deleted)

Error: "Offset 1000 out of range"

Solutions:
1. Start from earliest available (data loss)
2. Start from latest (skip old data)
3. Restore Kafka backup (if available)
```

**Prevention:** Match Kafka retention > expected downtime.

### Scenario 4: Backpressure (Slow Processing)

```
Kafka ingestion rate: 10k msg/sec
Spark processing rate: 5k msg/sec

Lag grows:
├─ Latest offset: 1,000,000
├─ Spark offset: 500,000
└─ Lag: 500k messages (100 seconds behind)

Kafka behavior:
├─ Buffer messages (up to retention)
├─ No data loss (persisted)
└─ Consumers catch up eventually

Spark must scale out or optimize processing
```

**Kafka absorbs bursts, gives Spark time to catch up.**

---

## How Spark Guarantees Progress

### 1. Monotonic Offset Progression

```
Checkpoint guarantees offsets never go backward:

Batch 1: offsets [0-100] ✓
Batch 2: offsets [100-200] ✓
Batch 3: crash, retry
  ├─ Load: offset 100
  ├─ Process: [100-200]
  └─ Cannot go back to 50 (forward-only)

Forward progress guaranteed
```

### 2. Bounded Batch Size

```python
# Spark controls batch size
.option("maxOffsetsPerTrigger", 10000)

Micro-batch reads max 10k offsets:
├─ Prevents overwhelming processing
├─ Predictable batch latency
└─ Controlled memory usage
```

**Trade-off:** Smaller batches = lower latency, higher overhead.

### 3. Rate Limiting

```python
# Limit processing rate
.option("maxRecordsPerSecond", 5000)

Spark throttles consumption:
├─ Max 5k records/sec across all partitions
├─ Prevents overload
└─ Smooth processing rate
```

**Use case:** Protect downstream sinks (databases) dari spike.

### 4. Partition Assignment

```
Kafka topic: 10 partitions
Spark executors: 3

Assignment:
├─ Executor 1: partitions 0, 1, 2, 3
├─ Executor 2: partitions 4, 5, 6
└─ Executor 3: partitions 7, 8, 9

Parallel consumption across executors
```

**Scalability:** More partitions = more parallelism (up to executor count).

---

## Why Kafka + Spark is Industry Standard

### 1. Decoupling Producers & Consumers

**Without Kafka:**
```
Mobile App → (direct) → Spark
Problem: App must retry, buffer jika Spark down
```

**With Kafka:**
```
Mobile App → Kafka → Spark
Benefit: App writes fire-and-forget, Kafka handles buffering
```

### 2. Replay & Reprocessing

**Scenario: Bug in processing logic**

```
Without Kafka:
├─ Data already processed
├─ Cannot reprocess
└─ Fix forward only

With Kafka:
├─ Messages retained (7 days)
├─ Reset offset to 7 days ago
├─ Reprocess with fixed logic
└─ Correct historical data ✓
```

**Kafka = audit log untuk reprocessing.**

### 3. Multi-Consumer Pattern

```
Kafka Topic: "user_events"
├─ Consumer 1: Spark (real-time aggregation)
├─ Consumer 2: Flink (fraud detection)
├─ Consumer 3: S3 sink (archival)
└─ All independent, own pace
```

**One producer, many consumers - no coupling.**

### 4. Fault Tolerance at Scale

**Production reality:**

```
Without Kafka:
├─ Spark crash → data loss dari in-flight events
├─ Source unavailable → processing stops
└─ Recovery complex

With Kafka:
├─ Spark crash → Kafka buffers, no data loss
├─ Source unavailable → Kafka retains last events
└─ Recovery automatic (replay from offset)
```

**Kafka provides buffering layer untuk failures.**

### 5. Stream-Batch Hybrid (Lambda Architecture)

```
Events → Kafka
         ├─→ Spark Streaming (real-time, seconds latency)
         │   └─ Update dashboard
         └─→ Spark Batch (hourly, complete accuracy)
             └─ Historical reports

Same data source, different processing models
```

---

## When Kafka Alone is Sufficient

### Use Case 1: Simple Message Routing

```
Scenario: Route events berdasarkan type

Kafka Streams:
├─ Read from "raw_events"
├─ Filter by event_type
├─ Write to specific topics
└─ No complex aggregation

No need Spark (overhead tidak worth it)
```

### Use Case 2: Stateless Transformations

```
Scenario: Enrich events dengan lookup

Kafka Streams/ksqlDB:
├─ Read event
├─ Lookup in key-value store
├─ Add enrichment
├─ Write output

Simple, low-latency, Kafka-native
```

### Use Case 3: Low-Latency Requirements

```
Requirement: <100ms latency

Kafka Streams:
├─ Process per-event (not micro-batch)
├─ Latency: milliseconds
└─ Suitable untuk ultra-low latency

Spark Streaming:
├─ Micro-batch model
├─ Latency: 1-10 seconds
└─ Overkill untuk millisecond needs
```

### Use Case 4: Small Data Volume

```
Volume: 100 events/sec

Kafka Streams:
├─ Single JVM application
├─ Simple deployment
└─ Low operational overhead

Spark:
├─ Cluster management
├─ Executor overhead
└─ Complex untuk small scale
```

---

## Decision Framework: Kafka Alone vs Kafka + Spark

**Use Kafka alone (Kafka Streams/ksqlDB) if:**
- [ ] Simple transformations (filter, map, route)
- [ ] Stateless atau simple stateful (count, sum per key)
- [ ] Low latency critical (<100ms)
- [ ] Small-medium scale (< 10k msg/sec)
- [ ] Team familiar dengan Kafka ecosystem

**Add Spark if:**
- [ ] Complex aggregations (windows, joins multiple streams)
- [ ] Machine learning inference (MLlib integration)
- [ ] SQL-like analytics (Spark SQL familiar)
- [ ] Large-scale processing (> 100k msg/sec)
- [ ] Integration dengan existing Spark batch jobs
- [ ] Windowing dengan event-time semantics

**Example decisions:**

```
Use Case: Click stream analytics
├─ Simple routing → Kafka Streams
├─ Session analysis (complex windows) → Spark
└─ Real-time fraud ML → Spark (MLlib)

Use Case: IoT sensor aggregation
├─ Filter outliers → Kafka Streams
├─ Multi-hour windows, late data handling → Spark
└─ Store to data lake → Spark (Parquet output)
```

---

## Common Integration Patterns

### Pattern 1: Kafka → Spark → Kafka

```
Input topic → Spark aggregation → Output topic

Benefits:
├─ Spark untuk complex processing
├─ Output back to Kafka untuk downstream consumers
└─ Composable pipeline (chain multiple Spark jobs)
```

### Pattern 2: Kafka → Spark → Database

```
Events → Spark → PostgreSQL dashboard

Use case: Real-time metrics dashboard
├─ Kafka buffers incoming events
├─ Spark aggregates (windows)
└─ Database serves queries
```

### Pattern 3: Multi-Source → Kafka → Spark

```
Multiple sources:
├─ App logs → Kafka topic A
├─ Database CDC → Kafka topic B
└─ IoT sensors → Kafka topic C

Spark:
└─ Join streams A, B, C → unified analytics
```

---

## Key Takeaways

**Kafka as Buffer:**
- Decouples producers & consumers
- Provides replay capability
- Handles backpressure naturally

**Spark + Kafka Integration:**
- Offsets managed dalam Spark checkpoint (not Kafka consumer groups)
- Exactly-once through atomic checkpoint + replay
- Failure recovery automatic (seek to last offset)

**Guarantees:**
- Forward progress (monotonic offsets)
- No data loss (Kafka retention + Spark replay)
- Exactly-once state updates

**Industry Pattern:**
- Kafka + Spark = standard untuk complex stream processing
- Kafka alone sufficient untuk simple use cases
- Choice based on complexity, latency, scale

**Critical Considerations:**
- Kafka retention > expected downtime
- Partition count = parallelism ceiling
- Monitor lag untuk detect processing issues

---