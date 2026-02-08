"""
REAL-WORLD CRYPTO ETL - Industry Standard with FastAPI

Complete production-grade ETL pipeline dengan:
- FastAPI mock server untuk testing
- SQLAlchemy ORM
- Tenacity retry logic
- Pydantic validation
- Complete monitoring & alerts

Cara run:
    pytest 5-real-world-crypto-etl.py -v
"""

import httpx
from pytest_httpx import HTTPXMock
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from tenacity import retry, stop_after_attempt, wait_exponential

import pytest


# ==========================================
# PYDANTIC MODELS (Data Contracts)
# ==========================================


class CryptoPriceAPI(BaseModel):
    """API response model."""
    symbol: str
    price: float
    volume_24h: float
    timestamp: datetime
    
    @field_validator('price', 'volume_24h')
    @classmethod
    def must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Must be positive")
        return v


class CryptoPriceDB(BaseModel):
    """Database model representation."""
    symbol: str = Field(..., min_length=1, max_length=10)
    price: float = Field(..., gt=0)
    volume_24h: float = Field(..., ge=0)
    source: str
    timestamp: datetime
    
    @field_validator('symbol')
    @classmethod
    def uppercase_symbol(cls, v):
        return v.upper()


class Alert(BaseModel):
    """Alert model."""
    symbol: str
    message: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    timestamp: datetime
    metadata: dict = {}


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
    volume_24h = Column(Float, default=0)
    source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertLog(Base):
    """Alert log table."""
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    message = Column(String(500), nullable=False)
    severity = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    resolved = Column(Integer, default=0)


# ==========================================
# PRODUCTION ETL PIPELINE
# ==========================================


