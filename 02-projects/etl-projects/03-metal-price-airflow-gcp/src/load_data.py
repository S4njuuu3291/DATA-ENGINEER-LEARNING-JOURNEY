import logging
from google.cloud import bigquery
from datetime import datetime

# def fix_datetime(row):
#     """Convert ISO 8601 Z time to RFC3339 format that BigQuery accepts."""
#     for key, value in row.items():
#         if isinstance(value, str) and value.endswith("Z"):
#             try:
#                 dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
#                 row[key] = dt.isoformat()
#             except Exception:
#                 pass
#     return row

def load_data(**context):
    ti = context["ti"]
    client = bigquery.Client(project="metal-price-pipeline")
    logging.info("🚚 Starting Load to Data Warehouse")
    data_fact_metal_price = ti.xcom_pull(key="data_fact_metal_price", task_ids="transform_data")
    table = "metal-price-pipeline.metal_price_dw.fact_metal_price"
    if data_fact_metal_price:
        logging.info(f"Preparing data for: {table}")
        # fixed_row = fix_datetime(data_fact_metal_price)
        errors = client.insert_rows_json(table, data_fact_metal_price)
        if errors == []:
            logging.info(f"✅ Inserted {len(data_fact_metal_price)} rows into {table}")
        else:
            logging.error(f"❌ Insert error in {table}: {errors}")
    else:
        logging.warning("⚠️ No data_fact_metal_price found, skipping...")

    data_fact_currency_rates = ti.xcom_pull(key="data_fact_currency_rates", task_ids="transform_data")
    table = "metal-price-pipeline.metal_price_dw.fact_currency_rates"
    if data_fact_currency_rates:
        logging.info(f"💱 Preparing data for: {table}")
        # fixed_rows = [fix_datetime(r) for r in data_fact_currency_rates]
        errors = client.insert_rows_json(table, data_fact_currency_rates)
        if errors == []:
            logging.info(f"✅ Inserted {len(data_fact_currency_rates)} rows into {table}")
        else:
            logging.error(f"❌ Insert error in {table}: {errors}")
    else:
        logging.warning("⚠️ No data_fact_currency_rates found, skipping...")

    logging.info("🎯 Load completed")

