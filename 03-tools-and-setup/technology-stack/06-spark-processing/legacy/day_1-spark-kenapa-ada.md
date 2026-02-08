# Day 1: Mengapa Spark Ada? — Fondasi Mental Model

Baik, kita mulai dari akar masalahnya. Tidak ada kode hari ini, hanya membangun intuisi yang benar.

---

## 1. Masalah: Kenapa Pandas Tidak Cukup?

Bayangkan kamu punya DataFrame Pandas dengan 100 juta baris. Kamu mau:
- Filter berdasarkan kondisi
- Join dengan tabel lain (50 juta baris)
- Agregasi per kategori
- Simpan hasilnya

**Apa yang terjadi?**

```
RAM laptop/server kamu: 16 GB
Data mentah: ~8 GB
Pandas perlu load SEMUA data ke memory
Join operation: butuh ~20 GB (temporary objects)
Result: 💥 MemoryError atau swap disk (super lambat)
```

**Limitasi fundamental Pandas:**
1. **Single-machine**: Semua komputasi di 1 mesin, terbatas RAM-nya
2. **Eager execution**: Setiap operasi langsung dieksekusi, hasilnya disimpan di memory
3. **Tidak bisa scale horizontal**: Nambah mesin lain tidak membantu

---

## 2. Apa Itu Apache Spark? — Ekosistem dan Kapabilitas

### Spark Bukan Cuma "Engine Komputasi"

Banyak yang pikir Spark = alat untuk proses data besar. **Benar**, tapi tidak lengkap.

**Spark adalah UNIFIED ANALYTICS ENGINE** — 1 platform untuk berbagai kebutuhan:

```
┌─────────────────────────────────────────────────┐
│         APACHE SPARK ECOSYSTEM                   │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 Spark SQL        📡 Spark Streaming         │
│  (SQL queries,       (Real-time processing,     │
│   DataFrames)        Kafka, streaming data)     │
│                                                  │
│  🤖 MLlib            🕸️  GraphX                  │
│  (Machine Learning,  (Graph processing,         │
│   classification,    PageRank, network)         │
│   clustering)                                    │
│                                                  │
└─────────────────────────────────────────────────┘
                       ↓
         ┌─────────────────────────┐
         │   SPARK CORE ENGINE     │
         │   (RDD, scheduling,     │
         │    memory management)   │
         └─────────────────────────┘
```

### 1. Spark SQL
**Untuk apa:** Query data dengan SQL atau DataFrame API
```python
# Bisa pakai SQL langsung!
spark.sql("""
    SELECT country, COUNT(*) as total
    FROM users
    WHERE age > 30
    GROUP BY country
""").show()

# Atau DataFrame API (sama aja di balik layar)
df.filter(df.age > 30).groupBy("country").count().show()
```

**Use case:**
- ETL pipelines (extract, transform, load)
- Data warehousing queries
- Business intelligence reporting

---

### 2. Spark Streaming (Structured Streaming)
**Untuk apa:** Real-time data processing
```python
# Read streaming data dari Kafka
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .load()

# Process real-time (micro-batches)
df_stream.groupBy("user_id").count() \
    .writeStream \
    .format("console") \
    .start()
```

**Use case:**
- Real-time analytics (dashboard metrics live)
- Fraud detection (detect anomali langsung)
- IoT sensor processing (millions events/sec)

---

### 3. MLlib (Machine Learning)
**Untuk apa:** Distributed machine learning
```python
from pyspark.ml.classification import LogisticRegression

# Train model di data besar (terabytes)
lr = LogisticRegression(featuresCol="features", labelCol="label")
model = lr.fit(training_df)  # Distributed training!

# Predict di data besar juga
predictions = model.transform(test_df)
```

**Use case:**
- Classification (spam detection, churn prediction)
- Clustering (customer segmentation)
- Recommendation systems (collaborative filtering)

---

### 4. GraphX
**Untuk apa:** Graph processing (network analysis)
```python
# Analyze social network, find communities
from pyspark import GraphFrame

result = graph.pageRank(resetProbability=0.15, maxIter=10)
```

**Use case:**
- Social network analysis (influencer detection)
- Fraud detection (find suspicious patterns)
- Network topology (routing optimization)

---

### Kenapa "Unified" Itu Penting?

**Traditional approach (Pre-Spark):**
```
Batch processing  → Hadoop MapReduce
SQL queries       → Hive (di atas Hadoop)
Streaming         → Storm atau Flink
Machine learning  → Mahout atau custom

Problem:
- Beda tools = beda codebase, beda team skills
- Data movement antar systems (inefficient!)
- Hard to maintain
```

