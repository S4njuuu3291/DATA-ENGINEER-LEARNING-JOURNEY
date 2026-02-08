# 03 - Window Functions

Window functions let you compute values across related rows without collapsing them.

## Basic window

```python
spark.sql("""
SELECT
  user_id,
  event_time,
  amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_time) AS rn
FROM events
""")
```

## Common functions

```python
spark.sql("""
SELECT
  user_id,
  event_time,
  amount,
  LAG(amount, 1) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_amount,
  LEAD(amount, 1) OVER (PARTITION BY user_id ORDER BY event_time) AS next_amount,
  SUM(amount) OVER (PARTITION BY user_id ORDER BY event_time
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM events
""")
```

## Common pitfalls

- Missing `ORDER BY` can produce non-deterministic results.
- Large partitions can be expensive.

## Checklist

- Always define `PARTITION BY` and `ORDER BY` explicitly
- Use window functions instead of self-joins for ranking or running totals

## Summary

Window functions are essential for analytics like ranking, deltas, and running totals.
