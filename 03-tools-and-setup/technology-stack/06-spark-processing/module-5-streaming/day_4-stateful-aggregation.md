# Day 4: Stateful Processing - Memory di Infinite Stream

## Real Problem: Counting Unique Users

**Batch approach (simple):**

```python
# Load semua data
df = spark.read.parquet("users.parquet")

# Count unique
unique_users = df.select("user_id").distinct().count()
# Result: 15,000 unique users
# Done ✓
```

**Streaming attempt (broken):**

```python
# Streaming version
stream = spark.readStream.format("kafka")...

# Count unique per micro-batch
batch_1: 100 users → 95 unique
batch_2: 100 users → 88 unique (some overlap dengan batch 1!)
batch_3: 100 users → 90 unique

Total unique: 95 + 88 + 90 = 273? ✗
Actual: Many duplicates across batches!
```

**Problem fundamental:** Untuk tahu "unique", harus INGAT siapa saja yang sudah dilihat sebelumnya.

**Solusi:** STATE - memory yang persist across micro-batches.

---

## What is "State" in Streaming?

### Definition: Information Remembered Across Time

**State = data yang harus disimpan untuk melanjutkan computation**

```
Mental model:

Stateless processing:
Input → Transform → Output
(tidak perlu ingat apapun dari sebelumnya)

Stateful processing:
         ┌─────────────┐
Input → │ Transform   │ → Output
         │ + Memory    │
         └─────────────┘
              ↑ ↓
          Read/Update State
```

### Contoh Sederhana: Running Total

**Tanpa state (SALAH):**

```
Micro-batch 1: [10, 20, 30]
  └─ sum = 60

Micro-batch 2: [15, 25]
  └─ sum = 40

Total output: 60, 40
└─ Tidak ada "running total" ✗
```

**Dengan state (BENAR):**

```
State: running_total = 0

Micro-batch 1: [10, 20, 30]
├─ Read state: 0
├─ Compute: 0 + 10 + 20 + 30 = 60
├─ Update state: 60
└─ Output: 60 ✓

Micro-batch 2: [15, 25]
├─ Read state: 60
├─ Compute: 60 + 15 + 25 = 100
├─ Update state: 100
└─ Output: 100 ✓

Result: 60 → 100 (continuous growth)
```

---

## Why Aggregation REQUIRES Memory

### Case 1: Count Distinct (Unique Values)

**Tantangan:** Harus ingat semua values yang sudah dilihat

```
Stream events:
t1: user_A → State: {A} → unique_count = 1
t2: user_B → State: {A, B} → unique_count = 2
t3: user_A → State: {A, B} → unique_count = 2 (sudah ada)
t4: user_C → State: {A, B, C} → unique_count = 3

Tanpa state: Cannot detect duplicate user_A
Dengan state: Track semua users, detect duplicates
```

**State yang dibutuhkan:** Set of all unique values
**Problem:** State grows unbounded! (infinite unique values = infinite memory)

### Case 2: Windowed Aggregation

**Tantangan:** Harus ingat events dalam window yang belum close

```
Window: [10:00 - 10:05], watermark delay: 2 min

10:01 → Event A (amount: 100)
  └─ State: window [10:00-10:05] = {Event A}

10:03 → Event B (amount: 200)
  └─ State: window [10:00-10:05] = {Event A, Event B}

10:06 → Event C (amount: 50, late for previous window!)
  └─ State: window [10:00-10:05] = {Event A, Event B, Event C}
  └─ Must still accept (within watermark)

10:07 → Watermark passes 10:05
  └─ Finalize window: sum = 350
  └─ Clear state for [10:00-10:05]
```

**State yang dibutuhkan:** Partial aggregates untuk active windows
**Size:** Proportional to number of active windows

### Case 3: Join Across Streams

**Tantangan:** Harus buffer events sambil tunggu matching event dari stream lain

```
Orders stream:
10:00 → Order #123 (user_id: A, product: X)
  └─ State: pending_orders = {123: waiting for payment}

Payments stream:
10:02 → Payment (order_id: 123, status: success)
  └─ Match dengan Order #123
  └─ Output: Completed order
  └─ Clear from state

10:05 → Order #456 (user_id: B, product: Y)
  └─ State: pending_orders = {456: waiting for payment}
  └─ (still waiting...)

10:15 → Timeout (15 min watermark)
  └─ Order #456 tidak dapat payment
  └─ Output: Failed order
  └─ Clear from state
```

**State yang dibutuhkan:** Buffered events dari both streams
**Size:** Depends on time to match + watermark delay

---

## How Spark Tracks State: Conceptual Model

### State Store: Distributed Key-Value Store

