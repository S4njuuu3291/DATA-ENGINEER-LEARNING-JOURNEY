# Day 2: Spark DataFrame API — Cara Spark "Berpikir" Tentang Kode Kamu

Hari ini kita masuk ke **mesin di balik layar**. Bukan tentang `.select()` atau `.filter()`, tapi **bagaimana Spark mengeksekusi kode kamu**.

---

## 1. RDD (Resilient Distributed Dataset) — Fondasi Spark

Sebelum bicara DataFrame, kamu harus paham **RDD** — the original Spark abstraction.

### Apa Itu RDD?

**RDD = Resilient Distributed Dataset**

```
┌─────────────────────────────────────────────────────────┐
│  RDD = Collection of objects distributed across cluster │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ Resilient    → Fault-tolerant (auto-recovery)      │
│  ✅ Distributed  → Partitioned across nodes            │
│  ✅ Dataset      → Collection of data elements         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 3 Karakteristik Utama RDD:

#### 1. **Immutable (Tidak Bisa Diubah)**

```python
# RDD original
rdd1 = sc.parallelize([1, 2, 3, 4, 5])

# Operasi menghasilkan RDD BARU (rdd1 tidak berubah!)
rdd2 = rdd1.map(lambda x: x * 2)

print(rdd1.collect())  # [1, 2, 3, 4, 5]  ← masih sama!
print(rdd2.collect())  # [2, 4, 6, 8, 10] ← hasil baru
```

**Analogi:**
Kayak string di Python:
```python
s = "hello"
s.upper()  # Tidak ubah s!
print(s)   # "hello" ← masih lowercase

s2 = s.upper()  # Harus assign ke variable baru
print(s2)  # "HELLO"
```

**Kenapa immutable?**
- Fault tolerance: Spark bisa rebuild RDD dari parent RDD kalau node crash
- Thread-safe: Tidak ada race condition di parallel processing
- Optimization: Spark bisa optimize execution plan

---

#### 2. **Distributed (Terdistribusi Across Partitions)**

```python
rdd = sc.parallelize([1, 2, 3, 4, 5, 6], numSlices=3)
```

**Physical distribution:**
```
RDD (logical view):  [1, 2, 3, 4, 5, 6]

Partitions (physical):
Executor 1: Partition 0 → [1, 2]
Executor 2: Partition 1 → [3, 4]
Executor 3: Partition 2 → [5, 6]
```

**Operations execute in parallel:**
```python
rdd.map(lambda x: x * 2)

# What happens:
Executor 1: [1, 2] → map → [2, 4]      ┐
Executor 2: [3, 4] → map → [6, 8]      ├─ Paralel!
Executor 3: [5, 6] → map → [10, 12]    ┘
```

---

#### 3. **Fault-Tolerant (Auto Recovery)**

**RDD menyimpan "lineage" (silsilah):**

```python
# Step 1
rdd1 = sc.textFile("data.txt")
# Step 2
rdd2 = rdd1.filter(lambda x: len(x) > 10)
# Step 3
rdd3 = rdd2.map(lambda x: x.upper())

# Lineage graph:
# rdd1 → rdd2 → rdd3
```

**Kalau Executor 2 crash:**
```
Executor 2 processing partition 5 of rdd3... 💥 CRASH!

Spark:
1. Check lineage: rdd3 = rdd2.map(...)
2. Check lineage: rdd2 = rdd1.filter(...)
3. Check lineage: rdd1 = textFile(...)
4. Rebuild: Read partition 5 → filter → map
5. ✅ Continue execution

