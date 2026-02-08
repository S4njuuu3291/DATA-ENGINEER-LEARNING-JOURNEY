# Day 3: Partitioning & Shuffle — Rahasia Performa Spark

Hari ini kita **deep dive ke mekanik parallelism**. Ini yang bikin Spark cepat... atau lambat kalau salah pakai.

---

## 1. Partitions: Unit Dasar Parallelism

### Apa Itu Partition?

**Analogi: Pizza Dibagi untuk Rombongan**

Kamu punya pizza besar (data), rombongan 8 orang (executors):

```
Pizza utuh (1 partition):
┌─────────────────┐
│  🍕🍕🍕🍕🍕🍕🍕🍕  │  ← 1 orang makan sendiri, lambat!
└─────────────────┘

Pizza dipotong 8 (8 partitions):
┌──┬──┬──┬──┬──┬──┬──┬──┐
│🍕│🍕│🍕│🍕│🍕│🍕│🍕│🍕│  ← 8 orang makan paralel, cepat!
└──┴──┴──┴──┴──┴──┴──┴──┘
  P1 P2 P3 P4 P5 P6 P7 P8
```

**Partition = potongan independen dari data**
- Setiap partition diproses oleh **1 task** pada **1 executor**
- **1 partition = 1 task** (core concept!)
- Parallelism = jumlah partitions yang bisa diproses simultan

---

### Kenapa Partitions Matter?

**Formula performa:**
```
Total time = (Biggest partition size) / (Executor speed)
```

**Bukan:**
```
Total time = (Total data size) / (All executors combined)
```

**Contoh:**

```
Scenario A: Data 100 GB, 10 partitions TIDAK RATA
├─ P1: 50 GB  ← BOTTLENECK! (butuh 50 menit)
├─ P2: 5 GB   (5 menit, lalu idle)
├─ P3: 5 GB   (5 menit, lalu idle)
└─ ... P10: 5 GB

Total time: 50 menit (executors lain nganggur!)
```

```
Scenario B: Data 100 GB, 10 partitions RATA
├─ P1: 10 GB  (10 menit)
├─ P2: 10 GB  (10 menit)
├─ P3: 10 GB  (10 menit)
└─ ... P10: 10 GB

Total time: 10 menit (semua executors sibuk!)
```

**🎯 Key Insight:** Partition terbesar menentukan total waktu eksekusi!

---

## 2. Bagaimana Data Didistribusikan Antar Executors?

### Initial Partitioning (Saat Read)

**Skenario 1: Read dari File**
```python
df = spark.read.parquet("data/")
```

```
HDFS/S3 Storage:
data/
├─ part-00000.parquet (128 MB)  → Partition 1 → Executor 1
├─ part-00001.parquet (128 MB)  → Partition 2 → Executor 2
├─ part-00002.parquet (128 MB)  → Partition 3 → Executor 3
└─ part-00003.parquet (128 MB)  → Partition 4 → Executor 4
```

**Default:** 1 file = 1 partition (atau pecah per 128 MB block)

---

**Skenario 2: parallelize() dari Collection**
```python
data = range(1000)
rdd = spark.sparkContext.parallelize(data, numSlices=4)
```

```
Data di Driver:
[1, 2, 3, ..., 1000]

Distributed ke Executors:
Executor 1: [1-250]    ← Partition 1
Executor 2: [251-500]  ← Partition 2
Executor 3: [501-750]  ← Partition 3
Executor 4: [751-1000] ← Partition 4
```

---

### Narrow vs Wide Transformations

**Ini konsep PALING PENTING untuk understand performa!**

#### Narrow Transformations (Tidak Perlu Shuffle)

**Karakteristik:**
- Setiap output partition hanya depend pada **1 input partition**
- Tidak ada data movement antar executors
- **CEPAT!** (tidak ada network overhead)

**Contoh:**
```python
df.filter(df.age > 30)
df.select("name", "city")
df.withColumn("country", "ID")
df.map(lambda x: x * 2)
```

