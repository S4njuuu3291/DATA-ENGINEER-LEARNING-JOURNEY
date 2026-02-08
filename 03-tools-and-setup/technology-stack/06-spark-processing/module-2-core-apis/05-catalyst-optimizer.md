# Catalyst Optimizer — Spark's Query Optimization Engine

> **Learning Objective:** Understand how Catalyst automatically optimizes Spark queries for better performance.

## What is Catalyst?

Spark's **query optimizer** that automatically improves execution plans.

Like a GPS that finds the fastest route automatically!

---

## Optimization Phases

```
Your Code
    ↓
Logical Plan (unoptimized)
    ↓
Catalyst Optimizer
    ↓
Optimized Logical Plan
    ↓
Physical Plan
    ↓
Execution
```

---

## Key Optimizations

### 1. Predicate Pushdown

**Your code:**
```python
df = spark.read.parquet("big_file.parquet")  # 100 columns
df_filtered = df.filter(df.age > 30).select("name", "city")
```

**Catalyst optimizes:**
```python
# Read only needed columns
# Filter while reading
# Result: 30x faster!
```

---

### 2. Column Pruning

```python
# Your code reads all columns
df.filter(...).select("name", "age")

# Catalyst reads only 2 columns
# Ignores other 98 columns
# Massive I/O savings!
```

---

### 3. Filter Reordering

```python
df.filter(df.status == "active")  # Filters 50%
  .filter(df.age > 30)             # Filters 20%

# Catalyst runs more selective filter first!
# Processes less data in subsequent steps
```

---

### 4. Join Optimization

```python
big_df.join(small_df, "id")  # 1 TB join 10 MB

# Catalyst detects small table
# Uses BROADCAST join automatically
# No shuffle needed!
```

---

## Using `.explain()`

Check Catalyst's work:

```python
df.filter(df.age > 30).select("name").explain(True)
```

**output:**
```
== Parsed Logical Plan ==     ← Your code
== Analyzed Logical Plan ==   ← After schema validation
== Optimized Logical Plan ==  ← After Catalyst!
== Physical Plan ==           ← Final execution plan
```

---

## What to Look For

```python
df.explain(True)
```

**Good signs:**
- `PushedFilters: [age > 30]` ← Predicate pushdown working
- `ReadSchema: struct<name,age>` ← Only needed columns
- `BroadcastHashJoin` ← Efficient join


**Bad signs:**
- Multiple `Exchange` (shuffles)
- Missing `PushedFilters`
- `SortMergeJoin` when broadcast possible

---

## Summary

- **Catalyst:** Automatic query optimizer
- **Optimizations:** Pushdown, pruning, reordering, join strategy
- **`.explain()`:** View optimization results
- **Best part:** Works automatically!

**Key takeaway:** Write clean code, let Catalyst optimize!

---

**Previous:** [← Transformations & Actions](04-transformations-actions.md) | **Module Complete!** [Module 2 Overview →](README.md)
