import logging
import json
from datetime import datetime
from extract_load_gcs import extract_from_api
from uuid import uuid4

def transform_data(**context):
    logging.info("Transforming data")
    raw_data = context["ti"].xcom_pull(key = "raw_metal_data",task_ids = 'extract_from_api')
    def metal_id_mapper(metal_name):
        metal_map = {
            "gold": 1,
            "silver": 2,
            "platinum": 3,
            "palladium": 4,
            "copper": 5,
            "aluminum": 6,
            "lead": 7,
            "nickel": 8,
            "zinc": 9
        }
        return metal_map.get(metal_name, None)
    
    # Transform raw data for fact_metal_price
    metal_list = ["gold","silver","platinum","palladium","copper","aluminum","lead","nickel","zinc"]
    
    data_fact_metal_price = [
        {
            "id": uuid4().int % (10**15),
            "date":raw_data["timestamps"]["metal"],
            "metal_id":metal_id_mapper(metal),
            "unit":raw_data["unit"],
            "price_usd":raw_data["metals"][metal]
        }
        for metal in metal_list
    ]
    
    # Transform raw data for fact_currency_rates
    currency_rates = raw_data["currencies"]
    data_fact_currency_rates = [
        {
            "currency_code": code,
            "date": raw_data["timestamps"]["currency"],
            "rate_to_usd": rate
        }
        for code, rate in currency_rates.items()
    ]
    context["ti"].xcom_push(key = "data_fact_metal_price",value = data_fact_metal_price)
    context["ti"].xcom_push(key = "data_fact_currency_rates",value = data_fact_currency_rates)
    logging.info("Data successfully transformed")

    return data_fact_metal_price, data_fact_currency_rates