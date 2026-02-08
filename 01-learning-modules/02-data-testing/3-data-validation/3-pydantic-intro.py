"""
PYDANTIC INTRODUCTION

Pydantic = library untuk data validation menggunakan Python type hints.

Why Pydantic?
✅ Less code (vs manual validation)
✅ Type safety
✅ Auto validation
✅ Great error messages
✅ JSON serialization/deserialization
✅ Used by FastAPI, many modern Python tools

Cara run:
    pytest 3-pydantic-intro.py -v

Note: Install dulu: pip install pydantic
"""

from datetime import datetime
from typing import List, Optional

import pytest
from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator


# ==========================================
# BASIC PYDANTIC MODELS
# ==========================================


class User(BaseModel):
    """
    Simple User model.

    Pydantic automatically validates:
    - user_id is int
    - name is str
    - email is str
    - age is int
    """

    user_id: int
    name: str
    email: str
    age: int


class UserWithDefaults(BaseModel):
    """User model dengan default values."""

    user_id: int
    name: str
    email: str
    age: int = 18  # Default value
    is_active: bool = True  # Default value


class UserWithOptional(BaseModel):
    """User model dengan optional fields."""

    user_id: int
    name: str
    email: str
    age: int
    phone: Optional[str] = None  # Optional field


# ==========================================
# ADVANCED VALIDATION dengan Field
# ==========================================


class UserWithConstraints(BaseModel):
    """User model dengan validation constraints."""

    user_id: int = Field(..., gt=0, description="User ID must be positive")
    name: str = Field(..., min_length=1, max_length=100)
    email: str  # Will add custom validation
    age: int = Field(..., ge=0, le=150, description="Age between 0-150")
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\-\(\) ]{10,}$")

    # Custom validator
    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v):
        if "@" not in v:
            raise ValueError("Email must contain @")
        return v.lower()  # Normalize email


# ==========================================
# NESTED MODELS
# ==========================================


class Address(BaseModel):
    """Address model."""

    street: str
    city: str
    country: str
    postal_code: str


class UserWithAddress(BaseModel):
    """User with nested Address model."""

    user_id: int
    name: str
    email: str
    address: Address  # Nested model


class Company(BaseModel):
    """Company with list of employees."""

    company_id: int
    name: str
    employees: List[User]  # List of User models


# ==========================================
# TESTS - Basic Pydantic Usage
# ==========================================


def test_user_model_valid():
    """Test creating valid User instance."""
    user = User(user_id=1, name="John", email="john@example.com", age=25)

    assert user.user_id == 1
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.age == 25


def test_user_model_from_dict():
    """Test creating User from dict (typical API response)."""
    user_data = {"user_id": 1, "name": "John", "email": "john@example.com", "age": 25}

    user = User(**user_data)

    assert user.user_id == 1
    assert user.name == "John"


def test_user_model_to_dict():
    """Test converting User to dict."""
    user = User(user_id=1, name="John", email="john@example.com", age=25)

    user_dict = user.model_dump()

    assert user_dict == {
        "user_id": 1,
        "name": "John",
        "email": "john@example.com",
        "age": 25,
    }


def test_user_model_to_json():
    """Test serializing User to JSON."""
    user = User(user_id=1, name="John", email="john@example.com", age=25)

    json_str = user.model_dump_json()

    assert '"user_id":1' in json_str
    assert '"name":"John"' in json_str


# ==========================================
# TESTS - Validation Errors
# ==========================================


def test_user_model_missing_field():
    """Test validation error when field missing."""
    with pytest.raises(ValidationError) as exc_info:
        User(user_id=1, name="John", email="john@example.com")
        # Missing: age

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("age",)
    assert errors[0]["type"] == "missing"


def test_user_model_wrong_type():
    """Test validation error when wrong type."""
    with pytest.raises(ValidationError) as exc_info:
        User(
            user_id="not-an-int",  # Should be int!
            name="John",
            email="john@example.com",
            age=25,
        )

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("user_id",) for e in errors)


