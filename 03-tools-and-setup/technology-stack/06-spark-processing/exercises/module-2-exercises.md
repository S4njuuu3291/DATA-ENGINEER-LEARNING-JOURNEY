# Module 2: Core APIs — Hands-On

Practice the DataFrame and RDD APIs with small, focused tasks.

## Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.getOrCreate()
```

## Exercise 1: Build a DataFrame

1. Create a DataFrame from a list of dicts with fields: `id`, `name`, `age`, `city`.
2. Print the schema.
3. Select only `name` and `age`.

## Exercise 2: Filtering and Columns

1. Filter rows where `age` >= 21.
2. Add a column `age_bucket` = (age // 10) * 10.
3. Drop the `city` column.

## Exercise 3: Aggregations

1. Group by `city`, compute count and avg age.
2. Sort by count descending.

## Exercise 4: RDD Basics

1. Convert DataFrame to RDD and get number of partitions.
2. Map each row to `(city, 1)` and reduce by key.
3. Convert back to DataFrame with columns `city`, `count`.

## Exercise 5: Schema Control

1. Create a StructType schema for the data.
2. Recreate the DataFrame with the explicit schema.
3. Verify that types are correct (e.g., `age` is IntegerType).

---

**Target time:** 45-60 minutes
**Next:** [Module 3 Exercises →](module-3-exercises.md)
