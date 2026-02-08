# Day 3: Windowing - Making Sense of Infinite Data

---

## The Fundamental Problem: Cannot Aggregate Infinity

**Batch thinking yang tidak work:**

```python
# Batch: aggregate ALL data
total_sales = df.agg(sum("amount"))
# Works: data bounded, can sum everything
```

**Streaming reality:**

```python
# Streaming: aggregate infinite stream?
total_sales = stream.agg(sum("amount"))
# Problem: sum NEVER completes
# 10:00 → $1000
# 10:01 → $1050 (new event)
# 10:02 → $1200 (new event)
# ... forever
```

**Question:** "Berapa total sales?" → Answer: "Which time period?"

**Windows = partition infinite time into finite buckets**

---

## Windows: The Core Abstraction

### Mental Model: Time Buckets

```
Infinite timeline:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→
09:00  10:00  11:00  12:00  13:00

With 1-hour windows:
┌─────┐┌─────┐┌─────┐┌─────┐
│09-10││10-11││11-12││12-13│
└─────┘└─────┘└─────┘└─────┘

Question: "Sales per hour" now answerable
```

**Window = bounded scope untuk computation**

Each window:
- Has start and end time
- Collects events dalam time range
- Produces ONE aggregated result
- Independent dari windows lain

---

## Tumbling Windows: Non-Overlapping Buckets

### Concept: Fixed-Size, No Gap, No Overlap

```
Window size: 5 minutes

10:00:00 ┌───────────┐
         │  Window 1 │
10:05:00 └───────────┘
         ┌───────────┐
         │  Window 2 │
10:10:00 └───────────┘
         ┌───────────┐
         │  Window 3 │
10:15:00 └───────────┘
```

**Properties:**
- Each event belongs to EXACTLY one window
- No overlap between windows
- No gap between windows
- Perfect untuk distinct time buckets

### Real Example: Hourly Sales Report

```
Business question: "Sales per hour"

Events:
├─ 10:15:30 → $100 → Window [10:00-11:00]
├─ 10:45:00 → $200 → Window [10:00-11:00]
├─ 11:05:00 → $150 → Window [11:00-12:00]
└─ 11:30:00 → $300 → Window [11:00-12:00]

Results:
├─ [10:00-11:00]: $300 (100+200)
└─ [11:00-12:00]: $450 (150+300)
```

**Spark implementation:**

```python
from pyspark.sql.functions import window, sum

# Tumbling window: 1 hour
windowed = df \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(window("event_time", "1 hour")) \
    .agg(sum("amount").alias("total_sales"))

# Output schema:
# window: {start: timestamp, end: timestamp}
# total_sales: double
```

**When to use tumbling:**
- Distinct time periods (daily reports, hourly metrics)
- No event overlap needed
- Simple, efficient (each event processed once)

---

## Sliding Windows: Overlapping Analysis

### Concept: Fixed Size, Moves by Slide Interval

```
Window size: 10 minutes
Slide: 5 minutes

10:00 ┌──────────────┐
      │   Window 1   │
10:05 └──────────────┘
      ┌──────────────┐
      │   Window 2   │
10:10 └──────────────┘
      ┌──────────────┐
      │   Window 3   │
10:15 └──────────────┘

Notice: Windows overlap!
Event at 10:07 in BOTH Window 1 & Window 2
```

**Properties:**
- Event can belong to MULTIPLE windows
- Overlap = window_size - slide
- More computation (process same event multiple times)

### Real Example: Moving Average (Traffic Monitoring)

```
Goal: "Average requests in last 5 minutes" (updated every minute)

Window size: 5 minutes
Slide: 1 minute

Events:
10:00 → 100 req
10:01 → 120 req
10:02 → 110 req
10:03 → 130 req
10:04 → 115 req
10:05 → 125 req

Windows:
[10:00-10:05]: (100+120+110+130+115) / 5 = 115 avg
[10:01-10:06]: (120+110+130+115+125) / 5 = 120 avg
[10:02-10:07]: ...

Notice: Smooth transitions, captures trends
```

**Spark implementation:**

```python
# Sliding window: 10 min window, slide every 5 min
windowed = df \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(window("event_time", "10 minutes", "5 minutes")) \
    .agg(avg("request_count").alias("avg_requests"))
```

**Trade-off:**
- **Benefit**: Smoother metrics, catch patterns across boundaries
- **Cost**: Same event processed multiple times (more CPU, more state)

### When to Use Sliding:

**Use sliding if:**
- Need "last N minutes" metrics updated frequently
- Smooth trends important (avoid abrupt jumps)
- Example: Moving averages, rate calculations

**Avoid sliding if:**
- Distinct periods needed (daily reports)
- Resource constrained (sliding = more work)
- Simple aggregation sufficient

---

## Session Windows: Activity-Based Grouping

### Concept: Dynamic Windows Based on Gaps

```
Session timeout: 5 minutes (gap threshold)

Events:
10:00 → Event A │
10:02 → Event B │ Session 1 (gap < 5 min)
10:03 → Event C │
                (gap: 8 minutes, > 5 min timeout)
10:11 → Event D │ Session 2
10:13 → Event E │
```