Total: No data loss! Auto-recovery!
```

**Analogy:**
Kayak recipe masakan:
- Kalau masakanmu tumpah, kamu tidak perlu minta ke orang lain
- Kamu bisa baca recipe dari awal dan masak ulang
- RDD lineage = recipe (cara rebuild data)

---

### Operasi di RDD: Transformations vs Actions

Just like DataFrame, RDD punya 2 jenis operasi:

#### Transformations (Lazy)
```python
rdd2 = rdd1.map(lambda x: x * 2)       # Lazy
rdd3 = rdd2.filter(lambda x: x > 5)    # Lazy
rdd4 = rdd3.distinct()                 # Lazy
```

#### Actions (Eager)
```python
result = rdd.collect()      # Bring all data to driver
count = rdd.count()         # Count elements
first = rdd.first()         # Get first element
rdd.saveAsTextFile("out/") # Write to disk
```

---

### RDD vs DataFrame: The Evolution

**RDD (Low-level API):**
```python
# Process text file
rdd = sc.textFile("users.txt")
rdd_split = rdd.map(lambda line: line.split(","))
rdd_filtered = rdd_split.filter(lambda fields: int(fields[2]) > 30)
rdd_result = rdd_filtered.map(lambda fields: (fields[1], 1))
result = rdd_result.reduceByKey(lambda a, b: a + b)
```

**DataFrame (High-level API):**
```python
# Same operation, more expressive
df = spark.read.csv("users.csv", header=True)
result = df.filter(df.age > 30).groupBy("city").count()
```

---

### Kapan Pakai RDD vs DataFrame?

**✅ Pakai RDD Kalau:**

1. **Unstructured data** (text, logs, binary)
   ```python
   # Log parsing
   logs = sc.textFile("app.log")
   errors = logs.filter(lambda line: "ERROR" in line)
   ```

2. **Fine-grained control** (optimization manual)
   ```python
   # Custom partitioning logic
   rdd.partitionBy(custom_partitioner)
   ```

3. **Legacy code** (codebase lama pakai RDD)

4. **Complex transformations** tidak supported di DataFrame
   ```python
   # Complex nested operations
   rdd.mapPartitions(custom_complex_function)
   ```

---

**✅ Pakai DataFrame Kalau:**

1. **Structured/semi-structured data** (CSV, JSON, Parquet, SQL tables)
   ```python
   df = spark.read.parquet("users.parquet")
   ```

2. **SQL-like operations** (filter, join, groupBy, aggregate)
   ```python
   df.groupBy("country").agg(sum("amount"))
   ```

3. **Better performance** dengan Catalyst optimizer
   - Predicate pushdown
   - Column pruning
   - Join optimization

4. **Type safety** dengan schema
   ```python
   df.printSchema()  # Know data types!
   ```

5. **Interoperability** dengan Spark SQL
   ```python
   df.createOrReplaceTempView("users")
   spark.sql("SELECT * FROM users WHERE age > 30")
   ```

---

### Performance Comparison

**Benchmark: Filter + Aggregate 1 TB data**

```
RDD approach:
rdd.filter(lambda x: x[2] > 30) \
   .map(lambda x: (x[1], x[3])) \
   .reduceByKey(lambda a, b: a + b)
Time: 120 seconds

DataFrame approach:
df.filter(df.age > 30) \
  .groupBy("city") \
  .sum("amount")
Time: 45 seconds

🚀 DataFrame 2.5x faster!
```

**Kenapa DataFrame lebih cepat?**

1. **Catalyst optimizer:**
   - Pushdown filters (read less data)
   - Column pruning (read only needed columns)
   - Join reordering

2. **Tungsten execution engine:**
   - Binary format (not JVM objects)
   - Code generation (JIT compilation)
   - Memory management (off-heap)

3. **Schema awareness:**
   - Skip deserialization when possible
   - Vectorized operations

---

### RDD to DataFrame Conversion

**From RDD to DataFrame:**
```python
# RDD of tuples
rdd = sc.parallelize([("Alice", 30), ("Bob", 25)])

# Convert to DataFrame (with schema)
from pyspark.sql import Row
df = rdd.map(lambda x: Row(name=x[0], age=x[1])).toDF()

# Or dengan schema explicit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])
df = spark.createDataFrame(rdd, schema)
```

**From DataFrame to RDD:**
```python
df = spark.read.json("users.json")
rdd = df.rdd  # Convert to RDD of Row objects

# Process as RDD
rdd.map(lambda row: row.name.upper())
```

---

### Summary: RDD Concepts

**Key Takeaways:**

1. **RDD = fundamental abstraction** (tapi jarang dipakai directly nowadays)
2. **3 properties:** Immutable, Distributed, Fault-tolerant
3. **Lineage graph** → auto-recovery kalau failure
4. **DataFrame built on top of RDD** (high-level API)
5. **Use DataFrame by default** (better performance + easier to use)
6. **Use RDD only** untuk unstructured data atau complex custom logic

**Mental model:**
```
RDD = Assembly language (low-level, powerful, complex)
DataFrame = Python/Java (high-level, optimized, easier)

