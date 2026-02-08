from google.cloud import bigquery

client = bigquery.Client()

schema = [
    bigquery.SchemaField("city","STRING"),
    bigquery.SchemaField("temp","FLOAT"),
    bigquery.SchemaField("humidity","FLOAT"),
]

table = bigquery.Table("weather-cloud-lab.weather_raw.weather_daily",schema)

client.create_table(table)

print("✅ Table created")
