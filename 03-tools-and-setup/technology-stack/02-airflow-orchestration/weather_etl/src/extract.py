import logging
import requests
from airflow.models import Variable
from airflow.hooks.base import BaseHook
import json

def extract():
    logging.getLogger('airflow.models.base').setLevel(logging.WARNING)
    logging.getLogger('airflow.providers').setLevel(logging.WARNING)
    
    logging.info("Attempted to extract data..")
    conn = BaseHook.get_connection('weather_openmeteo')
    parameter = "?latitude=-6.9&longitude=107.6&current=temperature_2m,precipitation,wind_speed_10m,weather_code,relative_humidity_2m,apparent_temperature"
    url = conn.host + parameter
    
    response = requests.get(url)
    if response:
        logging.info("Successfully extract data..")
    else:
        logging.error("Error when extract data..")
        return None
    raw = json.loads(response.text)
    return raw
