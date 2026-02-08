"""
PYDANTIC MODELS - Type-Safe Data Validation

Topics:
- Pydantic BaseModel basics
- Field validation
- Custom validators
- Nested models
- JSON schema generation
- Error handling

Why Pydantic?
- ✅ Runtime validation
- ✅ Type safety
- ✅ Auto JSON serialization
- ✅ IDE autocomplete
- ✅ Clear error messages

Cara run:
    python 2-pydantic-models.py
    pytest 2-pydantic-models.py -v
"""

from pydantic import BaseModel, Field, validator, root_validator, ValidationError
from typing import List, Optional, Dict
from datetime import datetime, date
from decimal import Decimal
import pytest

# ==========================================
# BASIC PYDANTIC MODELS
# ==========================================

class User(BaseModel):
    """Basic user model dengan validation."""
    
    id: int
    name: str
    email: str
    age: int = Field(ge=0, le=150)  # Greater than or equal, less than or equal
    score: float = Field(ge=0.0, le=100.0)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class Address(BaseModel):
    """Address model."""
    street: str
    city: str
    country: str = "Indonesia"
    postal_code: Optional[str] = None


class UserWithAddress(BaseModel):
    """Nested model example."""
    id: int
    name: str
    email: str
    address: Address  # Nested model


# ==========================================
# CUSTOM VALIDATORS
# ==========================================

class ValidatedUser(BaseModel):
    """User dengan custom validation."""
    
    id: int
    name: str
    email: str
    password: str
    confirm_password: str
    age: int
    score: float
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v:
            raise ValueError('Email harus contain @')
        if '.' not in v.split('@')[1]:
            raise ValueError('Email harus valid domain')
        return v.lower()  # Normalize to lowercase
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        if not any(c.isupper() for c in v):
            raise ValueError('Password harus contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password harus contain angka')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate and clean name."""
        # Remove extra whitespace
        v = ' '.join(v.split())
        if len(v) < 2:
            raise ValueError('Name terlalu pendek')
        return v.title()  # Capitalize each word
    
    @root_validator
    def check_passwords_match(cls, values):
        """Validate password confirmation."""
        pw = values.get('password')
        confirm_pw = values.get('confirm_password')
        
        if pw != confirm_pw:
            raise ValueError('Password tidak match')
        
        return values


# ==========================================
# DATA ENGINEERING MODELS
# ==========================================

class CryptoPrice(BaseModel):
    """Crypto price record."""
    
    symbol: str = Field(..., min_length=3, max_length=10)
    price: Decimal = Field(..., gt=0)  # Must be > 0
    volume_24h: Decimal = Field(default=Decimal('0'))
    market_cap: Optional[Decimal] = None
    timestamp: datetime
    source: str = Field(default="api")
    
    @validator('symbol')
    def uppercase_symbol(cls, v):
        """Normalize symbol to uppercase."""
        return v.upper()
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Ensure timestamp not in future."""
        if v > datetime.now():
            raise ValueError('Timestamp tidak boleh di masa depan')
        return v
    
    class Config:
        json_encoders = {
            Decimal: str,  # Convert Decimal to string for JSON
            datetime: lambda v: v.isoformat()
        }


class ETLConfig(BaseModel):
    """ETL pipeline configuration."""
    
    # API Config
    api_url: str = Field(..., regex=r'^https?://')  # Must be http/https
    api_key: str = Field(..., min_length=10)
    api_timeout: int = Field(default=30, ge=1, le=300)
    
    # Database Config
    database_url: str
    db_pool_size: int = Field(default=5, ge=1, le=50)
    
    # Processing Config
    batch_size: int = Field(default=100, ge=1, le=10000)
    max_retries: int = Field(default=3, ge=0, le=10)
    enable_caching: bool = False
    
    # Paths
    data_dir: str = "/tmp/data"
    log_level: str = Field(default="INFO", regex=r'^(DEBUG|INFO|WARNING|ERROR)$')
    
    @validator('database_url')
    def validate_db_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(('postgresql://', 'sqlite://', 'mysql://')):
            raise ValueError('Invalid database URL scheme')
        return v


class DataRecord(BaseModel):
    """Generic data record untuk ETL."""
    
    id: int
    data: Dict[str, any]
    processed_at: datetime = Field(default_factory=datetime.now)
    pipeline_version: str = "1.0.0"
    
    @validator('data')
    def validate_data_not_empty(cls, v):
        """Ensure data dict is not empty."""
        if not v:
            raise ValueError('Data cannot be empty')
        return v


# ==========================================
# ADVANCED: DYNAMIC MODELS
# ==========================================

