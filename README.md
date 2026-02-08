# DATA ENGINEER - Learning & Projects Repository

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-3.1.3-orange.svg)](https://airflow.apache.org/)
[![Spark](https://img.shields.io/badge/Spark-3.5-red.svg)](https://spark.apache.org/)
[![Tests](https://img.shields.io/badge/Tests-115%2B-green.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Portfolio Data Engineering** - From fundamentals to production-ready pipelines
> 
> 🎓 **Current Status:** Advanced Junior / Mid-Level (100+ tests, real-time streaming, multi-cloud)

Repository ini berisi materi pembelajaran dan project-project data engineering yang terorganisir dengan baik.

## 📁 Struktur Folder

### 00-documentation/
Dokumentasi umum, terminologi, dan referensi data engineering.

### 01-learning-modules/
Modul-modul pembelajaran data engineering yang terstruktur:
- **01-data-serialization** - Konsep serialisasi data (Avro, Parquet, dll)
- **02-data-testing** - Framework testing untuk data pipeline
- **03-api-integration** - Pattern integrasi API
- **04-cloud-services** - Cloud data services (AWS, GCP, Azure)
- **05-pipeline-architecture** - Arsitektur data pipeline
- **06-performance-optimization** - Optimasi performance sistem data
- **07-devops-infrastructure** - Infrastructure as Code & DevOps
- **08-python-patterns** - Best practices Python untuk data engineering
- **09-security-compliance** - Security & compliance dalam data engineering

### 02-projects/
Semua project data engineering:

#### etl-projects/
- **01-basic-etl** - ETL script dasar
- **02-gold-silver-price** - ETL harga emas & perak
- **03-metal-price-airflow-gcp** - Pipeline Airflow di GCP untuk metal price
- **04-global-commodity** - Global commodity data pipeline

#### realtime-projects/
- **01-crypto-dashboard** - Real-time crypto price dashboard
- **02-sales-analytics-spark** - Real-time sales analytics dengan Spark
- **03-sales-analytics-spark-v2** - Versi 2 sales analytics

#### archived/
Project lama atau broken yang disimpan untuk referensi

### 03-tools-and-setup/
Tools, utilities, dan technology-based learning materials:
- **technology-stack/** - Learning materials per teknologi (Python, Airflow, Cloud, dbt, Kafka, Spark)
- **aws-data-engineering/** - Structured AWS learning path (3 phases)
- **misc-repo/** - Repository tambahan

### config/
File-file konfigurasi project (pyproject.toml, dll)

## 🌟 Highlighted Projects (Portfolio)

### 1. Global Commodity Data Pipeline ⭐ Production-Ready
**Tech Stack:** Airflow 3.1.3 | GCP (BigQuery, GCS) | dbt | Pydantic | pytest

- 4 external API integrations (metals, FX, macro indicators, news)
- 115 passing tests (73 unit + 42 integration)
- Custom exception hierarchy & exponential backoff retry
- dbt dimensional modeling (staging → dim → fact → mart)
- Multi-currency conversion with LOCF (Last Observation Carried Forward)
- Data partitioning & clustering in BigQuery

📂 [View Project](02-projects/etl-projects/04-global-commodity/)

### 2. Real-time Crypto Dashboard ⭐ Streaming Production
**Tech Stack:** Kafka (KRaft) | Spark Structured Streaming | Avro | PostgreSQL | Grafana

- Binance WebSocket → Kafka producer (idempotent, acks=all)
- Confluent Schema Registry with Avro serialization
- Stateful windowed aggregations (OHLC candlesticks)
- Real-time UPSERT to PostgreSQL
- Watermarking for late events (10s delay tolerance)

📂 [View Project](02-projects/realtime-projects/01-crypto-dashboard/)

### 3. Metal Price Airflow GCP Pipeline
**Tech Stack:** Airflow | Docker | GCP (GCS, BigQuery)

- 5-task orchestrated DAG (extract → GCS → transform → validate → load)
- Dimensional modeling (fact + dimension tables)
- XCom data passing patterns
- Cloud storage integration tested

📂 [View Project](02-projects/etl-projects/03-metal-price-airflow-gcp/)

---

## 🚀 Getting Started

1. Mulai dari folder `00-documentation` untuk memahami terminologi
2. Ikuti learning modules di `01-learning-modules` secara berurutan
3. Praktik dengan projects di `02-projects`
4. **NEW - AWS Learning:** Ikuti structured path di `03-tools-and-setup/aws-data-engineering/`
   - Phase 1: Foundation (S3 + Athena)
   - Phase 2: Serverless (Lambda + EventBridge)
   - Phase 3: Integration (Data lake architecture)
5. Gunakan tools di `03-tools-and-setup` untuk setup environment

## 📝 Notes

- Semua folder menggunakan prefix angka untuk urutan yang jelas
- ETL projects dipisahkan dari realtime projects untuk kemudahan navigasi
- Archived projects tetap disimpan untuk referensi historis
