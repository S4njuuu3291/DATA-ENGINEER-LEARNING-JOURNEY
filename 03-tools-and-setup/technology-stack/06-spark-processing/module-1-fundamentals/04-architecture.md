# Spark Architecture — Components and Cluster Managers

> **Learning Objective:** Understand Spark's distributed architecture, the roles of Driver and Executors, and how different cluster managers coordinate resources.

---

## Spark Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  DRIVER (Manager)                               │
│  - Receives your queries                        │
│  - Creates execution plan (DAG)                 │
│  - Coordinates all executors                    │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
   ┌────▼───┐ ┌──▼─────┐ ┌─▼──────┐
   │Executor│ │Executor│ │Executor│  (Workers)
   │ Task 1 │ │ Task 2 │ │ Task 3 │
   │ Task 4 │ │ Task 5 │ │ Task 6 │
   └────────┘ └────────┘ └────────┘
        │         │         │
   Data Part1  Part2   Part3
```

---

## Core Components

### 1. Driver

**Role:** The "brain" of Spark application

**Responsibilities:**
- Receives user program
- Translates to logical plan
- Optimizes execution plan (Catalyst)
- Schedules tasks across executors
- Monitors task execution
- Collects results

**Where it runs:**
- Your laptop (local mode)
- Master node (cluster mode)
- Client machine (client mode)

**⚠️ Important:**
- Driver doesn't process big data directly
- Avoid `.collect()` — brings all data to driver!

---

### 2. Executors

**Role:** The "workers" that process data

**Characteristics:**
- Run on worker nodes
- Each has own JVM process
- Own memory and CPU cores
- Execute tasks in parallel

**Responsibilities:**
- Execute tasks assigned by driver
- Store partitions in memory/disk
- Return results to driver
- Report status back

**Parallelism:**
```
1 Executor = Multiple cores
1 Core = 1 task at a time

Example:
10 executors × 4 cores = 40 tasks in parallel
```

---

### 3. Tasks

**Definition:** Smallest unit of work

**Characteristics:**
- 1 task = operation on 1 partition
- Tasks run in parallel on executor cores
- Multiple tasks per executor

**Example:**
```python
df.filter(df.age > 30)  # Creates 1 task per partition

If df has 100 partitions:
→ 100 tasks created
→ Run in parallel on available cores
```

---

### 4. Partitions

**Definition:** Chunks of distributed data

**How it works:**
```
Large file (10 GB)
    ↓
Split into partitions (100 MB each)
    ↓
100 partitions
    ↓
Distributed across executors
```

**Key Concept:** 1 partition = 1 task

**Impact on performance:**
- Too few partitions → underutilize cluster
- Too many partitions → overhead
- Optimal: 100-200 MB per partition

---

## Cluster Managers — Resource Allocation

**Question:** Who allocates RAM and CPU to Driver and Executors?

**Answer:** **Cluster Manager**

```
┌─────────────────────────────────────────────────┐
│         CLUSTER MANAGER OPTIONS                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. Standalone        (bundled with Spark)      │
│  2. YARN              (Hadoop ecosystem)        │
│  3. Kubernetes        (container orchestration) │
│  4. Mesos             (legacy, rarely used)     │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Option 1: Spark Standalone

### Overview:
- Default cluster manager bundled with Spark
- No external dependencies
- Simple to set up

### Architecture:
```
Master Process (coordinates)
    ↓
Worker Processes (run executors)
```

### Starting a Cluster:
```bash
# Start master
$ ./sbin/start-master.sh
# Master will be at spark://master-ip:7077

# Start workers
$ ./sbin/start-worker.sh spark://master-ip:7077

# Submit job
$ spark-submit --master spark://master-ip:7077 my_job.py
```

### Best For:
- ✅ Development and testing
- ✅ Small clusters (< 100 nodes)
- ✅ Dedicated Spark workloads

### Limitations:
- ❌ Spark-only (can't share with other frameworks)
- ❌ Basic resource isolation
- ❌ Limited fault tolerance

---

## Option 2: YARN (Yet Another Resource Negotiator)

### Overview:
- Hadoop's resource manager
- Industry standard for enterprises
- Multi-tenant support

### Architecture:
```
┌─────────────────┐
│ ResourceManager │ ← Cluster-wide resource coordination
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌──▼───┐
│ NM 1 │   │ NM 2 │  ← NodeManagers (per node)
└──────┘   └──────┘
   │          │
   ├─ Container 1 (Spark Executor)
   ├─ Container 2 (Spark Executor)
   └─ Container 3 (MapReduce task)
```

### Submit Job:
```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 10 \
  --executor-memory 4G \
  --executor-cores 2 \
  my_job.py
```

### Best For:
- ✅ Existing Hadoop clusters
- ✅ Multi-tenant environments (Spark + Hive + MR)
- ✅ Enterprise production
- ✅ Resource quota management

### Benefits:
- Shared cluster resources
- Mature security (Kerberos)
- Well-tested at scale

---

## Option 3: Kubernetes

### Overview:
- Modern container orchestration
- Cloud-native, vendor-neutral
- Dynamic scaling

### Architecture:
```yaml
# spark-job.yaml
apiVersion: v1
kind: Pod
metadata:
  name: spark-driver
spec:
  containers:
  - name: spark
    image: spark:3.5.0
    command: ["/opt/spark/bin/spark-submit"]
```

### Submit Job:
```bash
spark-submit \
  --master k8s://https://k8s-api:6443 \
  --deploy-mode cluster \
  --conf spark.executor.instances=5 \
  --conf spark.kubernetes.container.image=my-spark:latest \
  my_job.py
```

### Best For:
- ✅ Cloud environments (GKE, EKS, AKS)
- ✅ Microservices architecture
- ✅ Auto-scaling requirements
- ✅ Multi-cloud deployments

### Benefits:
- Native cloud integration
- Container isolation
- Horizontal pod autoscaling
- Easy CI/CD integration

---

## Cluster Manager Comparison

| Aspect | Standalone | YARN | Kubernetes |
|--------|-----------|------|------------|
| **Setup Complexity** | Easy | Medium | Medium-Hard |
| **Use Case** | Dev/Test | Hadoop Ecosystem | Cloud-Native |
| **Multi-Tenancy** | ❌ No | ✅ Yes | ✅ Yes |
| **Resource Isolation** | Basic | Good | Excellent |
| **Scaling** | Manual | Good | Auto-Scale |
| **Security** | Basic | Excellent (Kerberos) | Good (RBAC) |
| **Best For** | Dedicated Spark | Enterprise On-Prem | Cloud Deployments |

---

## Decision Tree: Which Cluster Manager?

```
Do you have existing Hadoop cluster?
├─ Yes → Use YARN
│
└─ No
   │
   ├─ Are you in cloud (AWS, GCP, Azure)?
   │  ├─ Yes → Use Kubernetes
   │  │
   │  └─ No
   │     │
   │     └─ Small dedicated Spark cluster?
   │        └─ Use Standalone
```

---

## Summary

**Spark Architecture:**
- **Driver:** Coordinates and plans
- **Executors:** Process data tasks
- **Tasks:** 1 task per partition
- **Partitions:** Data chunks

**Cluster Managers:**
- **Standalone:** Simple, dedicated Spark
- **YARN:** Hadoop ecosystem, enterprise
- **Kubernetes:** Cloud-native, modern

**Key Insight:** Architecture choice depends on existing infrastructure and requirements.

---

**Previous:** [← In-Memory Processing](03-in-memory-processing.md) | **Next:** [When to Use Spark →](05-when-to-use-spark.md)
