from google.cloud import bigquery

def validate_table_row_count(table, min_rows=1):
    client = bigquery.Client()
    query = f"SELECT COUNT(*) as cnt FROM `{table}`"
    result = client.query(query).result()
    
    count = list(result)[0].cnt
    
    if count < min_rows:
        raise Exception(f"❌ Validation failed! Row count {count} < {min_rows}")
    
    print(f"✅ Validation passed: {count} rows")