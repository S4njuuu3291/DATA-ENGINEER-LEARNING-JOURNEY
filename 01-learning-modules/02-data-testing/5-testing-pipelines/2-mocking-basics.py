"""
MOCKING BASICS - Industry Standard Libraries

Topics:
- HTTP mocking dengan pytest-httpx
- Database operations dengan SQLAlchemy ORM
- Modern HTTP client dengan httpx
- Proper fixtures & dependency injection

Cara run:
    pytest 2-mocking-basics.py -v
"""

import httpx
from pytest_httpx import HTTPXMock
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

import pandas as pd
import pytest


# ==========================================
# SQLALCHEMY MODELS (Industry Standard)
# ==========================================

Base = declarative_base()


class User(Base):
    """User model dengan SQLAlchemy ORM."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CryptoPrice(Base):
    """Crypto price model."""
    __tablename__ = "crypto_prices"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)


# ==========================================
# DATA ACCESS LAYER (Repository Pattern)
# ==========================================


class UserRepository:
    """User repository untuk database operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str, email: str) -> User:
        """Create new user."""
        user = User(name=name, email=email)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.session.query(User).filter(User.id == user_id).first()
    
    def get_all(self) -> List[User]:
        """Get all users."""
        return self.session.query(User).all()
    
    def bulk_create(self, users: List[dict]) -> int:
        """Bulk create users."""
        user_objects = [User(**user) for user in users]
        self.session.bulk_save_objects(user_objects)
        self.session.commit()
        return len(user_objects)


class CryptoPriceRepository:
    """Crypto price repository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, symbol: str, price: float, source: str, timestamp: datetime) -> CryptoPrice:
        """Create crypto price record."""
        price_record = CryptoPrice(
            symbol=symbol,
            price=price,
            source=source,
            timestamp=timestamp
        )
        self.session.add(price_record)
        self.session.commit()
        self.session.refresh(price_record)
        return price_record
    
    def get_latest_price(self, symbol: str) -> CryptoPrice | None:
        """Get latest price for symbol."""
        return (
            self.session.query(CryptoPrice)
            .filter(CryptoPrice.symbol == symbol)
            .order_by(CryptoPrice.timestamp.desc())
            .first()
        )


# ==========================================
# API CLIENT (Using httpx)
# ==========================================


class CryptoAPIClient:
    """
    Modern API client using httpx.
    
    httpx > requests karena:
    - Async support
    - HTTP/2 support
    - Better API design
    """
    
    def __init__(self, base_url: str = "https://api.coingecko.com"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=10.0)
    
    def get_price(self, symbol: str) -> dict:
        """Get crypto price."""
        url = f"{self.base_url}/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_multiple_prices(self, symbols: List[str]) -> dict:
        """Get multiple crypto prices."""
        symbols_str = ",".join(symbols)
        url = f"{self.base_url}/api/v3/simple/price?ids={symbols_str}&vs_currencies=usd"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    def close(self):
        """Close HTTP client."""
        self.client.close()


# ==========================================
# FIXTURES - Production-like Setup
# ==========================================


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture: SQLAlchemy session with in-memory database.
    
    Industry standard pattern:
    - In-memory SQLite untuk speed
    - Transaction rollback untuk isolation
    - Proper session management
    """
    # Create engine
    engine = create_engine("sqlite:///:memory:", echo=False)
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    engine.dispose()


@pytest.fixture
def user_repo(db_session):
    """Fixture: User repository."""
    return UserRepository(db_session)


@pytest.fixture
def crypto_repo(db_session):
    """Fixture: Crypto price repository."""
    return CryptoPriceRepository(db_session)


@pytest.fixture
def sample_users():
    """Fixture: Sample user data."""
    return [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Alice Smith", "email": "alice@example.com"},
        {"name": "Bob Johnson", "email": "bob@example.com"},
    ]


# ==========================================
# TESTS - HTTP Mocking dengan pytest-httpx
# ==========================================


def test_fetch_crypto_price_with_httpx_mock(httpx_mock: HTTPXMock):
    """
    Test HTTP dengan pytest-httpx (better for httpx client).
    
    pytest-httpx > responses karena:
    - Native support for httpx
    - Cleaner API
    - Better async support
    """
    # Setup mock response
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        json={"bitcoin": {"usd": 50000}},
        status_code=200
    )
    
    # Execute
    client = CryptoAPIClient()
    result = client.get_price("bitcoin")
    client.close()
    
    # Verify
    assert result == {"bitcoin": {"usd": 50000}}