```
Logical view:
Key              | Value
-----------------|---------------------------
"window_10:00"   | {sum: 500, count: 10}
"window_10:05"   | {sum: 300, count: 7}
"user_A"         | {last_seen: 10:15, count: 5}
"user_B"         | {last_seen: 10:20, count: 3}
```

**Characteristics:**
- **Partitioned:** State distributed across executors (by key)
- **Versioned:** Each micro-batch creates new version
- **Persisted:** Saved to disk (not just memory)

### State Updates Per Micro-Batch

```
Micro-batch N execution:

1. Read current state
   ├─ Load from disk/memory
   └─ Get relevant keys untuk events di batch ini

2. Process events
   ├─ Apply transformations
   └─ Update state values

3. Write new state version
   ├─ Persist to disk (checkpoint)
   └─ Keep in memory untuk next batch

4. Output results
   └─ Based on updated state
```

**Key insight:** State tidak hilang between micro-batches - persisted!

---

## State Partitioning: How Spark Distributes State

### Partitioning by Key

```
Events distributed by grouping key:

Partition 1 (Executor 1):
├─ Keys: user_A, user_C, user_E
└─ State: {A: data, C: data, E: data}

Partition 2 (Executor 2):
├─ Keys: user_B, user_D
└─ State: {B: data, D: data}

Partition 3 (Executor 3):
├─ Keys: user_F, user_G, user_H
└─ State: {F: data, G: data, H: data}
```

**Mengapa partitioning?**
- **Parallelism:** Multiple executors process state simultaneously
- **Locality:** Events untuk same key → same partition
- **Scalability:** Add more executors = handle more state

**Trade-off:**
- **Skew risk:** Jika satu key terlalu banyak data (hot key)
- **Shuffle cost:** Events harus ke correct partition

---

## What Happens When Job Crashes?

### Scenario: Crash di Tengah Processing

```
Timeline:

10:00 - Batch 1 completed
  └─ State version 1 saved ✓
  └─ Output written ✓

10:01 - Batch 2 processing...
  └─ State updated in memory
  └─ Job crashes! ✗
  └─ State version 2 NOT saved
  └─ Output NOT written

10:02 - Job restarts
  └─ Where to continue?
```

**Problem tanpa recovery:**
- State di memory hilang
- Tidak tahu batch 2 sudah processed atau belum
- Risk: duplicate processing atau lost data

---

## State Recovery: Checkpointing Mechanism

### How Spark Recovers State

**1. Write-Ahead Log (WAL)**

```
Setiap micro-batch:

Step 1: Checkpoint offset
  └─ "Last processed: offset 12345"

Step 2: Process batch
  └─ Read events 12346-12400

Step 3: Update state
  └─ Save state version N

Step 4: Commit
  └─ "Completed: offset 12400"

Crash recovery:
  └─ Read last committed offset: 12345
  └─ Reprocess from 12346
```

**2. State Versioning**

```
State checkpoints:

Version 1 (batch 1): saved to disk
Version 2 (batch 2): saved to disk
Version 3 (batch 3): processing... crash!

Recovery:
├─ Load version 2 (last committed)
├─ Reprocess batch 3
└─ Create version 3 again
```

**Guarantee: Exactly-once state updates**
- Reprocess batch if crash
- State recovered to last successful batch
- No duplicate state updates

### Recovery Flow

```
Normal execution:
Batch N → Update State → Checkpoint → Batch N+1

Failure:
Batch N → Update State → Checkpoint ✓
Batch N+1 → Processing... CRASH ✗

Recovery:
Restart → Load State (version N) → Reprocess Batch N+1
```

**Idempotency critical:**
- Reprocessing batch must produce same state
- Deterministic processing required

---

## Why State Grows Over Time

### Problem 1: Unbounded Cardinality

**Count distinct users (no windowing):**

```
Day 1: 1,000 unique users
  └─ State size: 1,000 entries

Day 7: 10,000 unique users
  └─ State size: 10,000 entries

Day 30: 100,000 unique users
  └─ State size: 100,000 entries

Day 365: 1,000,000 unique users
  └─ State size: 1,000,000 entries

State growth: unbounded!
```

**Without cleanup:** State eventually exceeds memory → OOM crash

### Problem 2: Long Windows

**Window 24 hours, watermark 1 hour:**

```
10:00 - Window [10:00-10:00 tomorrow] opens
  └─ Start accumulating events

11:00 - Still accumulating...
12:00 - Still accumulating...
...
10:00 (next day) - Window closes
11:00 - Watermark passes, finalize window

State held: 25 hours (24h window + 1h watermark)
```

**Larger window = longer state retention = more memory**

### Problem 3: Slow-Moving Keys

