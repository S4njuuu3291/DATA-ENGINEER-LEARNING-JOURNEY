"""
ERROR HANDLING & RETRY LOGIC - Industry Standard

Real-world scenario: Production-grade error handling.

Topics:
- Retry logic dengan Tenacity library (industry standard!)
- Circuit breaker pattern
- Graceful degradation
- Idempotent operations

Cara run:
    pytest 4-error-handling-retry.py -v
"""

import httpx
from pytest_httpx import HTTPXMock
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
    RetryError
)
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

import pytest


# ==========================================
# SQLALCHEMY MODELS
# ==========================================

Base = declarative_base()


class DataRecord(Base):
    """Generic data record."""
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(1000), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==========================================
# RETRY PATTERNS dengan TENACITY
# ==========================================


class APIClient:
    """
    API Client dengan retry logic menggunakan Tenacity.
    
    Tenacity > custom decorators karena:
    - Industry standard
    - Feature-rich (wait strategies, stop conditions)
    - Battle-tested
    - Better error reporting
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=5.0)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException) | (
            retry_if_exception_type(httpx.HTTPStatusError) & 
            retry_if_exception(lambda e: e.response.status_code >= 500)
        ),
        reraise=True
    )
    def fetch_with_retry(self, endpoint: str) -> dict:
        """
        Fetch data dengan automatic retry.
        
        Tenacity configuration:
        - Max 3 attempts
        - Exponential backoff: 1s, 2s, 4s
        - Only retry on timeout/5xx errors
        - Don't retry on 4xx (client errors)
        """
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=30),
    )
    def fetch_with_aggressive_retry(self, endpoint: str) -> dict:
        """More aggressive retry for critical endpoints."""
        response = self.client.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        self.client.close()


# ==========================================
# CIRCUIT BREAKER PATTERN
# ==========================================


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by stopping requests
    to failing services.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Service down, fail fast
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "HALF_OPEN"
                print("Circuit HALF_OPEN: Testing service recovery")
            else:
                raise Exception("Circuit breaker is OPEN - failing fast")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "HALF_OPEN":
                print("Circuit CLOSED: Service recovered")
                self.state = "CLOSED"
            
            self.failure_count = 0
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                print(f"Circuit OPEN: {self.failure_count} failures")
            
            raise


# ==========================================
# GRACEFUL DEGRADATION
# ==========================================


class DataService:
    """
    Service with graceful degradation.
    
    Falls back to cached data if primary source fails.
    """
    
    def __init__(self):
        self.cache: dict = {}
        self.cache_ttl = timedelta(minutes=5)
    
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=5))
    def fetch_data(self, key: str) -> Optional[dict]:
        """Fetch from primary source with retry."""
        # Simulate API call
        import httpx
        response = httpx.get(f"https://api.example.com/data/{key}")
        response.raise_for_status()
        
        # Update cache
        self.cache[key] = {
            "data": response.json(),
            "timestamp": datetime.now()
        }
        
        return response.json()
    
    def fetch_with_fallback(self, key: str) -> Optional[dict]:
        """
        Fetch with fallback to cache.
        
        Graceful degradation pattern:
        1. Try primary source
        2. On failure, check cache
        3. Return stale data if available
        4. Return None if no fallback
        """
        try:
            return self.fetch_data(key)
        except Exception as e:
            print(f"Primary source failed: {e}")
            
            # Check cache
            if key in self.cache:
                cached = self.cache[key]
                age = datetime.now() - cached["timestamp"]
                
                if age < self.cache_ttl:
                    print("Returning fresh cached data")
                    return cached["data"]
                else:
                    print("Returning stale cached data (degraded)")
                    return cached["data"]
            
            print("No fallback available")
            return None


# ==========================================
# IDEMPOTENT OPERATIONS
# ==========================================


class IdempotentLoader:
    """
    Idempotent data loader.
    
    Can safely retry without duplicating data.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def upsert(self, key: str, value: str) -> DataRecord:
        """
        Upsert operation (insert or update).
        
        Idempotent: Running multiple times = same result.
        """
        # Check if exists
        record = self.session.query(DataRecord).filter_by(key=key).first()
        
        if record:
            # Update existing
            record.value = value
            record.updated_at = datetime.utcnow()
        else:
            # Insert new
            record = DataRecord(key=key, value=value)
            self.session.add(record)
        
        self.session.commit()
        self.session.refresh(record)
        return record
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1))
    def safe_load(self, key: str, value: str) -> DataRecord:
        """Load with retry - safe because operation is idempotent."""
        return self.upsert(key, value)


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
def api_client():
    """API client fixture."""
    client = APIClient("https://api.example.com")
    yield client
    client.close()


