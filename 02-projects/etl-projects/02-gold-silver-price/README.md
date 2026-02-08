# 🪙 Metal Price ETL Pipeline (Gold & Silver) — Airflow + PostgreSQL

This project automatically collects live gold/silver prices, validates the data, and stores it into PostgreSQL every **6 hours** using Apache Airflow. It is built as a clean, modular ETL pipeline: **Extract → Transform → Validate → Load**.

The goal: maintain a reliable metal-price dataset for analysis, dashboards, and trading insights.

## 🚀 What This Pipeline Does
| Step      | Action                                                                             |
| --------- | ---------------------------------------------------------------------------------- |
| Extract   | Fetch gold/silver prices from **GoldAPI** + USD→IDR rate from **ExchangeRate API** |
| Transform | Convert timestamp, compute IDR price, clean & shape record                         |
| Validate  | Check required fields + logical data sanity                                        |
| Load      | Insert clean record into PostgreSQL table `metal_prices`                           |

Runs automatically every **6 hours**.

## 📂 Project Structure

```
dags/
 └─ metal_price_dags.py      # Airflow DAG
src/
 ├─ extract.py               # API calls
 ├─ transform.py             # Data mapping + price conversion
 ├─ validate.py              # Data QC rules
 └─ load.py                  # DB insert logic
table_schema.sql             # Database table schema
docker-compose.yml           # Airflow + Postgres services
```


## ⏱ Schedule

```python
schedule_interval="0 */6 * * *"
```

Pipeline runs daily at: **00:00, 06:00, 12:00, 18:00 UTC**


## ⚙️ Setup

### 1️⃣ Start Airflow + PostgreSQL

```bash
docker compose up -d
```

### 2️⃣ Open Airflow UI

📍 [http://localhost:8080](http://localhost:8080)

User: `airflow`
Pass: `airflow`

### 3️⃣ Configure Connections in Airflow

| ID                  | Purpose                                       |
| ------------------- | --------------------------------------------- |
| `metal_api`         | GoldAPI (HTTP; API key stored in Extras JSON) |
| `exchange_rate_api` | ExchangeRate API (HTTP; API key in Extras)    |
| `my_postgres`       | Postgres database connection                  |


## 💾 Database Table

```sql
CREATE TABLE metal_prices (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL,
  metal TEXT,
  currency TEXT,
  exchange TEXT,
  symbol TEXT,
  price_usd NUMERIC,
  price_idr NUMERIC,
  prev_close_price NUMERIC,
  open_price NUMERIC,
  high_price NUMERIC,
  low_price NUMERIC,
  ch NUMERIC,
  chp NUMERIC,
  ingestion_times TIMESTAMP NOT NULL
);
```


## 🎯 Why This Pipeline Exists

* Demonstrates real-world Data Engineering skills
* Shows Airflow DAG design & modular ETL code
* Captures market data reliably over time
* Great foundation for dashboards & trading models

This can easily extend to other assets: crypto, forex, commodities, indices, etc.

## 📸 Screenshot

DAG Graph   

![alt text](image-1.png)

DB Data Preview 

![alt text](image.png)

## 🚧 Future Upgrades

* Slack/telegram alerts for failures
* Backfill historical price data
* Grafana dashboard

## ✅ Summary

This project shows:

* Automated data ingestion pipeline
* Airflow orchestration & XCom usage
* API integration & error handling
* ETL separation with validation layer
* Persistent storage in PostgreSQL

## 👨‍💻 Author

Data Engineering Portfolio Project
Built with ❤️ using Python, Airflow, Docker, and PostgreSQL