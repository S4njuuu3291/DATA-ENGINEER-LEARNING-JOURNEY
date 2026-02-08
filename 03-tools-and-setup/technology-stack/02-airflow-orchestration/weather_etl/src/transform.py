import logging
from datetime import datetime, timedelta, timezone

def transform(data):
    time_str_gmt = data['current']['time']
    
    dt_gmt = datetime.fromisoformat(time_str_gmt).replace(tzinfo=timezone.utc)
    tz_wib = timezone(timedelta(hours=7))
    dt_wib = dt_gmt.astimezone(tz_wib)
    
    formatted_time_iso_wib = dt_wib.isoformat()
    
    data['current']['time'] = formatted_time_iso_wib
    
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
        'time':formatted_time_iso_wib,
        "temperature_2m": data['current']['temperature_2m'],
        "precipitation": data['current']['precipitation'],
        "wind_speed_10m": data['current']['wind_speed_10m'],
        "relative_humidity_2m": data['current']['relative_humidity_2m'],
        "apparent_temperature": data['current']['apparent_temperature'],
        "weather": weather_description(data['current']['weather_code']),
    }
    
    return final_data