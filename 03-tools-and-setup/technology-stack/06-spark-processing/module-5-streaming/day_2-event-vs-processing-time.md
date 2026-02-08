# Day 2: Event Time vs Processing Time - The Foundation of Streaming Correctness

## Real-World Problem: The Trading Floor Disaster

**Scenario:** Stock trading system, deadline untuk trade adalah 16:00:00 WIB (market close).

```
Trade submitted by trader: 15:59:58 (event time)
Network congestion...
Arrived at system:        16:00:03 (processing time)

Question: Accept trade atau reject?
```

**Processing-time logic:**
- System clock: 16:00:03
- Market closed
- **Reject trade ❌**
- Trader complains: "I submitted before deadline!"

**Event-time logic:**
- Event timestamp: 15:59:58
- Before deadline
- **Accept trade ✓**
- Correct business decision

**Real cost:** Salah reject = lawsuit, reputation damage, lost revenue.

---

## Event Time: What It Actually Represents

### Definition: When Event OCCURRED in Real World

**Event time = business timestamp**

```
User clicks "checkout": 14:30:15.234
│
├─ This is TRUTH
├─ When business event happened
└─ What analytics should reflect
```

**Sources of event time:**
- User device timestamp
- IoT sensor clock
- Database transaction time
- Application log timestamp

### Real System Example: Ride-Sharing App

```
Event: Driver accepts ride
├─ Event time: When driver tapped "Accept" (device clock)
├─ GPS coordinates at that moment
└─ Business metric: "Response time" calculated from this

Processing time: When server received message (server clock)
└─ Irrelevant for business logic (just network latency)
```

**Why event time matters:**
- **Analytics:** "Peak hours" based on actual ride times, not server processing
- **SLA:** "Driver response time" = event time difference, not arrival time
- **Billing:** Charge customer for actual ride duration (event time)

---

## Processing Time: Why It's Misleading

### Definition: When System PROCESSES the Event

```
14:30:15 Event happens
   ↓
   │ (network delay, queue backlog, system restart...)
   ↓
14:35:42 System processes

Processing time: 14:35:42
└─ Says nothing about actual event
```

### Problem 1: Non-Deterministic Results

**Same data, different results:**

```
Scenario A: System healthy, low latency
Event @ 10:00:00 → Processed @ 10:00:01
"Sales at 10:00" window includes this ✓

Scenario B: System under load, high latency
Same event @ 10:00:00 → Processed @ 10:01:30
"Sales at 10:00" window EXCLUDES this ✗

Same event, different window → WRONG
```

**Analytics corruption:** Historical analysis bergantung pada system performance saat itu.

### Problem 2: Cannot Replay Correctly

```
Original run (system slow):
Event A @ 10:00:00 → processed @ 10:05:00
Assigned to "10:05 window"

Replay (system fast):
Same event A @ 10:00:00 → processed @ 10:00:05
Assigned to "10:00 window"

Different windows → Different results → BROKEN
```

### Problem 3: Business Logic Breaks

**E-commerce example:**
```
User adds item to cart: 23:59:50 (event time)
Black Friday promo ends: 00:00:00

Processing time: 00:00:15 (after midnight, server delay)

Processing-time logic: No discount ❌ (processed after promo)
Event-time logic: Apply discount ✓ (added during promo)

Customer rightfully angry
```

---

## The Reality: Clock Skew, Network Delay, Out-of-Order

### Problem 1: Clock Skew (Device Clocks Wrong)

**IoT scenario: Temperature sensors di pabrik**

```
Sensor A clock: 14:00:00 (correct)
Sensor B clock: 13:45:00 (clock 15 minutes behind)
Sensor C clock: 14:20:00 (clock 20 minutes ahead)

All send readings "now":
├─ Sensor A: timestamp 14:00:00
├─ Sensor B: timestamp 13:45:00 (looks "late")
└─ Sensor C: timestamp 14:20:00 (looks "future")

Challenge: How to aggregate "current temperature"?
```

**Real case:** Mobile devices dengan wrong timezone, GPS devices dengan clock drift.

**Mitigation strategies:**
- Server-side timestamp correction (when possible)
- Bounded tolerance untuk timestamp drift
- Monitoring untuk anomalous timestamps