**Spark approach:**
```
Batch, SQL, Streaming, ML → SEMUA di Spark

Benefit:
- 1 codebase (Python/Scala/Java)
- 1 cluster, 1 team skillset
- Data tidak perlu move (share memory)
- Easier integration
```

**Contoh Real-world Pipeline:**
```python
# 1. Batch ETL (Spark SQL)
df_raw = spark.read.parquet("transactions/")
df_clean = df_raw.filter(...).transform(...)

# 2. Feature engineering untuk ML (MLlib)
from pyspark.ml.feature import VectorAssembler
df_features = VectorAssembler(...).transform(df_clean)

# 3. Train model
model = LogisticRegression().fit(df_features)

# 4. Real-time prediction (Streaming)
stream = spark.readStream.format("kafka").load()
predictions = model.transform(stream)

# SEMUA dalam 1 platform!
```

---

## 3. In-Memory Processing: Kenapa Spark Jauh Lebih Cepat dari Hadoop MapReduce?

### Hadoop MapReduce: The Old Way

**Cara kerja MapReduce:**
```
1. Read data dari disk (HDFS)
   ↓
2. Map operation (process)
   ↓
3. Write intermediate results ke DISK ← LAMBAT!
   ↓
4. Read dari disk lagi
   ↓
5. Reduce operation
   ↓
6. Write final result ke DISK
```

**Problem:** Setiap step tulis-baca disk!

**Analogi:**
Kayak kamu ngerjain soal matematika, setiap step:
1. Tulis hasil di kertas
2. Simpan kertas di laci
3. Buka laci, ambil kertas
4. Baca hasil
5. Lanjut step berikutnya

**SANGAT LAMBAT!** Disk I/O = bottleneck (100-1000x lebih lambat dari RAM)

---

### Spark: In-Memory Processing

**Cara kerja Spark:**
```
1. Read data dari disk ke MEMORY
   ↓
2. Operation 1 (di memory)
   ↓
3. Operation 2 (di memory)
   ↓
4. Operation 3 (di memory)
   ↓
5. Write final result ke disk (1x aja!)
```

**Keuntungan:** Intermediate results di RAM, tidak perlu tulis-baca disk!

**Analogi:**
Kamu ngerjain soal matematika di kepala:
1. Ingat hasil sementara (di otak)
2. Lanjut step berikutnya
3. Tulis cuma hasil akhir

**JAUH LEBIH CEPAT!**

---

### Comparison: MapReduce vs Spark

**Iterative algorithm example (Machine Learning):**

```
MapReduce:
Iteration 1: Read disk → compute → write disk (10 sec)
Iteration 2: Read disk → compute → write disk (10 sec)
Iteration 3: Read disk → compute → write disk (10 sec)
...
Iteration 10: Read disk → compute → write disk (10 sec)
Total: 100 seconds


Spark:
Read disk → cache in memory (5 sec)
Iteration 1: compute in memory (1 sec)
Iteration 2: compute in memory (1 sec)
Iteration 3: compute in memory (1 sec)
...
Iteration 10: compute in memory (1 sec)
Write disk (2 sec)
Total: 17 seconds

🚀 Spark 5-6x lebih cepat!
```

**Real-world benchmark:**
- Spark: **100x faster** untuk iterative algorithms (ML)
- Spark: **10x faster** untuk typical ETL workloads

---

### Kapan In-Memory Tidak Cukup?

**Spark bukan magic:**
```
Data size: 10 TB
Cluster RAM: 1 TB total

Problem: Data tidak muat di memory!

Solution:
- Spark otomatis "spill to disk" (tulis sebagian ke disk)
- Tetap lebih cepat dari MapReduce (partial in-memory)
- Tapi tidak dapet speedup 100x (maybe 10x aja)
```

**Key insight:** Spark fast **because** in-memory, tapi bisa handle data > RAM (dengan trade-off performa)

---

## 4. Mental Model: "Distributed Computing" Itu Apa Sebenarnya?

### Analogi: Tim Pabrik vs Pekerja Solo

**Pandas = 1 orang pekerja super cepat**
- Dia kerja sendirian
- Punya meja kerja (RAM) yang terbatas
- Kalau tugasnya terlalu banyak, mejanya penuh → stuck

**Spark = 1 manajer + banyak pekerja**
- **Manajer (Driver)**: Bikin rencana kerja, koordinasi
- **Pekerja (Executors)**: Terima task, eksekusi paralel
- **Meja kerja terdistribusi**: Setiap pekerja punya mejanya sendiri (RAM masing-masing)

