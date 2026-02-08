"""
SIMPLE VALIDATION - Manual Approach

Sebelum pakai library fancy, kita harus paham validasi manual.
Ini foundation yang penting!

Topics:
- Type checking
- Range validation
- Format validation
- Required fields
- Business rules

Cara run:
    pytest 2-simple-validation.py -v
"""

import re
from datetime import datetime
from typing import Any, Dict, List


# ==========================================
# VALIDATION FUNCTIONS
# ==========================================


def validate_email_format(email: str) -> tuple[bool, str]:
    """
    Validate email format.

    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"

    # Basic regex for email validation
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, f"Invalid email format: {email}"

    return True, ""


def validate_age(age: Any) -> tuple[bool, str]:
    """
    Validate age.

    Rules:
    - Must be integer or float
    - Must be >= 0
    - Must be <= 150
    """
    if not isinstance(age, (int, float)):
        return False, f"Age must be a number, got {type(age).__name__}"

    if age < 0:
        return False, "Age cannot be negative"

    if age > 150:
        return False, "Age cannot exceed 150"

    return True, ""


def validate_phone_number(phone: str) -> tuple[bool, str]:
    """
    Validate phone number.

    Rules:
    - Must contain only digits, +, -, (, ), spaces
    - Must have at least 10 digits
    """
    if not phone:
        return False, "Phone number cannot be empty"

    # Extract only digits
    digits = "".join([c for c in phone if c.isdigit()])

    if len(digits) < 10:
        return False, f"Phone number must have at least 10 digits, got {len(digits)}"

    return True, ""


def validate_user_dict(user: Dict) -> List[str]:
    """
    Validate complete user dictionary.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required_fields = ["user_id", "name", "email", "age"]
    for field in required_fields:
        if field not in user:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors  # Stop here if missing fields

    # Validate user_id
    if not isinstance(user["user_id"], int) or user["user_id"] <= 0:
        errors.append("user_id must be a positive integer")

    # Validate name
    if not user["name"] or not isinstance(user["name"], str):
        errors.append("name must be a non-empty string")

    # Validate email
    is_valid, error = validate_email_format(user["email"])
    if not is_valid:
        errors.append(error)

    # Validate age
    is_valid, error = validate_age(user["age"])
    if not is_valid:
        errors.append(error)

    # Validate phone (optional field)
    if "phone" in user:
        is_valid, error = validate_phone_number(user["phone"])
        if not is_valid:
            errors.append(error)

    return errors


def validate_transaction(txn: Dict) -> List[str]:
    """
    Validate transaction data.

    Business rules:
    - amount must be positive
    - currency must be valid (USD, EUR, IDR)
    - timestamp must be within last 24 hours
    """
    errors = []

    # Check required fields
    required_fields = ["transaction_id", "amount", "currency", "timestamp"]
    for field in required_fields:
        if field not in txn:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors

    # Validate amount
    if not isinstance(txn["amount"], (int, float)):
        errors.append("amount must be a number")
    elif txn["amount"] <= 0:
        errors.append("amount must be positive")

    # Validate currency
    valid_currencies = ["USD", "EUR", "IDR", "SGD"]
    if txn["currency"] not in valid_currencies:
        errors.append(f"currency must be one of {valid_currencies}")

    # Validate timestamp (ISO format)
    try:
        txn_time = datetime.fromisoformat(txn["timestamp"].replace("Z", "+00:00"))

        # Check if within last 24 hours
        now = datetime.now(txn_time.tzinfo)
        age_hours = (now - txn_time).total_seconds() / 3600

        if age_hours < 0:
            errors.append("timestamp cannot be in the future")
        elif age_hours > 24:
            errors.append("timestamp must be within last 24 hours")

    except (ValueError, AttributeError):
        errors.append("timestamp must be valid ISO format")

    return errors


# ==========================================
# TESTS - Email Validation
# ==========================================


def test_validate_email_valid():
    """Test valid email formats."""
    valid_emails = [
        "user@example.com",
        "john.doe@company.co.id",
        "admin+tag@site.org",
        "test_123@domain.com",
    ]

    for email in valid_emails:
        is_valid, error = validate_email_format(email)
        assert is_valid, f"{email} should be valid, but got error: {error}"