### Problem 2: Network Delay (Variable Latency)

**Mobile app example:**

```
User in tunnel: weak signal
├─ Event: Click "buy" @ 10:00:00
├─ Network delay: 5 minutes (tunnel)
└─ Arrives: 10:05:00

User in office: strong WiFi
├─ Event: Click "buy" @ 10:01:00
├─ Network delay: 100ms
└─ Arrives: 10:01:00

Arrival order: Office user first
Event-time order: Tunnel user first

Out-of-order arrival!
```

**Consequences:**
- Aggregations must handle late data
- Cannot assume "latest arrival = latest event"
- Need buffering untuk reorder events

### Problem 3: Out-of-Order Events (The Norm, Not Exception)

**Financial system example:**

```
Arrival sequence:
1. Trade C @ 10:02:00 (arrives 10:02:01)
2. Trade A @ 10:00:00 (arrives 10:02:02) ← late!
3. Trade D @ 10:03:00 (arrives 10:03:01)
4. Trade B @ 10:01:00 (arrives 10:05:00) ← very late!

Processing-time: C → A → D → B
Event-time: A → B → C → D

"Trades per minute" based on processing-time:
├─ 10:02 minute: 2 trades (C, A) ✗
└─ Wrong distribution

Event-time:
├─ 10:00 minute: 1 trade (A)
├─ 10:01 minute: 1 trade (B)
├─ 10:02 minute: 1 trade (C)
└─ 10:03 minute: 1 trade (D) ✓
```

**Out-of-order is EXPECTED:**
- Distributed systems inherently lack global clock
- Network paths different latencies
- System failures/restarts cause batching
- Mobile devices offline then reconnect

---

## Why Event-Time Correctness is Critical for Analytics

### Use Case 1: Peak Hour Analysis (Transportation)

**Goal:** Identify peak hours untuk optimize fleet allocation

**Processing-time approach:**
```
Analysis: "Peak at 08:15 based on GPS signal arrivals"
Reality: Signals delayed because network congestion at 08:00
Decision: Deploy extra vehicles at 08:15
Result: Too late, actual peak was 08:00 ✗
```

**Event-time approach:**
```
Analysis: "Peak at 08:00 based on actual ride times"
Decision: Deploy extra vehicles at 08:00
Result: Match actual demand ✓
```

### Use Case 2: Conversion Funnel (E-commerce)

**Goal:** Measure time from "view product" to "checkout"

```
User journey:
├─ View product: 14:00:00
├─ Add to cart: 14:05:00
└─ Checkout: 14:10:00

Processing arrival (system under load):
├─ View: processed @ 14:02:00
├─ Add: processed @ 14:12:00 (delayed!)
└─ Checkout: processed @ 14:11:00

Processing-time calculation:
Time to checkout: 14:11 - 14:02 = 9 minutes ✗

Event-time calculation:
Time to checkout: 14:10 - 14:00 = 10 minutes ✓

Wrong metric → wrong optimization
```

### Use Case 3: SLA Compliance (Operations)

**Goal:** "95% of requests processed within 1 second"

```
Request event @ 10:00:00.000
Service responds @ 10:00:00.500 (500ms - meets SLA)
Network delay: 2 seconds
Arrives @ 10:00:02.500

Processing-time: 10:00:02.500 - 10:00:00.000 = 2.5s
└─ SLA violated ✗ (but service was actually fast!)

Event-time: 10:00:00.500 - 10:00:00.000 = 500ms
└─ SLA met ✓
```

**Business impact:** Unfair blame on service when issue is network.

---

## How Spark Handles Event Time

### Core Principle: Timestamp is Just Another Column

**Spark's approach:** Event time is NOT special system time; it's data in your events.

```python
Event schema:
├─ user_id: String
├─ action: String
├─ amount: Double
└─ event_timestamp: Timestamp  ← event time is data
```

**You explicitly tell Spark:** "Use this column as event time"

```python
# NOT automatic, YOU specify
df.withWatermark("event_timestamp", "10 minutes")
  .groupBy(window("event_timestamp", "1 hour"))
```

### Event-Time Tracking: How Spark Thinks

**Mental model:**

