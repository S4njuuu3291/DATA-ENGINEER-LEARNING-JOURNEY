# When to Use Spark — Decision Framework & Lazy Evaluation

> **Learning Objective:** Understand when Spark is the right tool, when it's overkill, and how lazy evaluation enables optimization.

---

## Lazy Evaluation: Spark's Smart Execution

### The Concept

**Pandas (Eager):**
```python
df = pd.read_csv("big.csv")  # ← Executes immediately!
df_filtered = df[df.age > 30]  # ← Executes immediately!
```

**Spark (Lazy):**
```python
df = spark.read.csv("big.csv")  # ← Just creates plan!
df_filtered = df.filter(df.age > 30)  # ← Still just planning!

# Only executes when action is called:
df_filtered.count()  # ← NOW Spark actually works!
```

---

### Why Delay Execution?

**Analogy: Restaurant Chef**

**Pandas (Eager Chef):**
- Customer: "Make salad"
- Chef: *cooks immediately* (5 min)
- Customer: "Add tomatoes"
- Chef: "Oops, already done... remake!" (5 min more)
- **Total: 10 minutes**

**Spark (Lazy Chef):**
- Customer: "Make salad"
- Chef: *writes on notepad*
- Customer: "Add tomatoes"
- Chef: *updates notepad*
- Customer: "Serve now!"
- Chef: *reads notes*, "I can make salad with tomatoes directly!" (3 min)
- **Total: 3 minutes**

---

### Benefits of Lazy Evaluation

#### 1. **Optimization Opportunities**
```python
df.filter(df.age > 30).filter(df.city == "Jakarta").select("name")
```

Spark optimizes:
```
Original plan: read → filter → filter → select
Optimized plan: read (only 'name', 'age', 'city' columns) → filter (age AND city) → select
```

#### 2. **Avoid Unnecessary Work**
```python
df.filter(df.age > 30).limit(10)
```

Spark: "Only need 10 rows? I'll stop after finding 10, not process entire dataset!"

#### 3. **Efficient Pipelining**
```python
df.filter(...).select(...).groupBy(...).agg(...)
```

All transformations chain efficiently without intermediate storage.

---

## Decision Framework: When to Use Spark?

### ✅ Use Spark When:

#### 1. **Data > Single Machine RAM**
```
Data size: 100 GB+
RAM available: 16 GB
→ Spark! Distribute across cluster
```

#### 2. **Need Horizontal Scaling**
```
Current: 1 machine, 16 GB RAM
Add: 9 more machines → 160 GB total
→ Spark handles distribution automatically
```

#### 3. **Processing Can Be Parallelized**
```
✅ Good for Spark:
- Filtering large datasets
- Aggregations (groupBy, sum, count)
- Joins across tables
- Map/transform operations

❌ Bad for Spark:
- Sequential operations
- Complex stateful processing
- Single-row operations
```

#### 4. **Data in Distributed Storage**
```
Data already in:
- HDFS (Hadoop)
- S3 (AWS)
- GCS (Google Cloud)
- Azure Blob Storage
→ Spark reads natively
```

---

### ❌ Spark is OVERKILL When:

#### 1. **Data Fits in RAM**
```
Data size: 2 GB
RAM available: 16 GB
→ Use Pandas! Faster and simpler
```

**Why?**
- No cluster coordination overhead
- Simpler code
- Faster for small data

#### 2. **Quick Prototyping**
```
Scenario: Exploratory data analysis on laptop
→ Use Pandas/Jupyter
```

**Reason:**
- Instant feedback
- No cluster setup needed
- Full Python ecosystem

#### 3. **Sequential Operations**
```
Operations that can't parallelize well:
- Ordered window functions
- Complex state management
- Row-by-row dependencies
→ Consider alternatives
```

#### 4. **Small Result, Large Intermediate**
```
Query: Count distinct values in 1 TB file
Result: 100 unique values

Better approach:
1. Aggregate in database first
2. Pull summary to Pandas
→ No need for Spark cluster
```

---

### 🤔 Gray Area (Depends on Context):

#### Data: 20-50 GB

**Use Pandas if:**
- Have 64+ GB RAM machine
- Single operation, not repeated
- Quick one-off analysis

**Use Spark if:**
- Plan to scale later
- Repeated analysis
- Part of larger pipeline
- Limited RAM available

---

## Common Misconceptions

### ❌ Myth 1: "Spark is Pandas but Faster"

**Reality:**
- Spark has coordination overhead
- For small data, Pandas is actually faster
- Spark is for data that doesn't fit on one machine

### ❌ Myth 2: "Lazy Evaluation is Slow"

**Reality:**
- Lazy = Spark can optimize before executing
- Eager (Pandas) = executes immediately, no optimization
- Lazy enables smart execution plans

### ❌ Myth 3: "Everything Parallelizes Automatically"

**Reality:**
- `.collect()` brings all data to driver (bottleneck!)
- Some operations require shuffles (expensive)
- Need to design partition-friendly pipelines

---

## Real-World Decision Examples

### Case A: E-commerce Analytics
```
Data: 5 million transactions (2 GB CSV)
Task: Daily sales report
Environment: Laptop with 16 GB RAM

Decision: Use Pandas ✅
Reason: Data fits in memory, simpler for reporting
```

### Case B: Clickstream Analysis
```
Data: 500 million events (200 GB on S3)
Task: User behavior analysis, join with user data
Environment: AWS with EMR cluster

Decision: Use Spark ✅
Reason: Large data, distributed storage, complex joins
```

### Case C: Real-Time Sensor Processing
```
Data: Streaming from Kafka (millions events/sec)
Task: Real-time aggregation, anomaly detection
Environment: GCP with Dataproc

Decision: Use Spark Streaming ✅
Reason: Real-time processing at scale
```

### Case D: Small Excel Report
```
Data: 100 MB Excel file
Task: Pivot table, formatting
Environment: Laptop

Decision: Use Excel/Pandas ✅
Reason: Overkill to use Spark for this
```

---

## Summary

### Lazy Evaluation:
- ✅ Enables optimization
- ✅ Avoids unnecessary work
- ✅ Efficient pipelining
- ❌ Not "slow" — actually enables speed!

### When to Use Spark:
- ✅ Data > RAM
- ✅ Horizontal scaling needed
- ✅ Parallelizable operations
- ✅ Distributed storage

### When NOT to Use Spark:
- ❌ Data fits in memory
- ❌ Quick prototyping
- ❌ Sequential operations
- ❌ Simple one-off queries

**Golden Rule:** Use Spark when single machine can't handle the load!

---

**Previous:** [← Architecture](04-architecture.md) | **Module Complete!** Return to [Module 1 Overview →](README.md)
