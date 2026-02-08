"""
DATA TRANSFORMATION TESTING

Sekarang kita test fungsi-fungsi yang biasa dipakai di Data Engineering:
- Data cleaning
- Data validation
- Data transformation

Masih pakai pure Python, belum pakai pytest.

Cara run:
    python 3-test-data-transformation.py
"""

import json
from datetime import datetime
from typing import Dict, List
import pytest

# ==========================================
# FUNGSI TRANSFORMASI DATA (Yang mau di-test)
# ==========================================


def clean_email(email: str) -> str:
    """
    Clean email address:
    - Trim whitespace
    - Convert to lowercase
    - Remove invalid characters
    """
    if not email:
        return ""

    cleaned = email.strip().lower()

    # Basic validation
    if "@" not in cleaned:
        raise ValueError(f"Invalid email format: {email}")

    return cleaned

def parse_transaction_amount(amount_str: str) -> float:
    if not amount_str:
        return 0.0

    # 1. Bersihkan simbol mata uang dan spasi
    cleaned = amount_str.replace("$", "").replace("Rp", "").replace(" ", "")

    # 2. Logika Penanganan Separator
    if "," in cleaned and "." in cleaned:
        # Format US: 1,234.56 -> hapus koma
        if cleaned.find(",") < cleaned.find("."):
            cleaned = cleaned.replace(",", "")
        # Format EU/ID: 1.234,56 -> hapus titik, ganti koma ke titik
        else:
            cleaned = cleaned.replace(".", "").replace(",", ".")
    
    elif "," in cleaned:
        # Jika hanya ada koma (misal: 1234,56 atau 1,234,567)
        # Jika komanya ada di posisi desimal (2 angka di belakang)
        if len(cleaned.split(",")[-1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
            
    elif "." in cleaned:
        # Kasus error kamu: "1.234.567"
        # Jika ada lebih dari satu titik, itu pasti ribuan
        if cleaned.count(".") > 1:
            cleaned = cleaned.replace(".", "")
        # Heuristic: Jika titik diikuti 3 angka, kemungkinan besar ribuan (ID format)
        # Contoh: "1.234" -> 1234.0
        elif len(cleaned.split(".")[-1]) == 3:
            cleaned = cleaned.replace(".", "")
            
    return float(cleaned)

def aggregate_sales_by_product(transactions: List[Dict]) -> Dict[str, float]:
    """
    Aggregate total sales per product.

    Args:
        transactions: List of dicts dengan keys: product, amount, quantity

    Returns:
        Dict: {product_name: total_sales}
    """
    sales_by_product = {}

    for txn in transactions:
        product = txn.get("product")
        amount = txn.get("amount", 0)
        quantity = txn.get("quantity", 1)

        if not product:
            continue  # Skip invalid transactions

        total = amount * quantity

        if product in sales_by_product:
            sales_by_product[product] += total
        else:
            sales_by_product[product] = total

    return sales_by_product


def validate_user_data(user: Dict) -> List[str]:
    """
    Validate user data dan return list of errors.

    Required fields:
    - email: harus valid format
    - age: harus >= 18
    - username: harus alphanumeric

    Returns:
        List of error messages (empty jika valid)
    """
    errors = []

    # Check required fields
    if not user.get("email"):
        errors.append("Email is required")
    elif "@" not in user.get("email", ""):
        errors.append("Email format invalid")

    if not user.get("username"):
        errors.append("Username is required")
    elif not user.get("username", "").replace("_", "").isalnum():
        errors.append("Username must be alphanumeric")

    if "age" not in user:
        errors.append("Age is required")
    elif user.get("age", 0) < 18:
        errors.append("User must be at least 18 years old")

    return errors


def convert_timestamp_format(timestamp_str: str, output_format: str = "%Y-%m-%d") -> str:
    """
    Convert timestamp dari berbagai format ke format yang diinginkan.

    Args:
        timestamp_str: String timestamp (ISO format atau epoch)
        output_format: Format output (default: YYYY-MM-DD)
    """
    # Try parse as ISO format
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        return dt.strftime(output_format)
    except ValueError:
        pass

    # Try parse as epoch (in milliseconds)
    try:
        epoch_ms = int(timestamp_str)
        dt = datetime.fromtimestamp(epoch_ms / 1000)
        return dt.strftime(output_format)
    except (ValueError, OSError):
        pass

    raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


# ==========================================
# TESTS
# ==========================================


def test_clean_email():
    """Test email cleaning function."""
    print("\n🧪 Testing clean_email()...")

    # Test case 1: Normal email
    assert clean_email("User@Example.COM") == "user@example.com"

    # Test case 2: Email dengan whitespace
    assert clean_email("  test@gmail.com  ") == "test@gmail.com"

    # Test case 3: Empty string
    assert clean_email("") == ""

    # Test case 4: Invalid email (harus raise error)
    try:
        clean_email("invalid-email")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Invalid email format" in str(e)

    print("✅ All email cleaning tests passed")


@pytest.mark.parametrize("amount_str, expected", [
    ("$1,234.56", 1234.56),          # US format
    ("Rp 1.234.567", 1234567.0),    # Indonesian format
    ("1234.56", 1234.56),           # Simple number
    ("", 0.0),                       # Empty string
    ("1.234,56", 1234.56),          # European format
])
def test_parse_transaction_amount(amount_str, expected):
    """Test parsing amount dari berbagai format."""
    print("\n🧪 Testing parse_transaction_amount()...")
    assert parse_transaction_amount(amount_str) == expected

    print("✅ All amount parsing tests passed")


def test_aggregate_sales_by_product():
    """Test sales aggregation."""
    print("\n🧪 Testing aggregate_sales_by_product()...")

    transactions = [
        {"product": "Laptop", "amount": 1000, "quantity": 2},
        {"product": "Mouse", "amount": 50, "quantity": 5},
        {"product": "Laptop", "amount": 1000, "quantity": 1},  # Same product
        {"product": None, "amount": 100, "quantity": 1},  # Invalid - skip
    ]

    result = aggregate_sales_by_product(transactions)

    # Expected: Laptop = (1000*2) + (1000*1) = 3000
    assert result["Laptop"] == 3000

    # Expected: Mouse = 50*5 = 250
    assert result["Mouse"] == 250

    # Invalid transaction should be skipped
    assert None not in result

    print("✅ All aggregation tests passed")


def test_validate_user_data():
    """Test user data validation."""
    print("\n🧪 Testing validate_user_data()...")

    # Test case 1: Valid user
    valid_user = {"email": "test@example.com", "username": "john_doe", "age": 25}
    errors = validate_user_data(valid_user)
    assert len(errors) == 0, f"Valid user should have no errors, got: {errors}"

    # Test case 2: Missing email
    invalid_user_1 = {"username": "john", "age": 25}
    errors = validate_user_data(invalid_user_1)
    assert any("Email is required" in e for e in errors)

    # Test case 3: Invalid email format
    invalid_user_2 = {"email": "not-an-email", "username": "john", "age": 25}
    errors = validate_user_data(invalid_user_2)
    assert any("Email format invalid" in e for e in errors)

    # Test case 4: Under age
    invalid_user_3 = {"email": "kid@example.com", "username": "kid", "age": 15}
    errors = validate_user_data(invalid_user_3)
    assert any("at least 18" in e for e in errors)

    # Test case 5: Invalid username
    invalid_user_4 = {"email": "test@example.com", "username": "john@doe!", "age": 25}
    errors = validate_user_data(invalid_user_4)
    assert any("alphanumeric" in e for e in errors)

    print("✅ All validation tests passed")


def test_convert_timestamp_format():
    """Test timestamp conversion."""
    print("\n🧪 Testing convert_timestamp_format()...")

    # Test case 1: ISO format
    iso_timestamp = "2024-01-15T10:30:00Z"
    result = convert_timestamp_format(iso_timestamp)
    assert result == "2024-01-15"

    # Test case 2: Epoch milliseconds
    epoch_ms = "1705318200000"  # 2024-01-15 10:30:00
    result = convert_timestamp_format(epoch_ms)
    # Just check it's a valid date format
    assert len(result) == 10
    assert result.count("-") == 2

    # Test case 3: Custom output format
    result = convert_timestamp_format(iso_timestamp, "%d/%m/%Y")
    assert result == "15/01/2024"

    # Test case 4: Invalid format
    try:
        convert_timestamp_format("invalid-timestamp")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unable to parse" in str(e)

    print("✅ All timestamp conversion tests passed")


# ==========================================
# REAL-WORLD SCENARIO
# ==========================================


def test_real_world_etl_scenario():
    """
    Scenario: ETL pipeline untuk process data transaksi e-commerce.

    Steps:
    1. Clean data (email, amount)
    2. Validate data
    3. Transform & aggregate
    4. Output clean data
    """
    print("\n" + "=" * 60)
    print("REAL-WORLD SCENARIO: E-commerce Transaction ETL")
    print("=" * 60)

    # Raw data dari API (kotor)
    raw_transactions = [
        {
            "user_email": "  JohN@Example.COM  ",
            "product": "Laptop",
            "amount": "$1,299.99",
            "quantity": 1,
            "timestamp": "2024-01-15T10:30:00Z",
        },
        {
            "user_email": "alice@test.com",
            "product": "Mouse",
            "amount": "$29.99",
            "quantity": 3,
            "timestamp": "2024-01-15T11:00:00Z",
        },
        {
            "user_email": "BOB@SHOP.COM",
            "product": "Laptop",
            "amount": "$1,299.99",
            "quantity": 2,
            "timestamp": "1705318800000",  # Epoch format
        },
    ]

    # ETL Process
    cleaned_transactions = []

    for txn in raw_transactions:
        try:
            # Step 1: Clean email
            clean_email_addr = clean_email(txn["user_email"])

            # Step 2: Parse amount
            clean_amount = parse_transaction_amount(txn["amount"])

            # Step 3: Convert timestamp
            clean_date = convert_timestamp_format(txn["timestamp"])

            # Step 4: Build clean record
            clean_txn = {
                "email": clean_email_addr,
                "product": txn["product"],
                "amount": clean_amount,
                "quantity": txn["quantity"],
                "date": clean_date,
            }

            cleaned_transactions.append(clean_txn)

        except Exception as e:
            print(f"⚠️  Skipping invalid transaction: {e}")

    # Verify hasil ETL
    assert len(cleaned_transactions) == 3, "Should process all 3 transactions"

    # Check email cleaning
    assert cleaned_transactions[0]["email"] == "john@example.com"
    assert cleaned_transactions[2]["email"] == "bob@shop.com"

    # Check amount parsing
    assert cleaned_transactions[0]["amount"] == 1299.99
    assert cleaned_transactions[1]["amount"] == 29.99

    # Step 5: Aggregate sales
    sales_summary = aggregate_sales_by_product(cleaned_transactions)
    print("\n📊 Sales Summary:")
    for product, total in sales_summary.items():
        print(f"  {product}: ${total:,.2f}")

    # Verify aggregation
    # Laptop: 1299.99 * 1 + 1299.99 * 2 = 3899.97
    assert abs(sales_summary["Laptop"] - 3899.97) < 0.01
    # Mouse: 29.99 * 3 = 89.97
    assert abs(sales_summary["Mouse"] - 89.97) < 0.01

    print("\n✅ ETL Pipeline test passed!")
    print("\n💡 Key Learning:")
    print("  - Test setiap step transformasi secara terpisah")
    print("  - Test end-to-end flow dengan real data")
    print("  - Handle errors gracefully (skip bad data)")


# ==========================================
# RUNNER
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 DATA TRANSFORMATION TESTING")
    print("=" * 60)

    # Run all tests
    test_clean_email()
    test_parse_transaction_amount()
    test_aggregate_sales_by_product()
    test_validate_user_data()
    test_convert_timestamp_format()

    # Real-world scenario
    test_real_world_etl_scenario()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

    print("\n💡 KEY TAKEAWAYS:")
    print("1. Test fungsi transformasi dengan berbagai edge cases")
    print("2. Test dengan data yang mirip production (kotor, beragam format)")
    print("3. Test error handling (invalid data harus di-handle)")
    print("4. Test end-to-end scenario untuk verify integration")
    print("\n🚀 Next: Install pytest dan lanjut ke folder 2-pytest-fundamentals")
    print("   Command: cd .. && pip install pytest pandas faker")