Sama kayak kamu jarang tulis assembly,
kamu jarang perlu tulis RDD code directly.
```

---

## 2. Apa Itu DataFrame Sebenarnya?

### Pandas DataFrame vs Spark DataFrame

**Pandas DataFrame:**
```python
df = pd.read_csv("data.csv")  # ← Data LANGSUNG di RAM
type(df)  # pandas.core.frame.DataFrame
# df = objek konkret berisi data
```

**Spark DataFrame:**
```python
df = spark.read.csv("data.csv")  # ← BELUM ada data!
type(df)  # pyspark.sql.dataframe.DataFrame
# df = RENCANA bagaimana data akan dibaca
```

### Mental Model: Blueprint vs Bangunan

**Pandas DataFrame = Bangunan sudah jadi**
- Kamu bisa lihat, sentuh, ukur langsung
- Kalau mau ubah, harus bongkar-bangun ulang

**Spark DataFrame = Blueprint / Denah Arsitek**
- Bukan bangunan fisik, cuma rencana
- Kamu bisa edit denah berkali-kali (murah, cepat)
- Bangunan baru dibangun kalau kamu bilang "Oke, eksekusi!"

---

## 3. Schema: Blueprint Data Structure

### Apa Itu Schema?

**Schema = metadata yang describe struktur DataFrame**
- Nama kolom
- Tipe data setiap kolom
- Nullable (boleh NULL atau tidak)

**Analogi:**
Schema = "form pendaftaran" dengan field-field yang sudah ditentukan:
```
┌────────────────────────────────┐
│  FORMULIR PENDAFTARAN          │
├────────────────────────────────┤
│  Nama:    [________] (String)  │
│  Umur:    [___] (Integer)      │
│  Email:   [________] (String)  │
│  Aktif:   [☐] (Boolean)        │
└────────────────────────────────┘
```

Tanpa schema = data bentuk bebas (RDD), susah di-optimize!

---

### Lihat Schema DataFrame

```python
df = spark.read.json("users.json")

# Method 1: Print schema
df.printSchema()
```

**Output:**
```
root
 |-- name: string (nullable = true)
 |-- age: integer (nullable = true)
 |-- email: string (nullable = true)
 |-- is_active: boolean (nullable = true)
 |-- salary: double (nullable = true)
```

**Baca:**
- `name` = kolom nama, tipe String, boleh NULL
- `age` = kolom umur, tipe Integer, boleh NULL
- dst.

```python
# Method 2: Get schema object
schema = df.schema
print(schema)
# StructType([
#     StructField('name', StringType(), True),
#     StructField('age', IntegerType(), True),
#     ...
# ])

# Method 3: DDL string (SQL-style)
print(df.schema.simpleString())
# struct<name:string,age:int,email:string,is_active:boolean,salary:double>
```

---

### Schema Inference vs Explicit Schema

#### 1. **Schema Inference (Otomatis)**

Spark "scan" sample data untuk detect tipe:

```python
# Spark akan scan file untuk detect schema
df = spark.read.json("users.json")
df = spark.read.csv("data.csv", header=True, inferSchema=True)
```

**Pros:**
- ✅ Mudah (tidak perlu define manual)
- ✅ Cepat untuk prototyping

**Cons:**
- ❌ Butuh extra scan (read data 2x: 1x inference, 1x actual processing)
- ❌ Bisa salah detect (contoh: "123" dibaca as String padahal mau Integer)
- ❌ Tidak deterministic (kalau data sample beda, schema bisa beda)

**Contoh masalah:**
```python
# File CSV:
# id,amount
# 1,100
# 2,200
# 3,null

df = spark.read.csv("data.csv", header=True, inferSchema=True)
df.printSchema()
# amount: string (nullable = true)  ← SALAH! Harusnya integer/double

# Kenapa? Karena "null" dibaca sebagai string
```

---

#### 2. **Explicit Schema (Manual)**

Kamu tentukan schema sebelum read:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType

# Define schema
schema = StructType([
    StructField("name", StringType(), nullable=True),
    StructField("age", IntegerType(), nullable=True),
    StructField("email", StringType(), nullable=True),
    StructField("is_active", BooleanType(), nullable=True),
    StructField("salary", DoubleType(), nullable=True)
])

# Read dengan schema explicit
df = spark.read.schema(schema).json("users.json")
```

**Pros:**
- ✅ Lebih cepat (skip inference step)
- ✅ Predictable (schema selalu sama)
- ✅ Type safety (error kalau data tidak match)

**Cons:**
- ❌ Verbose (banyak code)
- ❌ Harus update manual kalau schema berubah

---

### DDL String (Shortcut untuk Define Schema)

Instead of StructType, bisa pakai DDL string:

```python
# DDL string (SQL-style, lebih ringkas)
ddl_schema = "name STRING, age INT, email STRING, is_active BOOLEAN, salary DOUBLE"

df = spark.read.schema(ddl_schema).json("users.json")
```

