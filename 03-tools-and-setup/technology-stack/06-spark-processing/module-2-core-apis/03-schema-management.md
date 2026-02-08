# Schema Management — Data Structure Definition

> **Learning Objective:** Master schema definition, inference, and best practices for production DataFrames.

## What is Schema?

**Schema = DataFrame metadata:**
- Column names
- Data types
- Nullable constraints

Think of it as a "form" with predefined fields.

---

## Viewing Schema

```python
df =spark.read.json("users.json")

# Method 1: Pretty print
df.printSchema()
# root
#  |-- name: string (nullable = true)
#  |-- age: integer (nullable = true)
#  |-- email: string (nullable = true)

# Method 2: Get schema object
schema = df.schema

# Method 3: DDL string
df.schema.simpleString()
# struct<name:string,age:int,email:string>
```

---

## Schema Inference vs Explicit

### Inference (Automatic)

```python
df = spark.read.csv("data.csv", header=True, inferSchema=True)
```

**Pros:**
- ✅ Easy, no manual work
- ✅ Fast for prototyping

**Cons:**
- ❌ Extra data scan (slower)
- ❌ Can misdetect types
- ❌ Not deterministic

---

### Explicit Schema (Manual)

```python
from pyspark.sql.types import *

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("email", StringType(), True)
])

df = spark.read.schema(schema).json("users.json")
```

**Pros:**
- ✅ Faster (skip inference scan)
- ✅ Predictable
- ✅ Type safety

**Cons:**
- ❌ Verbose code

---

### DDL String Shortcut

```python
# Simpler syntax
ddl = "name STRING, age INT, email STRING"
df = spark.read.schema(ddl).json("users.json")
```

---

## Nested Schema

```python
# Nested JSON
{
  "name": "Alice",
  "address": {
    "city": "Jakarta",
    "country": "Indonesia"
  },
  "phones": ["08123", "08765"]
}
```

**Schema:**
```python
nested_schema = StructType([
    StructField("name", StringType(), True),
    StructField("address", StructType([
        StructField("city", StringType(), True),
        StructField("country", StringType(), True)
    ]), True),
    StructField("phones", ArrayType(StringType()), True)
])
```

**Access:**
```python
df.select("address.city")
df.select(col("phones")[0].alias("primary"))
```

---

## Production Best Practices

### ✅ DO:

1. **Always explicit schema in production**
```python
df = spark.read.schema(KNOWN_SCHEMA).parquet("s3://data/")
```

2. **Centralize schema definitions**
```python
# schemas.py
USER_SCHEMA = StructType([...])

# main.py  
from schemas import USER_SCHEMA
df = spark.read.schema(USER_SCHEMA).json("users.json")
```

3. **Version schemas**
```python
USER_SCHEMA_V1 = StructType([...])
USER_SCHEMA_V2 = StructType([...])  # Added fields
```

---

### ❌ DON'T:

1. **Inference on large production data**
```python
# ❌ Scans 1 TB just for schema!
df = spark.read.csv("s3://huge-data/", inferSchema=True)
```

2. **Assume schema never changes**
```python
# ❌ Brittle
df.select("col1", "col2", "col3")

# ✅ Defensive
cols = [c for c in ["col1", "col2"] if c in df.columns]
df.select(cols)
```

---

## Summary

- **Schema:** Structure definition (columns + types)
- **Inference:** Auto-detect (dev/test only)
- **Explicit:** Manual define (always in production)
- **Nested:** Struct, Array, Map supported
- **Best practice:** Centralize, version, explicit

---

**Previous:** [← DataFrame Basics](02-dataframe-basics.md) | **Next:** [Transformations & Actions →](04-transformations-actions.md)