def test_validate_email_invalid():
    """Test invalid email formats."""
    invalid_emails = [
        ("", "cannot be empty"),
        ("notanemail", "Invalid email format"),
        ("missing@domain", "Invalid email format"),
        ("@nodomain.com", "Invalid email format"),
    ]

    for email, expected_error_substring in invalid_emails:
        is_valid, error = validate_email_format(email)
        assert not is_valid, f"{email} should be invalid"
        assert expected_error_substring in error


# ==========================================
# TESTS - Age Validation
# ==========================================


def test_validate_age_valid():
    """Test valid ages."""
    valid_ages = [0, 1, 25, 100, 150]

    for age in valid_ages:
        is_valid, error = validate_age(age)
        assert is_valid, f"Age {age} should be valid, but got error: {error}"


def test_validate_age_invalid():
    """Test invalid ages."""
    test_cases = [
        (-1, "cannot be negative"),
        (-100, "cannot be negative"),
        (151, "cannot exceed 150"),
        (999, "cannot exceed 150"),
        ("25", "must be a number"),
        (None, "must be a number"),
    ]

    for age, expected_error_substring in test_cases:
        is_valid, error = validate_age(age)
        assert not is_valid, f"Age {age} should be invalid"
        assert expected_error_substring in error


# ==========================================
# TESTS - Phone Validation
# ==========================================


def test_validate_phone_valid():
    """Test valid phone numbers."""
    valid_phones = [
        "+1234567890",
        "(123) 456-7890",
        "123-456-7890",
        "+62 812 3456 7890",
    ]

    for phone in valid_phones:
        is_valid, error = validate_phone_number(phone)
        assert is_valid, f"{phone} should be valid, but got error: {error}"


def test_validate_phone_invalid():
    """Test invalid phone numbers."""
    test_cases = [
        ("", "cannot be empty"),
        ("123", "must have at least 10 digits"),
        ("abc", "must have at least 10 digits"),
    ]

    for phone, expected_error_substring in test_cases:
        is_valid, error = validate_phone_number(phone)
        assert not is_valid, f"{phone} should be invalid"
        assert expected_error_substring in error


# ==========================================
# TESTS - Complete User Validation
# ==========================================


def test_validate_user_dict_valid():
    """Test valid user data."""
    valid_user = {
        "user_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "age": 25,
        "phone": "+1234567890",
    }

    errors = validate_user_dict(valid_user)
    assert len(errors) == 0, f"Valid user should have no errors, got: {errors}"


def test_validate_user_dict_missing_fields():
    """Test user dengan missing required fields."""
    incomplete_user = {"user_id": 1, "name": "John"}  # missing email, age

    errors = validate_user_dict(incomplete_user)

    assert len(errors) >= 2
    assert any("email" in e for e in errors)
    assert any("age" in e for e in errors)


def test_validate_user_dict_invalid_email():
    """Test user dengan invalid email."""
    invalid_user = {
        "user_id": 1,
        "name": "John",
        "email": "not-an-email",  # Invalid!
        "age": 25,
    }

    errors = validate_user_dict(invalid_user)

    assert len(errors) > 0
    assert any("email" in e.lower() for e in errors)


def test_validate_user_dict_invalid_age():
    """Test user dengan invalid age."""
    invalid_user = {
        "user_id": 1,
        "name": "John",
        "email": "john@example.com",
        "age": -5,  # Invalid!
    }

    errors = validate_user_dict(invalid_user)

    assert len(errors) > 0
    assert any("age" in e.lower() for e in errors)


def test_validate_user_dict_multiple_errors():
    """Test user dengan multiple errors."""
    invalid_user = {
        "user_id": -1,  # Invalid
        "name": "",  # Invalid
        "email": "bad-email",  # Invalid
        "age": 200,  # Invalid
    }

    errors = validate_user_dict(invalid_user)

    # Should have multiple errors
    assert len(errors) >= 4


