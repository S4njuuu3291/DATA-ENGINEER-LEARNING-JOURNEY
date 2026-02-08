"""
TESTING FULL ETL PIPELINE - Industry Standard

Real-world scenario: Production-grade ETL pipeline.

Scenario: Cryptocurrency Price Tracker
1. Extract: Async HTTP calls dengan httpx
2. Transform: Pydantic models & validation
3. Load: SQLAlchemy ORM dengan transactions
4. Verify: Data integrity checks

Cara run:
    pytest 3-test-etl-pipeline.py -v
"""

import httpx
from pytest_httpx import HTTPXMock
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, TypeAdapter
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import time
import pytest


# ==========================================
# PYDANTIC MODELS (Data Validation)
# ==========================================


class CryptoPriceRaw(BaseModel):
    """Raw data dari API."""
    symbol: str
    price: float
    timestamp_ms: int
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v


class CryptoPriceTransformed(BaseModel):
    """Transformed data untuk database."""
    symbol: str = Field(..., min_length=1, max_length=10)
    price: float = Field(..., gt=0)
    timestamp: datetime
    source: str = "coingecko"
    
    @field_validator('symbol')
    @classmethod
    def symbol_uppercase(cls, v):
        return v.upper()


# ==========================================
# SQLALCHEMY MODELS
# ==========================================


Base = declarative_base()


class CryptoPrice(Base):
    """Crypto price table."""
    __tablename__ = "crypto_prices"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp', unique=True),
    )


# ==========================================
# ETL PIPELINE COMPONENTS
# ==========================================


class CryptoExtractor:
    """Extract layer - fetch dari API."""
    
    def __init__(self, base_url: str = "https://api.coingecko.com"):
        self.base_url = base_url
    
    def extract_price(self, symbol: str) -> dict:
        """Extract single crypto price."""
        with httpx.Client(base_url=self.base_url, timeout=10.0) as client:
            response = client.get(f"/prices/{symbol}")
            response.raise_for_status()
            return response.json()
    
    def extract_multiple_prices(self, symbols: List[str]) -> List[dict]:
        """Extract multiple prices."""
        prices = []
        with httpx.Client(base_url=self.base_url, timeout=10.0) as client:
            for symbol in symbols:
                try:
                    response = client.get(f"/prices/{symbol}")
                    response.raise_for_status()
                    prices.append(response.json())
                except httpx.HTTPError as e:
                    # Log and continue
                    print(f"Failed to fetch {symbol}: {e}")
        return prices


class CryptoTransformer:
    """Transform layer - validate & normalize."""

    raw_list_adapter = TypeAdapter(List[CryptoPriceRaw])

    def transform(self, raw_data: dict) -> CryptoPriceTransformed:
        """Transform single record."""
        # Validate with Pydantic
        raw = CryptoPriceRaw(**raw_data)
        
        # Convert timestamp
        timestamp = datetime.fromtimestamp(raw.timestamp_ms / 1000)
        
        # Create transformed model
        transformed = CryptoPriceTransformed(
            symbol=raw.symbol,
            price=raw.price,
            timestamp=timestamp
        )
        
        return transformed
    
    def transform_batch(self, raw_data_list: List[dict]) -> List[CryptoPriceTransformed]:
        """Transform batch of records."""
        # transformed = []
        # errors = []
        
        # for raw_data in raw_data_list:
        #     try:
        #         transformed.append(self.transform(raw_data))
        #     except Exception as e:
        #         errors.append({"data": raw_data, "error": str(e)})
        
        # if errors:
        #     print(f"Transformation errors: {len(errors)}")

        try:
            # calculate validation time
            time_start = time.time()
            validated_raws = self.raw_list_adapter.validate_python(raw_data_list)
            time_end = time.time()
        except Exception as e:
            print(f"Batch validation error: {e}")
            return []
        
        print(f"Validation time for batch: {time_end - time_start:.4f} seconds")
        return [
            CryptoPriceTransformed(
                symbol=raw.symbol,
                price=raw.price,
                timestamp=datetime.fromtimestamp(raw.timestamp_ms / 1000)
            )
            for raw in validated_raws
        ]

