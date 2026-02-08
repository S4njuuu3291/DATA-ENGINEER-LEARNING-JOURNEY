# Module 3: Performance — Hands-On

Focus on partitioning, shuffles, joins, and caching.

## Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.getOrCreate()
```

## Exercise 1: Partitioning

1. Create a DataFrame with 1 million rows (range).
2. Check number of partitions.
3. Repartition to 64 and check again.
4. Coalesce to 8 and check again.

## Exercise 2: Shuffle Awareness

1. Perform a `groupBy` on a random key.
[text](../notebooks)2. Call `explain()` and observe shuffle stages.
3. Compare with a `select` + `filter` (no shuffle).

## Exercise 3: Join Strategy

1. Create a small dimension DataFrame (e.g., 100 rows).
2. Join a large DataFrame with and without `broadcast()`.
3. Use `explain(True)` to compare plans.

## Exercise 4: Cache vs No Cache

1. Create a DataFrame and run two actions without caching.
2. Cache the DataFrame and run the same actions.
3. Compare runtime (use `time` or notebook timing).

## Exercise 5: Skew Simulation

1. Create a DataFrame where 90% of rows have the same key.
2. Group by the key and measure time.
3. Apply key salting and compare.

---

**Target time:** 60-90 minutes
**Next:** [Module 4 Exercises →](module-4-exercises.md)
