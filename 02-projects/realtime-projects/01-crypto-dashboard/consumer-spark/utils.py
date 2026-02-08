from sqlalchemy import create_engine,text
import psycopg2
import traceback

def write_to_postgres_price(batch_df, batch_id):
    try:
        batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost:5432/crypto-stream-sink") \
        .option("dbtable", "crypto_prices") \
        .option("user", "crypto-stream-user") \
        .option("password", "crypto-stream-pass") \
        .option("batchsize", "100") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()
        print(f"✅ Batch {batch_id}: Crypto prices written successfully.")
    except Exception as e:
        print(f"❌ Batch {batch_id}: Error writing to crypto_prices - {str(e)}")

def write_to_postgres_window(batch_df, batch_id):
    try:
        db_url = "jdbc:postgresql://localhost:5432/crypto-stream-sink"
        db_properties = {
            "user": "crypto-stream-user",
            "password": "crypto-stream-pass",
            "driver": "org.postgresql.Driver"
        }
        
        batch_df.write.jdbc(
            url=db_url, 
            table="temp_window_1m", 
            mode="overwrite", 
            properties=db_properties
        )

        from sqlalchemy import create_engine, text
        engine = create_engine("postgresql+psycopg2://crypto-stream-user:crypto-stream-pass@localhost:5432/crypto-stream-sink")
        
        upsert_query = text("""
            INSERT INTO window_1m (window_start, window_end, symbol, open, high, low, close)
            SELECT window_start, window_end, symbol, open, high, low, close 
            FROM temp_window_1m
            ON CONFLICT (window_start, symbol) 
            DO UPDATE SET 
                high = GREATEST(window_1m.high, EXCLUDED.high),
                low = LEAST(window_1m.low, EXCLUDED.low),
                close = EXCLUDED.close;
        """)
        
        with engine.connect() as conn:
            conn.execute(upsert_query)
            conn.commit()
        print(f"✅ Batch {batch_id}: OHLC Upsert Successful.")
    except Exception as e:
        print(f"❌ Batch {batch_id}: Error writing to window_1m - {str(e)}")