**Visualisasi:**
```
Input Partitions        Narrow Op         Output Partitions
─────────────────       ─────────        ──────────────────
Executor 1:
  [1,2,3] ──────────> filter(>2) ────> [3]
  
Executor 2:
  [4,5,6] ──────────> filter(>2) ────> [4,5,6]
  
Executor 3:
  [7,8,9] ──────────> filter(>2) ────> [7,8,9]

✅ Tidak ada data movement antar executors!
```

---

#### Wide Transformations (PERLU SHUFFLE!)

**Karakteristik:**
- Output partition depend pada **MULTIPLE input partitions**
- Butuh **redistribute data** antar executors
- **LAMBAT!** (network + disk I/O + serialization)

**Contoh:**
```python
df.groupBy("city").count()
df.orderBy("age")
df.repartition(10)
df.join(other_df, "id")
df.distinct()
```

**Visualisasi:**
```
Input Partitions       Wide Op (Shuffle)      Output Partitions
─────────────────      ─────────────────     ──────────────────
Executor 1:
  city: [Jakarta, Bandung] ──┐
                              ├──> SHUFFLE ─> Jakarta: [...]
Executor 2:                   │
  city: [Jakarta, Surabaya] ──┤              Bandung: [...]
                              │
Executor 3:                   │              Surabaya: [...]
  city: [Bandung, Jakarta] ───┘

❌ Semua data "Jakarta" harus ke partition yang sama!
   → Network transfer, disk spill, serialization
```

---

## 3. Shuffle: Operasi Paling Mahal di Spark

### Apa yang Terjadi Saat Shuffle?

**Step-by-step:**

```python
df.groupBy("city").count()
```

**Phase 1: Map Side (Write Phase)**
```
Executor 1 (Partition 1):
  Rows: [Jakarta, Bandung, Jakarta]
  
  1. Hash setiap city → tentukan target partition
     Jakarta  → hash("Jakarta") % 3 = 0 → Target Partition 0
     Bandung  → hash("Bandung") % 3 = 1 → Target Partition 1
  
  2. Tulis ke local disk, dikelompokkan per target partition
     ├─ shuffle_output_0.tmp (Jakarta rows)
     └─ shuffle_output_1.tmp (Bandung rows)
```

**Phase 2: Network Transfer**
```
Executor 1 → Network → Executor tujuan
Executor 2 → Network → Executor tujuan
Executor 3 → Network → Executor tujuan

Semua data "Jakarta" → Executor A
Semua data "Bandung" → Executor B
Semua data "Surabaya" → Executor C
```

**Phase 3: Reduce Side (Read Phase)**
```
Executor A (Partition 0):
  Terima semua "Jakarta" rows dari semua executors
  Aggregate: count()
  
Executor B (Partition 1):
  Terima semua "Bandung" rows dari semua executors
  Aggregate: count()
```

---

### Kenapa Shuffle Mahal?

**Cost breakdown:**

1. **Disk I/O** (Write shuffled data ke disk)
   - Setiap executor tulis intermediate files
   - Disk write = 100-1000x lebih lambat dari memory

2. **Network Transfer** (Move data antar executors)
   - Network bandwidth limited (1-10 Gbps typical)
   - Contoh: 100 GB shuffle di 10 Gbps = minimal 80 detik (hanya transfer!)

3. **Serialization/Deserialization**
   - Convert Java objects → bytes (serialize)
   - Transfer
   - Convert bytes → Java objects (deserialize)
   - CPU intensive!

4. **Sorting** (untuk operasi tertentu)
   - SortMergeJoin butuh sort data sebelum join
   - O(n log n) complexity

**Total overhead:** 10-100x lebih lambat dibanding narrow operations!

---

## 4. `repartition()` vs `coalesce()`

### Mental Model: Pindah Rumah

**`repartition()` = Pindah rumah dengan jasa professional**
- Semua barang dipindah ulang
- Bisa nambah atau kurangi kamar
- Mahal tapi hasil rata

**`coalesce()` = Gabungkan kamar tanpa pindah barang**
- Hanya merge partitions yang sudah ada
- Hanya bisa kurangi jumlah
- Murah tapi hasil bisa tidak rata

---

### `repartition()`: Full Shuffle

```python
df.repartition(10)
```