**Session windows with long timeout:**

```
User A:
├─ 10:00 - Activity
├─ 10:05 - Activity
├─ 10:10 - Activity
├─ (inactive for 30 minutes, timeout = 30 min)
└─ 10:40 - Session timeout, clear state

User B (inactive user):
├─ 10:00 - Single activity
└─ State held for 30 minutes waiting for timeout
    (占用 memory meski tidak ada aktivitas)
```

**Inactive keys hold state until timeout → memory waste**

---

## State Cleanup: How Spark Manages Growth

### 1. Watermark-Based Cleanup

**Window aggregation:**

```
Configuration:
├─ Window: 1 hour
└─ Watermark: 10 minutes

Lifecycle:
10:00 - Window [10:00-11:00] opens
  └─ State: accumulate events

11:00 - Window closes (boundary reached)
  └─ State: still held (waiting for late data)

11:10 - Watermark passes (10 min after close)
  └─ State: CLEARED ✓
  └─ Window finalized, no more updates
```

**Watermark = signal untuk state cleanup**

### 2. TTL (Time-To-Live) for Stateful Operations

**MapGroupsWithState (custom stateful logic):**

```scala
def updateState(
  key: String,
  values: Iterator[Event],
  state: GroupState[MyState]
): Output = {
  
  // Set timeout
  state.setTimeoutDuration("30 minutes")
  
  // Process events...
  
  // State auto-cleared after 30 min inactivity
}
```

**Manual control:** Developer specify state lifetime

### 3. What Happens Without Cleanup?

```
Scenario: Count distinct, no windowing, no cleanup

Month 1: 1M users → 100 MB state
Month 2: 2M users → 200 MB state
Month 6: 10M users → 1 GB state
Year 2: 50M users → 5 GB state

Eventually: OutOfMemoryError → job fails ✗
```

**Critical:** Every stateful operation MUST have cleanup strategy

---

## Stateful Operations: State Characteristics

### Operation 1: Simple Aggregation (sum, count, avg)

```python
stream.groupBy("category").agg(sum("amount"))
```

**State needed:** Partial aggregates per key
- Example: `{electronics: 15000, clothing: 8000}`

**State size:** 
- Fixed per key (one number per aggregate)
- Growth: O(number of distinct keys)

**Cleanup:** 
- With windowing: watermark-based
- Without windowing: grows forever ⚠️

### Operation 2: Distinct Count

```python
stream.groupBy("category").agg(approx_count_distinct("user_id"))
```

**State needed:** Set of all unique values (atau approximate data structure)
- Example: `{electronics: {user1, user2, ...}}`

**State size:**
- Grows with unique values
- Growth: O(cardinality of distinct values)

**Cleanup:**
- MUST use windowing
- Without windows: OOM guaranteed ⚠️

### Operation 3: Join

```python
orders.join(payments, "order_id")
```

**State needed:** Buffered events dari both streams
- Example: Pending orders waiting for payment

**State size:**
- Depends on matching rate
- High if one stream much slower

**Cleanup:**
- Watermark defines max wait time
- Unmatched events dropped after watermark

### Operation 4: Custom Stateful Logic

```python
stream.groupByKey().mapGroupsWithState(...)
```

**State needed:** Whatever you define
- Full flexibility, full responsibility

**State size:**
- Completely custom
- Can be unbounded if not careful ⚠️

**Cleanup:**
- Must implement timeout logic
- No automatic cleanup

---

## Risks of Stateful Streaming

### Risk 1: Out of Memory (OOM)

**Cause:** State grows faster than cleanup

```
Symptoms:
├─ Executor memory usage increases over time
├─ Frequent GC pauses
├─ Eventually: java.lang.OutOfMemoryError
└─ Job crashes

Prevention:
├─ Use windowing dengan reasonable watermark
├─ Monitor state size metrics
├─ Test dengan production data volume
└─ Set memory appropriately
```

### Risk 2: Data Loss from Aggressive Cleanup

**Cause:** Watermark terlalu short

```
Configuration:
├─ Window: 1 hour
└─ Watermark: 1 minute (too aggressive!)

Scenario:
10:00 - Window [10:00-11:00] processing
11:01 - Watermark passes, window closed
11:05 - Late event arrives (timestamp 10:30)
  └─ Dropped! (window already finalized)

Result: Incomplete aggregation ✗
```

**Trade-off:** Longer watermark = more complete data, more memory

### Risk 3: Hot Key Skew

**Cause:** Satu key dengan data terlalu banyak

```
State distribution:
Partition 1: category "popular_item" → 10 GB state
Partition 2: category "niche_A" → 10 MB state
Partition 3: category "niche_B" → 5 MB state

Problem:
├─ Partition 1 OOM (hot key)
├─ Partition 2, 3 underutilized
└─ Cannot scale horizontally (adding executors tidak help)
```

