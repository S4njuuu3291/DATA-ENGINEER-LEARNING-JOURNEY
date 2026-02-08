from google.cloud import bigquery

client = bigquery.Client()

query = """
    SELECT * FROM `weather-cloud-lab.weather_raw.airtravel` LIMIT 5;
"""

results = client.query(query).result()

for row in results:
    print(row)
    
df = client.query("SELECT * FROM `weather-cloud-lab.weather_raw.airtravel`").to_dataframe()
print(df.head())