# Caching & Persistence — Memory Management

> **Learning Objective:** Master DataFrame caching for performance optimization.

## Why Cache?

**Problem:** DataFrame used multiple times = recomputed each time

```python
df_filtered = df.filter(df.age > 30)

df_filtered.count()  # Computation 1
df_filtered.show()   # Computation 2 (WASTEFUL!)
```

**Solution:** Cache after first computation

```python
df_filtered = df.filter(df.age > 30).cache()

df_filtered.count()  # Compute + cache
df_filtered.show()   # From cache (fast!)
```

---

## Storage Levels

```python
from pyspark import StorageLevel

# Memory only (fastest, but can fail if OOM)
df.persist(StorageLevel.MEMORY_ONLY)

# Memory + disk spillover (safer)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Serialized (saves space)
df.persist(StorageLevel.MEMORY_ONLY_SER)

# cache() = shortcut for MEMORY_AND_DISK
df.cache()  # == df.persist(StorageLevel.MEMORY_AND_DISK)
```

---

## When to Cache?

### ✅ Cache When:
- DataFrame used 2+ times
- Expensive computation
- Iterative algorithms (ML)

```python
# Good use case
df_expensive = df.join(...).groupBy(...).agg(...)
df_expensive.cache()

result1 = df_expensive.count()
result2 = df_expensive.filter(...).show()
```

### ❌ Don't Cache When:
- Single use
- Large DataFrame (> available memory)
- Sequential one-pass operations

---

## Unpersist

Free memory when done:

```python
df.cache()
# ... use df ...
df.unpersist()  # Free memory
```

---

## Checkpointing (Disk Persistence)

For long lineages, break dependency chain:

```python
spark.sparkContext.setCheckpointDir("hdfs://checkpoints")

df.checkpoint()  # Write to reliable storage
# Lineage truncated, faster recovery
```

---

## Summary

- **cache():** Store in memory for reuse
- **persist():** Fine-grained storage level control
- **Use when:** DataFrame accessed 2+ times
- **unpersist():** Free memory when done
- **checkpoint():** Break long lineages

---

**Previous:** [← Skew Handling](04-skew-handling.md) | **Module Complete!** [Module 3 Overview →](README.md)