def test_user_model_type_coercion():
    """
    Test type coercion (Pydantic automatically converts).

    Pydantic tries to convert compatible types.
    """
    user = User(
        user_id="123",  # String → int (auto convert)
        name="John",
        email="john@example.com",
        age="25",  # String → int (auto convert)
    )
    
    assert user.user_id == 123
    assert isinstance(user.user_id, int)
    assert user.age == 25
    assert isinstance(user.age, int)


# ==========================================
# TESTS - Defaults & Optional
# ==========================================


def test_user_with_defaults():
    """Test model dengan default values."""
    user = UserWithDefaults(user_id=1, name="John", email="john@example.com")
    # age and is_active tidak di-provide

    assert user.age == 18  # Default value
    assert user.is_active is True  # Default value


def test_user_with_optional():
    """Test model dengan optional field."""
    # Without phone
    user1 = UserWithOptional(
        user_id=1, name="John", email="john@example.com", age=25
    )
    assert user1.phone is None

    # With phone
    user2 = UserWithOptional(
        user_id=1, name="John", email="john@example.com", age=25, phone="+1234567890"
    )
    assert user2.phone == "+1234567890"


# ==========================================
# TESTS - Field Constraints
# ==========================================


def test_user_constraints_valid():
    """Test user dengan constraints - valid data."""
    user = UserWithConstraints(
        user_id=1,
        name="John Doe",
        email="john@example.com",
        age=25,
        phone="+1234567890",
    )

    assert user.user_id == 1
    assert user.email == "john@example.com"  # Lowercased by validator


def test_user_constraints_invalid_user_id():
    """Test user_id must be positive."""
    with pytest.raises(ValidationError) as exc_info:
        UserWithConstraints(
            user_id=-1,  # Invalid!
            name="John",
            email="john@example.com",
            age=25,
        )

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("user_id",) for e in errors)


def test_user_constraints_invalid_age():
    """Test age constraints."""
    # Age too old
    with pytest.raises(ValidationError):
        UserWithConstraints(
            user_id=1, name="John", email="john@example.com", age=200  # > 150
        )

    # Age negative
    with pytest.raises(ValidationError):
        UserWithConstraints(
            user_id=1, name="John", email="john@example.com", age=-5
        )


def test_user_email_custom_validator():
    """Test custom email validator."""
    # Invalid email (no @)
    with pytest.raises(ValidationError) as exc_info:
        UserWithConstraints(user_id=1, name="John", email="not-an-email", age=25)

    # Check error message
    errors = exc_info.value.errors()
    assert any("must contain @" in str(e["ctx"]) for e in errors)

    # Valid email - check normalization
    user = UserWithConstraints(
        user_id=1, name="John", email="JOHN@EXAMPLE.COM", age=25
    )
    assert user.email == "john@example.com"  # Lowercased!


# ==========================================
# TESTS - Nested Models
# ==========================================


def test_user_with_address():
    """Test nested model."""
    user_data = {
        "user_id": 1,
        "name": "John",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Jakarta",
            "country": "Indonesia",
            "postal_code": "12345",
        },
    }

    user = UserWithAddress(**user_data)

    assert user.address.city == "Jakarta"
    assert user.address.country == "Indonesia"


