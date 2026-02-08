import logging
import json

def transform(data,city):
    if isinstance(data, str):
        data = json.loads(data)
    logging.info("Transforming data..")
    
    def weather_description(code):
        if code == 0:
            return "Cerah"
        elif 1 <= code <= 3:
            return "Sebagian Berawan"
        elif 45 <= code <= 48:
            return "Kabut"
        elif 51 <= code <= 55:
            return "Gerimis"
        elif 61 <= code <= 65 or 80 <= code <= 82:
            return "Hujan"
        elif 71 <= code <= 75 or 85 <= code <= 86:
            return "Salju"
        elif 95 <= code <= 99:
            return "Badai Petir"
        else:
            return "Kondisi Tidak Diketahui"
        
    final_data = {
        'city': city,
        'time': data['current']['time'],
        'temperature_2m': float(data['current']['temperature_2m']),
        'precipitation': int(data['current']['precipitation']),
        'wind_speed_10m': float(data['current']['wind_speed_10m']),
        'relative_humidity_2m': float(data['current']['relative_humidity_2m']),
        'apparent_temperature': float(data['current']['apparent_temperature']),
        'weather': weather_description(int(data['current']['weather_code'])),
    }
    return final_data