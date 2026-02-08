# Transformations & Actions — Lazy vs Eager Execution

> **Learning Objective:** Master the distinction between lazy transformations and eager actions in Spark execution model.

## The Core Distinction

### Transformations (Lazy)
- Return new DataFrame/RDD
- Don't trigger execution
- Chainable at no cost
- Build execution plan

### Actions (Eager)
- Trigger execution of entire plan
- Return results or write to storage
- Expensive operations
- When Spark actually works

---

## Transformations

```python
# All lazy - instant return
df.filter(df.age > 30)
df.select("name", "city")
df.groupBy("country")  # ← Note: also lazy!
df.orderBy("age")
df.join(other_df, "id")
df.withColumn("new_col", ...)
df.distinct()
```

**Key insight:** Can chain hundreds of transformations with zero execution time!

---

## Actions

```python
# All eager - trigger computation
df.show()           # Display rows
df.count()          # Count elements
df.collect()        # Return all to driver (⚠️ DANGER!)
df.first()          # Get first row
df.take(10)         # Get first 10 rows
df.write.parquet() # Write to storage
```

---

## Why This Matters

### Scenario: Multiple Transformations
```python
df1 = df.filter(df.age > 30)           # 0 sec
df2 = df1.select("name", "city")       # 0 sec  
df3 = df2.withColumn("country", "ID")  # 0 sec
df4 = df3.filter(df3.city == "Jakarta") # 0 sec

# Total so far: ~0 seconds!

df4.count()  # ← ACTION! Now executes everything
```

**Spark optimizes:**
- Combines filters
- Prunes columns early
- Executes efficiently

---

## Common Mistake: Multiple Actions

```python
# ❌ INEFFICIENT!
df_filtered = df.filter(df.age > 30)
count = df_filtered.count()    # Scan 1
first = df_filtered.first()    # Scan 2
df_filtered.show()             # Scan 3
```

**Fix with cache:**
```python
# ✅ EFFICIENT!
df_filtered = df.filter(df.age > 30).cache()
count = df_filtered.count()    # Scan + cache
first = df_filtered.first()    # From cache
df_filtered.show()             # From cache
```

---

## DAG (Directed Acyclic Graph)

Spark builds execution graph:

```
read → filter → select → groupBy → write
 ↓      ↓        ↓         ↓        ↓
Stage 1          Stage 2         Stage 3
(no shuffle)   (shuffle!)     (no shuffle)
```

**Stages** = groups of tasks without shuffles
**Shuffle** = expensive data redistribution

---

## Summary

- **Transformations:** Lazy, build plan, fast
- **Actions:** Eager, execute plan, slow
- **Cache:** Reuse computed DataFrames
- **DAG:** Execution plan with stages

**Golden rule:** Chain transformations freely, minimize actions!

---

**Previous:** [← Schema Management](03-schema-management.md) | **Next:** [Catalyst Optimizer →](05-catalyst-optimizer.md)