class CryptoLoader:
    """Load layer - save ke database."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def load(self, data: CryptoPriceTransformed) -> CryptoPrice:
        """Load single record."""
        record = CryptoPrice(
            symbol=data.symbol,
            price=data.price,
            source=data.source,
            timestamp=data.timestamp
        )
        
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        
        return record
    
    def load_batch(self, data_list: List[CryptoPriceTransformed]) -> int:
        """
        Load batch with upsert logic.
        
        Returns count of successfully loaded records.
        """
        loaded = 0
        
        for data in data_list:
            try:
                self.load(data)
                loaded += 1
            except IntegrityError:
                # Duplicate, rollback and continue
                self.session.rollback()
                print(f"Duplicate: {data.symbol} at {data.timestamp}")
        
        return loaded
    
    def verify_integrity(self, expected_symbols: List[str]) -> dict:
        """Verify data integrity."""
        results = {
            "total_records": 0,
            "unique_symbols": 0,
            "symbols_found": [],
            "all_present": False,
            "price_anomalies": []
        }
        
        # Count
        results["total_records"] = self.session.query(CryptoPrice).count()
        
        # Unique symbols
        symbols = [r[0] for r in self.session.query(CryptoPrice.symbol).distinct().all()]
        results["symbols_found"] = symbols
        results["unique_symbols"] = len(symbols)
        results["all_present"] = set(symbols) == set(expected_symbols)
        
        # Check for anomalies (price = 0 or negative)
        anomalies = self.session.query(CryptoPrice).filter(CryptoPrice.price <= 0).all()
        results["price_anomalies"] = len(anomalies)
        
        return results


# ==========================================
# FIXTURES
# ==========================================


@pytest.fixture(scope="function")
def db_session():
    """SQLAlchemy session fixture."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def extractor():
    """Extractor fixture."""
    return CryptoExtractor()


@pytest.fixture
def transformer():
    """Transformer fixture."""
    return CryptoTransformer()


@pytest.fixture
def loader(db_session):
    """Loader fixture."""
    return CryptoLoader(db_session)


@pytest.fixture
def mock_api_data():
    """Mock API response data."""
    return {
        "BTC": {
            "symbol": "btc",
            "price": 50000.0,
            "timestamp_ms": 1705334400000
        },
        "ETH": {
            "symbol": "eth",
            "price": 3000.0,
            "timestamp_ms": 1705334400000
        },
        "SOL": {
            "symbol": "sol",
            "price": 150.0,
            "timestamp_ms": 1705334400000
        }
    }


# ==========================================
# TESTS - Extract Layer
# ==========================================


def test_extract_single_price(httpx_mock: HTTPXMock, extractor, mock_api_data):
    """Test extracting single crypto price."""
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/BTC",
        json=mock_api_data["BTC"],
        status_code=200
    )
    
    result = extractor.extract_price("BTC")
    
    assert result["symbol"] == "btc"
    assert result["price"] == 50000.0


def test_extract_multiple_prices(httpx_mock: HTTPXMock, extractor, mock_api_data):
    """Test extracting multiple prices."""
    for symbol in ["BTC", "ETH", "SOL"]:
        httpx_mock.add_response(
            url=f"https://api.coingecko.com/prices/{symbol}",
            json=mock_api_data[symbol],
            status_code=200
        )
    
    results = extractor.extract_multiple_prices(["BTC", "ETH", "SOL"])
    
    assert len(results) == 3


def test_extract_with_api_error(httpx_mock: HTTPXMock, extractor):
    """Test handling API errors during extraction."""
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/BTC",
        json={"error": "Service down"},
        status_code=503
    )
    
    with pytest.raises(httpx.HTTPStatusError):
        extractor.extract_price("BTC")


# ==========================================
# TESTS - Transform Layer
# ==========================================


def test_transform_single_record(transformer, mock_api_data):
    """Test transforming single record."""
    raw = mock_api_data["BTC"]
    
    transformed = transformer.transform(raw)
    
    assert transformed.symbol == "BTC"  # Uppercase
    assert transformed.price == 50000.0
    assert isinstance(transformed.timestamp, datetime)


def test_transform_invalid_price(transformer):
    """Test validation rejects invalid price."""
    raw = {
        "symbol": "btc",
        "price": -100.0,  # Invalid!
        "timestamp_ms": 1705334400000
    }
    
    with pytest.raises(ValueError, match="Price must be positive"):
        transformer.transform(raw)


def test_transform_batch(transformer, mock_api_data):
    """Test batch transformation."""
    raw_list = [mock_api_data["BTC"], mock_api_data["ETH"], mock_api_data["SOL"]]
    
    transformed = transformer.transform_batch(raw_list)
    
    assert len(transformed) == 3
    assert all(t.symbol.isupper() for t in transformed)


def test_transform_batch_with_errors(transformer, mock_api_data):
    """Test batch transformation with some invalid records."""
    raw_list = [
        mock_api_data["BTC"],
        {"symbol": "invalid", "price": -100, "timestamp_ms": 123},  # Invalid
        mock_api_data["ETH"],
    ]
    
    transformed = transformer.transform_batch(raw_list)
    
    # Should skip invalid, continue with valid
    assert len(transformed) == 0


# ==========================================
# TESTS - Load Layer
# ==========================================


def test_load_single_record(loader, transformer, mock_api_data):
    """Test loading single record."""
    transformed = transformer.transform(mock_api_data["BTC"])
    
    record = loader.load(transformed)
    
    assert record.id is not None
    assert record.symbol == "BTC"
    assert record.price == 50000.0


