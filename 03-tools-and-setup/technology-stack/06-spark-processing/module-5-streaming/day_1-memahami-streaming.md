# Day 1: Memahami Streaming - Beyond "Fast Batch"

## Real-World Problem: The Credit Card Fraud Dilemma

Bayangkan Anda kerja di bank. Setiap detik, ribuan transaksi kartu kredit masuk:
- 08:15:23.147 - Rp 450,000 di minimarket Jakarta
- 08:15:23.891 - Rp 15,000,000 di toko elektronik Singapore
- 08:15:24.234 - Rp 200,000 di SPBU Bandung

**Pertanyaan kritis:** Transaksi Singapore itu fraud atau bukan?

**Dengan batch processing:**
- Tunggu end of day (23:59)
- Load semua transaksi hari ini
- Run fraud detection model
- Hasil: Fraud terdeteksi... 16 jam setelah kejadian
- **Problem**: Uang sudah hilang, kartu sudah dibelanjakan di 10 tempat lain

**Dengan streaming:**
- Transaksi arrive → langsung proses dalam seconds
- Detect pattern: "Jakarta → Singapore dalam 8 jam? Suspicious!"
- Block kartu immediately
- **Value**: Prevent fraud sebelum terlambat

**Ini bukan tentang "lebih cepat"**—ini tentang **window of action** yang batch tidak bisa provide.

---

## Mental Model Shift: Bounded vs Unbounded Data

### Bounded Data (Batch World)

```
[Transaction 1] [Transaction 2] [Transaction 3] ... [Transaction N]
|______________________________________________|
             Data has END
```

**Asumsi batch yang kita bisa pakai:**
- Data complete → bisa sort seluruh dataset
- Size known → bisa allocate exact memory
- Result final → run sekali, answer selesai
- Time tidak ambigu → "yesterday's data" jelas artinya

**Batch thinking:**
"Berapa total sales bulan Januari?"
→ Tunggu sampai 1 Feb
→ Load semua data Jan
→ SUM(amount)
→ Done ✓

---

### Unbounded Data (Streaming World)

```
[Event 1] [Event 2] [Event 3] → [Event 4] → [Event 5] → ...
                                      ↑
                                   NOW
                          (but events keep coming)
```

**Batch assumptions yang BREAK:**

**1. "Data Complete"**
- ❌ Tidak ada "end" untuk streaming data
- ❌ Tidak bisa sort seluruh dataset (infinite!)
- ✅ Harus process data as it arrives

**2. "Size Known"**
- ❌ Cannot allocate memory untuk "semua data"
- ✅ Harus incremental processing dengan bounded state

**3. "Result Final"**
- ❌ Answer terus berubah seiring data baru masuk
- ✅ Results are continuous updates, bukan one-time answer

**4. "Time Straightforward"**
- ❌ Event arrival != event occurrence time
- ✅ Harus distinguish event-time vs processing-time

---

## What "Infinite Data" Truly Means

### Problem 1: Computational Impossibility

**Batch mindset yang tidak work:**

```python
# TIDAK BISA untuk streaming!
all_transactions = load_all_data()  # "all" = infinite?
sorted_data = all_transactions.sort()  # sort infinite data?
total = sum(sorted_data)  # sum infinite numbers?
```

**Streaming requires different question:**
Bukan "berapa total ALL transactions?"
Tapi "berapa total transactions dalam window tertentu?"

### Problem 2: State Management

**Contoh: Count unique users per day**

Batch:
```python
# Load 1 hari data (bounded)
df.groupBy("date").agg(countDistinct("user_id"))
# State: seluruh hari di memory → OK untuk 1 hari
```

Streaming:
```python
# User bisa muncul kapan saja dalam "hari" itu
# Jam 00:01 → user A arrives
# Jam 23:59 → user A arrives lagi
# Need remember: sudah count user A atau belum?
# State: must persist untuk 24 jam → grows unbounded!
```

**Challenge**: State management dengan memory terbatas untuk data unlimited.

---

## Why Streaming ≠ "Batch in a Loop"

### Naive Approach (DON'T DO THIS):

```python
# ANTI-PATTERN: Batch in a loop
while True:
    data = read_last_5_minutes()
    result = process_batch(data)
    write_results(result)
    sleep(5 * 60)
```

**Mengapa ini broken?**

**1. Correctness Issues:**
- Data yang arrive di minute boundary → masuk batch mana?
- Data late (arrive 10 minutes after event occurred) → lost!
- Duplicate processing jika job restart di tengah window