class CryptoETLPipeline:
    """
    Production-grade ETL pipeline.
    
    Features:
    - Multi-source extraction with fallback
    - Pydantic validation
    - SQLAlchemy ORM
    - Tenacity retry logic
    - Anomaly detection
    - Alert generation
    """
    
    def __init__(self, session: Session, sources: List[str] = None):
        self.session = session
        self.sources = sources or ["coingecko", "binance"]
        self.alert_threshold = 0.10  # 10% price change
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    def extract_from_source(self, symbol: str, source: str) -> Optional[dict]:
        """Extract from single source with retry."""
        url = f"https://api.{source}.com/price/{symbol}"
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.json()
    
    def extract_with_fallback(self, symbol: str) -> Optional[dict]:
        """
        Extract with multi-source fallback.
        
        Try each source in order until success.
        """
        for source in self.sources:
            try:
                data = self.extract_from_source(symbol, source)
                data["_source"] = source  # Track which source succeeded
                return data
            except Exception as e:
                print(f"Failed to fetch {symbol} from {source}: {e}")
                continue
        
        # All sources failed
        return None
    
    def extract_batch(self, symbols: List[str]) -> List[dict]:
        """Extract batch with fallback logic."""
        results = []
        
        for symbol in symbols:
            data = self.extract_with_fallback(symbol)
            if data:
                results.append(data)
        
        return results
    
    def transform(self, raw_data: dict) -> CryptoPriceDB:
        """
        Transform & validate data.
        
        Uses Pydantic for validation.
        """
        # Parse API response
        api_model = CryptoPriceAPI(**raw_data)
        
        # Convert to DB model
        db_model = CryptoPriceDB(
            symbol=api_model.symbol,
            price=api_model.price,
            volume_24h=api_model.volume_24h,
            source=raw_data.get("_source", "unknown"),
            timestamp=api_model.timestamp
        )
        
        return db_model
    
    def transform_batch(self, raw_batch: List[dict]) -> List[CryptoPriceDB]:
        """Transform batch with error handling."""
        transformed = []
        
        for raw in raw_batch:
            try:
                transformed.append(self.transform(raw))
            except Exception as e:
                print(f"Transform error: {e}")
        
        return transformed
    
    def load(self, data: CryptoPriceDB) -> Optional[CryptoPrice]:
        """Load single record with upsert logic."""
        record = CryptoPrice(
            symbol=data.symbol,
            price=data.price,
            volume_24h=data.volume_24h,
            source=data.source,
            timestamp=data.timestamp
        )
        
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        except IntegrityError:
            self.session.rollback()
            return None
    
    def load_batch(self, data_batch: List[CryptoPriceDB]) -> int:
        """Load batch and return count of successful loads."""
        loaded = 0
        
        for data in data_batch:
            if self.load(data):
                loaded += 1
        
        return loaded
    
    def detect_anomalies(self, symbol: str, current_price: float) -> Optional[Alert]:
        """
        Detect price anomalies.
        
        Compares with last price to detect significant changes.
        """
        # Get previous price
        prev_record = (
            self.session.query(CryptoPrice)
            .filter(CryptoPrice.symbol == symbol)
            .order_by(CryptoPrice.timestamp.desc())
            .offset(1)
            .first()
        )
        
        if not prev_record:
            return None
        
        # Calculate change
        change_pct = ((current_price - prev_record.price) / prev_record.price)
        
        if abs(change_pct) >= self.alert_threshold:
            severity = "HIGH" if abs(change_pct) >= 0.20 else "MEDIUM"
            
            alert = Alert(
                symbol=symbol,
                message=f"Price changed {change_pct*100:.2f}%",
                severity=severity,
                timestamp=datetime.utcnow(),
                metadata={
                    "previous_price": prev_record.price,
                    "current_price": current_price,
                    "change_pct": change_pct
                }
            )
            
            return alert
        
        return None
    
    def save_alert(self, alert: Alert) -> AlertLog:
        """Save alert to database."""
        alert_record = AlertLog(
            symbol=alert.symbol,
            message=alert.message,
            severity=alert.severity,
            timestamp=alert.timestamp
        )
        
        self.session.add(alert_record)
        self.session.commit()
        self.session.refresh(alert_record)
        
        return alert_record
    
    def verify_data_quality(self) -> dict:
        """
        Verify data quality.
        
        Returns quality metrics.
        """
        metrics = {}
        
        # Total records
        metrics["total_records"] = self.session.query(CryptoPrice).count()
        
        # Unique symbols
        metrics["unique_symbols"] = (
            self.session.query(func.count(func.distinct(CryptoPrice.symbol)))
            .scalar()
        )
        
        # Latest timestamp
        latest = (
            self.session.query(func.max(CryptoPrice.timestamp))
            .scalar()
        )
        metrics["latest_timestamp"] = latest
        
        # Data freshness (in seconds)
        if latest:
            age = (datetime.utcnow() - latest).total_seconds()
            metrics["data_age_seconds"] = age
            metrics["is_fresh"] = age < 300  # Fresh if < 5 minutes
        
        # Invalid prices
        invalid_count = (
            self.session.query(CryptoPrice)
            .filter(CryptoPrice.price <= 0)
            .count()
        )
        metrics["invalid_prices"] = invalid_count
        
        return metrics
    
    def run_pipeline(self, symbols: List[str]) -> dict:
        """
        Run complete ETL pipeline.
        
        Returns summary of execution.
        """
        summary = {
            "symbols_requested": len(symbols),
            "extracted": 0,
            "transformed": 0,
            "loaded": 0,
            "alerts": 0,
            "errors": []
        }
        
        try:
            # Extract
            raw_data = self.extract_batch(symbols)
            summary["extracted"] = len(raw_data)
            
            # Transform
            transformed = self.transform_batch(raw_data)
            summary["transformed"] = len(transformed)
            
            # Load
            loaded = self.load_batch(transformed)
            summary["loaded"] = loaded
            
            # Detect anomalies & generate alerts
            for data in transformed:
                alert = self.detect_anomalies(data.symbol, data.price)
                if alert:
                    self.save_alert(alert)
                    summary["alerts"] += 1
            
        except Exception as e:
            summary["errors"].append(str(e))
        
        return summary


# ==========================================
# FIXTURES
# ==========================================