**Kunci intuisi:**
- Data tidak perlu ada di 1 tempat sekaligus
- Pekerjaan dipecah jadi task-task kecil yang bisa dikerjakan paralel
- Hasil akhir "dikumpulkan" kembali oleh manajer

---

## 5. Arsitektur Spark: Driver, Executors, Tasks, Partitions

```
┌─────────────────────────────────────────────────┐
│  DRIVER (Manajer)                               │
│  - Terima query dari kamu                       │
│  - Bikin "execution plan" (DAG)                 │
│  - Koordinasi semua executors                   │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
   ┌────▼───┐ ┌──▼─────┐ ┌─▼──────┐
   │Executor│ │Executor│ │Executor│  (Pekerja)
   │ Task 1 │ │ Task 2 │ │ Task 3 │
   │ Task 4 │ │ Task 5 │ │ Task 6 │
   └────────┘ └────────┘ └────────┘
        │         │         │
   Data Part1  Part2   Part3
```

### Konsep Penting:

**Partition** = Potongan data
- Data besar dipecah jadi "chunks" (partitions)
- Setiap partition bisa diproses independen oleh executor berbeda
- Contoh: 1 file CSV 10 GB → dipecah jadi 100 partitions (100 MB each)

**Task** = Unit kerja paling kecil
- 1 task = operasi pada 1 partition
- Task berjalan paralel di executors yang berbeda
- Contoh: filter(), map(), aggregate() pada 1 partition = 1 task

**Executor** = Worker process
- Punya CPU cores dan RAM sendiri
- Bisa jalanin multiple tasks secara paralel (1 task per core)

**Driver** = Otak operasi
- Hidup di 1 mesin (laptop kamu / master node)
- Tidak proses data besar, hanya koordinasi
- Kalau kamu panggil `.collect()` → hasil dibawa ke driver (hati-hati!)

### Cluster Manager: Siapa yang Atur Resource?

**Driver dan Executors itu process**, tapi siapa yang alokasi RAM dan CPU untuk mereka?

**Jawabannya: Cluster Manager**

```
┌─────────────────────────────────────────────────┐
│         CLUSTER MANAGER OPTIONS                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Standalone        (bundled with Spark)      │
│  2. YARN              (Hadoop ecosystem)        │
│  3. Kubernetes        (container orchestration) │
│  4. Mesos             (legacy, jarang dipakai)  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

### 1. Spark Standalone

**Apa itu:**
- Cluster manager default dari Spark
- Tidak butuh install software tambahan
- Paling simple untuk mulai

**Cara kerja:**
```
1. Start master process:
   $ spark-master.sh start
   
2. Start worker processes di setiap node:
   $ spark-worker.sh start spark://master-ip:7077
   
3. Submit job:
   $ spark-submit --master spark://master-ip:7077 my_job.py
```

**Use case:**
- Development/testing
- Small clusters (< 100 nodes)
- Dedicated Spark clusters

**Limitation:**
- Hanya untuk Spark (tidak bisa share cluster dengan MapReduce, dll)
- Basic resource isolation

---

### 2. YARN (Yet Another Resource Negotiator)

**Apa itu:**
- Resource manager dari Hadoop ecosystem
- Industry standard untuk enterprise

**Cara kerja:**
```
YARN Architecture:

┌─────────────────┐
│ ResourceManager │ ← Koordinasi cluster resources
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌──▼───┐
│ NM 1 │   │ NM 2 │  ← NodeManagers (per node)
└──────┘   └──────┘
   │          │
   ├─ Container 1 (Spark Executor)
   ├─ Container 2 (Spark Executor)
   └─ Container 3 (MapReduce task)
```

**Submit job:**
```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 10 \
  --executor-memory 4G \
  --executor-cores 2 \
  my_job.py
```

**Use case:**
- Existing Hadoop clusters
- Multi-tenant environments (Spark + Hive + MapReduce)
- Enterprise production deployments

**Benefit:**
- Share cluster dengan workloads lain
- Mature resource management
- Security integration (Kerberos)

---

### 3. Kubernetes

**Apa itu:**
- Modern container orchestration platform
- Cloud-native, vendor-neutral

**Cara kerja:**
```yaml
# spark-job.yaml
apiVersion: v1
kind: Pod
metadata:
  name: spark-driver
spec:
  containers:
  - name: spark
    image: spark:3.5.0
    command: ["/opt/spark/bin/spark-submit"]