**What happens:**
```
Input (4 partitions):          Full Shuffle        Output (10 partitions):
────────────────────          ────────────        ────────────────────────
P1: [1,2,3,4,5] ──┐                               P1: [...]
P2: [6,7,8,9,10] ─┼──> HASH PARTITION ──>        P2: [...]
P3: [11,12,13] ───┤     (redistribute)            ...
P4: [14,15] ──────┘                               P10: [...]

✅ Data terdistribusi RATA (round-robin atau hash)
❌ MAHAL: Full shuffle, network + disk
```

**Use case:**
- Nambah partitions (scale up parallelism)
- Re-balance skewed partitions
- Sebelum operasi expensive (prepare untuk groupBy)

---

### `coalesce()`: Partition Merge (No Full Shuffle)

```python
df.coalesce(2)
```

**What happens:**
```
Input (4 partitions):          Merge Locally      Output (2 partitions):
────────────────────          ─────────────      ──────────────────────
P1: [1,2,3] ──┐                                  P1: [1,2,3,6,7]
              ├──> merge same executor ──>         (P1 + P2 merged)
P2: [6,7] ────┘

P3: [8,9] ────┐                                  P2: [8,9,10]
              ├──> merge same executor ──>         (P3 + P4 merged)
P4: [10] ─────┘

✅ MURAH: Tidak ada shuffle, hanya merge
❌ Bisa TIDAK RATA (tergantung distribusi awal)
```

**Use case:**
- Kurangi partitions setelah filter (reduce overhead)
- Sebelum write file (avoid small files)
- Reduce task overhead

---

### Comparison Table

| Aspek | `repartition()` | `coalesce()` |
|-------|----------------|--------------|
| **Direction** | Increase atau decrease | Decrease only |
| **Shuffle** | ✅ Full shuffle | ❌ No shuffle (merge local) |
| **Cost** | Mahal | Murah |
| **Balance** | ✅ Guaranteed rata | ⚠️ Bisa tidak rata |
| **Use when** | Butuh re-balance | Kurangi partitions murah |

---

### Contoh Decision Tree:

```
Butuh ubah jumlah partitions?
│
├─ Nambah partitions?
│  └─> repartition() (no choice, harus shuffle)
│
└─ Kurangi partitions?
   │
   ├─ Butuh hasil RATA SEMPURNA?
   │  └─> repartition() (lebih lambat tapi rata)
   │
   └─ Cukup "lumayan rata"?
      └─> coalesce() (lebih cepat)
```

---

## 5. Kenapa `groupBy` dan `join` Berbahaya?

### `groupBy`: Data Skew Problem

**Contoh:**
```python
df.groupBy("country").count()
```

**Scenario: 90% data dari 1 country**

```
Input (sebelum shuffle):
Executor 1: [ID, ID, SG, MY]
Executor 2: [ID, ID, ID, TH]
Executor 3: [ID, ID, ID, ID]

Shuffle (hash partition by country):
Target Partition 0 (Indonesia):  ← 90% data ke sini!
  [ID, ID, ID, ID, ID, ID, ID, ID, ID]  ← 1 executor kerjain semua
  
Target Partition 1 (Singapore):
  [SG]  ← Executor selesai cepat, idle
  
Target Partition 2 (Malaysia):
  [MY]  ← Executor selesai cepat, idle
  
Target Partition 3 (Thailand):
  [TH]  ← Executor selesai cepat, idle

❌ BOTTLENECK! 1 executor kerja berat, lainnya nganggur
```

**Impact:**
- Total time = waktu partition terbesar (Indonesia)
- Wasted resources (executors idle)
- Bisa OOM kalau 1 partition terlalu besar

---

### `join`: Shuffle + Potensi Skew

**Contoh:**
```python
users_df.join(transactions_df, "user_id")
```

**What happens:**

**Step 1: Shuffle kedua DataFrame**
```
users_df shuffle by user_id:
  Executor A: [user_1, user_2]
  Executor B: [user_3, user_4]

transactions_df shuffle by user_id:
  Executor A: [user_1 txns, user_2 txns]
  Executor B: [user_3 txns, user_4 txns]
```

