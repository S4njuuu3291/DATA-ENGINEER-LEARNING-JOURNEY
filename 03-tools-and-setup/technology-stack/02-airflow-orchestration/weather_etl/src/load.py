import logging
import psycopg2
from airflow.hooks.base import BaseHook

def load(data=None):
    weather_db = BaseHook.get_connection('weather_database')
    conn = psycopg2.connect(
        host = weather_db.host,
        database=weather_db.schema,
        user=weather_db.login,
        password=weather_db.password
    )
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id serial primary key,
                time TIMESTAMP WITH TIME ZONE,
                temperature_2m NUMERIC,
                precipitation NUMERIC,
                wind_speed_10m NUMERIC,
                relative_humidity_2m INTEGER,
                apparent_temperature NUMERIC,
                weather varchar(50)
            );
        """)
        cur.execute("""
            SET timezone TO 'Asia/Jakarta';
        """)
        logging.info("Koneksi PostgreSQL berhasil dibuat.")
        
        values = (
            data['time'],
            data['temperature_2m'],
            data['precipitation'],
            data['wind_speed_10m'],
            data['relative_humidity_2m'],
            data['apparent_temperature'],
            data['weather']
        )
        
        insert_query= """
            INSERT into weather_forecast (
                time,temperature_2m,precipitation,wind_speed_10m,relative_humidity_2m,apparent_temperature,weather)  values (%s,%s,%s,%s,%s,%s,%s)
        """
        cur.execute(insert_query,values)
        logging.info("Data berhasil di-INSERT.\n")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        logging.error(f"Error saat load data ke PostgreSQL: {e}")
    