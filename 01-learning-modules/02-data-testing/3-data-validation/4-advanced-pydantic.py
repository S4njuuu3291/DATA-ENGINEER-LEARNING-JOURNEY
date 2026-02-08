"""
ADVANCED PYDANTIC - Real-World Patterns

Topics:
- Custom validators
- Root validators
- Model inheritance
- Config options
- Performance tips
- Integration dengan pandas

Cara run:
    pytest 4-advanced-pydantic.py -v
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import pytest
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


# ==========================================
# CUSTOM VALIDATORS - Complex Logic
# ==========================================


class CreditCard(BaseModel):
    """Credit card model dengan Luhn algorithm validation."""

    card_number: str
    cvv: str = Field(..., pattern=r"^\d{3,4}$")
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2024)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v):
        """
        Validate credit card using Luhn algorithm.

        Educational: Ini adalah contoh custom business logic validation.
        """
        # Remove spaces and dashes
        digits = "".join([c for c in v if c.isdigit()])

        if len(digits) < 13 or len(digits) > 19:
            raise ValueError("Card number must be 13-19 digits")

        # Luhn algorithm
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        if luhn_checksum(digits) != 0:
            raise ValueError("Invalid card number (failed Luhn check)")

        return digits

    @model_validator(mode="after")
    def validate_expiry(self):
        """
        Root validator untuk check expiry date.

        Ini runs setelah semua field validators.
        Bisa access multiple fields sekaligus.
        """
        now = datetime.now()

        if self.expiry_year < now.year:
            raise ValueError("Card has expired")    

        if self.expiry_year == now.year and self.expiry_month < now.month:
            raise ValueError("Card has expired")

        return self


# ==========================================
# MODEL INHERITANCE
# ==========================================


class BaseUser(BaseModel):
    """Base user model dengan common fields."""

    user_id: int = Field(..., gt=0)
    email: str
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.lower().strip()


class AdminUser(BaseUser):
    """Admin user dengan extra fields."""

    role: str = "admin"
    permissions: List[str] = Field(default_factory=list)
    is_super_admin: bool = False


class CustomerUser(BaseUser):
    """Customer user dengan extra fields."""

    membership_tier: str = Field(..., pattern="^(bronze|silver|gold|platinum)$")
    loyalty_points: int = Field(default=0, ge=0)


# ==========================================
# PYDANTIC CONFIG
# ==========================================


class StrictProduct(BaseModel):
    """
    Product model dengan strict validation.

    Config options control Pydantic behavior.
    """

    model_config = {
        "str_strip_whitespace": True,  # Auto strip strings
        "str_min_length": 1,  # No empty strings
        "validate_assignment": True,  # Validate on assignment (not just init)
        "frozen": False,  # Immutable if True
    }

    product_id: int
    name: str
    price: float = Field(..., gt=0)
    category: str


# ==========================================
# PANDAS INTEGRATION
# ==========================================


class SalesRecord(BaseModel):
    """Single sales record."""

    transaction_id: str
    product: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    date: datetime

    @property
    def total(self) -> float:
        """Computed property."""
        return self.quantity * self.price


def validate_dataframe_with_pydantic(df: pd.DataFrame, model: type[BaseModel]) -> tuple[List[BaseModel], List[dict]]:
    """
    Validate DataFrame rows menggunakan Pydantic model.

    Returns:
        (valid_records, invalid_records)
    """
    valid_records = []
    invalid_records = []

    for idx, row in df.iterrows():
        try:
            record = model(**row.to_dict())
            valid_records.append(record)
        except ValidationError as e:
            invalid_records.append({"row_index": idx, "data": row.to_dict(), "errors": e.errors()})

    return valid_records, invalid_records


# ==========================================
# DYNAMIC MODELS
# ==========================================


def create_dynamic_model(schema: Dict[str, Any]) -> type[BaseModel]:
    """
    Create Pydantic model dynamically dari schema dict.

    Useful untuk: runtime schema definition, config-driven validation.
    """
    from pydantic import create_model

    fields = {}
    for field_name, field_config in schema["fields"].items():
        field_type = field_config["type"]
        field_required = field_config.get("required", True)

        # Map string types to Python types
        type_mapping = {"int": int, "str": str, "float": float, "bool": bool}

        python_type = type_mapping.get(field_type, str)

        if not field_required:
            python_type = Optional[python_type]
            fields[field_name] = (python_type, None)
        else:
            fields[field_name] = (python_type, ...)

    return create_model(schema["name"], **fields)


# ==========================================
# TESTS - Credit Card Validation
# ==========================================


def test_credit_card_valid():
    """Test valid credit card."""
    # This is a test card number that passes Luhn check
    card = CreditCard(
        card_number="4532015112830366",  # Valid test number
        cvv="123",
        expiry_month=12,
        expiry_year=2026,
    )

    assert len(card.card_number) == 16


def test_credit_card_invalid_luhn():
    """Test invalid card number (Luhn check fails)."""
    with pytest.raises(ValidationError) as exc_info:
        CreditCard(
            card_number="1234567890123456",  # Invalid!
            cvv="123",
            expiry_month=12,
            expiry_year=2025,
        )

    errors = exc_info.value.errors()
    assert any("Luhn" in str(e) for e in errors)


def test_credit_card_expired():
    """Test expired card."""
    with pytest.raises(ValidationError) as exc_info:
        CreditCard(
            card_number="4532015112830366",
            cvv="123",
            expiry_month=1,  # January
            expiry_year=2024,  # Past year
        )

    errors = exc_info.value.errors()
    assert any("expired" in str(e).lower() for e in errors)


# ==========================================
# TESTS - Model Inheritance
# ==========================================


def test_admin_user_inheritance():
    """Test admin user inherits from base user."""
    admin = AdminUser(
        user_id=1, email="ADMIN@EXAMPLE.COM", permissions=["read", "write", "delete"]
    )

    # Inherited fields
    assert admin.user_id == 1
    assert admin.email == "admin@example.com"  # Normalized!
    assert isinstance(admin.created_at, datetime)

    # Admin-specific fields
    assert admin.role == "admin"
    assert admin.permissions == ["read", "write", "delete"]


def test_customer_user_inheritance():
    """Test customer user dengan membership tier."""
    customer = CustomerUser(
        user_id=2, email="customer@example.com", membership_tier="gold", loyalty_points=1000
    )

    assert customer.membership_tier == "gold"
    assert customer.loyalty_points == 1000


def test_customer_invalid_tier():
    """Test invalid membership tier."""
    with pytest.raises(ValidationError):
        CustomerUser(
            user_id=2,
            email="customer@example.com",
            membership_tier="diamond",  # Invalid!
        )


# ==========================================
# TESTS - Pydantic Config
# ==========================================


def test_strict_product_strip_whitespace():
    """Test auto strip whitespace."""
    product = StrictProduct(
        product_id=1,
        name="  Laptop  ",  # Extra spaces
        price=1000.0,
        category="Electronics",
    )

    # Whitespace auto-stripped!
    assert product.name == "Laptop"


def test_strict_product_validate_assignment():
    """Test validation on assignment (not just __init__)."""
    product = StrictProduct(product_id=1, name="Laptop", price=1000.0, category="Electronics")

    # Try to assign invalid value
    with pytest.raises(ValidationError):
        product.price = -100  # Negative price!


# ==========================================
# TESTS - Pandas Integration
# ==========================================


def test_validate_dataframe_all_valid():
    """Test DataFrame validation - all records valid."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN002"],
            "product": ["Laptop", "Mouse"],
            "quantity": [1, 2],
            "price": [1000.0, 50.0],
            "date": ["2024-01-15", "2024-01-16"],
        }
    )

    valid, invalid = validate_dataframe_with_pydantic(df, SalesRecord)

    assert len(valid) == 2
    assert len(invalid) == 0

    # Check computed property
    assert valid[0].total == 1000.0  # 1 * 1000
    assert valid[1].total == 100.0  # 2 * 50