**Sama aja hasilnya**, tapi lebih ringkas!

---

### Nested Schema (Complex Types)

Spark support nested structures:

```python
# JSON dengan nested object
"""
{
  "name": "Alice",
  "age": 30,
  "address": {
    "city": "Jakarta",
    "country": "Indonesia"
  },
  "phones": ["081234567890", "087654321098"]
}
"""

df = spark.read.json("users_nested.json")
df.printSchema()
```

**Output:**
```
root
 |-- name: string (nullable = true)
 |-- age: integer (nullable = true)
 |-- address: struct (nullable = true)
 |    |-- city: string (nullable = true)
 |    |-- country: string (nullable = true)
 |-- phones: array (nullable = true)
 |    |-- element: string (containsNull = true)
```

**Explicit schema untuk nested:**
```python
from pyspark.sql.types import ArrayType

nested_schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("address", StructType([
        StructField("city", StringType(), True),
        StructField("country", StringType(), True)
    ]), True),
    StructField("phones", ArrayType(StringType()), True)
])

df = spark.read.schema(nested_schema).json("users_nested.json")
```

**Akses nested field:**
```python
# Dot notation
df.select("address.city").show()

# Column expression
from pyspark.sql.functions import col
df.select(col("address.city")).show()

# Array indexing
df.select(col("phones")[0].alias("primary_phone")).show()
```

---

### Schema Evolution & Compatibility

**Problem:** Schema berubah over time

```
Version 1 (2024):
users.parquet: name, age, email

Version 2 (2025):
users_new.parquet: name, age, email, phone, country
```

**Solution 1: Union with missing columns as NULL**
```python
df1 = spark.read.parquet("users_2024.parquet")
df2 = spark.read.parquet("users_2025.parquet")

# Add missing columns
from pyspark.sql.functions import lit
df1 = df1.withColumn("phone", lit(None).cast("string")) \
         .withColumn("country", lit(None).cast("string"))

# Now can union
df_combined = df1.union(df2)
```

**Solution 2: Schema merging (Parquet)**
```python
# Parquet support schema merging
df = spark.read.option("mergeSchema", "true").parquet("users/*.parquet")
```

---

### Kenapa Schema Penting?

**1. Performance Optimization**
```python
# Tanpa schema: Spark tidak tahu kolom apa yang ada
df = spark.read.text("data.txt")  # Everything as string!

# Process semua data as string (lambat!)
df.filter(...)  # No predicate pushdown

# Dengan schema: Spark bisa optimize
df = spark.read.schema(schema).json("data.json")
# Predicate pushdown, column pruning, filter pushdown to storage
```

---

**2. Type Safety**
```python
# Inferensi salah: age dibaca as String
df = spark.read.csv("users.csv")
result = df.select(df.age + 10)  # ERROR! Can't add string + int

# Explicit schema: age as Integer
df = spark.read.schema(schema).csv("users.csv")
result = df.select(df.age + 10)  # ✅ OK!
```

---

**3. Data Validation**
```python
# Schema dengan nullable=False
schema = StructType([
    StructField("id", IntegerType(), nullable=False),  # MUST not NULL
    StructField("name", StringType(), nullable=False)
])

df = spark.read.schema(schema).json("data.json")
# Kalau ada row dengan id=NULL → ERROR saat runtime
# Data validation otomatis!
```

---

### Best Practices: Schema Management

**✅ DO:**

1. **Explicit schema di production**
   ```python
   # Production code
   schema = StructType([...])
   df = spark.read.schema(schema).parquet("s3://data/")
   ```

2. **Centralize schema definitions**
   ```python
   # schemas.py
   USER_SCHEMA = StructType([...])
   TRANSACTION_SCHEMA = StructType([...])
   
   # main.py
   from schemas import USER_SCHEMA
   df = spark.read.schema(USER_SCHEMA).json("users.json")
   ```

3. **Version schema**
   ```python
   # schemas_v1.py
   USER_SCHEMA_V1 = StructType([...])
   
   # schemas_v2.py
   USER_SCHEMA_V2 = StructType([...])  # Added new fields
   ```

---

**❌ DON'T:**

1. **inferSchema di production (untuk data besar)**
   ```python
   # ❌ SLOW: scan 1 TB data just to infer schema
   df = spark.read.csv("s3://huge-data/", inferSchema=True)
   
   # ✅ FAST: schema already known
   df = spark.read.schema(known_schema).csv("s3://huge-data/")
   ```

