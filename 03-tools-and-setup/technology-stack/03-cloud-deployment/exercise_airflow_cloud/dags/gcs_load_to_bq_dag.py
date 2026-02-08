from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from datetime import datetime

BUCKET = "weather-data-sanjuds"
SOURCE_OBJECT = "raw/sample_weather.csv"
BQ_DATASET = "weather_staging"
BQ_TABLE = "sample_weather"

default_args = {"start_date": datetime(2025,1,1)}

with DAG(
    dag_id="gcs_to_bigquery_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False
):
    load_to_bq = GCSToBigQueryOperator(
        task_id="load_gcs_to_bq",
        bucket=BUCKET,
        source_objects=[SOURCE_OBJECT],
        destination_project_dataset_table=f"weather-cloud-lab.{BQ_DATASET}.{BQ_TABLE}",
        schema_fields=[
            {"name": "city", "type": "STRING", "mode": "NULLABLE"},
            {"name": "temp", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "humidity", "type": "FLOAT", "mode": "NULLABLE"},
        ],
        skip_leading_rows=1,
        write_disposition="WRITE_TRUNCATE",
        create_disposition="CREATE_IF_NEEDED",
    )

    load_to_bq