**Step 2: Join di setiap executor**
```
Executor A:
  user_1 → join 1 user row dengan 1000 transaction rows
  user_2 → join 1 user row dengan 10 transaction rows
  
Executor B:
  user_3 → join 1 user row dengan 100000 transaction rows  ← BOTTLENECK!
  user_4 → join 1 user row dengan 5 transaction rows
```

**Problems:**
1. **Shuffle cost:** 2x shuffle (kedua DataFrame)
2. **Data skew:** User dengan banyak transactions bikin partition besar
3. **Memory:** Large partitions bisa OOM
4. **Join algorithm:** SortMergeJoin butuh sort (expensive!)

---

### Mitigasi: Broadcast Join (Small Table)

**Kalau salah satu table KECIL (<10 MB):**

```python
from pyspark.sql.functions import broadcast

# users_df kecil (1 MB), transactions_df besar (100 GB)
result = transactions_df.join(broadcast(users_df), "user_id")
```

**What happens:**
```
1. Broadcast users_df ke SEMUA executors (copy ke memory)
   ├─ Executor 1: users_df copy (1 MB)
   ├─ Executor 2: users_df copy (1 MB)
   └─ Executor 3: users_df copy (1 MB)

2. Join locally di setiap executor (NO SHUFFLE!)
   Executor 1: transactions partition 1 join dengan users_df (in memory)
   Executor 2: transactions partition 2 join dengan users_df (in memory)
   Executor 3: transactions partition 3 join dengan users_df (in memory)

✅ CEPAT: Tidak ada shuffle transactions_df!
✅ SCALABLE: Parallelism penuh
```

**Syarat:**
- Small table muat di memory SETIAP executor (<10 MB ideal, <100 MB maksimal)
- Spark auto-detect kalau <10 MB (konfigurasi `spark.sql.autoBroadcastJoinThreshold`)

---

## 6. Rules of Thumb untuk Partitioning

### ✅ Ideal Partition Size

**Formula:**
```
Ideal partition size = 100-200 MB (uncompressed in memory)
```

**Reasoning:**
- < 100 MB: Too many partitions → overhead koordinasi, banyak small tasks
- \> 1 GB: Too few partitions → underutilize executors, risk OOM

**Contoh:**
```
Data size: 100 GB
Ideal partitions: 100 GB / 128 MB = ~800 partitions

Cluster: 10 executors, 4 cores each = 40 cores
Minimal partitions: 40 * 2 = 80 partitions (rule: 2-3x cores)
```

---

### ✅ Jumlah Partitions vs Cores

**Formula:**
```
Ideal partitions = (Number of executors) × (Cores per executor) × 2-4
```

**Example:**
```
Cluster: 10 executors, 4 cores each = 40 total cores
Ideal partitions: 40 × 3 = 120 partitions

Reasoning:
- 1x cores (40): Underutilize (tidak ada buffer kalau ada stragglers)
- 2-4x cores (80-160): Sweet spot
- 10x cores (400): Too many (overhead task scheduling)
```

---

### ✅ Kapan Re-partition?

**Scenario 1: Setelah filter besar**
```python
# Original: 1000 partitions, 100 GB
df = spark.read.parquet("big_data/")

# Filter 99% data
df_filtered = df.filter(df.status == "active")  # Now 1 GB

# Problem: Still 1000 partitions! (1 MB per partition, too small)
# Solution:
df_filtered = df_filtered.coalesce(10)  # Reduce to 10 partitions (100 MB each)
```

---

**Scenario 2: Sebelum expensive operation**
```python
# Bad: Skewed partitions sebelum groupBy
df.groupBy("city").count()  # Bisa skew!

# Good: Re-partition by key dulu (distribute rata)
df.repartition("city").groupBy("city").count()
```

---

**Scenario 3: Sebelum write files**
```python
# Bad: 1000 partitions → 1000 small files (overhead!)
df.write.parquet("output/")  # Creates 1000 files

# Good: Coalesce dulu
df.coalesce(10).write.parquet("output/")  # Creates 10 files
```

---

### ✅ Partition Key Selection

**Untuk `repartition(col)` atau `partitionBy(col)`:**