```
Micro-batch 1:
├─ System time: 10:05:00 (when batch runs)
├─ Events inside batch:
│   ├─ Event A: timestamp = 10:00:00
│   ├─ Event B: timestamp = 10:02:00
│   └─ Event C: timestamp = 10:04:00
└─ Spark groups by event timestamp, NOT system time
```

**Key insight:**
- Micro-batch runs at 10:05:00 (processing time)
- But windows computed using event timestamps (10:00, 10:02, 10:04)
- **Event time ≠ micro-batch trigger time**

### Watermark Mechanism (Conceptual)

**Problem:** Berapa lama tunggu late data?

```
Current watermark: 10:10:00
Meaning: "Events before 10:00:00 won't come anymore"
          (10:10 - 10 minute watermark delay)

Late event arrives: timestamp = 09:58:00
Decision: Too late (before watermark) → drop ✗

Another late event: timestamp = 10:03:00
Decision: Still acceptable (after watermark) → process ✓
```

**Watermark = trade-off:**
- Longer delay: Wait more late data, accurate results, higher latency
- Shorter delay: Process faster, might miss late data

---

## Real Examples: Late Arrivals

### Example 1: Stock Trades (Financial)

```
Market close: 16:00:00
Trade submitted: 15:59:58 (event time)
Network issue at broker...
Arrives at exchange: 16:05:00 (5 min late)

Processing-time: Reject (after close)
Event-time + watermark:
├─ Watermark delay: 10 minutes
├─ 15:59:58 still within acceptance window
└─ Accept trade ✓

Compliance requirement met
```

### Example 2: IoT Sensors (Manufacturing)

```
Factory sensor monitoring temperature:
├─ Normal reading every 1 second
├─ Sensor loses connectivity @ 14:00:00
├─ Buffering readings locally...
└─ Reconnects @ 14:10:00, sends 600 buffered readings

Batch of events:
├─ All have event_timestamp in 14:00:00 - 14:10:00 range
├─ All arrive at processing_time = 14:10:00
└─ Appear as massive "spike" in processing-time view

Event-time view:
└─ Correctly distributed over 10 minutes ✓

Alert system (processing-time): False alarm
Alert system (event-time): Correct behavior
```

### Example 3: Mobile Analytics (Consumer App)

```
User behavior:
├─ Opens app: 09:00:00 (online)
├─ Uses app: 09:00-09:30 (goes into subway, offline)
├─ Events buffered on device...
└─ Reconnects: 10:00:00, uploads buffered events

Processing-time: All events at 10:00
└─ "User session at 10:00" ✗

Event-time: Events distributed 09:00-09:30
└─ "User session at 09:00" ✓

Session analytics accurate only with event-time
```

---

## Rules for Choosing Event Time

### ALWAYS Use Event Time If:

**1. Analytics for business decisions**
```
Question: "When did customers actually buy?"
Answer: Event time
Rationale: Business cares about customer behavior, not system lag
```

**2. Regulatory compliance**
```
Question: "Was trade before deadline?"
Answer: Event time
Rationale: Legal requirement based on actual event occurrence
```

**3. Consistent replay results needed**
```
Question: "Recompute last month's metrics"
Answer: Event time
Rationale: Processing time different on replay → inconsistent
```

**4. SLA or performance metrics**
```
Question: "Service latency measurement"
Answer: Event time
Rationale: Exclude network/queue delays dari metric
```

**5. Late data is common**
```
Question: "Mobile devices, IoT sensors"
Answer: Event time
Rationale: Offline periods, network issues → expect delays
```

### Consider Processing Time Only If:

**1. Monitoring system health**
```
Question: "When did our system receive events?"
Answer: Processing time
Rationale: Debugging system latency/throughput
```

**2. Ingestion rate tracking**
```
Question: "Events per second arriving NOW"
Answer: Processing time
Rationale: Monitoring current system load
```

**3. Event time unavailable/unreliable**
```
Question: "Legacy system, no timestamps"
Answer: Processing time (fallback)
Rationale: No choice, document limitation
```

---

## Failure Cases: Wrong Time Semantics

### Failure 1: Lost Revenue (E-commerce Promo)

