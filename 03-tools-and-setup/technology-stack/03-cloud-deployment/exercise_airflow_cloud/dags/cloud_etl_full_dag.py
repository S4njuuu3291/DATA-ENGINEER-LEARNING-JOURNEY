import sys
sys.path.append("/opt/airflow/src")

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import datetime

from gcs_upload import upload_to_gcs
from bq_validate import validate_table_row_count

BUCKET = "weather-data-sanjuds"
SOURCE_FILE = "/opt/airflow/data/sample_weather.csv"
DEST_FILE = "raw/sample_weather.csv"
BQ_TABLE = "weather-cloud-lab.weather_staging.sample_weather"

default_args = {"start_date": datetime(2025, 1, 1)}

with DAG(
    dag_id="cloud_etl_with_validation",
    default_args=default_args,
    schedule_interval=None,
    catchup=False
):
    extract = PythonOperator(
        task_id="extract_file",
        python_callable=lambda: print("Simulated extract ✅")
    )

    upload = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs={"bucket": BUCKET, "source": SOURCE_FILE, "dest": DEST_FILE}
    )

    load = GCSToBigQueryOperator(
        task_id="gcs_to_bigquery",
        bucket=BUCKET,
        source_objects=[DEST_FILE],
        destination_project_dataset_table=BQ_TABLE,
        skip_leading_rows=1,
        schema_fields=[
            {"name": "city", "type": "STRING"},
            {"name": "temp", "type": "FLOAT"},
            {"name": "humidity", "type": "FLOAT"},
        ],
        write_disposition="WRITE_TRUNCATE",
        create_disposition="CREATE_IF_NEEDED",
    )

    validate = PythonOperator(
        task_id="validate_row_count",
        python_callable=validate_table_row_count,
        op_kwargs={"table": BQ_TABLE, "min_rows": 1}
    )

    extract >> upload >> load >> validate