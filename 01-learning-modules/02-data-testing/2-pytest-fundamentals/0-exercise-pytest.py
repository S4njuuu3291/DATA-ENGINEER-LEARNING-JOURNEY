import pytest
import re

def normalize_crypto_symbol(symbol: str) -> str:
    # Normal format: X-X

    if not symbol:
        return "UNKNOWN"
    symbol = symbol.upper().strip()
    symbol = re.sub(r"[^A-Z]", "-", symbol)
    return symbol

@pytest.mark.parametrize("input_symbol, expected", [
    ("btc-usd", "BTC-USD"),
    (" ETH_USD ", "ETH-USD"),
    ("LTC/USD", "LTC-USD"),
    ("xrpusd", "XRPUSD"),
    ("", "UNKNOWN"),
    (None, "UNKNOWN"),
])
def test_normalize_crypto_symbol(input_symbol, expected):
    """Test normalize_crypto_symbol function with various inputs."""
    assert normalize_crypto_symbol(input_symbol) == expected
    

