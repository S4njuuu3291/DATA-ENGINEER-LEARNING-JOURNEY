import logging
import json

def transform(data,city):
    if isinstance(data, str):
        data = json.loads(data)
    logging.info("Transforming data..")
    final_data = {
        'city': city,
        'timestamp': data['current']['time'],
        'temperature': float(data['current']['temperature_2m']),
        'precipitation': float(data['current']['precipitation']),
        'wind_speed': float(data['current']['wind_speed_10m']),
    }
    return final_data