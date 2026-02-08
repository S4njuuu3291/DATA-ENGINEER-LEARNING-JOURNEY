# 01 - Spark SQL Basics

Spark SQL lets you query DataFrames using SQL syntax. It is built on the same Catalyst optimizer, so SQL and DataFrame code usually produce the same plan.

## Goals

- Query DataFrames with SQL
- Create and manage temporary views
- Understand when SQL is a good fit

## Create a temp view

```python
# DataFrame -> SQL
people = spark.read.parquet("data/people")
people.createOrReplaceTempView("people")
```

## Run SQL

```python
spark.sql("""
SELECT name, age
FROM people
WHERE age >= 21
ORDER BY age DESC
LIMIT 10
""").show()
```

## SQL vs DataFrame API

- SQL is great for analysts and ad-hoc querying.
- DataFrame API is often better for complex logic and refactoring.
- Both compile to the same execution engine.

## Common pitfalls

- Temp views are session-scoped. If the session ends, the view is gone.
- Column names with spaces need backticks in SQL.

## Checklist

- Create a temp view for each DataFrame you want to query
- Use `spark.sql()` for ad-hoc analysis
- Prefer built-in functions before UDFs

## Summary

Spark SQL is a thin, powerful layer over DataFrames. Use it when SQL readability is a win.
