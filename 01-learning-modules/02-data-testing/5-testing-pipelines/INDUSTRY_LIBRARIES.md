# Industry-Standard Libraries Used in Folder 5

## Overview
Folder 5 telah di-refactor menggunakan **production-grade libraries** yang digunakan di industri data engineering.

## Libraries & Use Cases

### 1. **SQLAlchemy 2.0** - Database ORM
**File**: Semua file (2, 3, 4, 5)
**Fungsi**: Object-Relational Mapping untuk database operations

**Kenapa SQLAlchemy?**
- Industry standard untuk Python database operations
- Type-safe dengan declarative models
- Support berbagai database (PostgreSQL, MySQL, SQLite, dll)
- Automatic connection pooling
- Transaction management yang robust

**Contoh Usage**:
```python
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
```

**Benefits vs Raw SQL**:
- No SQL injection vulnerabilities
- Database-agnostic code
- Automatic schema migrations (dengan Alembic)
- Type safety

---

### 2. **httpx 0.27** - Modern HTTP Client
**File**: Semua file (2, 3, 4, 5)
**Fungsi**: HTTP requests dengan support async

**Kenapa httpx?**
- Successor dari `requests` library
- Support async/await (penting untuk concurrent requests)
- HTTP/2 support
- Better timeout handling
- Modern API design

**Contoh Usage**:
```python
import httpx

with httpx.Client(timeout=5.0) as client:
    response = client.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

**Benefits vs requests**:
- Async support tanpa library tambahan
- Better performance untuk concurrent calls
- Modern error handling

---

### 3. **pytest-httpx 0.34** - HTTP Mocking
**File**: Semua file (2, 3, 4, 5)
**Fungsi**: Mock HTTP requests untuk testing

**Kenapa pytest-httpx?**
- Designed khusus untuk httpx (tidak seperti `responses` yang untuk `requests`)
- Clean API untuk mocking
- Support untuk retry scenarios
- Auto-verification bahwa semua mocks digunakan

**Contoh Usage**:
```python
from pytest_httpx import HTTPXMock

def test_api_call(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://api.example.com/price",
        json={"price": 50000},
        status_code=200
    )
    
    result = fetch_price()
    assert result["price"] == 50000
```

**Benefits**:
- No actual HTTP calls (fast tests)
- Deterministic behavior
- Easy to test error scenarios

---

### 4. **Tenacity 9.0** - Retry Logic
**File**: 4-error-handling-retry.py, 5-real-world-crypto-etl.py
**Fungsi**: Declarative retry logic dengan exponential backoff

**Kenapa Tenacity?**
- Industry standard untuk retry patterns
- Declarative configuration (bukan imperative loops)
- Support berbagai retry strategies
- Built-in exponential backoff

**Contoh Usage**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
def fetch_data():
    response = client.get("/data")
    response.raise_for_status()
    return response.json()
```

**Benefits vs Manual Retry**:
- Configurable tanpa code duplication
- Testable retry behavior
- Built-in logging

---

### 5. **Pydantic 2.0** - Data Validation
**File**: 3-test-etl-pipeline.py, 5-real-world-crypto-etl.py
**Fungsi**: Data validation dan serialization

**Kenapa Pydantic?**
- Industry standard untuk data validation
- Type hints untuk auto-validation
- Fast (written in Rust)
- Integration dengan FastAPI

**Contoh Usage**:
```python
from pydantic import BaseModel, field_validator

class CryptoPriceRaw(BaseModel):
    symbol: str
    price: float
    timestamp_ms: int
    
    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

**Benefits**:
- Automatic validation pada data input
- Clear error messages
- JSON serialization built-in

---

### 6. **FastAPI** - Modern Web Framework
**Status**: Installed (siap dipakai untuk future examples)
**Fungsi**: Production-grade API framework

**Kenapa FastAPI?**
- Fastest Python web framework
- Auto-generated OpenAPI docs
- Type hints untuk validation
- Async support

---

## Architecture Patterns Introduced

### 1. **Repository Pattern**
```python
class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        return user
```

**Benefits**:
- Separation of concerns
- Easy to test (mock repository)
- Swappable data sources

---

### 2. **Circuit Breaker Pattern**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
```

**Benefits**:
- Prevent cascading failures
- Fast-fail when service down
- Automatic recovery

---

### 3. **Graceful Degradation**
```python
def fetch_with_fallback(self, key: str):
    try:
        return self.fetch_from_api(key)
    except Exception:
        # Fallback to cache
        return self.cache.get(key)
```

**Benefits**:
- Service availability during outages
- Better user experience

---

### 4. **Idempotent Operations**
```python
def upsert(self, key: str, value: str):
    record = session.query(Data).filter_by(key=key).first()
    if record:
        record.value = value  # Update
    else:
        record = Data(key=key, value=value)  # Insert
        session.add(record)
    session.commit()
```

**Benefits**:
- Safe retries
- No duplicate data

---

## Test Summary

### File 2: Mocking Basics
- **16 tests** - SQLAlchemy ORM, Repository pattern, httpx mocking
- **Speed**: ~1 second (no real HTTP calls)

### File 3: ETL Pipeline
- **15 tests** - Pydantic validation, ETL layers, pipeline integration
- **Speed**: ~0.5 seconds

### File 4: Error Handling
- **13 tests** - Tenacity retry, Circuit Breaker, Graceful degradation
- **Speed**: ~17 seconds (simulated delays)

### File 5: Real-World ETL
- **13 tests** - Complete production pipeline, multi-source fallback, anomaly detection
- **Speed**: ~16 seconds (retry simulations)

**Total**: **57 tests passing** ✅

---

## Comparison: Before vs After

| Aspect | Before (Basic) | After (Industry) |
|--------|---------------|------------------|
| **HTTP Client** | `requests` | `httpx` (async-capable) |
| **HTTP Mocking** | `responses` | `pytest-httpx` (designed for httpx) |
| **Database** | Raw `sqlite3` | `SQLAlchemy` ORM |
| **Retry Logic** | Manual loops | `Tenacity` (declarative) |
| **Validation** | Manual checks | `Pydantic` (automatic) |
| **Patterns** | Simple | Repository, Circuit Breaker, etc. |

---

## Key Takeaways

1. **Production-Ready**: All libraries digunakan di real-world production systems
2. **Best Practices**: Implement industry-standard patterns
3. **Maintainable**: Easier to extend and modify
4. **Testable**: Proper separation of concerns
5. **Type-Safe**: Better IDE support dan fewer runtime errors

---

## Next Steps

Jika ingin explore lebih lanjut:
1. Add **async/await** untuk concurrent operations
2. Add **logging** dengan `structlog`
3. Add **metrics** dengan `prometheus_client`
4. Add **distributed tracing** dengan `opentelemetry`
5. Deploy dengan **Docker** dan **Kubernetes**

---

**Author**: Refactored with industry-standard libraries  
**Date**: 2024  
**Purpose**: Educational - menunjukkan real-world data engineering practices
