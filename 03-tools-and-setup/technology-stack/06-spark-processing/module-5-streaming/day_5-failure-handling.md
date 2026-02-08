# Day 5: Failure Handling - Production Streaming Reality

## Failures are Normal, Not Exceptional

### Batch vs Streaming: Failure Frequency

**Batch job:**
```
Run: 1 hour
Failure probability: 0.1% per hour
Expected failures per year: ~9 failures

Impact: Rerun job, done
```

**Streaming job:**
```
Run: 24/7/365 (8760 hours/year)
Failure probability: 0.1% per hour
Expected failures per year: ~876 failures!

Impact: Must auto-recover atau service down
```

**Key insight:** Streaming runs 100x longer → 100x more failures expected.

### Real Failure Sources

**Infrastructure:**
- Executor crashes (OOM, hardware failure)
- Network partitions (cannot reach Kafka, checkpoint storage)
- Disk full (checkpoint writes fail)

**Data Issues:**
- Malformed events (deserialization errors)
- Schema changes (incompatible format)
- Backpressure (source producing faster than consumption)

**Operational:**
- Deployment/restart (new code version)
- Resource contention (other jobs competing)
- Configuration errors (wrong memory settings)

**Streaming must be designed untuk failures, bukan meskipun failures.**

---

## Exactly-Once vs At-Least-Once Semantics

### At-Least-Once: Simple but Duplicates

**Mechanism:**
```
Process batch → Output → Checkpoint

Failure scenario:
├─ Process batch 100 ✓
├─ Output written ✓
├─ Crash before checkpoint ✗

Recovery:
└─ Reprocess batch 100 → Output again!
   Result: Duplicate output ✗
```

**Guarantees:**
- No data loss ✓
- Possible duplicates ✗
- Simple implementation ✓

**Use case:** Monitoring dashboards (duplicate counts acceptable)

### Exactly-Once: Complex but Correct

**Mechanism:**
```
Process batch → Update state → Checkpoint state + offset → Output

Failure scenario:
├─ Process batch 100 ✓
├─ State updated ✓
├─ Crash before checkpoint ✗

Recovery:
├─ Load state from batch 99
├─ Reprocess batch 100 (idempotent)
└─ State same result, output once ✓
```

**Guarantees:**
- No data loss ✓
- No duplicates ✓
- Complex implementation ✗

**Use case:** Financial transactions, billing (duplicates unacceptable)

### Spark's Approach: Exactly-Once State, Output Depends on Sink

**State updates:** Always exactly-once
```
Micro-batch N:
├─ Read checkpoint offset
├─ Process events
├─ Update state
└─ Atomic checkpoint (offset + state)

Crash & restart:
└─ Reload last checkpoint, reprocess → same state ✓
```

**Output:** Depends on sink capabilities
```
Idempotent sink (e.g., key-value store):
└─ Rewrite same key → exactly-once ✓

Non-idempotent sink (e.g., append-only file):
└─ Rewrite appends duplicate → at-least-once ✗
```

---

## Checkpointing: What is Saved and Why

### Checkpoint Contents

**1. Offset Information**
```
{
  "source": "kafka",
  "topic": "transactions",
  "partition": 0,
  "offset": 123456
}
```
**Purpose:** Know where to resume reading

**2. State Store**
```
{
  "window_[10:00-11:00]": {sum: 5000, count: 120},
  "window_[11:00-12:00]": {sum: 3200, count: 98},
  "user_A": {last_seen: "10:45:00", total: 1500}
}
```
**Purpose:** Recover aggregation results

**3. Metadata**
```
{
  "batchId": 1234,
  "timestamp": "2024-01-15T10:30:00Z",
  "sparkVersion": "3.5.0",
  "queryId": "abc-123"
}
```
**Purpose:** Track execution progress, versioning

### Why Checkpoint Everything?

**Offset alone insufficient:**
```
Checkpoint offset: 123456
State: (not checkpointed)

Recovery:
├─ Resume from offset 123457
├─ But state lost! (aggregations reset to zero)
└─ Results incorrect ✗
```

**State alone insufficient:**
```
Checkpoint state: {...}
Offset: (not checkpointed)

Recovery:
├─ Where to resume reading? Unknown!
├─ Read from beginning → duplicate processing
└─ Or skip data → data loss
```

