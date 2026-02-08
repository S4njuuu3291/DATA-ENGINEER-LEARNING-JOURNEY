# Module 5: Streaming — Hands-On

Work with Structured Streaming concepts: windows, state, and sinks.

## Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.getOrCreate()
```

## Exercise 1: Stream from Rate Source

1. Create a streaming DataFrame from the rate source.
2. Add a `timestamp` and a derived `value_bucket`.
3. Write to console sink.

## Exercise 2: Windowed Aggregation

1. Use a 10-second window with 5-second slide.
2. Compute count per window.
3. Output to console with `complete` mode.

## Exercise 3: Stateful Aggregation

1. Group by key and aggregate running count.
2. Explain why `update` or `complete` is required.

## Exercise 4: Watermarking

1. Add watermark on event time (e.g., 10 minutes).
2. Use a windowed aggregation and observe late data behavior.

## Exercise 5: Kafka Integration (Optional)

1. Read from a Kafka topic.
2. Parse JSON payloads into columns.
3. Write to a different topic.

---

**Target time:** 60-90 minutes
**Back to:** [Exercises Home →](README.md)
