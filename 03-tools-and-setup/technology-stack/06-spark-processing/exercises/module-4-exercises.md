# Module 4: Spark SQL — Hands-On

Practice SQL queries, windows, UDFs, and complex types.

## Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.getOrCreate()
```

## Exercise 1: SQL Basics

1. Create a DataFrame `people` with columns: `id`, `name`, `age`, `city`.
2. Create a temp view `people`.
3. Write SQL to select adults (age >= 21) ordered by age desc.

## Exercise 2: Aggregations and Joins

1. Create `orders` and `customers` DataFrames.
2. Join and compute total amount per customer.
3. Add a `HAVING` filter to keep totals >= 100.

## Exercise 3: Window Functions

1. Create an events table with `user_id`, `event_time`, `amount`.
2. Add `row_number` over `user_id` ordered by `event_time`.
3. Add `running_total` per user.

## Exercise 4: UDF vs Built-in

1. Create a `normalize_city` UDF.
2. Apply it to a column with messy city strings.
3. Replace it with a built-in alternative if possible.

## Exercise 5: Complex Types

1. Create a nested struct column `profile` with name + age.
2. Explode an array of tags.
3. Parse a JSON column using `from_json`.

---

**Target time:** 45-60 minutes
**Next:** [Module 5 Exercises →](module-5-exercises.md)