# ==========================================
# TESTS - Tenacity Retry Logic
# ==========================================


def test_retry_succeeds_on_third_attempt(httpx_mock: HTTPXMock, api_client):
    """Test retry succeeds after failures."""
    # Setup: Fail twice, succeed third time
    httpx_mock.add_response(url="https://api.example.com/data", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/data", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/data", json={"status": "ok"}, status_code=200)
    
    result = api_client.fetch_with_retry("/data")
    
    assert result == {"status": "ok"}


def test_retry_fails_after_max_attempts(httpx_mock: HTTPXMock, api_client):
    """Test retry fails after exhausting attempts."""
    # All attempts fail
    httpx_mock.add_response(url="https://api.example.com/data", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/data", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/data", status_code=503)
    
    with pytest.raises(httpx.HTTPStatusError):
        api_client.fetch_with_retry("/data")


def test_no_retry_on_client_error(httpx_mock: HTTPXMock, api_client):
    """Test 4xx errors are NOT retried."""
    httpx_mock.add_response(url="https://api.example.com/data", status_code=404)
    
    with pytest.raises(httpx.HTTPStatusError):
        api_client.fetch_with_retry("/data")


def test_aggressive_retry_more_attempts(httpx_mock: HTTPXMock, api_client):
    """Test aggressive retry with more attempts."""
    # Fail 4 times, succeed on 5th
    for _ in range(4):
        httpx_mock.add_response(url="https://api.example.com/critical", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/critical", json={"data": "ok"}, status_code=200)
    
    result = api_client.fetch_with_aggressive_retry("/critical")
    
    assert result == {"data": "ok"}


# ==========================================
# TESTS - Circuit Breaker
# ==========================================


def test_circuit_breaker_opens_after_failures():
    """Test circuit breaker opens after threshold."""
    breaker = CircuitBreaker(failure_threshold=3)
    
    def failing_func():
        raise Exception("Service down")
    
    # First 3 failures
    for i in range(3):
        with pytest.raises(Exception):
            breaker.call(failing_func)
    
    assert breaker.state == "OPEN"


def test_circuit_breaker_fails_fast_when_open():
    """Test circuit breaker fails fast when open."""
    breaker = CircuitBreaker(failure_threshold=2)
    
    def failing_func():
        raise Exception("Fail")
    
    # Trigger circuit open
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failing_func)
    
    # Next call should fail fast
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        breaker.call(failing_func)


def test_circuit_breaker_transitions_to_half_open():
    """Test circuit transitions to HALF_OPEN after timeout."""
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    def failing_func():
        raise Exception("Fail")
    
    # Open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            breaker.call(failing_func)
    
    assert breaker.state == "OPEN"
    
    # Wait for recovery timeout
    import time
    time.sleep(1.1)
    
    # Next call should attempt (HALF_OPEN)
    def success_func():
        return "ok"
    
    result = breaker.call(success_func)
    
    assert result == "ok"
    assert breaker.state == "CLOSED"


# ==========================================
# TESTS - Graceful Degradation
# ==========================================


