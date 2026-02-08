# Realtime Crypto Price Streaming Pipeline

**Kafka • Spark Structured Streaming • PostgreSQL • Grafana**

## Overview

This project implements a **real-time crypto price streaming pipeline** designed to demonstrate core **Data Engineering streaming concepts** using industry-standard tools.

Live trade data from **Binance WebSocket** is ingested into **Apache Kafka**, processed in real time using **Apache Spark Structured Streaming**, aggregated into **OHLC candlestick metrics**, stored reliably in **PostgreSQL**, and visualized via **Grafana**.

> 🎯 **Goal**: Practice and showcase event-driven data ingestion, stateful stream processing, fault tolerance, and analytics-ready data modeling — not trading or prediction.

---

## Visualization (Grafana)

Features:

* Real-time price line chart
* Candlestick chart (multi-timeframe)
* Symbol selector
* Timeframe selector

📷 **Grafana Dashboard**

> ![!\[!\\[alt text\\](<img/dashboard.gif>)\](img/dashboard.gif)](img/dashboard.gif)

## High-Level Architecture

```
Binance WebSocket
      ↓
Kafka Producer (idempotent)
      ↓
Kafka Topic (crypto_prices)
      ↓
Spark Structured Streaming
      ↓
PostgreSQL (UPSERT, PK-based)
      ↓
Grafana Dashboard
```

## Data Source

* **Source**: Binance WebSocket API
* **Endpoint**:

  ```
  wss://stream.binance.com:9443/ws/{symbol}@trade
  ```
* **Assets** (config-driven):

  * BTCUSDT
  * ETHUSDT
  * SOLUSDT
  * (extendable without code changes)

Each WebSocket message represents a **single trade event** emitted by the exchange.

---

## Event Schema

All incoming events are serialized using **Apache Avro** and validated against a schema registry before entering Kafka.

| Field          | Type      | Description                 |
| -------------- | --------- | --------------------------- |
| symbol         | string    | Asset symbol (e.g. BTCUSDT) |
| price          | float     | Trade price                 |
| event_time     | long      | Event-time from source (Unix seconds) |
| processed_time | long      | Ingestion time (Unix seconds) |

**Schema Management**

* Format: Apache Avro
* Registry: Confluent Schema Registry
* Schema Location: `avro_schema/producer_schema_v1.avsc`
* Schema Evolution: Handled by registry for backward compatibility

Avro serialization ensures **compact, typed, and schema-validated** events across the pipeline.

---

## Streaming Design

### Kafka

* Distribution: **Confluent Kafka**
* Mode: **KRaft (ZooKeeper-less)**
* Topic: `crypto_prices`
* Partitions: 20
* Key: `symbol`
* Serialization: **Apache Avro** with Confluent Schema Registry

**Producer guarantees**

* `acks=all`
* `enable.idempotence=true`
* Batched delivery
* Avro schema validation on every message

➡️ Ensures **at-least-once delivery** with minimal duplicates and **type-safe** serialization.

---

### Spark Structured Streaming

Spark acts as the **stateful processing engine**.

Key features:

* Event-time processing with corrected timestamp conversion
* Avro deserialization using Abris library
* Watermarking to bound state
* Windowed aggregation (1-minute)
* Checkpointing for fault recovery

**Avro Processing**

```python
# Deserialize Avro messages from Kafka using Abris
from_avro_func = jvm.za.co.absa.abris.avro.functions.from_avro
abris_config = AbrisConfig.fromConfluentAvro() \
    .downloadReaderSchemaByLatestVersion() \
    .usingSchemaRegistry(schema_registry_url)

parsed_stream = raw_stream.select(
    Column(from_avro_func(col("value")._jc, abris_config)).alias("data")
).select("data.*")
```

**Timestamp Handling**

```python
# Convert Unix seconds (from producer) to Spark Timestamp
final_stream = parsed_stream \
    .withColumn("event_time", timestamp_seconds(col("event_time"))) \
    .withColumn("processed_time", timestamp_seconds(col("processed_time"))) \
    .withWatermark("event_time", "10 seconds")
```

✔ Avro library: `za.co.absa:abris_2.12:6.1.1` - This introduces **true streaming state**, stored in Spark checkpoints.

---

## Aggregation Logic (OHLC)

Spark computes **1-minute OHLC candles**:

* Open
* High
* Low
* Close

Higher timeframes (5m, 15m, 45m, 1h) are derived **inside PostgreSQL using SQL views**, not Spark.

> 💡 This design keeps Spark focused on **heavy computation**, while PostgreSQL handles **cheap roll-ups**.

---

## Database Design (PostgreSQL)

## Tables

**Raw ticks**

```sql
crypto_prices(symbol, price, event_time, processed_time)
```

**Aggregated candles**

```sql
window_1m(
  window_start,
  window_end,
  symbol,
  open,
  high,
  low,
  close,
  PRIMARY KEY (window_start, symbol)
)
```

---

## Failure Scenarios (Handled by Design)

| Scenario         | Behavior                             |
| ---------------- | ------------------------------------ |
| Producer crash   | Kafka buffers events                 |
| Spark restart    | State recovered from checkpoint      |
| DB downtime      | Offsets not committed, data replayed |
| Duplicate events | Prevented via PK + UPSERT            |

This pipeline prioritizes **data safety over throughput**.

---

## Tech Stack

* Apache Kafka (Confluent, KRaft)
* Apache Spark Structured Streaming (3.5.0)
* Apache Avro + Confluent Schema Registry
* Abris (Avro deserialization for Spark)
* PostgreSQL
* Grafana
* Python 3.12
* Docker & Docker Compose
* Poetry

---

##  How to Run

```bash
# Start infrastructure
make start-compose

# Initialize database
make init-db

# Create Kafka topic
make setup-kafka

# Run producer
make run-producer

# Run Spark consumer
make run-consumer
```

📷 **Sample Database Output**

> ![alt text](img/image.png)

---

## Design Rationale

* **Kafka** decouples ingestion and processing
* **Spark** handles stateful, event-time computation
* **PostgreSQL** provides transactional safety and simple roll-ups
* **Grafana** visualizes without impacting the pipeline

---

## What This Project Demonstrates

* Event-driven streaming ingestion
* Stateful stream processing
* Watermarking & windowing
* Idempotent sink design
* Practical streaming architecture

This project is built as a **learning-oriented but production-inspired** streaming pipeline suitable for **intern / junior data engineering roles**.

---