2. **Assume schema never changes**
   ```python
   # ❌ Hard-coded column names
   df.select("col1", "col2", "col3")
   # Kalau schema berubah → code break!
   
   # ✅ Defensive
   available_cols = df.columns
   cols_to_select = [c for c in ["col1", "col2", "col3"] if c in available_cols]
   df.select(cols_to_select)
   ```

---

### Schema Summary

**Key Takeaways:**

1. **Schema = struktur data** (column names + types + nullable)
2. **Inference = auto-detect** (mudah tapi lambat, bisa salah)
3. **Explicit = manual define** (cepat, predictable, type-safe)
4. **StructType** = schema untuk structured data
5. **DDL string** = shortcut untuk define schema
6. **Nested schema** supported (struct, array, map)
7. **Production: always explicit schema!**

---

## 4. Logical Plan vs Physical Execution

Setiap kali kamu tulis kode Spark, ada **2 fase**:

```
Kode kamu → Logical Plan → Optimized Plan → Physical Plan → Eksekusi
```

### Contoh Konkret:

```python
# Kode kamu
df = spark.read.parquet("users.parquet")
df_filtered = df.filter(df.age > 30)
df_selected = df_filtered.select("name", "city")
result = df_selected.groupBy("city").count()

# Di tahap ini: BELUM ADA eksekusi!
# Spark cuma bikin "logical plan" (pohon operasi)
```

**Logical Plan** (Abstract Syntax Tree):
```
┌─────────────┐
│  groupBy    │  ← Agregasi per city
└──────┬──────┘
       │
┌──────▼──────┐
│   select    │  ← Ambil kolom name, city
└──────┬──────┘
       │
┌──────▼──────┐
│   filter    │  ← Filter age > 30
└──────┬──────┘
       │
┌──────▼──────┐
│    read     │  ← Baca file
└─────────────┘
```

**Catalyst Optimizer** kemudian:
1. Analisa logical plan
2. Cari cara lebih efisien (predicate pushdown, column pruning, dll)
3. Bikin **Optimized Logical Plan**

**Physical Plan** (eksekusi konkret):
- Tentukan berapa partitions
- Alokasi tasks ke executors
- Baru eksekusi kalau ada **action**

---

## 5. Transformations vs Actions: The Core Distinction

### Transformations = Edit Blueprint (Lazy)

**Karakteristik:**
- **Lazy**: Tidak trigger eksekusi
- **Chainable**: Bisa ditumpuk tanpa cost
- Return DataFrame/RDD baru

**Contoh:**
```python
df.filter()
df.select()
df.withColumn()
df.join()
df.groupBy()  # ← ini transformation! Belum aggregate
df.orderBy()
```

**Analogi:**
Kamu kasih instruksi ke arsitek:
- "Tambah kamar"
- "Pindah pintu"
- "Ubah warna"

Arsitek cuma update denah, belum bangun apa-apa.

---

### Actions = "Bangun Bangunannya Sekarang!" (Eager)

**Karakteristik:**
- **Eager**: Trigger eksekusi SELURUH plan
- Return hasil ke driver atau tulis ke storage
- **EXPENSIVE**: Ini saat Spark benar-benar kerja

**Contoh:**
```python
df.count()         # ← Hitung total rows → return int
df.show()          # ← Tampilkan 20 rows → print ke console
df.collect()       # ← Ambil SEMUA data ke driver (BAHAYA!)
df.write.parquet() # ← Tulis ke disk
df.take(10)        # ← Ambil 10 rows ke driver
df.first()         # ← Ambil 1 row
```

**Analogi:**
Kamu bilang: "Oke, bangun bangunannya sekarang!"
Arsitek panggil kontraktor (executors), baru mulai kerja fisik.

---

### Kenapa Perbedaan Ini Penting?

**Scenario 1: Multiple Transformations**
```python
df1 = df.filter(df.age > 30)           # Lazy, instan
df2 = df1.select("name", "city")       # Lazy, instan
df3 = df2.withColumn("country", "ID")  # Lazy, instan
df4 = df3.filter(df3.city == "Jakarta")# Lazy, instan

# Total waktu sejauh ini: ~0 detik (cuma update logical plan)

df4.count()  # ← ACTION! Baru eksekusi SEMUA operasi di atas
```

**Spark optimize:**
```
Original plan: read → filter1 → select → withColumn → filter2 → count
Optimized plan: read (hanya kolom yang dibutuhkan) → filter1 AND filter2 (combined) → count
```