**Both required:** Offset + State = consistent recovery

---

## Failure Mid-Window: What Happens?

### Scenario: Crash During Window Processing

```
Window: [10:00-11:00], watermark: 10 min

Timeline:
10:00 - Events arrive, accumulate in state
10:30 - Checkpoint saved (batch 50)
  └─ State: {window_[10:00-11:00]: sum=2000, count=50}

10:45 - More events processed
  └─ State in memory: {sum=3500, count=80}
  └─ Not yet checkpointed

10:46 - CRASH! ✗

Recovery:
10:47 - Restart
  ├─ Load checkpoint from 10:30
  ├─ State: {sum=2000, count=50}
  └─ Resume from offset after batch 50

10:48 - Reprocess events 10:30-10:46
  └─ State rebuild: {sum=3500, count=80}
  └─ Same result as before crash ✓

11:10 - Watermark passes, window finalizes
  └─ Output: sum=5000 (complete, no duplicates)
```

**Key points:**
- State rolled back to last checkpoint
- Events reprocessed (idempotent)
- Window result eventually consistent
- No data loss, no duplicates

### Partial Aggregation Safety

**Why reprocessing works:**

```python
# Aggregation idempotent dengan state
def aggregate(state, new_events):
    # State tracks what's already processed
    for event in new_events:
        state.sum += event.amount
        state.count += 1
    return state

# Reprocess same events → same state update
# Because events deterministic, state deterministic
```

**Critical requirement:** Deterministic processing
- Same input → same output
- No random values, no current timestamp
- Replay produces identical results

---

## How Spark Resumes Computation

### Recovery Flow

**1. Detect Failure**
```
Driver monitors executors
Executor heartbeat timeout → failure detected
```

**2. Load Last Checkpoint**
```
Read checkpoint directory:
├─ offsets/12345 (last committed batch)
├─ state/12345/* (state store snapshots)
└─ metadata (batch info)
```

**3. Rebuild State**
```
Load state into memory:
├─ Distributed across executors
├─ Partitioned by key
└─ Ready for new events
```

**4. Resume from Offset**
```
Kafka: seek to offset 123456
File source: skip processed files
Socket: (not recoverable - data lost)
```

**5. Continue Processing**
```
Next micro-batch starts
Processing continues seamlessly
```

### Recovery Time

**Factors affecting RTO:**

```
Checkpoint size: 10 GB
└─ Load time: ~30 seconds

State partitions: 100
└─ Parallel load: distributed

Source replay speed:
└─ Kafka: fast (offset seek)
└─ Files: medium (skip files)
└─ Socket: impossible (ephemeral)

Total RTO: Typically 1-5 minutes
```

**Production consideration:** RTO acceptable untuk use case?

---

## Failure Scenarios Engineers Must Consider

### Scenario 1: Cascading Failures

**Problem:**
```
Failure 1: Executor crash
├─ Recovery starts
├─ Reprocess backlog
└─ Increased load → another executor crash

Failure 2: Chain reaction
└─ Cluster overwhelmed → full outage
```

**Prevention:**
- Rate limiting during recovery
- Gradual backfill, tidak full throttle
- Separate recovery resources

### Scenario 2: Checkpoint Storage Failure

**Problem:**
```
HDFS/S3 unavailable
├─ Cannot read checkpoint
├─ Cannot write new checkpoint
└─ Job cannot start/continue
```

**Prevention:**
- Reliable storage (replicated HDFS, S3 standard)
- Monitor checkpoint write latency
- Alerting on checkpoint failures

### Scenario 3: Schema Evolution Breaks Checkpoint

**Problem:**
```
V1: State {sum: Long, count: Int}
Deploy V2: State {sum: Long, count: Int, avg: Double}

Recovery:
├─ Load V1 checkpoint
├─ Schema mismatch
└─ Deserialization error ✗
```

**Prevention:**
- Test upgrade path with checkpoint compatibility
- Consider state schema versioning
- Planned downtime for breaking changes

### Scenario 4: Watermark Passes During Downtime

**Problem:**
```
10:00 - Job stops
10:00-11:00 - Downtime (1 hour)
11:00 - Job restarts

Events buffered: timestamps 10:05-10:55
Watermark before downtime: 10:00
Watermark after recovery: 11:00

Result: All buffered events dropped (too late) ✗
```