# ==========================================
# TESTS - Transaction Validation
# ==========================================


def test_validate_transaction_valid():
    """Test valid transaction."""
    valid_txn = {
        "transaction_id": "TXN001",
        "amount": 100.50,
        "currency": "USD",
        "timestamp": datetime.now().isoformat(),
    }

    errors = validate_transaction(valid_txn)
    assert len(errors) == 0, f"Valid transaction should have no errors, got: {errors}"


def test_validate_transaction_negative_amount():
    """Test transaction dengan negative amount."""
    invalid_txn = {
        "transaction_id": "TXN001",
        "amount": -100,  # Invalid!
        "currency": "USD",
        "timestamp": datetime.now().isoformat(),
    }

    errors = validate_transaction(invalid_txn)

    assert len(errors) > 0
    assert any("amount must be positive" in e for e in errors)


def test_validate_transaction_invalid_currency():
    """Test transaction dengan invalid currency."""
    invalid_txn = {
        "transaction_id": "TXN001",
        "amount": 100,
        "currency": "XXX",  # Invalid!
        "timestamp": datetime.now().isoformat(),
    }

    errors = validate_transaction(invalid_txn)

    assert len(errors) > 0
    assert any("currency" in e for e in errors)


def test_validate_transaction_future_timestamp():
    """Test transaction dengan future timestamp."""
    from datetime import timedelta

    future_time = datetime.now() + timedelta(hours=1)

    invalid_txn = {
        "transaction_id": "TXN001",
        "amount": 100,
        "currency": "USD",
        "timestamp": future_time.isoformat(),
    }

    errors = validate_transaction(invalid_txn)

    assert len(errors) > 0
    assert any("future" in e for e in errors)


# ==========================================
# REAL-WORLD SCENARIO
# ==========================================


def test_batch_validation_scenario():
    """
    Real-world: Validate batch of users from API.

    Scenario:
    - API return list of users
    - Some valid, some invalid
    - We want to: collect all errors, process valid ones
    """
    users_from_api = [
        {
            "user_id": 1,
            "name": "John",
            "email": "john@example.com",
            "age": 25,
        },  # Valid
        {
            "user_id": 2,
            "name": "Alice",
            "email": "invalid-email",
            "age": 30,
        },  # Invalid email
        {"user_id": 3, "name": "", "email": "bob@test.com", "age": -5},  # Multiple errors
        {
            "user_id": 4,
            "name": "Carol",
            "email": "carol@example.com",
            "age": 28,
        },  # Valid
    ]

    valid_users = []
    invalid_users = []

    for user in users_from_api:
        errors = validate_user_dict(user)

        if len(errors) == 0:
            valid_users.append(user)
        else:
            invalid_users.append({"user": user, "errors": errors})

    # Verify results
    assert len(valid_users) == 2, "Should have 2 valid users"
    assert len(invalid_users) == 2, "Should have 2 invalid users"

    # Valid users
    assert valid_users[0]["name"] == "John"
    assert valid_users[1]["name"] == "Carol"

    # Invalid users have error details
    assert len(invalid_users[0]["errors"]) > 0
    assert len(invalid_users[1]["errors"]) > 1  # Multiple errors


# ==========================================
# TIPS & LEARNINGS
# ==========================================


def test_validation_learnings():
    """
    💡 KEY LEARNINGS:

    1. Manual validation gives you full control:
       ✅ Custom error messages
       ✅ Complex business rules
       ✅ No dependencies

    2. But has downsides:
       ❌ Lots of boilerplate code
       ❌ Easy to forget edge cases
       ❌ Hard to maintain as schema grows

    3. Best practices:
       - Return (is_valid, error_message) tuples
       - Collect all errors, not just first one
       - Validate early (fail fast)
       - Clear, actionable error messages

    4. When to use manual validation:
       - Simple schemas
       - Custom business logic
       - Learning/understanding

    5. When to use libraries (Pydantic, etc):
       - Complex schemas
       - Need type safety
       - Want auto-documentation
       - Production systems

    Next: We'll see how Pydantic makes this MUCH easier!
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 2-simple-validation.py -v")