```

**Submit job:**
```bash
spark-submit \
  --master k8s://https://kubernetes-api:6443 \
  --deploy-mode cluster \
  --conf spark.executor.instances=5 \
  --conf spark.kubernetes.container.image=my-spark:latest \
  my_job.py
```

**Use case:**
- Cloud environments (GKE, EKS, AKS)
- Microservices architecture
- Dynamic scaling (auto-scale executors)

**Benefit:**
- Native cloud integration
- Container isolation
- Easy scaling (horizontal pod autoscaler)
- Multi-cloud portability

---

### Comparison: Kapan Pakai Yang Mana?

| Aspect | Standalone | YARN | Kubernetes |
|--------|-----------|------|------------|
| **Setup** | Mudah | Medium | Medium-Hard |
| **Use case** | Dev/test | Hadoop ecosystem | Cloud-native |
| **Multi-tenancy** | ❌ No | ✅ Yes | ✅ Yes |
| **Resource isolation** | Basic | Good | Excellent |
| **Scaling** | Manual | Good | Auto-scale |
| **Best for** | Dedicated Spark | Enterprise on-prem | Cloud deployments |

**Decision tree:**
```
Punya Hadoop cluster existing?
├─ Yes → YARN
└─ No
   │
   ├─ Pakai cloud (AWS, GCP, Azure)?
   │  ├─ Yes → Kubernetes
   │  └─ No
   │     │
   │     └─ Cluster kecil, dedicated Spark?
   │        └─ Standalone
```

---

## 6. Lazy Evaluation: Kenapa Spark "Menunda" Eksekusi?

**Pandas:**
```python
df = pd.read_csv("big.csv")  # ← Langsung load semua ke RAM!
df_filtered = df[df.age > 30]  # ← Langsung eksekusi filter!
```

**Spark:**
```python
df = spark.read.csv("big.csv")  # ← Belum baca file! Cuma "rencana"
df_filtered = df.filter(df.age > 30)  # ← Belum eksekusi! Cuma tambah rencana

