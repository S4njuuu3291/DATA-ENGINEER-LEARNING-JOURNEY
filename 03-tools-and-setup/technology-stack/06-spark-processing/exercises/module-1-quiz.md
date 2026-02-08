# Module 1: Fundamentals — Quiz

Test your understanding of Spark fundamentals.

## Questions

### 1. Multiple Choice

**What are the three fundamental limitations of Pandas?**
- A) Single-machine, lazy execution, no scaling
- B) Single-machine, eager execution, no horizontal scaling  
- C) Multi-machine, eager execution, limited RAM
- D) Single-machine, no optimization, slow

<details>
<summary>Answer</summary>
B) Single-machine, eager execution, no horizontal scaling
</details>

### 2. True/False

**Spark is always faster than Pandas for all data sizes.**

<details>
<summary>Answer</summary>
False - Pandas is faster for small data that fits in memory. Spark has coordination overhead.
</details>

### 3. Fill in the Blank

Spark achieves 10-100x speedup over Hadoop MapReduce through __________ processing.

<details>
<summary>Answer</summary>
in-memory
</details>

### 4. Short Answer

Explain the difference between Driver and Executor in Spark architecture.

<details>
<summary>Answer</summary>
- Driver: Coordinates execution, creates plans, schedules tasks
- Executor: Processes data, executes tasks on partitions
</details>

### 5. Scenario

You have 5 GB of data and need to perform aggregations. Should you use Spark or Pandas? Why?

<details>
<summary>Answer</summary>
Depends on RAM. If you have 16+ GB RAM → Pandas (simpler, faster).
If limited RAM or plan to scale → Spark.
</details>

---

**Score:** ___/5  
**Pass:** 4/5 or better

**Next:** [Module 2 Quiz →](module-2-quiz.md)