def test_graceful_degradation_uses_cache(httpx_mock: HTTPXMock):
    """Test fallback to cache on primary failure."""
    service = DataService()
    
    # First call succeeds - populates cache
    httpx_mock.add_response(
        url="https://api.example.com/data/key1",
        json={"value": "cached"},
        status_code=200
    )
    
    result1 = service.fetch_with_fallback("key1")
    assert result1 == {"value": "cached"}
    
    # Second call fails - should return cached
    httpx_mock.add_response(
        url="https://api.example.com/data/key1",
        status_code=503
    )
    httpx_mock.add_response(
        url="https://api.example.com/data/key1",
        status_code=503
    )
    
    result2 = service.fetch_with_fallback("key1")
    assert result2 == {"value": "cached"}


def test_graceful_degradation_no_fallback(httpx_mock: HTTPXMock):
    """Test returns None when no cache available."""
    service = DataService()
    
    # All attempts fail, no cache
    httpx_mock.add_response(url="https://api.example.com/data/key1", status_code=503)
    httpx_mock.add_response(url="https://api.example.com/data/key1", status_code=503)
    
    result = service.fetch_with_fallback("key1")
    
    assert result is None


# ==========================================
# TESTS - Idempotent Operations
# ==========================================


def test_idempotent_upsert_insert(db_session):
    """Test upsert creates new record."""
    loader = IdempotentLoader(db_session)
    
    record = loader.upsert("key1", "value1")
    
    assert record.key == "key1"
    assert record.value == "value1"


def test_idempotent_upsert_update(db_session):
    """Test upsert updates existing record."""
    loader = IdempotentLoader(db_session)
    
    # First insert
    loader.upsert("key1", "value1")
    
    # Second upsert - should update
    record = loader.upsert("key1", "value2")
    
    assert record.value == "value2"
    
    # Verify only 1 record
    count = db_session.query(DataRecord).count()
    assert count == 1


def test_idempotent_safe_load_retry(db_session):
    """Test safe_load can retry without duplicating."""
    loader = IdempotentLoader(db_session)
    
    # Load multiple times (simulating retries)
    loader.safe_load("key1", "value1")
    loader.safe_load("key1", "value1")
    loader.safe_load("key1", "value1")
    
    # Should still be only 1 record
    count = db_session.query(DataRecord).count()
    assert count == 1


# ==========================================
# BEST PRACTICES
# ==========================================


def test_industry_patterns():
    """
    🏭 INDUSTRY ERROR HANDLING PATTERNS:

    1. TENACITY LIBRARY
       ✅ Industry standard for retry logic
       ✅ Declarative retry configuration
       ✅ Multiple wait strategies (exponential, fixed)
       ✅ Flexible stop conditions
       ✅ Exception filtering

    2. CIRCUIT BREAKER
       ✅ Prevent cascading failures
       ✅ Fail fast when service down
       ✅ Automatic recovery attempts
       ✅ Protects downstream services

    3. GRACEFUL DEGRADATION
       ✅ Fallback to cache/stale data
       ✅ Partial functionality > complete failure
       ✅ User experience preserved

    4. IDEMPOTENT OPERATIONS
       ✅ Safe to retry without side effects
       ✅ Upsert pattern (INSERT OR UPDATE)
       ✅ Critical for distributed systems

    5. ERROR CLASSIFICATION
       ✅ Transient errors → Retry
       ✅ Permanent errors → Don't retry
       ✅ Client errors (4xx) → Don't retry
       ✅ Server errors (5xx) → Retry

    PRODUCTION CHECKLIST:
    [✅] Use Tenacity for retry logic
    [✅] Implement circuit breakers
    [✅] Graceful degradation patterns
    [✅] Idempotent operations
    [✅] Classify errors correctly
    [✅] Monitor failure rates
    [✅] Set appropriate timeouts

    VS OLD APPROACH:
    ❌ Custom retry loops → ✅ Tenacity
    ❌ No circuit breaker → ✅ Circuit breaker
    ❌ Fail completely → ✅ Graceful degradation
    ❌ Non-idempotent ops → ✅ Upsert pattern
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 4-error-handling-retry.py -v")
    print("\n🏭 Production patterns:")
    print("   - Tenacity untuk retry logic")
    print("   - Circuit breaker pattern")
    print("   - Graceful degradation")
    print("   - Idempotent operations dengan upsert")