# Baru dieksekusi kalau ada "action" (misal: count, show, write)
df_filtered.count()  # ← INI baru Spark kerja!
```

### Kenapa Menunda Eksekusi?

**Analogi: Chef Restoran**

Pandas = Chef yang langsung masak begitu kamu pesan
- Kamu: "Bikin salad"
- Chef: *masak* (5 menit)
- Kamu: "Tambah tomat"
- Chef: "Aduh, salad sudah jadi... buang, bikin ulang" (5 menit lagi)

Spark = Chef yang catat semua pesanan dulu, baru masak
- Kamu: "Bikin salad"
- Chef: *tulis di kertas*
- Kamu: "Tambah tomat"
- Chef: *tulis di kertas*
- Kamu: "Oke, sajikan"
- Chef: *lihat catatan*, "Oh bisa langsung bikin salad + tomat sekaligus!" (3 menit)

**Keuntungan Lazy Evaluation:**

1. **Optimization**: Spark bisa "merge" operations, skip yang tidak perlu
   - `filter().filter().select()` → Spark bisa optimize jadi 1 scan
   
2. **Avoid unnecessary work**: Kalau kamu cuma butuh 10 baris (`.limit(10)`), Spark tidak proses semua data

3. **Efficient pipelining**: Semua transformasi bisa di-"chain" tanpa intermediate results di disk

---

## 7. Kapan Spark Adalah Tool yang Tepat?

### ✅ Gunakan Spark Kalau:
1. **Data > RAM 1 mesin** (100 GB+, milyaran baris)
2. **Butuh scale horizontal** (nambah mesin = nambah kapasitas)
3. **Processing bisa diparalelkan** (aggregations, joins, transformations)
4. **Data sudah di distributed storage** (HDFS, S3, GCS, BigQuery)

### ❌ Spark OVERKILL Kalau:
1. **Data kecil** (< 10 GB, muat di RAM)
   - Pandas lebih cepat (no overhead koordinasi)
2. **Operasi yang susah diparalelkan** (operasi sequential, stateful)
3. **Prototyping cepat** (Spark butuh setup cluster, Pandas cukup laptop)
4. **Hasil akhir kecil tapi intermediate besar** (kadang cukup SQL + aggregation dulu)

### 🤔 Gray Area:
- Data 20-50 GB: bisa Pandas (kalau RAM cukup) atau Spark (kalau mau scale nanti)
- Depends on: kompleksitas query, budget, team expertise

---

## 8. Spark ≠ "Pandas But Faster"

**Misconceptions paling umum:**

### ❌ Salah: "Spark itu Pandas yang cepat"
**Kenapa salah:**
- Spark punya overhead (koordinasi, serialization, network)
- Untuk data kecil, Pandas lebih cepat
- Spark bukan "drop-in replacement"

### ✅ Benar: "Spark itu untuk data yang TIDAK MUAT di 1 mesin"
- Spark scale ke ratusan GB - petabytes
- Trade-off: kompleksitas infrastruktur vs kapasitas data

---

### ❌ Salah: "Lazy evaluation = lambat"
**Kenapa salah:**
- Lazy = Spark bisa optimize execution plan
- Pandas eager = setiap step langsung, banyak temporary data

### ✅ Benar: "Lazy evaluation = Spark pintar tunggu sampe punya gambaran lengkap baru eksekusi optimal"

---

### ❌ Salah: "Semua operasi Spark paralel otomatis"
**Kenapa salah:**
- Operasi kayak `.collect()` atau `.toPandas()` → bawa semua data ke driver (bottleneck!)
- Operasi sequential (window functions dengan order) susah di-paralelkan

### ✅ Benar: "Spark parallelize operasi yang bisa di-partition (filter, map, join, groupby), tapi kamu harus desain pipeline yang partition-friendly"

---

## 9. Reflection: Apakah Spark Membantu di Kasus Ini?

Pikirkan skenario berikut dan jawab: **Spark tepat, overkill, atau gray area?**

1. **Kasus A:**
   - Data: 5 juta baris transaction logs (2 GB CSV)
   - Task: Filter by date, aggregate sum per user
   - Env: Laptop 16 GB RAM

2. **Kasus B:**
   - Data: 500 juta baris clickstream events (200 GB Parquet di S3)
   - Task: Join dengan user dimension table (1 juta users), aggregate per hour
   - Env: Punya akses ke cluster 10 nodes

3. **Kasus C:**
   - Data: 50 GB sensor data (streaming from Kafka)
   - Task: Real-time aggregation per 5 menit window, save ke BigQuery
   - Env: GCP environment

4. **Kasus D:**
   - Data: 100 MB Excel file
   - Task: Pivot table, conditional formatting
   - Env: Laptop

---

## 10. Checkpoint: Apa yang Sudah Kamu Pelajari?

### ✅ Foundation yang Sudah Dikuasai:

**1. Big Picture:**
- Pandas = single-machine, eager, limited by RAM
- Spark = distributed, lazy, scale horizontal
- Spark bukan "Pandas but faster" → untuk data yang TIDAK MUAT di 1 mesin

**2. Spark Ecosystem:**
- **Spark SQL** → queries dan DataFrame operations
- **Spark Streaming** → real-time data processing
- **MLlib** → distributed machine learning
- **GraphX** → graph/network analysis
- Unified platform = 1 codebase untuk semua use cases

**3. Why Spark is Fast:**
- **In-memory processing** vs Hadoop MapReduce (disk I/O)
- 10-100x speedup untuk iterative algorithms
- Tetap bisa handle data > RAM (spill to disk)

**4. Architecture Components:**
- **Driver** = manajer (coordination, logical planning)
- **Executors** = pekerja (data processing)
- **Partitions** = potongan data (unit of parallelism)
- **Tasks** = unit kerja (1 task per partition)

**5. Cluster Managers:**
- **Standalone** → simple, dedicated Spark clusters
- **YARN** → Hadoop ecosystem, enterprise
- **Kubernetes** → cloud-native, containers

**6. Lazy Evaluation:**
- Transformations = cheap (cuma update plan)
- Actions = expensive (trigger execution)
- Catalyst optimizer bekerja di balik layar

---

### 🎯 Apa yang Perlu Kamu Ingat:

1. **Spark untuk data BESAR** (> memory 1 mesin)
2. **In-memory = kunci kecepatan** (vs MapReduce)
3. **Ecosystem lengkap** (batch, streaming, ML dalam 1 platform)
4. **Lazy = smart** (optimize sebelum execute)
5. **Pilih cluster manager** sesuai environment

---

### 📚 Next: Deep Dive ke Code

**Belum dibahas (coming next):**
- **RDD** (Resilient Distributed Dataset) → low-level API
- **RDD vs DataFrame** → when to use each
- **Schema** (StructType, schema inference)
- **Transformations vs Actions** → detail operations
- **Partitioning strategies** → performance tuning
- **Shuffle operations** → what makes Spark slow
- **Code konkret** → hands-on examples

---
