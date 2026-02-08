import pandas as pd
import pandera as pa
from pandera.typing import Series, DataFrame
import pytest

class WhaleTransactionSchema(pa.SchemaModel):
    txn_id: Series[int] = pa.Field(unique=True, nullable=False)
    coin_symbol: Series[str] = pa.Field(isin=["BTC", "ETH", "SOL"])
    amount: Series[float] = pa.Field(gt=0)
    usd_value: Series[float] = pa.Field(gt=0)
    wallet_address: Series[str] = pa.Field(str_startswith="0x")
    timestamp: Series[pd.Timestamp] = pa.Field()

    @pa.dataframe_check
    def usd_greater_than_amount(cls, df: pd.DataFrame) -> Series[bool]:
        return df["usd_value"] > df["amount"]

class ProcessedWhaleSchema(WhaleTransactionSchema):
    is_mega_whale: Series[bool] = pa.Field()

@pa.check_types
def process_whale_data(df:DataFrame[WhaleTransactionSchema]) -> DataFrame[ProcessedWhaleSchema]:
    df["is_mega_whale"] = df["usd_value"] > 1_000_000
    return df

def test_data_kotor():
    data = {
        "txn_id": ["TXN_001", "TXN_002", "TXN_003", "TXN_004"], 
        "coin_symbol": ["BTC", "DOGE", "ETH", "SOL"],           
        "amount": [0.5, 100.0, -10.0, 5.0],                    
        "usd_value": [45000.0, 10.0, 2500.0, 0.5],             
        "wallet_address": ["0xABC", "bc1q", "0xDEF", "0xGHI"], 
        "timestamp": pd.to_datetime(["2024-01-25"] * 4)
    }
    df_kotor = pd.DataFrame(data)
    with pytest.raises(pa.errors.SchemaErrors) as exc_info:
        WhaleTransactionSchema.validate(df_kotor, lazy=True)
    print("\nTABEL DOSA DATA KAMU:")
    print(exc_info.value.failure_cases[['column', 'check', 'failure_case']])

def test_data_bagus():
    data = {
        "txn_id": [1, 2, 3, 4], 
        "coin_symbol": ["BTC", "ETH", "SOL", "ETH"],           
        "amount": [0.5, 100.0, 10.0, 5.0],                    
        "usd_value": [45000.0, 3000000.0, 2500.0, 15000.0],             
        "wallet_address": ["0xABC", "0xDEF", "0xGHI", "0xJKL"], 
        "timestamp": pd.to_datetime(["2024-01-25"] * 4)
    }
    df_bagus = pd.DataFrame(data)
    df_processed = process_whale_data(df_bagus)
    assert all(df_processed["is_mega_whale"] == [False, True, False, False])

if __name__ == "__main__":
    print("Running bad data test...")
    test_data_kotor()
    print("\nRunning good data test...")
    processed_df = test_data_bagus()
    print("Processed DataFrame:\n", processed_df)
    