**Scenario 2: Multiple Actions (INEFFICIENT!)**
```python
df_filtered = df.filter(df.age > 30)  # Lazy

# ❌ SALAH: 3 actions = 3x eksekusi dari awal!
count = df_filtered.count()      # Action 1: scan data
first_row = df_filtered.first()  # Action 2: scan data LAGI
df_filtered.show()               # Action 3: scan data LAGI
```

**✅ BENAR: Pakai cache kalau mau re-use**
```python
df_filtered = df.filter(df.age > 30).cache()  # Masih lazy

count = df_filtered.count()      # Action 1: eksekusi + simpan di memory
first_row = df_filtered.first()  # Action 2: baca dari cache (cepat!)
df_filtered.show()               # Action 3: baca dari cache
```

---

## 6. DAG (Directed Acyclic Graph) — Peta Eksekusi Spark

### Apa Itu DAG?

**DAG = Pohon operasi tanpa loop**

```
read → filter → select → join → groupBy → write
  ↓      ↓       ↓       ↓       ↓        ↓
Stage 1       Stage 2         Stage 3
```

**Konsep Penting:**

**Stage** = Kumpulan tasks yang bisa dijalankan paralel tanpa shuffle
- 1 stage = operasi narrow (tidak perlu exchange data antar partitions)
- Stage boundary = shuffle operation (groupBy, join, repartition)

**Shuffle** = Redistribusi data antar executors
- **MAHAL**: butuh network transfer, disk I/O, serialization
- Contoh: `groupBy("city")` → semua data dengan city yang sama harus ke executor yang sama

### Visualisasi DAG:

```python
df = spark.read.parquet("users.parquet")
df_filtered = df.filter(df.age > 30)
df_joined = df_filtered.join(cities_df, "city_id")  # ← SHUFFLE!
result = df_joined.groupBy("city").count()          # ← SHUFFLE!

result.write.parquet("output/")  # ← ACTION
```

**DAG yang terbentuk:**
```
Stage 1 (Narrow):
  read users.parquet → filter age > 30
  read cities.parquet
         ↓
    [SHUFFLE] ← join (exchange)
         ↓
Stage 2 (Narrow):
  join operation
         ↓
    [SHUFFLE] ← groupBy (exchange)
         ↓
Stage 3 (Narrow):
  count per group → write
```

**Key Insight:**
- Spark otomatis pecah jadi stages berdasarkan shuffle boundaries
- Setiap stage punya banyak tasks (1 task per partition)
- Tasks dalam 1 stage jalan paralel
- Antar stage harus sequential (stage 2 tunggu stage 1 selesai)

---

## 7. Catalyst Optimizer — "Otak" di Balik Layar

### Apa yang Catalyst Lakukan?

**Analogi: GPS Navigation**

Kamu bilang: "Aku mau ke mall"
GPS tidak langsung kasih rute, tapi:
1. Analisa semua kemungkinan jalan
2. Cek traffic, jarak, waktu
3. Pilih rute OPTIMAL
4. Baru kasih instruksi turn-by-turn

**Catalyst:**
1. Terima logical plan dari kode kamu
2. Apply optimization rules
3. Hasilkan physical plan yang efisien

### Optimization Contoh:

#### 1. Predicate Pushdown
```python
# Kode kamu:
df = spark.read.parquet("big_file.parquet")  # 100 columns
df_filtered = df.filter(df.age > 30)
df_selected = df_filtered.select("name", "city")

# Catalyst optimize:
# ✅ Baca hanya kolom "name", "city", "age" (column pruning)
# ✅ Filter age > 30 SAAT BACA parquet (predicate pushdown)
# Hasil: Baca 3 columns instead of 100 → 30x lebih cepat!
```

#### 2. Filter Reordering
```python
# Kode kamu:
df.filter(df.status == "active")  # Filter 50% data
  .filter(df.age > 30)            # Filter 20% data

# Catalyst optimize:
# Jalankan filter yang lebih selektif DULU (age > 30)
# Baru filter status
# → Proses lebih sedikit data di step berikutnya
```

#### 3. Join Optimization
```python
# Kode kamu:
big_df.join(small_df, "id")  # big_df = 1 TB, small_df = 10 MB

# Catalyst optimize:
# Deteksi small_df kecil → gunakan BROADCAST JOIN
# Instead of shuffle big_df, broadcast small_df ke semua executors
# → Skip shuffle yang mahal!
```

---

## 8. `.explain()` — X-Ray Spark Code