**2. State Consistency:**
```
Batch 1: Process [00:00 - 00:05]
Batch 2: Process [00:05 - 00:10]
Question: Event di 00:05:00.001 masuk batch mana?
Batch overlap? Gap? Duplicate?
```

**3. Failure Handling:**
- Batch 2 fails → restart dari mana?
- Already wrote Batch 1 → partial results di output
- No transactional guarantee across batches

**4. Aggregation Problems:**
```python
# Counting unique users dalam 1 jam
# Batch 1 (00:00-00:05): user A, B, C → count = 3
# Batch 2 (00:05-00:10): user C, D    → count = 2
# Total untuk hour? 3 + 2 = 5? SALAH! (C duplicate)
# Need state: "sudah count user C?"
```

---

## Real Streaming Needs: Event-Time vs Processing-Time

### The Fundamental Problem

```
Event happens: 10:00:00 (user clicks "buy")
Network delay: 5 seconds
Arrive at system: 10:00:05

Question: Process based on 10:00:00 atau 10:00:05?
```

**Processing-time (naive approach):**
- Process based on arrival time (10:00:05)
- **Problem**: Network delay, system downtime → results salah
- "Sales at 10:00" include transaksi yang actually happened at 9:59

**Event-time (correct approach):**
- Process based on event occurrence (10:00:00)
- **Challenge**: Late data, out-of-order events
- Need **watermarks** untuk handle "seberapa late kita tunggu?"

### Real Example: Ride-Sharing Analytics

```
Event: Driver picks up passenger
- Event-time: 14:30:00 (actual pickup)
- Processing-time: 14:35:00 (GPS signal delay di tunnel)

Question: "Peak hours" dihitung based on?
- Processing-time → Peak di 14:35 (SALAH)
- Event-time → Peak di 14:30 (BENAR)
```

**Streaming frameworks must support event-time correctness.**

---

## Spark Structured Streaming: The Mental Model

### Core Concept: Continuous Query

Batch thinking:
```
Data → Query → Result (done)
```

Streaming thinking:
```
                Continuous Query
Data Stream → [ always running ] → Result Stream
    ↓              (stateful)           ↓
 never ends                         never ends
```

**"Structured Streaming"** = Treat stream as unbounded table

```
       Input Table (unbounded)
Time | user_id | action  | amount
-----|---------|---------|--------
10:00| u1      | click   | -
10:01| u2      | buy     | 100
10:02| u1      | buy     | 50
...  | ...     | ...     | ...
(rows keep appending forever)

Query: SELECT user_id, SUM(amount) FROM table GROUP BY user_id

       Result Table (continuously updating)
user_id | total_amount
--------|-------------
u1      | 50
u2      | 100
(updates setiap new row masuk)
```

**Key insight:** Write query seperti batch, engine handle streaming complexity.

---

## Why Spark Chose Micro-Batch Model

### Design Decision: Micro-Batch vs Pure Streaming

**Pure streaming (Flink model):**
```
Event → Process → Event → Process → Event → Process
(process one event at a time)
```
- Pro: Ultra-low latency (milliseconds)
- Con: Complex failure recovery, exact-once hard

**Micro-batch (Spark model):**
```
[Event Event Event] → Process → [Event Event Event] → Process
     (small batch)                  (small batch)
```
- Pro: Leverage existing batch engine, fault-tolerance easier
- Con: Higher latency (seconds, not milliseconds)

**Spark's rationale:**
1. **Reuse Spark SQL engine** → streaming sama dengan batch code
2. **Fault tolerance** → checkpointing micro-batches simple
3. **Exactly-once** → transactional writes per micro-batch
4. **Latency trade-off** → 100ms-1s latency acceptable untuk most use cases

**Real talk:** Kalau perlu <100ms latency → Flink/Kafka Streams better. Kalau 1-10s OK dan mau simplicity → Spark perfect.

---

## Real-World Examples: When Streaming is Necessary

### 1. **Fraud Detection (Banking)**
- **Why streaming**: Window of action < 1 minute
- **Why not batch**: Fraud completed sebelum detection

### 2. **Real-Time Recommendation (E-commerce)**
- **Why streaming**: User browsing NOW → show relevant products
- **Why not batch**: "Yesterday's interest" tidak relevant untuk sekarang

### 3. **Operational Monitoring (Tech Ops)**
- **Why streaming**: Detect system failure dalam seconds
- **Why not batch**: Downtime cost $10k/minute

### 4. **IoT Sensor Processing (Manufacturing)**
- **Why streaming**: Machine temperature spike → alert immediately
- **Why not batch**: Equipment damage sebelum alert