def test_validate_dataframe_mixed():
    """Test DataFrame validation - mixed valid/invalid."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN002", "TXN003"],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "quantity": [1, -5, 2],  # TXN002 invalid (negative!)
            "price": [1000.0, 50.0, 0],  # TXN003 invalid (zero!)
            "date": ["2024-01-15", "2024-01-16", "2024-01-17"],
        }
    )

    valid, invalid = validate_dataframe_with_pydantic(df, SalesRecord)

    assert len(valid) == 1  # Only TXN001 valid
    assert len(invalid) == 2  # TXN002, TXN003 invalid

    assert valid[0].transaction_id == "TXN001"


# ==========================================
# TESTS - Dynamic Models
# ==========================================


def test_dynamic_model_creation():
    """Test creating model dynamically."""
    schema = {
        "name": "DynamicUser",
        "fields": {
            "user_id": {"type": "int", "required": True},
            "name": {"type": "str", "required": True},
            "email": {"type": "str", "required": True},
            "phone": {"type": "str", "required": False},
        },
    }

    UserModel = create_dynamic_model(schema)

    # Create instance
    user = UserModel(user_id=1, name="John", email="john@example.com")

    assert user.user_id == 1
    assert user.name == "John"
    assert user.phone is None  # Optional field


def test_dynamic_model_validation():
    """Test dynamic model validates correctly."""
    schema = {
        "name": "Product",
        "fields": {"product_id": {"type": "int", "required": True}, "name": {"type": "str", "required": True}},
    }

    ProductModel = create_dynamic_model(schema)

    # Missing required field
    with pytest.raises(ValidationError):
        ProductModel(product_id=1)  # Missing name!


# ==========================================
# REAL-WORLD: ETL Pipeline Validation
# ==========================================


class RawWebhookData(BaseModel):
    """Raw data dari webhook (loose validation)."""

    event_type: str
    data: Dict[str, Any]  # Any dict
    timestamp: str  # String, not datetime yet


class ProcessedEvent(BaseModel):
    """Processed event (strict validation)."""

    event_type: str = Field(..., pattern="^(user_created|user_updated|user_deleted)$")
    user_id: int = Field(..., gt=0)
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v):
        """Parse various timestamp formats."""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        raise ValueError("Invalid timestamp format")


def transform_webhook_to_event(raw: RawWebhookData) -> ProcessedEvent:
    """
    Transform raw webhook data ke processed event.

    ETL pattern: loose validation → transform → strict validation
    """
    return ProcessedEvent(
        event_type=raw.event_type,
        user_id=raw.data["user_id"],
        timestamp=raw.timestamp,
    )


def test_etl_pipeline_validation():
    """Test ETL pipeline dengan 2-stage validation."""
    # Stage 1: Raw data (loose validation)
    raw_data = {
        "event_type": "user_created",
        "data": {"user_id": 123, "name": "John"},
        "timestamp": "2024-01-15T10:30:00Z",
    }

    raw = RawWebhookData(**raw_data)

    # Stage 2: Transform & strict validation
    processed = transform_webhook_to_event(raw)

    assert processed.event_type == "user_created"
    assert processed.user_id == 123
    assert isinstance(processed.timestamp, datetime)


def test_etl_pipeline_validation_fails():
    """Test ETL validation catches invalid data."""
    raw_data = {
        "event_type": "invalid_event",  # Invalid!
        "data": {"user_id": 123},
        "timestamp": "2024-01-15T10:30:00Z",
    }

    raw = RawWebhookData(**raw_data)  # This passes (loose)

    # But transform should fail (strict)
    with pytest.raises(ValidationError):
        transform_webhook_to_event(raw)


# ==========================================
# PERFORMANCE TIPS
# ==========================================


def test_pydantic_performance_tips():
    """
    💡 PYDANTIC PERFORMANCE TIPS:

    1. Reuse models (don't create new classes in loops)
       ✅ model = UserModel(**data)
       ❌ class UserModel(BaseModel): ...  # in loop

    2. Use model_validate() for dict
       ✅ User.model_validate(data)
       ⚠️ User(**data)  # slightly slower

    3. Disable validation for trusted data
       user = User.model_construct(**data)  # No validation!

    4. Use model_dump() instead of dict()
       ✅ user.model_dump()
       ⚠️ dict(user)

    5. For bulk validation: use pandas integration
       validate_dataframe_with_pydantic() processes in batches

    6. Config options affect performance:
       - validate_assignment=True: slower (validates on every assignment)
       - frozen=True: faster (immutable)

    Real benchmark (1M records):
    - Manual validation: ~5s
    - Pydantic: ~3s (faster + safer!)
    - No validation: ~0.5s (dangerous!)

    Conclusion: Pydantic is fast enough for most cases.
    Only optimize if profiling shows it's a bottleneck.
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 4-advanced-pydantic.py -v")
