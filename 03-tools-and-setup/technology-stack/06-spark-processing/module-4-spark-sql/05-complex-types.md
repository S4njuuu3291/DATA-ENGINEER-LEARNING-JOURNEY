# 05 - Complex Types and JSON

Spark SQL can handle arrays, maps, structs, and JSON strings with built-in functions.

## Structs and arrays

```python
spark.sql("""
SELECT
  user_id,
  struct(name, age) AS profile,
  array(tags) AS tag_list
FROM people
""")
```

## Access nested fields

```python
spark.sql("""
SELECT
  profile.name AS name,
  profile.age AS age
FROM people_struct
""")
```

## JSON parsing

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])

spark.read.json("data/people.json", schema=schema).show()
```

```python
from pyspark.sql.functions import from_json, to_json, col

spark.table("raw_json") \
    .withColumn("parsed", from_json(col("payload"), schema)) \
    .select("parsed.*")
```

## Explode arrays

```python
from pyspark.sql.functions import explode

spark.table("events").select("user_id", explode("items").alias("item"))
```

## Summary

Complex types are first-class in Spark SQL. Use built-ins like `from_json` and `explode` for nested data.