### 5. **Live Dashboards (Analytics)**
- **Why streaming**: Executive mau lihat metrics NOW
- **Why not batch**: Hourly updates tidak cukup

---

## When Batch is STILL Better

### Stay with Batch if:

**1. Historical Analysis**
```
Question: "Total sales per quarter untuk last 5 years"
→ Data complete, no urgency
→ Batch perfect
```

**2. Complex Transformations**
```
Needs: Multiple passes over data, sorting, complex joins
→ Streaming state management too complex
→ Batch simpler
```

**3. Cost Sensitivity**
```
Streaming: Always-on resources ($$$)
Batch: Pay only during job execution ($)
→ Kalau latency tidak critical, batch cheaper
```

**4. Reprocessing Frequent**
```
Logic changes often → need recompute historical data
→ Streaming state hard to reprocess
→ Batch allows easy replay
```

**5. Small Data Volume**
```
1GB data per day
→ Streaming overhead tidak worth it
→ Hourly batch cukup
```

---

## Common Beginner Misconceptions

### Misconception 1: "Streaming is just faster batch"
**Reality:** Streaming is different computational model
- Batch: Complete data → compute once
- Streaming: Incremental computation → continuous updates

### Misconception 2: "Streaming always better karena real-time"
**Reality:** Streaming adds complexity
- More infrastructure (Kafka, state stores)
- Harder debugging (stateful operations)
- Higher operational cost
- Only worth it kalau latency critical

### Misconception 3: "Streaming cannot handle late data"
**Reality:** Streaming designed untuk late data
- Watermarks define "how late"
- Event-time correctness primary goal
- Better than batch untuk handling delays

### Misconception 4: "Streaming means no aggregations"
**Reality:** Streaming supports aggregations dengan windowing
- Tumbling windows (1 hour buckets)
- Sliding windows (last 5 minutes)
- Session windows (user activity sessions)

### Misconception 5: "Spark Streaming = always fast"
**Reality:** Micro-batch has latency (1-10s typical)
- NOT for <100ms requirements
- Good for second-level latency
- Trade-off: simplicity vs ultra-low latency

### Misconception 6: "Streaming means no storage"
**Reality:** Streaming still needs storage
- Checkpoints untuk fault tolerance
- State stores untuk aggregations
- Output sinks (databases, files)

---

## Decision Framework: Streaming or Batch?

### Ask These Questions:

**1. Latency requirement?**
- < 1 minute → Streaming
- Hourly/Daily OK → Batch

**2. Data arrival pattern?**
- Continuous flow → Streaming
- Periodic dumps → Batch

**3. Use case?**
- Operational decisions → Streaming
- Historical analysis → Batch

**4. State complexity?**
- Simple aggregations → Streaming OK
- Complex multi-pass → Batch simpler

**5. Team readiness?**
- Familiar dengan streaming ops? → Streaming
- Learning curve concern? → Start batch

**6. Budget?**
- Always-on acceptable? → Streaming
- Cost optimization critical? → Batch

---

## Reflection Questions (THINK Before Moving On)

### Conceptual Understanding:
1. **Mengapa tidak bisa "sort entire dataset" dalam streaming?**
   - Apa implication untuk operations lain (distinct, join)?

2. **Berikan contoh use case di company Anda:**
   - Yang HARUS pakai streaming (latency critical)
   - Yang BETTER pakai batch (cost/complexity)

3. **Event vs Processing time:**
   - Kapan processing-time acceptable?
   - Kapan event-time necessary?

### Practical Thinking:
4. **Kalau streaming job crash di tengah processing:**
   - Apa happens dengan partial results?
   - Bagaimana guarantee exactly-once?

5. **State management:**
   - Kalau count unique users dalam 1 day window
   - Memory usage grows selama 24 jam?
   - How to bound state size?

6. **Late data scenario:**
   - Event di jam 10:00 arrive jam 10:15
   - Sudah output result untuk window 10:00-10:05
   - Re-compute? Ignore? Update?

---

## Summary: Key Takeaways

**Streaming ≠ Fast Batch:**
- Different computational model
- Designed untuk unbounded, continuous data
- Requires thinking about time, state, failures differently

**Spark Structured Streaming:**
- Micro-batch model (trade latency untuk simplicity)
- Treat stream as unbounded table
- Leverage Spark SQL engine

**When to Stream:**
- Latency critical (<1 hour)
- Continuous data flow
- Operational decisions need real-time info

**When to Batch:**
- Historical analysis
- Cost sensitive
- Complex transformations
- Reprocessing frequent

---