**Solution:** Salting (split hot key into sub-keys), custom partitioning

### Risk 4: Checkpoint Corruption

**Cause:** Incompatible schema changes

```
Version 1: State schema {sum: Long, count: Int}
Deploy version 2: State schema {sum: Long, count: Int, avg: Double}

Recovery attempt:
├─ Load checkpoint from version 1
├─ Schema mismatch!
└─ Cannot deserialize state ✗

Result: Must restart from scratch (lose all state)
```

**Prevention:** Careful schema evolution, test upgrades

### Risk 5: Slow Checkpoint Performance

**Cause:** Large state + synchronous checkpoint

```
State size: 10 GB
Checkpoint time: 30 seconds

Impact:
├─ Micro-batch processing: 5 seconds
├─ Checkpoint wait: 30 seconds
├─ Total latency: 35 seconds (6x slower!)
└─ Throughput degraded
```

**Solution:** Async checkpointing (Spark handles internally), tune checkpoint interval

---

## Mental Model for Reasoning About Correctness

### Framework: ACID for State

**1. Atomicity: State updates transactional**

```
Question: Kalau crash di tengah micro-batch, state corrupt?
Answer: No - checkpoint atomic, rollback to last version

Mental check:
├─ State updated?
├─ Checkpoint saved?
└─ Both or neither (atomic)
```

**2. Consistency: State reflects processed data**

```
Question: Apakah state match dengan output yang sudah di-emit?
Answer: Yes - exactly-once semantics

Mental check:
├─ Output emitted → State updated
├─ State updated → Output will be emitted
└─ No divergence
```

**3. Isolation: Concurrent batches don't interfere**

```
Question: Dua micro-batches simultaneously update state?
Answer: No - sequential processing per key partition

Mental check:
├─ Same key always same partition
├─ Partition processed sequentially
└─ No race conditions
```

**4. Durability: State survives failures**

```
Question: Restart after crash, state lost?
Answer: No - recovered from checkpoint

Mental check:
├─ State persisted to reliable storage
├─ Recovery mechanism tested
└─ No data loss
```

### Correctness Checklist

**Before deploying stateful streaming:**

**State Size:**
- [ ] Estimated state size per key?
- [ ] Growth rate measured?
- [ ] Cleanup strategy defined?
- [ ] Memory allocated sufficient?

**Watermark:**
- [ ] Late data distribution analyzed?
- [ ] Watermark delay justified?
- [ ] Trade-off between completeness & latency understood?

**Recovery:**
- [ ] Checkpoint location reliable?
- [ ] Recovery tested?
- [ ] RTO (Recovery Time Objective) acceptable?

**Scalability:**
- [ ] Hot key identified?
- [ ] Partition distribution checked?
- [ ] Scale-out tested?

**Schema Evolution:**
- [ ] State schema versioned?
- [ ] Upgrade path planned?
- [ ] Rollback strategy defined?

---

## Reflection Questions

### Conceptual:
1. **Mengapa aggregation butuh state?**
   - Operasi mana yang stateless vs stateful?
   - Bisa distinct tanpa state?

2. **State cleanup trade-off:**
   - Watermark 1 minute vs 1 hour - impact?
   - Kapan aggressive cleanup acceptable?

3. **Recovery guarantee:**
   - Exactly-once untuk state updates - how?
   - Bisa duplicate state?

### Practical:
4. **State size estimation:**
   - Count distinct 1 million users per day
   - Window 24 hour, watermark 1 hour
   - Berapa state size? Berapa memory perlu?

5. **Failure scenario:**
   - Crash saat processing batch 100
   - State checkpoint sampai batch 99
   - What happens pada restart?

6. **Hot key problem:**
   - Satu category 80% traffic
   - Other categories minimal
   - Bagaimana handle skew?

---

## Key Takeaways

**State = Memory Across Time:**
- Essential untuk aggregation, joins, custom logic
- Persisted untuk survive failures
- Partitioned untuk parallelism

**State Growth Challenge:**
- Unbounded tanpa cleanup → OOM
- Watermark triggers cleanup
- Window size directly affects memory

**Recovery Mechanism:**
- Checkpointing ensures durability
- Exactly-once state updates
- Replay dari last checkpoint

**Design Principles:**
- Every stateful operation needs cleanup strategy
- Monitor state size in production
- Test recovery scenarios
- Plan untuk schema evolution

**Risks:**
- OOM dari uncontrolled growth
- Data loss dari aggressive cleanup
- Hot key skew
- Checkpoint overhead

---