**Properties:**
- Window size NOT fixed
- Determined by event activity gaps
- Each user/entity can have different window size

### Real Example: User Session Analysis

```
User browsing website:
10:00:00 → View product A
10:01:30 → View product B
10:03:00 → Add to cart
         (inactive for 20 minutes...)
10:23:00 → Return to site, view product C
10:25:00 → Checkout

Session timeout: 10 minutes

Result:
Session 1: [10:00:00 - 10:03:00] (3 minutes)
  └─ Actions: view, view, add_cart
  
Session 2: [10:23:00 - 10:25:00] (2 minutes)
  └─ Actions: view, checkout
```

**Spark implementation (conceptual):**

```python
# Session window: timeout after 30 min inactivity
from pyspark.sql.functions import session_window

windowed = df \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        "user_id",
        session_window("event_time", "30 minutes")
    ) \
    .agg(
        count("*").alias("actions_per_session"),
        sum("amount").alias("session_value")
    )
```

**When to use sessions:**
- User behavior analysis (web sessions, app usage)
- Device telemetry (machine active periods)
- Communication patterns (call sessions, chat conversations)

**Challenge:**
- Cannot predict window end (depends on future inactivity)
- Late data can "merge" sessions retroactively
- More complex state management

---

## Window Boundaries: The Critical Details

### Problem: Events at Boundaries

```
Window: [10:00:00 - 10:05:00]

Event at 10:05:00.000 → Which window?
├─ [10:00-10:05]? (inclusive end)
└─ [10:05-10:10]? (exclusive end)
```

**Spark behavior: [start, end) - inclusive start, exclusive end**

```python
window("event_time", "5 minutes")
# Creates: [10:00:00, 10:05:00)

Event 10:04:59.999 → [10:00:00, 10:05:00) ✓
Event 10:05:00.000 → [10:05:00, 10:10:00) ✓
```

**Why this matters:**

```
Business requirement: "Hourly report at top of hour"
Window: [10:00:00, 11:00:00)

Event at 10:59:59 → Included ✓
Event at 11:00:00 → Next window ✓
```

### Timezone Considerations

**Problem: Midnight rollover**

```
User in Jakarta (WIB = UTC+7):
Local midnight: 00:00:00 WIB
UTC equivalent: 17:00:00 (previous day)

Daily window based on UTC:
└─ User's "today" split across 2 windows ✗

Daily window based on local time:
└─ User's "today" in single window ✓
```

**Solution:** Convert to local timezone BEFORE windowing

```python
from pyspark.sql.functions import from_utc_timestamp

df_local = df.withColumn(
    "event_time_jakarta",
    from_utc_timestamp("event_time", "Asia/Jakarta")
)

windowed = df_local.groupBy(
    window("event_time_jakarta", "1 day")
)
```

---

## Choosing Window Type: Decision Framework

### Decision Tree:

**Question 1: Are you tracking user/entity activity?**
→ YES: Session windows
→ NO: Go to Q2

**Question 2: Do you need overlapping analysis?**
→ YES: Sliding windows (moving average, trend detection)
→ NO: Go to Q3

**Question 3: Do you need distinct time periods?**
→ YES: Tumbling windows (reports, summaries)

### Detailed Comparison:

**Tumbling Windows:**
```
Use cases:
✓ Hourly/daily reports
✓ Batch-like aggregations
✓ Distinct, non-overlapping periods

Pros:
+ Simple, efficient
+ Each event processed once
+ Clear boundaries

Cons:
- Abrupt transitions at boundaries
- Miss patterns across windows
- Cannot answer "last N minutes"

Example: "Total sales per day"
```

**Sliding Windows:**
```
Use cases:
✓ Moving averages
✓ Rate calculations
✓ Trend detection

Pros:
+ Smooth metric transitions
+ Capture cross-boundary patterns
+ Answer "last N minutes" queries

Cons:
- More computation (overlap)
- Higher resource usage
- More complex state management

Example: "Average requests in last 5 minutes"
```

**Session Windows:**
```
Use cases:
✓ User session analysis
✓ Activity-based grouping
✓ Communication sessions

Pros:
+ Natural grouping by behavior
+ Flexible window sizes
+ Reflects actual usage patterns

Cons:
- Unpredictable window end
- Complex late-data handling
- Higher state complexity

Example: "Actions per user session"
```

---

## Window Size: The Accuracy vs Latency Trade-off

### Small Windows (e.g., 1 minute)

**Pros:**
- Low latency results (quick feedback)
- Fine-grained analysis
- Catch short-term anomalies

**Cons:**
- Noisy metrics (high variance)
- More windows = more state
- Sensitive to late data

**Example: Real-time alerting**
```
Window: 1 minute
Use case: "Alert if error rate > 5% in last minute"
Trade-off: Quick detection vs false alarms from spikes
```

### Large Windows (e.g., 1 hour, 1 day)

**Pros:**
- Smooth metrics (low variance)
- Fewer windows = less state
- More tolerant to late data

**Cons:**
- Higher latency (wait longer)
- Miss short-term patterns
- Delayed detection