class APIResponse(BaseModel):
    """Generic API response."""
    
    status: str = Field(..., regex=r'^(success|error)$')
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @root_validator
    def check_data_or_error(cls, values):
        """Either data or error must be present."""
        status = values.get('status')
        data = values.get('data')
        error = values.get('error')
        
        if status == 'success' and not data:
            raise ValueError('Success response harus punya data')
        
        if status == 'error' and not error:
            raise ValueError('Error response harus punya error message')
        
        return values


class PaginatedResponse(BaseModel):
    """Paginated API response."""
    
    data: List[Dict]
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    has_more: bool
    
    @root_validator
    def calculate_has_more(cls, values):
        """Auto-calculate has_more based on pagination."""
        page = values.get('page', 1)
        per_page = values.get('per_page', 10)
        total = values.get('total', 0)
        
        values['has_more'] = (page * per_page) < total
        return values


# ==========================================
# TESTING PYDANTIC MODELS
# ==========================================

class TestBasicModels:
    """Test basic Pydantic functionality."""
    
    def test_valid_user_creation(self):
        """Test creating valid user."""
        user = User(
            id=1,
            name="Alice",
            email="alice@example.com",
            age=30,
            score=95.5
        )
        
        assert user.id == 1
        assert user.name == "Alice"
        assert user.is_active is True
    
    def test_invalid_age(self):
        """Test age validation."""
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                name="Alice",
                email="alice@example.com",
                age=200,  # Invalid!
                score=95.5
            )
        
        assert 'age' in str(exc_info.value)
    
    def test_invalid_score(self):
        """Test score validation."""
        with pytest.raises(ValidationError):
            User(
                id=1,
                name="Alice",
                email="alice@example.com",
                age=30,
                score=150.0  # Invalid! Max is 100
            )
    
    def test_nested_model(self):
        """Test nested models."""
        user = UserWithAddress(
            id=1,
            name="Alice",
            email="alice@example.com",
            address=Address(
                street="Jl. Sudirman",
                city="Jakarta"
            )
        )
        
        assert user.address.city == "Jakarta"
        assert user.address.country == "Indonesia"  # Default value


class TestCustomValidators:
    """Test custom validators."""
    
    def test_email_validation(self):
        """Test email validator."""
        user = ValidatedUser(
            id=1,
            name="alice johnson",
            email="ALICE@EXAMPLE.COM",  # Should be lowercased
            password="Password123",
            confirm_password="Password123",
            age=30,
            score=95
        )
        
        assert user.email == "alice@example.com"
        assert user.name == "Alice Johnson"  # Title cased
    
    def test_invalid_email(self):
        """Test invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedUser(
                id=1,
                name="Alice",
                email="invalid_email",  # No @
                password="Password123",
                confirm_password="Password123",
                age=30,
                score=95
            )
        
        assert 'email' in str(exc_info.value)
    
    def test_password_validation(self):
        """Test password strength."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedUser(
                id=1,
                name="Alice",
                email="alice@example.com",
                password="weak",  # Too short, no uppercase, no digit
                confirm_password="weak",
                age=30,
                score=95
            )
        
        assert 'password' in str(exc_info.value).lower()
    
    def test_password_mismatch(self):
        """Test password confirmation."""
        with pytest.raises(ValidationError) as exc_info:
            ValidatedUser(
                id=1,
                name="Alice",
                email="alice@example.com",
                password="Password123",
                confirm_password="Different123",  # Doesn't match!
                age=30,
                score=95
            )
        
        assert 'match' in str(exc_info.value).lower()


class TestDataEngineeringModels:
    """Test DE-specific models."""
    
    def test_crypto_price(self):
        """Test crypto price model."""
        price = CryptoPrice(
            symbol="btc",  # Should be uppercased
            price=Decimal("50000.50"),
            volume_24h=Decimal("1000000"),
            timestamp=datetime.now()
        )
        
        assert price.symbol == "BTC"
        assert price.source == "api"
    
    def test_invalid_timestamp(self):
        """Test future timestamp validation."""
        with pytest.raises(ValidationError):
            CryptoPrice(
                symbol="BTC",
                price=Decimal("50000"),
                timestamp=datetime(2030, 1, 1)  # Future!
            )
    
    def test_etl_config(self):
        """Test ETL configuration."""
        config = ETLConfig(
            api_url="https://api.example.com",
            api_key="secret_key_123",
            database_url="postgresql://user:pass@localhost/db"
        )
        
        assert config.batch_size == 100  # Default
        assert config.api_timeout == 30  # Default
    
    def test_invalid_api_url(self):
        """Test API URL validation."""
        with pytest.raises(ValidationError):
            ETLConfig(
                api_url="ftp://invalid.com",  # Not http/https!
                api_key="secret_key_123",
                database_url="postgresql://user:pass@localhost/db"
            )


