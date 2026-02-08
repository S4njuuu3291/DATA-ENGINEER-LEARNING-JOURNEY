# 04 - UDFs (User Defined Functions)

UDFs let you apply custom logic, but they can be slower than built-in functions.

## Python UDF

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def normalize_city(city):
    return city.strip().title() if city else None

spark.sql("SELECT name, city FROM people") \
    .withColumn("city_clean", normalize_city("city")) \
    .show()
```

## Pandas UDF (vectorized)

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import IntegerType

@pandas_udf(IntegerType())
def bucket_age(s: pd.Series) -> pd.Series:
    return (s // 10) * 10

spark.table("people").withColumn("age_bucket", bucket_age("age"))
```

## Best practices

- Prefer built-in functions whenever possible
- Use Pandas UDFs for vectorized operations
- Watch for serialization overhead

## Summary

UDFs are powerful, but they bypass some optimizations. Use them as a last resort.