**SELALU gunakan `.explain()` untuk understand execution plan!**

```python
df = spark.read.parquet("users.parquet")
df_filtered = df.filter(df.age > 30).select("name", "city")

df_filtered.explain(True)  # True = tampilkan semua fase optimization
```

**Output:**
```
== Parsed Logical Plan ==     ← Logical plan awal (sebelum optimize)
== Analyzed Logical Plan ==   ← Setelah validasi schema
== Optimized Logical Plan ==  ← Setelah Catalyst optimize
== Physical Plan ==           ← Execution plan konkret
```

**Yang perlu kamu cek:**
1. Apakah ada **predicate pushdown**? (PushedFilters)
2. Apakah column pruning terjadi? (ReadSchema hanya kolom yang dibutuhkan)
3. Berapa banyak **Exchange** (shuffle)? → Semakin sedikit semakin baik
4. Join strategy: **BroadcastHashJoin** (bagus) vs **SortMergeJoin** (butuh shuffle)

---

## 9. Kenapa Chaining Transformations Itu Murah?

**Analogi: Resep Masak**

```python
df.filter(...)      # Tulis: "Cuci sayuran"
  .select(...)      # Tulis: "Potong dadu"
  .withColumn(...)  # Tulis: "Tambah bumbu"
  .groupBy(...)     # Tulis: "Masak 10 menit"
```

**Sebelum action:**
- Kamu cuma tulis resep di kertas (logical plan)
- Tidak ada sayuran yang dipotong, tidak ada api yang nyala
- **Cost: 0 detik, 0 memory**

**Saat action (`.count()`):**
- Spark baca SEMUA instruksi sekaligus
- Optimize: "Oh, bisa potong sambil cuci" (combine operations)
- Baru eksekusi efisien

**Kebalikannya (Pandas):**
```python
df = df[df.age > 30]      # Eksekusi → copy data
df = df[["name", "city"]] # Eksekusi → copy data LAGI
df["country"] = "ID"      # Eksekusi → copy data LAGI
```
Setiap step = intermediate result disimpan → memory penuh!

---

## 10. Mental Checklist Sebelum Tulis Spark Code

### ✅ Pre-Code Checklist:

1. **Apakah dataku besar?**
   - < 10 GB → pertimbangkan Pandas
   - \> 50 GB → Spark make sense

2. **Apakah operasiku bisa diparalelkan?**
   - Filter, map, join, groupBy → YES
   - Sequential processing, complex stateful → HARD

3. **Berapa kali aku pakai DataFrame yang sama?**
   - Sekali → langsung chain transformations
   - Berkali-kali → pakai `.cache()` atau `.persist()`

4. **Apakah aku butuh semua data di driver?**
   - Tidak → gunakan `.write()` atau distributed actions
   - Ya → **HATI-HATI** dengan `.collect()` (bisa OOM!)

5. **Apakah aku bisa reduce data sebelum shuffle?**
   - Filter dulu sebelum join
   - Aggregate dulu sebelum collect

---

## 11. Common Beginner Mistakes

### ❌ Mistake 1: Collect Too Early
```python
# BAHAYA!
df = spark.read.parquet("1TB_data.parquet")
data = df.collect()  # ← Coba bawa 1 TB ke driver → CRASH!

# ✅ BENAR:
df.write.parquet("output/")  # Tulis distributed, bukan ke driver
```

---

### ❌ Mistake 2: Multiple Actions Without Cache
```python
# INEFFICIENT!
df_filtered = df.filter(df.age > 30)
print(df_filtered.count())    # Scan dari awal
print(df_filtered.first())    # Scan dari awal LAGI!
df_filtered.show()            # Scan dari awal LAGI!

# ✅ BENAR:
df_filtered = df.filter(df.age > 30).cache()
df_filtered.count()  # Scan + cache
df_filtered.first()  # Baca dari cache
df_filtered.show()   # Baca dari cache
```

---

### ❌ Mistake 3: Unnecessary Shuffles
```python
# LAMBAT!
df.repartition(200)           # Shuffle!
  .filter(df.age > 30)        
  .repartition(100)           # Shuffle LAGI!

# ✅ BENAR:
df.filter(df.age > 30)        # Filter dulu (reduce data)
  .repartition(100)           # Baru shuffle sekali
```

---

### ❌ Mistake 4: Iterating Over Rows
```python
# ❌ SANGAT LAMBAT! (Serial processing di driver)
for row in df.collect():  # Bawa semua ke driver
    process(row)

# ✅ BENAR: Use UDF atau built-in functions (distributed)
from pyspark.sql.functions import udf
process_udf = udf(process)
df.withColumn("result", process_udf(df.column))
```