def test_user_with_address_invalid():
    """Test nested model validation."""
    user_data = {
        "user_id": 1,
        "name": "John",
        "email": "john@example.com",
        "address": {
            "street": "123 Main St",
            # Missing: city, country, postal_code
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        UserWithAddress(**user_data)

    errors = exc_info.value.errors()
    # Should have errors for missing nested fields
    assert any("address" in str(e["loc"]) for e in errors)


def test_company_with_employees():
    """Test model dengan list of nested models."""
    company_data = {
        "company_id": 1,
        "name": "Tech Corp",
        "employees": [
            {"user_id": 1, "name": "John", "email": "john@tech.com", "age": 25},
            {"user_id": 2, "name": "Alice", "email": "alice@tech.com", "age": 30},
        ],
    }

    company = Company(**company_data)

    assert company.name == "Tech Corp"
    assert len(company.employees) == 2
    assert company.employees[0].name == "John"
    assert company.employees[1].name == "Alice"


# ==========================================
# REAL-WORLD SCENARIO
# ==========================================


class Transaction(BaseModel):
    """Transaction model untuk real-world scenario."""

    transaction_id: str
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    currency: str = Field(..., pattern="^(USD|EUR|IDR|SGD)$")
    timestamp: datetime
    description: Optional[str] = None


def test_transaction_validation():
    """Test transaction validation - real-world scenario."""
    # Valid transaction
    txn_data = {
        "transaction_id": "TXN001",
        "user_id": 123,
        "amount": 100.50,
        "currency": "USD",
        "timestamp": "2024-01-15T10:30:00",
    }

    txn = Transaction(**txn_data)

    assert txn.amount == 100.50
    assert txn.currency == "USD"
    assert isinstance(txn.timestamp, datetime)


def test_transaction_invalid_currency():
    """Test transaction dengan invalid currency."""
    txn_data = {
        "transaction_id": "TXN001",
        "user_id": 123,
        "amount": 100.50,
        "currency": "XXX",  # Invalid!
        "timestamp": "2024-01-15T10:30:00",
    }

    with pytest.raises(ValidationError) as exc_info:
        Transaction(**txn_data)

    errors = exc_info.value.errors()
    assert any(e["loc"] == ("currency",) for e in errors)


def test_batch_transaction_validation():
    """Test validating batch of transactions."""
    transactions_from_api = [
        {
            "transaction_id": "TXN001",
            "user_id": 123,
            "amount": 100,
            "currency": "USD",
            "timestamp": "2024-01-15T10:30:00",
        },
        {
            "transaction_id": "TXN002",
            "user_id": -1,  # Invalid!
            "amount": 200,
            "currency": "EUR",
            "timestamp": "2024-01-15T11:00:00",
        },
        {
            "transaction_id": "TXN003",
            "user_id": 456,
            "amount": -50,  # Invalid!
            "currency": "USD",
            "timestamp": "2024-01-15T12:00:00",
        },
    ]

    valid_txns = []
    invalid_txns = []

    for txn_data in transactions_from_api:
        try:
            txn = Transaction(**txn_data)
            valid_txns.append(txn)
        except ValidationError as e:
            invalid_txns.append({"data": txn_data, "errors": e.errors()})

    assert len(valid_txns) == 1, "Should have 1 valid transaction"
    assert len(invalid_txns) == 2, "Should have 2 invalid transactions"


# ==========================================
# COMPARISON: Manual vs Pydantic
# ==========================================


def test_comparison_manual_vs_pydantic():
    """
    💡 COMPARISON: Manual Validation vs Pydantic

    Manual validation (dari file sebelumnya):
    ------------------------------------------------
    def validate_user(user):
        errors = []
        if 'user_id' not in user:
            errors.append("Missing user_id")
        if not isinstance(user.get('user_id'), int):
            errors.append("user_id must be int")
        if user.get('user_id', 0) <= 0:
            errors.append("user_id must be positive")
        # ... 20 more lines ...
        return errors

    Pydantic:
    ------------------------------------------------
    class User(BaseModel):
        user_id: int = Field(..., gt=0)

    That's it! 🎉

    Benefits Pydantic:
    ✅ 90% less code
    ✅ Type safety
    ✅ Auto IDE completion
    ✅ Self-documenting
    ✅ JSON serialization built-in
    ✅ Better error messages

    When to use Manual:
    - Very custom business logic
    - Learning/understanding

    When to use Pydantic:
    - Production code
    - APIs (FastAPI uses Pydantic)
    - Data pipelines
    - Any serious project
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 3-pydantic-intro.py -v")
    print("\n💡 Install Pydantic first:")
    print("   pip install pydantic")