**Setup:**
```
Promo: "50% off until midnight"
Event: User adds item @ 23:59:55
Processing: System processes @ 00:00:10 (15s delay)
```

**Wrong (processing-time):**
```python
if processing_time <= midnight:
    apply_discount()
# User gets NO discount
# Customer service nightmare, refund costs
```

**Correct (event-time):**
```python
if event_time <= midnight:
    apply_discount()
# User gets discount, happy customer
```

**Cost:** Angry customers, refunds, reputation damage.

### Failure 2: Incorrect Capacity Planning (Operations)

**Setup:** Traffic analysis untuk capacity planning

**Wrong (processing-time):**
```
Analysis: "Peak traffic at 14:30 based on processing time"
Reality: Network congestion at 14:00 caused delay
Decision: Scale up at 14:30
Result: Actual peak at 14:00 causes outages ✗
```

**Correct (event-time):**
```
Analysis: "Peak traffic at 14:00 based on event time"
Decision: Scale up at 14:00
Result: Handle peak correctly ✓
```

**Cost:** Downtime, lost transactions, user frustration.

### Failure 3: Compliance Violation (Financial Services)

**Setup:** Regulation requires "report trades within T+1"

**Wrong (processing-time):**
```
Trade @ 15:00:00 Friday
Delayed arrival @ 09:00:00 Monday (processing time)
Report: Monday (looks like T+1 violation)
Regulatory fine ✗
```

**Correct (event-time):**
```
Trade @ 15:00:00 Friday (event time)
Report: Saturday (T+1, Friday → Saturday)
Compliance met ✓
```

**Cost:** Regulatory fines, legal issues.

### Failure 4: Broken Session Analysis (Product Analytics)

**Setup:** Measure user session duration

**Wrong (processing-time):**
```
User opens app: 10:00:00, events processed 10:00:01
User closes app: 10:30:00, events processed 10:35:00 (delay)
Session duration: 10:35:00 - 10:00:01 = ~35 minutes ✗
```

**Correct (event-time):**
```
Session duration: 10:30:00 - 10:00:00 = 30 minutes ✓
```

**Cost:** Wrong product insights, bad decisions.

---

## Checklist: Event Time Decision

Before building streaming pipeline, ask:

**Business Logic:**
- [ ] Apakah results harus reflect "when event occurred"?
- [ ] Apakah processing delays boleh affect results?
- [ ] Apakah replay harus produce same results?

**Data Characteristics:**
- [ ] Apakah late data expected? (mobile, IoT, distributed sources)
- [ ] Apakah event timestamps available dan reliable?
- [ ] Berapa maximum lateness yang reasonable?

**Compliance/SLA:**
- [ ] Apakah ada regulatory requirements based on event time?
- [ ] Apakah SLA measurements harus exclude system delays?

**If ANY answer "yes" → Use event time**

---

## Reflection Questions

### Conceptual:
1. **Berikan contoh use case di company Anda:**
   - Yang HARUS pakai event time (why?)
   - Yang boleh pakai processing time (why?)

2. **Clock skew problem:**
   - Mobile users across timezones, clocks wrong
   - How to detect? How to handle?

3. **Watermark trade-off:**
   - Wait 1 minute untuk late data: pros/cons?
   - Wait 1 hour untuk late data: pros/cons?

### Practical:
4. **Late data scenario:**
   - Event @ 10:00, arrives @ 10:20
   - Window 10:00-10:05 already outputted result
   - What should happen? Update? Ignore?

5. **Out-of-order handling:**
   - Events arrive: C, A, B (should be A, B, C)
   - How does windowing handle this?
   - When can we "close" a window?

---

## Key Takeaways

**Event Time = Truth:**
- Represents when event occurred in real world
- Foundation untuk correct analytics
- Required untuk regulatory compliance

**Processing Time = Misleading:**
- Reflects system performance, not business reality
- Non-deterministic results
- Only useful untuk monitoring system itself

**Real Systems = Messy:**
- Clock skew, network delay, out-of-order normal
- Event-time framework designed untuk handle this
- Watermarks define "acceptable lateness"

**Correctness > Performance:**
- Better to process correctly late than incorrectly fast
- Event-time adds complexity but ensures accuracy

---