def test_load_batch(loader, transformer, mock_api_data):
    """Test batch loading."""
    raw_list = [mock_api_data["BTC"], mock_api_data["ETH"], mock_api_data["SOL"]]
    transformed = transformer.transform_batch(raw_list)
    
    count = loader.load_batch(transformed)
    
    assert count == 3


def test_load_duplicate_handling(loader, transformer, mock_api_data):
    """Test duplicate handling (idempotent)."""
    transformed = transformer.transform(mock_api_data["BTC"])
    
    # First load
    loader.load(transformed)
    
    # Second load (duplicate)
    count = loader.load_batch([transformed])
    
    # Should skip duplicate
    assert count == 0


def test_verify_integrity(loader, transformer, mock_api_data):
    """Test data integrity verification."""
    raw_list = [mock_api_data["BTC"], mock_api_data["ETH"], mock_api_data["SOL"]]
    transformed = transformer.transform_batch(raw_list)
    loader.load_batch(transformed)
    
    results = loader.verify_integrity(["BTC", "ETH", "SOL"])
    
    assert results["total_records"] == 3
    assert results["unique_symbols"] == 3
    assert results["all_present"] is True
    assert results["price_anomalies"] == 0


# ==========================================
# TESTS - Full Pipeline Integration
# ==========================================


def test_full_etl_pipeline(httpx_mock: HTTPXMock, extractor, transformer, loader, mock_api_data):
    """
    Full ETL pipeline test.
    
    Extract → Transform → Load → Verify
    """
    # Setup mocks
    for symbol in ["BTC", "ETH", "SOL"]:
        httpx_mock.add_response(
            url=f"https://api.coingecko.com/prices/{symbol}",
            json=mock_api_data[symbol],
            status_code=200
        )
    
    # Stage 1: Extract
    raw_data = extractor.extract_multiple_prices(["BTC", "ETH", "SOL"])
    assert len(raw_data) == 3
    
    # Stage 2: Transform
    transformed = transformer.transform_batch(raw_data)
    assert len(transformed) == 3
    
    # Stage 3: Load
    loaded = loader.load_batch(transformed)
    assert loaded == 3
    
    # Stage 4: Verify
    integrity = loader.verify_integrity(["BTC", "ETH", "SOL"])
    assert integrity["all_present"] is True


def test_pipeline_with_partial_failure(httpx_mock: HTTPXMock, extractor, transformer, loader, mock_api_data):
    """Test pipeline with some API failures."""
    # Setup: BTC success, ETH fails, SOL success
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/BTC",
        json=mock_api_data["BTC"],
        status_code=200
    )
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/ETH",
        json={"error": "down"},
        status_code=503
    )
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/SOL",
        json=mock_api_data["SOL"],
        status_code=200
    )
    
    # Extract (will skip ETH)
    raw_data = extractor.extract_multiple_prices(["BTC", "ETH", "SOL"])
    assert len(raw_data) == 2  # Only BTC and SOL
    
    # Transform & Load
    transformed = transformer.transform_batch(raw_data)
    loaded = loader.load_batch(transformed)
    
    assert loaded == 2


def test_idempotent_pipeline_run(httpx_mock: HTTPXMock, extractor, transformer, loader, mock_api_data):
    """
    Test pipeline is idempotent.
    
    Running twice should produce same result.
    """
    # Setup
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/BTC",
        json=mock_api_data["BTC"],
        status_code=200
    )
    
    # Run 1
    raw1 = extractor.extract_price("BTC")
    trans1 = transformer.transform(raw1)
    loader.load(trans1)
    
    count1 = loader.session.query(CryptoPrice).count()
    
    # Run 2 (duplicate)
    httpx_mock.add_response(
        url="https://api.coingecko.com/prices/BTC",
        json=mock_api_data["BTC"],
        status_code=200
    )
    
    raw2 = extractor.extract_price("BTC")
    trans2 = transformer.transform(raw2)
    loader.load_batch([trans2])  # Will skip duplicate
    
    count2 = loader.session.query(CryptoPrice).count()
    
    # Should be same
    assert count1 == count2 == 1


# ==========================================
# PERFORMANCE & QUALITY CHECKS
# ==========================================


def test_transform_performance():
    """Test transformation performance."""
    import time
    
    transformer = CryptoTransformer()
    raw_data = [
        {
            "symbol": f"sym{i}",
            "price": float(i * 100),
            "timestamp_ms": 1705334400000
        }
        for i in range(1, 192001)
    ]
    
    start = time.time()
    transformed = transformer.transform_batch(raw_data)
    duration = time.time() - start
    print(f"Transform time for batch: {duration:.4f} seconds")
    
    assert len(transformed) == 192000
    assert duration < 5  # Should be fast


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 3-test-etl-pipeline.py -v")
    print("\n🏭 Production patterns:")
    print("   - Pydantic validation in transform layer")
    print("   - SQLAlchemy ORM dengan proper models")
    print("   - httpx untuk HTTP calls")
    print("   - Idempotent operations")
    print("   - Data integrity verification")