**Example: Business reporting**
```
Window: 1 day
Use case: "Daily sales report"
Trade-off: Stable metrics vs delayed insights
```

### Finding Balance:

```
Business requirement: Detect traffic spike

Option A: 10-second windows
├─ Detect spike in 10 seconds ✓
├─ Many false positives (noise) ✗
└─ High resource usage ✗

Option B: 5-minute windows
├─ Detect spike in 5 minutes (reasonable) ✓
├─ Fewer false positives ✓
└─ Balanced resource usage ✓

Option C: 1-hour windows
├─ Detect spike after 1 hour (too late) ✗
├─ Smooth, stable metrics ✓
└─ Low resource usage ✓

Decision: Option B (5 minutes) - balance detection speed & accuracy
```

---

## Window Size vs Watermark Interaction

**Critical relationship:**

```
Window size: 1 hour
Watermark delay: 10 minutes

Timeline:
10:00 ┌─────────────┐
      │  Window 1   │
11:00 └─────────────┘
      ↓ wait 10 min...
11:10 Window 1 finalized (watermark passed)
```

**Rules:**
1. **Watermark < Window size**: Normal (wait for late data within window)
2. **Watermark > Window size**: Weird (waiting longer than window itself)
3. **Watermark = 0**: Strict (no late data accepted)

**Example scenarios:**

```
Scenario A: Loose tolerance
├─ Window: 5 minutes
├─ Watermark: 10 minutes
└─ Wait 10 min for late data (longer than window!)

Scenario B: Tight tolerance
├─ Window: 1 hour
├─ Watermark: 5 minutes
└─ Wait 5 min for late data (reasonable)

Scenario C: No tolerance
├─ Window: 1 hour
├─ Watermark: 0 minutes
└─ Finalize immediately (strict, may lose data)
```

---

## Common Pitfalls

### Pitfall 1: Window Too Small + High Latency Data

```
Configuration:
├─ Window: 1 minute
├─ Watermark: 30 seconds
└─ Typical data latency: 2 minutes

Problem: Most data arrives AFTER watermark
Result: Lost data ✗

Fix: Increase watermark to match data latency
```

### Pitfall 2: Sliding Window with Large Overlap

```
Configuration:
├─ Window: 1 hour
├─ Slide: 1 minute
└─ Overlap: 59 minutes

Problem: Each event processed in 60 windows!
Result: 60x computation overhead ✗

Fix: Increase slide interval (e.g., 15 minutes)
```

### Pitfall 3: Session Window with No Timeout

```
Configuration:
└─ Session timeout: infinite

Problem: Session never ends
Result: State grows forever, OOM ✗

Fix: Set reasonable timeout based on business logic
```

---

## Practical Guidelines

**Window size selection:**

1. **Start with business requirement**
   - "Need alert within X minutes" → window ≤ X
   - "Daily summary" → window = 1 day

2. **Consider data characteristics**
   - High volume → larger windows (reduce overhead)
   - Low volume → smaller windows OK

3. **Test with real data**
   - Measure state size
   - Check result quality (noise vs smoothness)
   - Monitor resource usage

**Watermark tuning:**

1. **Measure actual latency**
   - Processing time - event time distribution
   - P99 latency = good watermark starting point

2. **Trade-off awareness**
   - Longer watermark = more complete data, higher latency
   - Shorter watermark = faster results, may lose late data

3. **Monitor late data metrics**
   - Track dropped events (after watermark)
   - Adjust watermark if too many drops

---

## Reflection Questions

### Conceptual:
1. **Mengapa tidak bisa aggregate infinite stream tanpa windows?**
   - Apa happens kalau coba sum() tanpa window?

2. **Tumbling vs Sliding trade-off:**
   - Use case Anda butuh yang mana?
   - Apa cost dari sliding window?

3. **Session window challenge:**
   - Bagaimana tahu session sudah selesai?
   - Apa happens kalau late event arrives setelah session "closed"?

### Practical:
4. **Window boundary effect:**
   - Event at exactly 10:00:00.000 masuk window mana?
   - Kenapa penting untuk consistent boundary definition?

5. **Window + Watermark interaction:**
   - Window 1 hour, watermark 2 hours - masuk akal?
   - Window 5 minutes, watermark 1 minute - cukup?

6. **Resource usage:**
   - 1-minute tumbling vs 1-hour sliding (1 min slide) - mana lebih berat?
   - Kenapa?

---

## Key Takeaways

**Windows = Necessary:**
- Cannot aggregate infinite data without boundaries
- Windows partition time into computable chunks

**Three core types:**
- **Tumbling**: Distinct periods, no overlap (reports)
- **Sliding**: Overlapping analysis (moving averages)
- **Session**: Activity-based, dynamic (user behavior)

**Design decisions:**
- Window size: latency vs accuracy trade-off
- Window type: based on business logic
- Watermark: based on data latency characteristics

**Correctness first:**
- Understand boundary behavior
- Consider timezone implications
- Test with late/out-of-order data

---

**Next:** Kita implement windowing dengan Spark Structured Streaming, handle watermarks, dan lihat apa terjadi dengan late data.