**Prevention:**
- Longer watermark tolerates downtime
- Monitor lag during incidents
- Consider pause/resume vs full stop

### Scenario 5: Poison Message

**Problem:**
```
Event #123456: Malformed JSON
├─ Deserialization fails
├─ Micro-batch fails
├─ Retry same batch → same error
└─ Infinite loop, job stuck ✗
```

**Prevention:**
```python
# Dead letter queue pattern
try:
    process_event(event)
except Exception as e:
    send_to_dlq(event, error)
    continue  # skip poison message
```

### Scenario 6: Backpressure Overload

**Problem:**
```
Source rate: 100k events/sec
Processing rate: 50k events/sec
Backlog: Growing infinitely

Eventually:
├─ Memory overflow
├─ State too large
└─ Crash ✗
```

**Prevention:**
- Monitor lag metrics
- Scale out (more executors)
- Source rate limiting
- Alerting thresholds

---

## Checkpoint Directory Structure

### What's Inside?

```
/checkpoint/my-streaming-job/
│
├── offsets/
│   ├── 0        # Batch 0 offset
│   ├── 1        # Batch 1 offset
│   ├── 2        # Batch 2 offset
│   └── ...
│
├── state/
│   ├── 0/
│   │   ├── 0/   # Partition 0 state
│   │   └── 1/   # Partition 1 state
│   ├── 1/
│   │   ├── 0/
│   │   └── 1/
│   └── ...
│
├── commits/
│   ├── 0        # Batch 0 completion marker
│   ├── 1
│   └── ...
│
└── metadata
    └── checkpoint metadata
```

### What Each Component Represents

**Offsets:**
- Source positions (Kafka offsets, file names)
- Where to resume reading
- One file per batch

**State:**
- Key-value snapshots
- Aggregation intermediate results
- Organized by batch & partition

**Commits:**
- Completion markers
- "Batch N fully processed"
- Used untuk exactly-once guarantee

**Metadata:**
- Query ID, configuration
- Schema information
- Version tracking

### Checkpoint Size Considerations

**Size factors:**
```
State size:
├─ Number of distinct keys
├─ Size per key value
├─ Number of active windows
└─ Watermark delay (retention period)

Example calculation:
├─ 1M unique users
├─ 100 bytes per user state
├─ 10 active windows
└─ Checkpoint size: 1M × 100 × 10 = 1 GB
```

**Growth over time:**
```
Day 1: 100 MB
Week 1: 500 MB
Month 1: 2 GB
Year 1: 10 GB

Concern: Checkpoint I/O latency increases
```

**Cleanup:**
- Old checkpoints auto-deleted (configurable retention)
- Keep recent N versions (default: 10)
- Balance recovery options vs storage cost

---

## Monitoring Checklist

**Before production:**

**Recovery:**
- [ ] Test crash recovery (kill executor, verify restart)
- [ ] Measure RTO (acceptable downtime?)
- [ ] Test checkpoint corruption (handle gracefully?)

**Performance:**
- [ ] Checkpoint write latency (<10% of batch time?)
- [ ] State size tracking (growing unbounded?)
- [ ] Backlog monitoring (lag increasing?)

**Alerting:**
- [ ] Checkpoint write failures
- [ ] Lag exceeds threshold
- [ ] Consecutive batch failures
- [ ] State size approaching memory limits

---

## Key Takeaways

**Failures Expected:**
- Streaming runs forever → failures inevitable
- Design untuk auto-recovery, not manual intervention

**Checkpointing Critical:**
- Offsets + State together ensure consistency
- Atomic checkpoint → exactly-once state updates
- Recovery seamless dengan proper checkpointing

**Exactly-Once Guarantees:**
- State updates: always exactly-once (Spark guarantees)
- Output: depends on sink (idempotent vs append-only)
- End-to-end exactly-once requires idempotent sinks

**Recovery Mechanism:**
- Rollback to last checkpoint
- Replay events (deterministic processing)
- Rebuild state identically
- Continue processing

**Production Considerations:**
- RTO (recovery time) acceptable?
- Checkpoint storage reliable?
- Schema evolution planned?
- Backpressure monitoring?

---