def test_fetch_multiple_crypto_prices(httpx_mock: HTTPXMock):
    """Test fetching multiple prices."""
    # Setup
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
        json={
            "bitcoin": {"usd": 50000},
            "ethereum": {"usd": 3000}
        },
        status_code=200
    )
    
    # Execute
    client = CryptoAPIClient()
    result = client.get_multiple_prices(["bitcoin", "ethereum"])
    client.close()
    
    # Verify
    assert result["bitcoin"]["usd"] == 50000
    assert result["ethereum"]["usd"] == 3000


def test_api_error_handling(httpx_mock: HTTPXMock):
    """Test API error handling."""
    # Setup error response
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        json={"error": "Service unavailable"},
        status_code=503
    )
    
    # Execute & Verify
    client = CryptoAPIClient()
    
    with pytest.raises(httpx.HTTPStatusError):
        client.get_price("bitcoin")
    
    client.close()


def test_api_timeout_simulation(httpx_mock: HTTPXMock):
    """Test timeout handling."""
    # Setup timeout
    httpx_mock.add_exception(
        httpx.TimeoutException("Connection timeout"),
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    )
    
    client = CryptoAPIClient()
    
    with pytest.raises(httpx.TimeoutException):
        client.get_price("bitcoin")
    
    client.close()


# ==========================================
# TESTS - SQLAlchemy ORM Operations
# ==========================================


def test_create_user(user_repo):
    """Test creating user dengan SQLAlchemy."""
    user = user_repo.create(name="John Doe", email="john@example.com")
    
    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
    assert user.created_at is not None


def test_get_user_by_id(user_repo):
    """Test retrieving user by ID."""
    # Create user
    created = user_repo.create(name="Alice", email="alice@example.com")
    
    # Retrieve
    user = user_repo.get_by_id(created.id)
    
    assert user is not None
    assert user.name == "Alice"


def test_get_all_users(user_repo, sample_users):
    """Test getting all users."""
    # Create multiple users
    user_repo.bulk_create(sample_users)
    
    # Retrieve all
    users = user_repo.get_all()
    
    assert len(users) == 3
    assert users[0].name == "John Doe"


def test_bulk_create_users(user_repo, sample_users):
    """Test bulk create operation."""
    count = user_repo.bulk_create(sample_users)
    
    assert count == 3
    
    # Verify in database
    all_users = user_repo.get_all()
    assert len(all_users) == 3


def test_unique_email_constraint(user_repo):
    """Test unique constraint on email."""
    user_repo.create(name="John", email="john@example.com")
    
    # Try duplicate email
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        user_repo.create(name="Jane", email="john@example.com")


def test_crypto_price_operations(crypto_repo):
    """Test crypto price CRUD operations."""
    # Create
    price = crypto_repo.create(
        symbol="BTC",
        price=50000.0,
        source="coingecko",
        timestamp=datetime(2024, 1, 15, 12, 0, 0)
    )
    
    assert price.id is not None
    assert price.symbol == "BTC"
    
    # Retrieve latest
    latest = crypto_repo.get_latest_price("BTC")
    assert latest.price == 50000.0


def test_get_latest_price_multiple_records(crypto_repo):
    """Test getting latest price when multiple exist."""
    # Create multiple prices
    crypto_repo.create("BTC", 49000.0, "coingecko", datetime(2024, 1, 15, 10, 0, 0))
    crypto_repo.create("BTC", 50000.0, "coingecko", datetime(2024, 1, 15, 11, 0, 0))
    crypto_repo.create("BTC", 51000.0, "coingecko", datetime(2024, 1, 15, 12, 0, 0))
    
    # Get latest
    latest = crypto_repo.get_latest_price("BTC")
    
    assert latest.price == 51000.0
    assert latest.timestamp == datetime(2024, 1, 15, 12, 0, 0)


# ==========================================
# TESTS - Integration: API + Database
# ==========================================


