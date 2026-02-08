# DataFrame Basics — High-Level Structured API

> **Learning Objective:** Understand DataFrame as Spark's primary high-level API for structured data processing.

## DataFrame: Blueprint vs Building

**Pandas DataFrame:**
```python
df = pd.read_csv("data.csv")  # ← Data loaded immediately!
type(df)  # Actual data in memory
```

**Spark DataFrame:**
```python
df = spark.read.csv("data.csv")  # ← Just a plan!
type(df)  # pyspark.sql.dataframe.DataFrame
# No data loaded yet - just blueprint
```

---

## Mental Model: Blueprint Analogy

**Pandas = Completed Building**
- Can inspect immediately
- Modification requires rebuild

**Spark DataFrame = Architectural Blueprint**
-Not physical data
- Can modify cheaply
- Built only when action triggered

---

## DataFrame vs RDD vs Pandas

| Feature | RDD | DataFrame | Pandas |
|---------|-----|-----------|--------|
| **Structure** | Unstructured | Structured (schema) | Structured |
| **Optimization** | None | Catalyst optimizer | None |
| **Execution** | Lazy | Lazy | Eager |
| **Distribution** | Yes | Yes | No |
| **Performance** | Baseline | 2-10x faster | N/A (single machine) |
| **Use Case** | Custom logic | SQL-like ops | Small data |

---

## Why DataFrame > RDD?

### 1. **Catalyst Optimizer**
```python
# Your code:
df.filter(df.age > 30).select("name", "city")

# Spark optimizes to:
# - Read only needed columns (column pruning)
# - Push filter to data source (predicate pushdown)
```

### 2. **Tungsten Execution Engine**
- Binary in-memory format
- Code generation (JIT)
- Faster than RDD's JVM objects

### 3. **Schema Awareness**
- Type safety
- Better error messages
- Query optimization opportunities

---

## Creating DataFrames

### From Files
```python
# CSV
df = spark.read.csv("data.csv", header=True, inferSchema=True)

# JSON
df = spark.read.json("data.json")

# Parquet
df = spark.read.parquet("data.parquet")
```

### From RDD
```python
from pyspark.sql import Row
rdd = sc.parallelize([("Alice", 30), ("Bob", 25)])
df = rdd.map(lambda x: Row(name=x[0], age=x[1])).toDF()
```

### Programmatically
```python
data = [("Alice", 30), ("Bob", 25)]
df = spark.createDataFrame(data, ["name", "age"])
```

---

## Basic Operations

### Viewing Data
```python
df.show()          # Display 20 rows
df.show(5)         # Display 5 rows
df.printSchema()   # Show structure
df.columns         # List columns
df.count()         # Count rows
```

### Selecting
```python
df.select("name", "age")
df.select(df.name, df.age)
df.select(col("name"), col("age"))
```

### Filtering
```python
df.filter(df.age > 30)
df.filter("age > 30")
df.where(df.age > 30)
```

---

## Summary

- **DataFrame:** High-level structured API
- **Lazy execution:** Plan built, executed on action
- **Optimized:** Catalyst + Tungsten engines
- **Default choice:** Use DataFrame over RDD
- **Schema-aware:** Type safety and optimization

---

**Previous:** [← RDD Fundamentals](01-rdd-fundamentals.md) | **Next:** [Schema Management →](03-schema-management.md)