**Good keys:**
- High cardinality (banyak unique values)
- Evenly distributed
- Frequently used di filter/join

**Example:**
```python
# ✅ Good: user_id (millions of users, evenly distributed)
df.repartition("user_id")

# ❌ Bad: country (few values, skewed)
df.repartition("country")  # Indonesia 90%, Singapore 5%, dll

# ❌ Bad: timestamp (high cardinality tapi tidak untuk grouping)
df.repartition("timestamp")
```

---

## 7. Mental Model: Spotting Expensive Operations

### 🔴 RED FLAGS (Expensive!)

1. **Wide transformations:**
   ```python
   .groupBy()
   .join()      # (kalau bukan broadcast)
   .distinct()
   .orderBy()
   .repartition()
   ```

2. **Actions yang bawa data ke driver:**
   ```python
   .collect()       # ← ALL data to driver!
   .toPandas()      # ← ALL data to driver!
   .take(1000000)   # ← Large data to driver!
   ```

3. **Multiple passes:**
   ```python
   df.count()  # Pass 1
   df.show()   # Pass 2 (if not cached)
   ```

4. **Skewed keys:**
   ```python
   df.groupBy("low_cardinality_col")
   # Example: groupBy("country") when 90% is 1 country
   ```

---

### 🟢 GREEN FLAGS (Cheap!)

1. **Narrow transformations:**
   ```python
   .filter()
   .select()
   .withColumn()
   .map()
   ```

2. **Broadcast joins:**
   ```python
   big_df.join(broadcast(small_df), "key")
   ```

3. **Cached reuse:**
   ```python
   df.cache()
   df.count()  # Expensive
   df.show()   # Cheap (from cache)
   ```

4. **Coalesce (decrease only):**
   ```python
   df.coalesce(10)  # Cheap merge
   ```

---

### Mental Checklist Sebelum Eksekusi:

**Questions to ask:**

1. **Apakah ada shuffle?**
   - Look for: `groupBy`, `join`, `repartition`, `distinct`
   - Mitigasi: Filter early, broadcast small tables

2. **Apakah partitions balanced?**
   - Check: `.explain()` atau Spark UI
   - Mitigasi: `repartition(key)` sebelum `groupBy(key)`

3. **Apakah aku re-use DataFrame berkali-kali?**
   - Yes → `.cache()`
   - No → don't cache

4. **Apakah aku bawa data ke driver?**
   - Check: `.collect()`, `.toPandas()`
   - Mitigati: Use `.write()` atau limit dengan `.limit()`

5. **Berapa jumlah partitions sekarang?**
   - Check: `df.rdd.getNumPartitions()`
   - Too many → `coalesce()`
   - Too few → `repartition()`

---

## 8. Summary: Performance Mental Model

```
CHEAP Operations (Narrow):
  filter, select, map, withColumn
  ↓ (no data movement)
  Execute in parallel per partition
  ↓
  Fast! (limited by CPU only)

EXPENSIVE Operations (Wide):
  groupBy, join, distinct, orderBy, repartition
  ↓ (SHUFFLE!)
  Write to disk → Network transfer → Read from disk
  ↓
  Slow! (limited by disk + network)
```

**Key Formula:**
```
Total Time = 
  (Narrow ops time) + 
  (Shuffle time × number of shuffles) + 
  (Largest partition processing time)
```

**Optimization Priority:**
1. **Reduce shuffles** (filter early, broadcast joins)
2. **Balance partitions** (avoid skew)
3. **Cache reused DataFrames**
4. **Right-size partitions** (100-200 MB ideal)

---

## 9. Reflection Exercise

**Analyze this code:**

```python
# Data: 1 TB user transactions, 1 MB user dimension
transactions = spark.read.parquet("transactions/")  # 10000 partitions
users = spark.read.parquet("users/")  # 1 partition

# Query
result = (transactions
    .join(users, "user_id")  # Join 1
    .filter(col("amount") > 100)
    .groupBy("country")  # GroupBy
    .agg(sum("amount").alias("total"))
    .orderBy(desc("total"))  # OrderBy
    .limit(10)
)

result.show()
```

**Questions:**