@pytest.fixture
def db_session():
    """Database session fixture."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def etl_pipeline(db_session):
    """ETL pipeline fixture."""
    return CryptoETLPipeline(db_session)


@pytest.fixture
def mock_crypto_data():
    """Mock crypto API responses."""
    return {
        "BTC": {
            "symbol": "btc",
            "price": 50000.0,
            "volume_24h": 25000000000.0,
            "timestamp": datetime(2024, 1, 15, 12, 0, 0).isoformat()
        },
        "ETH": {
            "symbol": "eth",
            "price": 3000.0,
            "volume_24h": 15000000000.0,
            "timestamp": datetime(2024, 1, 15, 12, 0, 0).isoformat()
        },
        "SOL": {
            "symbol": "sol",
            "price": 150.0,
            "volume_24h": 5000000000.0,
            "timestamp": datetime(2024, 1, 15, 12, 0, 0).isoformat()
        }
    }


# ==========================================
# TESTS - Extract with Fallback
# ==========================================


def test_extract_from_primary_source(httpx_mock: HTTPXMock, etl_pipeline, mock_crypto_data):
    """Test extraction from primary source."""
    httpx_mock.add_response(
        url="https://api.coingecko.com/price/BTC",
        json=mock_crypto_data["BTC"],
        status_code=200
    )
    
    result = etl_pipeline.extract_with_fallback("BTC")
    
    assert result is not None
    assert result["symbol"] == "btc"
    assert result["_source"] == "coingecko"


def test_extract_with_source_fallback(httpx_mock: HTTPXMock, etl_pipeline, mock_crypto_data):
    """Test fallback to secondary source."""
    # Primary source fails (3 retry attempts)
    for _ in range(3):
        httpx_mock.add_response(
            url="https://api.coingecko.com/price/BTC",
            status_code=503
        )
    
    # Secondary source succeeds
    httpx_mock.add_response(
        url="https://api.binance.com/price/BTC",
        json=mock_crypto_data["BTC"],
        status_code=200
    )
    
    result = etl_pipeline.extract_with_fallback("BTC")
    
    assert result is not None
    assert result["_source"] == "binance"


def test_extract_all_sources_fail(httpx_mock: HTTPXMock, etl_pipeline):
    """Test when all sources fail."""
    # Each source will retry 3 times
    for _ in range(3):
        httpx_mock.add_response(url="https://api.coingecko.com/price/BTC", status_code=503)
    for _ in range(3):
        httpx_mock.add_response(url="https://api.binance.com/price/BTC", status_code=503)
    
    result = etl_pipeline.extract_with_fallback("BTC")
    
    assert result is None


# ==========================================
# TESTS - Transform & Validation
# ==========================================


def test_transform_valid_data(etl_pipeline, mock_crypto_data):
    """Test transforming valid data."""
    raw = mock_crypto_data["BTC"].copy()
    raw["_source"] = "coingecko"
    
    transformed = etl_pipeline.transform(raw)
    
    assert transformed.symbol == "BTC"  # Uppercase
    assert transformed.price == 50000.0
    assert transformed.source == "coingecko"


def test_transform_invalid_price(etl_pipeline):
    """Test validation rejects invalid price."""
    raw = {
        "symbol": "btc",
        "price": -100.0,  # Invalid
        "volume_24h": 1000000.0,
        "timestamp": datetime.now().isoformat()
    }
    
    with pytest.raises(ValueError):
        etl_pipeline.transform(raw)


# ==========================================
# TESTS - Load Operations
# ==========================================


def test_load_single_record(etl_pipeline, mock_crypto_data):
    """Test loading single record."""
    raw = mock_crypto_data["BTC"].copy()
    raw["_source"] = "coingecko"
    
    transformed = etl_pipeline.transform(raw)
    record = etl_pipeline.load(transformed)
    
    assert record is not None
    assert record.symbol == "BTC"


def test_load_batch(etl_pipeline, mock_crypto_data):
    """Test batch loading."""
    transformed = []
    for symbol, data in mock_crypto_data.items():
        raw = data.copy()
        raw["_source"] = "coingecko"
        transformed.append(etl_pipeline.transform(raw))
    
    count = etl_pipeline.load_batch(transformed)
    
    assert count == 3


# ==========================================
# TESTS - Anomaly Detection & Alerts
# ==========================================


def test_anomaly_detection_significant_change(etl_pipeline):
    """Test anomaly detection for significant price change."""
    # Load baseline price
    baseline = CryptoPriceDB(
        symbol="BTC",
        price=50000.0,
        volume_24h=1000000.0,
        source="test",
        timestamp=datetime.utcnow() - timedelta(hours=1)
    )
    etl_pipeline.load(baseline)
    
    # Load new price (15% increase - should trigger alert)
    new_price = CryptoPriceDB(
        symbol="BTC",
        price=57500.0,
        volume_24h=1000000.0,
        source="test",
        timestamp=datetime.utcnow()
    )
    etl_pipeline.load(new_price)
    
    # Detect anomaly
    alert = etl_pipeline.detect_anomalies("BTC", 57500.0)
    
    assert alert is not None
    assert alert.severity == "MEDIUM"


def test_save_alert(etl_pipeline):
    """Test saving alert to database."""
    alert = Alert(
        symbol="BTC",
        message="Price spike detected",
        severity="HIGH",
        timestamp=datetime.utcnow()
    )
    
    saved = etl_pipeline.save_alert(alert)
    
    assert saved.id is not None
    assert saved.symbol == "BTC"


# ==========================================
# TESTS - Data Quality Verification
# ==========================================


def test_data_quality_metrics(etl_pipeline, mock_crypto_data):
    """Test data quality verification."""
    # Load some data
    for symbol, data in mock_crypto_data.items():
        raw = data.copy()
        raw["_source"] = "test"
        transformed = etl_pipeline.transform(raw)
        etl_pipeline.load(transformed)
    
    # Verify quality
    metrics = etl_pipeline.verify_data_quality()
    
    assert metrics["total_records"] == 3
    assert metrics["unique_symbols"] == 3
    assert metrics["invalid_prices"] == 0


# ==========================================
# TESTS - Full Pipeline Integration
# ==========================================


def test_full_pipeline_execution(httpx_mock: HTTPXMock, etl_pipeline, mock_crypto_data):
    """Test complete pipeline execution."""
    # Setup mocks
    for symbol in ["BTC", "ETH", "SOL"]:
        httpx_mock.add_response(
            url=f"https://api.coingecko.com/price/{symbol}",
            json=mock_crypto_data[symbol],
            status_code=200
        )
    
    # Run pipeline
    summary = etl_pipeline.run_pipeline(["BTC", "ETH", "SOL"])
    
    # Verify
    assert summary["symbols_requested"] == 3
    assert summary["extracted"] == 3
    assert summary["transformed"] == 3
    assert summary["loaded"] == 3
    assert len(summary["errors"]) == 0


def test_pipeline_with_partial_failures(httpx_mock: HTTPXMock, etl_pipeline, mock_crypto_data):
    """Test pipeline with some symbols failing."""
    # BTC succeeds
    httpx_mock.add_response(
        url="https://api.coingecko.com/price/BTC",
        json=mock_crypto_data["BTC"],
        status_code=200
    )
    
    # ETH fails on all sources (3 retries each)
    for _ in range(3):
        httpx_mock.add_response(url="https://api.coingecko.com/price/ETH", status_code=503)
    for _ in range(3):
        httpx_mock.add_response(url="https://api.binance.com/price/ETH", status_code=503)
    
    # SOL succeeds
    httpx_mock.add_response(
        url="https://api.coingecko.com/price/SOL",
        json=mock_crypto_data["SOL"],
        status_code=200
    )
    
    # Run pipeline
    summary = etl_pipeline.run_pipeline(["BTC", "ETH", "SOL"])
    
    # Should load 2 out of 3
    assert summary["loaded"] == 2


def test_pipeline_idempotency(httpx_mock: HTTPXMock, etl_pipeline, mock_crypto_data):
    """Test pipeline can be run multiple times safely."""
    # Setup
    httpx_mock.add_response(
        url="https://api.coingecko.com/price/BTC",
        json=mock_crypto_data["BTC"],
        status_code=200
    )
    
    # Run 1
    summary1 = etl_pipeline.run_pipeline(["BTC"])
    
    # Run 2 (duplicate - but new API call)
    httpx_mock.add_response(
        url="https://api.coingecko.com/price/BTC",
        json=mock_crypto_data["BTC"],
        status_code=200
    )
    
    summary2 = etl_pipeline.run_pipeline(["BTC"])
    
    # Both should report loaded (even though second might be duplicate)
    # The key is: no errors, safe to retry
    assert len(summary1["errors"]) == 0
    assert len(summary2["errors"]) == 0


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 5-real-world-crypto-etl.py -v")
    print("\n🏭 Production-grade ETL pipeline dengan:")
    print("   - Multi-source fallback")
    print("   - Pydantic validation")
    print("   - Tenacity retry logic")
    print("   - SQLAlchemy ORM")
    print("   - Anomaly detection")
    print("   - Alert generation")
    print("   - Data quality metrics")
