
---

<p align="center">
  <img src="https://avatars.githubusercontent.com/u/110361282?s=400&v=4" width="110" height="110" style="border-radius: 50%;" />
</p>

<h2 align="center">Sanju</h2>
<p align="center"><strong>Data Engineer</strong> • Event-driven Streaming & Batch Data Pipelines</p>

---

## 👋 About Me

I am a Computer Science student with a strong focus on **Data Engineering**.

I build **reliable, production-grade data pipelines** — from ingestion and orchestration to transformation and analytics-ready datasets — using modern tools and industry best practices.

My work emphasizes:

* **Production-ready engineering**: Type safety (Pydantic), comprehensive testing (115+ tests), error handling with custom exceptions
* **Data reliability & quality**: Schema validation, idempotent operations, data quality checks
* **Pipeline architecture**: Clear layering (Bronze/Silver/Gold), modular design, configuration-driven
* **Streaming & batch systems**: Event-time processing, stateful aggregations, incremental transformations
* **Testing & observability**: Unit/integration/E2E tests, structured logging, monitoring dashboards

I also work with **stateful streaming pipelines** using Kafka and Spark, focusing on event-time processing, windowed aggregations, and failure-safe design.

---

## 🧱 Core Engineering Stack

* **Languages**: Python 3.12+, SQL, Bash
* **Streaming**: Apache Kafka (Confluent, KRaft mode), Avro serialization
* **Streaming Processing**: Apache Spark Structured Streaming
* **Orchestration**: Apache Airflow 3.1+ (TaskFlow API, Docker)
* **Transformation & Modeling**: dbt 1.8+ (incremental models, tests)
* **Databases**: PostgreSQL, BigQuery (partitioned & clustered tables)
* **Visualization**: Grafana
* **Cloud**: Google Cloud Platform (GCS, BigQuery, Secret Manager)
* **Infrastructure**: Docker, Docker Compose
* **Data Quality**: Pydantic v2 validation, dbt tests, custom exception handling
* **Testing**: pytest (115+ tests), httpx mocking, E2E validation
* **HTTP Clients**: httpx with exponential backoff, tenacity retry logic

---

## 🚀 Selected Projects

### 🔷 Realtime Crypto Streaming Pipeline — Kafka & Spark

**Stateful, event-driven streaming system with Avro serialization**

* Ingests live trade events from Binance WebSocket
* **Schema validation** with Pydantic before Kafka publish
* **Avro serialization** with Confluent Schema Registry for type safety
* **Idempotent Kafka producer** (at-least-once delivery, acks=all)
* Confluent Kafka (KRaft mode, 20 partitions)
* Spark Structured Streaming with **event-time windows & watermarking**
* **Stateful OHLC aggregation** (1-minute base candles)
* Multi-timeframe candles (5m, 15m, 45m, 1h) derived via PostgreSQL views
* **Idempotent PostgreSQL sink** using UPSERT + composite primary keys
* Real-time monitoring via Grafana dashboard with candlestick visualization
* Fault-tolerant design with checkpointing

**Tech**: Apache Kafka (Confluent, KRaft), Avro, Spark Structured Streaming, PostgreSQL, Grafana, Docker
🔗 Repo: [https://github.com/S4njuuu3291/realtime-crypto-price-dashboard](https://github.com/S4njuuu3291/realtime-crypto-price-dashboard)

---

### 🌍 Global Commodity Data Platform — Airflow, GCP & dbt

**Production-grade batch data platform with comprehensive testing**

* **115 unit + integration tests** (100% passing coverage)
* Multi-source ingestion (metals, FX, macro indicators, news APIs)
* **Type-safe data models** with Pydantic v2 validation
* **Custom exception hierarchy** (8 exception types) with structured error handling
* **Exponential backoff retry logic** using tenacity for API resilience
* Raw data persisted in GCS (Bronze layer, date-partitioned NDJSON)
* BigQuery warehouse with **incremental dbt models** (11 models total)
* Layered architecture: staging → dimension → fact → mart
* **SAFE_CAST** for handling invalid data gracefully
* Environment-based configuration (.env + GCP Secret Manager)
* **E2E validation pipeline** with automated quality checks
* Schema tests, data quality tests, and relationship tests

**Tech**: Apache Airflow 3.1.3 (TaskFlow API), GCP, BigQuery, dbt 1.8+, pytest, Pydantic v2, Docker
🔗 Repo: [https://github.com/S4njuuu3291/phase4_global_commodity](https://github.com/S4njuuu3291/phase4_global_commodity)

---

### 🌦️ Weather ETL Pipeline — Python & PostgreSQL

**Foundational ETL & automation**

* API ingestion with clear Extract → Transform → Load separation
* Configuration-driven pipeline using YAML
* Logging & error handling
* Automated scheduling via Cron

**Tech**: Python, PostgreSQL, SQLAlchemy, Cron
🔗 Repo: [https://github.com/S4njuuu3291/porto-01-data-preprocessing](https://github.com/S4njuuu3291/porto-01-data-preprocessing)

---

## 🧠 Engineering Interests

* **Production-grade code quality**: Type safety, comprehensive testing, error handling
* Event-driven architectures & pub/sub patterns
* Stateful stream processing & event-time semantics
* Streaming vs batch trade-offs & hybrid approaches
* Data modeling & analytics-ready datasets (dimensional modeling, SCD)
* **Reliability patterns**: Idempotency, retry mechanisms, circuit breakers
* **Data quality frameworks**: Schema validation, data contracts, quality checks
* Replayability, failure handling & observability

---

## 📌 Current Focus

Deepening expertise in **streaming systems**, **distributed data processing**, and **production-grade pipeline design**, with emphasis on:

* **Code quality & testing**: Type-safe Python (Pydantic), comprehensive test coverage (unit/integration/E2E)
* **Reliability engineering**: Custom exception hierarchies, exponential backoff, idempotent operations
* **Modern orchestration**: Airflow TaskFlow API, dynamic DAG generation, environment management
* **Cloud-native patterns**: GCP integration (GCS, BigQuery, Secret Manager), infrastructure as code
* **Data modeling**: dbt incremental models, dimensional modeling, data quality tests
* Correctness, observability, and operational safety

---

## 📬 Contact

* LinkedIn: [https://www.linkedin.com/in/sanjukin-pinem](https://www.linkedin.com/in/sanjukin-pinem)
* Email: [sanju329121@gmail.com](mailto:sanju329121@gmail.com)

---
