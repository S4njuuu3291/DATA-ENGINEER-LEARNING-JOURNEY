import json
import boto3
import pandas as pd
import datetime
import io

COLUMN = ["order_id","customer_id","order_date","amount","status","product_category","region"]

def lambda_handler(event, context):
    s3 = boto3.client("s3")

    bucket = event["detail"]["bucket"]["name"]
    key = event["detail"]["object"]["key"]

    if not key.startswith("bronze/") or not key.endswith(".csv"):
        return {"status": "skipped", "reason": "not a bronze csv"}
    
    output_key = key.replace("bronze/", "silver/").replace(".csv", ".parquet")
    try:
        s3.get_object(Bucket=bucket, Key=output_key)
        return {"status": "duplicate", "output": output_key}
    except s3.exceptions.ClientError:
        pass

    obj = s3.get_object(Bucket=bucket, Key=key)
    df = pd.read_csv(obj["Body"])

    missing = set(COLUMN) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    row_count_before = len(df)

    df = df.dropna(subset=["order_id", "customer_id"])
    row_count_after_id_clean = len(df)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    bad_amount = df["amount"].isna().sum()
    bad_dates = df["order_date"].isna().sum()

    # Logika "Sadar Diri": Kalau data rusak > 50%, mending gagalkan saja!
    if (bad_amount / row_count_after_id_clean) > 0.5:
        raise ValueError(f"Data Quality Alert: More than 50% of 'amount' columns are corrupted!")
    
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False, engine='pyarrow') # Pastikan engine tersedia di Layer
    buffer.seek(0)

    s3.put_object(Bucket=bucket, Key=output_key, Body=buffer.getvalue())

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "input": key,
                "output": output_key,
                "rows_processed": len(df),
            }
        ),
    }    