1. Berapa kali shuffle terjadi?
2. Apa masalah performa terbesar?
3. Bagaimana optimize code ini? (Hint: 3 improvements)

**Answers:**
1. **3 shuffles:** join, groupBy, orderBy
2. **Join tanpa broadcast** (users table kecil harusnya di-broadcast)
3. **Optimizations:**
   - `broadcast(users)` untuk avoid shuffle di join
   - Filter BEFORE join untuk reduce data volume
   - Limit 10 → tidak perlu full orderBy, bisa optimized

---

## 10. Checkpoint: Apa yang Sudah Kamu Pelajari?

### ✅ Core Concepts yang Sudah Dikuasai:

**1. Partitions = Unit Parallelism:**
- **1 partition = 1 task** (fundamental!)
- Data dipecah jadi chunks untuk parallel processing
- **Partition terbesar** menentukan total execution time
- Ideal size: **100-200 MB** per partition

**2. Narrow vs Wide Transformations:**
- **Narrow** = no data movement (filter, select, map)
  - ✅ FAST! Parallel processing tanpa network
- **Wide** = requires shuffle (groupBy, join, distinct)
  - ❌ SLOW! Network + disk I/O + serialization

**3. Shuffle: The Performance Killer:**
- **3 phases:** Map (write) → Network transfer → Reduce (read)
- **Cost:** Disk I/O + Network + Serialization
- **10-100x lebih lambat** dari narrow operations
- Terjadi di: groupBy, join, repartition, orderBy, distinct

**4. Partitioning Strategies:**
- **`repartition()`** = full shuffle (increase/decrease, guaranteed balance)
- **`coalesce()`** = merge only (decrease only, cheaper but may be unbalanced)
- **Rule of thumb:** 2-4x number of cores

**5. Join Optimization:**
- **Broadcast join** untuk small tables (< 10 MB)
  - No shuffle! Copy small table to all executors
  - 10-100x faster untuk large x small joins
- **Sort-merge join** untuk large x large
  - Requires shuffle both sides
  - Watch for data skew!

**6. Skew Handling:**
- **Problem:** Unbalanced partitions (1 partition >> others)
- **Impact:** 1 executor overloaded, others idle
- **Detection:** Check Spark UI (task time variance)
- **Solutions:** Salting, custom partitioning, broadcast

---

### 🎯 Performance Mental Model:

```
Total Time = Max(Partition Processing Time)
           ≈ (Largest Partition Size) / (Executor Speed)
           + (Number of Shuffles) × (Shuffle Overhead)
```

**Optimization Priority:**
1. ✅ **Reduce shuffles** (filter early, broadcast small tables)
2. ✅ **Balance partitions** (avoid skew, right-size partitions)
3. ✅ **Right partition count** (2-4x cores, 100-200 MB per partition)
4. ✅ **Cache reused DataFrames** (avoid recomputation)

---

### 🔴 Red Flags (Expensive Operations):

- `groupBy()` on skewed keys
- `join()` without broadcast (when possible)
- `repartition()` unnecessarily
- `distinct()` on large datasets
- `orderBy()` global sort
- Too many small partitions (overhead)
- Too few large partitions (underutilize cluster)

---

### 🟢 Best Practices Checklist:

**Before writing code:**
- [ ] Filter data as early as possible
- [ ] Use broadcast for small tables (< 10 MB)
- [ ] Check partition count (`df.rdd.getNumPartitions()`)
- [ ] Estimate partition size (data size / partition count)

**During development:**
- [ ] Use `.explain()` to check for shuffles
- [ ] Monitor Spark UI for skew
- [ ] Cache DataFrames used multiple times
- [ ] Avoid `.collect()` on large data

**Before production:**
- [ ] Verify partition balance
- [ ] Test with representative data size
- [ ] Set appropriate shuffle partitions config
- [ ] Monitor and tune based on metrics

---

### 📚 Next: Advanced Topics

**Coming next:**
- **Spark SQL** optimization techniques
- **Window functions** and their performance
- **Memory management** (storage levels, spill to disk)
- **Configuration tuning** (executor memory, cores, partitions)
- **Monitoring and debugging** (Spark UI deep dive)

---
