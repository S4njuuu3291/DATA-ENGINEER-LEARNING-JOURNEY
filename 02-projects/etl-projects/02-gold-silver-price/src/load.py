from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

def load_data(**context):
    logging.info("Loading data into database")

    clean_data = context['ti'].xcom_pull(key = 'metal_data_clean',task_ids = 'transform_task')

    hook = PostgresHook(postgres_conn_id="my_postgres")
    conn = hook.get_conn()
    cursor = conn.cursor()

    query = """
        INSERT INTO metal_prices (timestamp,metal,currency,exchange,symbol,price_usd,price_idr,prev_close_price,open_price,high_price,low_price,ch,chp,ingestion_times
        )
        VALUES (
            %(timestamp)s,%(metal)s,%(currency)s,%(exchange)s,%(symbol)s,%(price_usd)s,%(price_idr)s,%(prev_close_price)s,%(open_price)s,%(high_price)s,%(low_price)s,%(ch)s,%(chp)s,%(ingestion_times)s
        );
    """

    cursor.execute(query, clean_data)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Data loaded successfully")
