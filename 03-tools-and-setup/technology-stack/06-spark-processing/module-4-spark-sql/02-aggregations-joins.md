# 02 - Aggregations and Joins in SQL

Spark SQL supports all common aggregation and join patterns. These map directly to DataFrame operations.

## Aggregations

```python
spark.sql("""
SELECT country, COUNT(*) AS cnt, AVG(age) AS avg_age
FROM people
GROUP BY country
HAVING COUNT(*) >= 100
ORDER BY cnt DESC
""")
```

## Joins

```python
spark.sql("""
SELECT o.order_id, c.customer_name, o.amount
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE o.amount > 100
""")
```

## Join hints

```python
spark.sql("""
SELECT /*+ BROADCAST(c) */
  o.order_id, c.customer_name
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
""")
```

## Common pitfalls

- Join keys with skew can cause slow shuffles.
- `HAVING` is applied after aggregation.

## Checklist

- Use `GROUP BY` + aggregate functions for summaries
- Use join hints when a table is small and repeated
- Inspect plans with `explain()`

## Summary

Spark SQL handles joins and aggregations efficiently, but distribution and skew still matter.