def test_api_to_database_flow(httpx_mock: HTTPXMock, crypto_repo):
    """
    Integration test: Fetch dari API, save ke database.
    
    Industry pattern: API → Transform → Database
    """
    # Setup API mock
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        json={"bitcoin": {"usd": 50000}},
        status_code=200
    )
    
    # Step 1: Fetch from API
    client = CryptoAPIClient()
    api_data = client.get_price("bitcoin")
    client.close()
    
    # Step 2: Transform
    price = api_data["bitcoin"]["usd"]
    
    # Step 3: Save to database
    record = crypto_repo.create(
        symbol="BTC",
        price=price,
        source="coingecko",
        timestamp=datetime.utcnow()
    )
    
    # Step 4: Verify
    assert record.price == 50000
    
    latest = crypto_repo.get_latest_price("BTC")
    assert latest.price == 50000


def test_bulk_api_fetch_and_load(httpx_mock: HTTPXMock, crypto_repo):
    """Test fetching multiple prices and bulk loading."""
    # Setup
    httpx_mock.add_response(
        url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd",
        json={
            "bitcoin": {"usd": 50000},
            "ethereum": {"usd": 3000},
            "solana": {"usd": 150}
        },
        status_code=200
    )
    
    # Fetch
    client = CryptoAPIClient()
    prices = client.get_multiple_prices(["bitcoin", "ethereum", "solana"])
    client.close()
    
    # Load to database
    for crypto, data in prices.items():
        crypto_repo.create(
            symbol=crypto.upper()[:3],
            price=data["usd"],
            source="coingecko",
            timestamp=datetime.utcnow()
        )
    
    # Verify
    btc = crypto_repo.get_latest_price("BIT")
    eth = crypto_repo.get_latest_price("ETH")
    sol = crypto_repo.get_latest_price("SOL")
    
    assert btc.price == 50000
    assert eth.price == 3000
    assert sol.price == 150


# ==========================================
# TESTS - Context Managers & Resource Management
# ==========================================


def test_database_session_isolation(db_session):
    """
    Test session isolation.
    
    Each test gets fresh database = no side effects.
    """
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    count = db_session.query(User).count()
    assert count == 1


def test_database_session_isolation_second_test(db_session):
    """
    This test should NOT see data from previous test.
    
    Proves isolation works.
    """
    count = db_session.query(User).count()
    assert count == 0  # Fresh database!


# ==========================================
# BEST PRACTICES
# ==========================================


def test_industry_patterns_summary():
    """
    🏭 INDUSTRY PATTERNS LEARNED:

    1. SQLALCHEMY ORM
       ✅ Declarative models (Base)
       ✅ Repository pattern for data access
       ✅ Session management
       ✅ Query API (type-safe)

    2. HTTPX CLIENT
       ✅ Modern HTTP client
       ✅ Async support (bila perlu)
       ✅ HTTP/2 support
       ✅ Better timeout handling

    3. RESPONSES LIBRARY
       ✅ Cleaner HTTP mocking
       ✅ Declarative response setup
       ✅ Automatic URL matching
       ✅ Less boilerplate vs unittest.mock

    4. REPOSITORY PATTERN
       ✅ Abstraction over database
       ✅ Testable (can mock repository)
       ✅ Single responsibility
       ✅ Easy to swap implementations

    5. FIXTURES & DEPENDENCY INJECTION
       ✅ Pytest fixtures = DI container
       ✅ Scope control (function, session)
       ✅ Automatic cleanup
       ✅ Reusable across tests

    PRODUCTION CHECKLIST:
    [✅] Use ORM (SQLAlchemy) bukan raw SQL
    [✅] Repository pattern untuk data access
    [✅] Modern HTTP client (httpx)
    [✅] Clean mocking (responses)
    [✅] Proper resource management
    [✅] Session isolation per test
    [✅] Type hints everywhere

    VS OLD APPROACH:
    ❌ unittest.mock -> ✅ responses library
    ❌ sqlite3 raw -> ✅ SQLAlchemy ORM
    ❌ requests -> ✅ httpx
    ❌ Manual cleanup -> ✅ Fixtures handle it
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 2-mocking-basics.py -v")
    print("\n🏭 Industry patterns:")
    print("   - SQLAlchemy ORM untuk database")
    print("   - httpx untuk HTTP client")
    print("   - responses untuk HTTP mocking")
    print("   - Repository pattern untuk data access")