---

### ❌ Mistake 5: Ignore `.explain()`
```python
# Kamu tidak tahu apakah kode kamu efisien!
df.groupBy(...).count().write.parquet(...)

# ✅ BENAR:
result = df.groupBy(...).count()
result.explain(True)  # ← Cek optimization!
result.write.parquet(...)
```

---

## 12. Summary: How Spark Executes Code

```
Kode kamu (transformations)
    ↓
Logical Plan (tree of operations)
    ↓
Catalyst Optimizer (pushdown, pruning, reordering)
    ↓
Optimized Logical Plan
    ↓
Physical Plan (stages, tasks, partitions)
    ↓
Action triggered
    ↓
Executors run tasks in parallel
    ↓
Results aggregated/written
```

**Key Takeaways:**
1. **Transformations = cheap** (cuma update plan)
2. **Actions = expensive** (trigger eksekusi)
3. **Catalyst optimize behind the scenes** (kamu tidak perlu manual tuning biasanya)
4. **Always `.explain()`** untuk verify optimization
5. **Cache kalau re-use DataFrame** berkali-kali

---

## 13. Reflection Questions

Jawab pertanyaan ini untuk test understanding:

1. **Kenapa kode ini cepat?**
   ```python
   df.filter(df.age > 30).filter(df.city == "Jakarta").select("name")
   ```

2. **Kenapa kode ini lambat?**
   ```python
   df_filtered = df.filter(df.age > 30)
   df_filtered.count()
   df_filtered.show()
   df_filtered.write.parquet("output1/")
   df_filtered.count()
   ```

3. **Apa beda output `.explain()` antara:**
   ```python
   # A
   df.select("name").filter(df.age > 30)
   
   # B
   df.filter(df.age > 30).select("name")
   ```

4. **Kapan kamu HARUS pakai `.cache()`?**

---

## 14. Checkpoint: Apa yang Sudah Kamu Pelajari?

### ✅ Concepts yang Sudah Dikuasai:

**1. RDD (Resilient Distributed Dataset):**
- Foundation of Spark (low-level API)
- **3 properties:** Immutable, Distributed, Fault-tolerant
- **Lineage graph** → auto-recovery dari failures
- **Use case:** Unstructured data, custom complex logic

**2. RDD vs DataFrame:**
- RDD = low-level, flexible, tapi lebih lambat
- DataFrame = high-level, optimized, lebih mudah
- **Default: pakai DataFrame** (better performance)
- RDD hanya untuk edge cases

**3. Schema:**
- **Metadata** struktur data (column names, types, nullable)
- **Inference** = auto-detect (mudah, lambat, bisa salah)
- **Explicit** = manual define (cepat, predictable, type-safe)
- **Production: always explicit schema!**
- **StructType** untuk structured, DDL string untuk shortcut

**4. DataFrame Architecture:**
- DataFrame = blueprint, bukan data konkret
- Pandas DataFrame vs Spark DataFrame (concrete vs plan)

**5. Execution Model:**
- **Logical Plan** → Optimized Plan → Physical Plan
- **Catalyst Optimizer** → predicate pushdown, column pruning
- **Transformations** = lazy (cheap, chainable)
- **Actions** = eager (expensive, trigger execution)

**6. DAG (Directed Acyclic Graph):**
- Execution plan sebagai graph
- **Stages** = kumpulan tasks tanpa shuffle
- **Shuffle** = stage boundary (expensive!)

**7. Best Practices:**
- Always `.explain()` untuk verify optimization
- `.cache()` untuk DataFrame yang di-reuse
- Avoid `.collect()` di data besar
- Chain transformations (cheap!)

---

### 🎯 Key Mental Models:

1. **DataFrame = Blueprint** (bukan data konkret)
2. **Lazy = Smart** (Spark tunggu untuk optimize)
3. **Schema = Type Safety** (faster + safer)
4. **Actions trigger execution** (everything before is just planning)
5. **Catalyst optimizes automatically** (tapi verify dengan `.explain()`)

---

### 📚 Next: Performance Tuning

**Coming next (Day 3-4):**
- **Partitioning** deep dive (how data distributed)
- **Shuffle** mechanics (what makes Spark slow)
- **Skew handling** (unbalanced partitions)
- **Join strategies** (broadcast vs sort-merge)
- **Memory management** (cache vs persist)
- **Practical optimization tips**

---