# ==========================================
# JSON SERIALIZATION
# ==========================================

def test_json_serialization():
    """Test converting to/from JSON."""
    user = User(
        id=1,
        name="Alice",
        email="alice@example.com",
        age=30,
        score=95.5
    )
    
    # To dict
    user_dict = user.dict()
    assert isinstance(user_dict, dict)
    assert user_dict['name'] == "Alice"
    
    # To JSON
    user_json = user.json()
    assert isinstance(user_json, str)
    assert '"name": "Alice"' in user_json
    
    # From dict
    user2 = User(**user_dict)
    assert user2.name == user.name
    
    # From JSON
    user3 = User.parse_raw(user_json)
    assert user3.name == user.name


def test_partial_updates():
    """Test updating specific fields."""
    user = User(
        id=1,
        name="Alice",
        email="alice@example.com",
        age=30,
        score=95.5
    )
    
    # Create updated user
    updated_user = user.copy(update={'score': 98.0, 'age': 31})
    
    assert updated_user.score == 98.0
    assert updated_user.age == 31
    assert updated_user.name == "Alice"  # Unchanged


# ==========================================
# REAL-WORLD USAGE
# ==========================================

def validate_api_response(raw_data: dict) -> APIResponse:
    """Validate API response data."""
    try:
        response = APIResponse(**raw_data)
        return response
    except ValidationError as e:
        print(f"Invalid API response: {e}")
        raise


def process_crypto_data(raw_records: List[dict]) -> List[CryptoPrice]:
    """Process and validate crypto price data."""
    validated_records = []
    errors = []
    
    for record in raw_records:
        try:
            price = CryptoPrice(**record)
            validated_records.append(price)
        except ValidationError as e:
            errors.append({
                'record': record,
                'error': str(e)
            })
    
    if errors:
        print(f"Found {len(errors)} validation errors")
        for error in errors:
            print(f"  - {error['record']}: {error['error']}")
    
    return validated_records


# ==========================================
# BEST PRACTICES
# ==========================================

"""
✅ PYDANTIC BEST PRACTICES:

1. USE FOR:
   - API request/response validation
   - Configuration management
   - Data pipeline input/output validation
   - Database model validation

2. FIELD DEFINITIONS:
   - Use Field() for constraints (min, max, regex)
   - Provide default values when appropriate
   - Use Optional[] for nullable fields
   - Add descriptions for documentation

3. VALIDATORS:
   - Use @validator for field-level validation
   - Use @root_validator for cross-field validation
   - Return cleaned/normalized values
   - Raise ValueError dengan clear messages

4. JSON HANDLING:
   - Use Config.json_encoders untuk custom types
   - Use .dict() untuk Python dict
   - Use .json() untuk JSON string
   - Use .parse_raw() untuk parse JSON

5. ERROR HANDLING:
   - Catch ValidationError
   - Log validation errors
   - Provide user-friendly error messages
   - Track failed records untuk debugging

❌ COMMON MISTAKES:

1. ❌ Over-validating (too strict)
2. ❌ Under-validating (too loose)
3. ❌ Not using Optional for nullable fields
4. ❌ Ignoring ValidationError
5. ❌ Not cleaning/normalizing data in validators

🎯 WHEN TO USE:

✅ Use Pydantic for:
- API integrations
- Config files
- Data validation pipelines
- Type-safe data containers

❌ Don't use for:
- Simple data containers (use dataclasses)
- Performance-critical paths (overhead)
- When you don't need validation

🔗 NEXT STEPS:

1. Learn pydantic-settings untuk config management
2. Integrate dengan FastAPI untuk APIs
3. Use dengan SQLModel untuk database models
4. Add to existing data pipelines
"""

if __name__ == "__main__":
    print("=" * 60)
    print("PYDANTIC MODELS EXAMPLES")
    print("=" * 60)
    
    # Example 1: Basic user
    print("\n1. Basic User:")
    user = User(id=1, name="Alice", email="alice@example.com", age=30, score=95.5)
    print(user.json(indent=2))
    
    # Example 2: Crypto price
    print("\n2. Crypto Price:")
    price = CryptoPrice(
        symbol="btc",
        price=Decimal("50000.50"),
        volume_24h=Decimal("1000000"),
        timestamp=datetime.now()
    )
    print(price.json(indent=2))
    
    # Example 3: ETL Config
    print("\n3. ETL Config:")
    config = ETLConfig(
        api_url="https://api.example.com",
        api_key="secret_key_12345",
        database_url="postgresql://user:pass@localhost/db",
        batch_size=500
    )
    print(config.json(indent=2))
    
    print("\n✅ All examples passed!")
    print("\nRun: pytest 2-pydantic-models.py -v")
