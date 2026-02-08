from google.cloud import bigquery
import json

from google.cloud import bigquery

def create_data_warehouse():
    client = bigquery.Client()

    # ---------- Dimension: Currency ----------
    schema_dim_currency = [
        bigquery.SchemaField("currency_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("currency_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("region", "STRING", mode="NULLABLE")
    ]
    table_id = "metal-price-pipeline.metal_price_dw.dim_currency"     
    table = bigquery.Table(table_id, schema=schema_dim_currency)
    client.create_table(table, exists_ok=True)
    print(f"✅ Created table {table.project}.{table.dataset_id}.{table.table_id}")

    # ---------- Dimension: Metal ----------
    schema_dim_metal = [
        bigquery.SchemaField("metal_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("metal_name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("symbol", "STRING", mode="NULLABLE"),
    ]
    table_id = "metal-price-pipeline.metal_price_dw.dim_metal"     
    table = bigquery.Table(table_id, schema=schema_dim_metal)
    client.create_table(table, exists_ok=True)
    print(f"✅ Created table {table.project}.{table.dataset_id}.{table.table_id}")

    # ---------- Fact: Metal Price ----------
    schema_fact_metal_price = [
        bigquery.SchemaField("id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("date", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("metal_id", "INT64", mode="NULLABLE"),
        bigquery.SchemaField("unit", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("price_usd", "FLOAT64", mode="NULLABLE"),
    ]
    table_id = "metal-price-pipeline.metal_price_dw.fact_metal_price"
    table = bigquery.Table(table_id, schema=schema_fact_metal_price)
    client.create_table(table, exists_ok=True)
    print(f"✅ Created table {table.project}.{table.dataset_id}.{table.table_id}")

    # ---------- Fact: Currency Rates ----------
    schema_fact_currency_rates = [
        bigquery.SchemaField("currency_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("rate_to_usd", "FLOAT64", mode="NULLABLE"),
    ]
    table_id = "metal-price-pipeline.metal_price_dw.fact_currency_rates"
    table = bigquery.Table(table_id, schema=schema_fact_currency_rates)
    client.create_table(table, exists_ok=True)
    print(f"✅ Created table {table.project}.{table.dataset_id}.{table.table_id}")

def insert_dim():
    client = bigquery.Client()
    
    # insert data dim metal
    dim_metal_rows = [
        { "metal_id": 1, "metal_name": "Gold", "symbol": "Au" },
        { "metal_id": 2, "metal_name": "Silver", "symbol": "Ag" },
        { "metal_id": 3, "metal_name": "Platinum", "symbol": "Pt" },
        { "metal_id": 4, "metal_name": "Palladium", "symbol": "Pd" },
        { "metal_id": 5, "metal_name": "Copper", "symbol": "Cu" },
        { "metal_id": 6, "metal_name": "Aluminium", "symbol": "Al" },
        { "metal_id": 7, "metal_name": "Lead", "symbol": "Pb" },
        { "metal_id": 8, "metal_name": "Nickel", "symbol": "Ni" },
        { "metal_id": 9, "metal_name": "Zinc", "symbol": "Zn" },
    ]
    table_id = "metal-price-pipeline.metal_price_dw.dim_metal"
    errors = client.insert_rows_json(table_id, dim_metal_rows)
    if errors == []:
        print("✅ New rows have been added to dim_metal")
        
    # insert data dim currency from dim_currency.json
    with open("src/dim_currency.json") as f:
        dim_currency_rows = json.load(f)
    table_id = "metal-price-pipeline.metal_price_dw.dim_currency"
    errors = client.insert_rows_json(table_id,dim_currency_rows)
    if errors == []:
        print("✅ New rows have been added to dim_currency")
        
if __name__ == "__main__":
    create_data_warehouse()
    insert_dim()