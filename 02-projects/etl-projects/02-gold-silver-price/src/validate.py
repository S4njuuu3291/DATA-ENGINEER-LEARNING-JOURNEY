import logging

def validate_data(**context):
    data = context['ti'].xcom_pull(key = 'metal_data_clean',task_ids = 'transform_task')


    logging.info("Validating data..")
    if not data:
        raise ValueError("No data returned from transform task")

    required_fields = [
        "timestamp","metal","currency","exchange","symbol",
        "price_usd","price_idr","prev_close_price","open_price",
        "high_price","low_price","ch","chp","ingestion_times"
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"Missing or null value in field: {field}")

    if data["price_usd"] <= 0:
        raise ValueError(f"Invalid price_usd value: {data['price_usd']}")
    logging.info("All validations passed")
    
    return "VALID"
