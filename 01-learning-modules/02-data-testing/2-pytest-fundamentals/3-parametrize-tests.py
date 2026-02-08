"""
PARAMETRIZE - Test Banyak Cases Sekaligus

Parametrize = cara elegant untuk test fungsi dengan banyak input berbeda.

Tanpa parametrize:
    - Copy paste test function berkali-kali
    - Hard to maintain

Dengan parametrize:
    - 1 test function
    - Multiple test cases
    - DRY (Don't Repeat Yourself)

Cara run:
    pytest 3-parametrize-tests.py -v
"""

import pytest
import pandas as pd


# ==========================================
# FUNCTIONS TO TEST
# ==========================================


def convert_celsius_to_fahrenheit(celsius):
    """Convert Celsius ke Fahrenheit."""
    return (celsius * 9 / 5) + 32


def validate_email(email):
    """
    Validate email format.
    Returns True if valid, False otherwise.
    """
    if not email or "@" not in email:
        return False

    parts = email.split("@")
    if len(parts) != 2:
        return False

    username, domain = parts
    if not username or not domain:
        return False

    if "." not in domain:
        return False

    return True


def categorize_age(age):
    """
    Categorize age into groups.

    Returns:
        - "child" if age < 13
        - "teenager" if 13 <= age < 18
        - "adult" if 18 <= age < 60
        - "senior" if age >= 60
    """
    if age < 13:
        return "child"
    elif age < 18:
        return "teenager"
    elif age < 60:
        return "adult"
    else:
        return "senior"


def clean_phone_number(phone):
    """
    Clean phone number:
    - Remove spaces, dashes, parentheses
    - Keep only digits and +
    """
    if not phone:
        return ""

    allowed_chars = "0123456789+"
    cleaned = "".join([c for c in phone if c in allowed_chars])
    return cleaned


# ==========================================
# PARAMETRIZE - Basic Example
# ==========================================


@pytest.mark.parametrize(
    "celsius,expected_fahrenheit",
    [
        (0, 32),  # Water freezing point
        (100, 212),  # Water boiling point
        (-40, -40),  # Same value in both scales!
        (37, 98.6),  # Human body temperature
        (-273.15, -459.67),  # Absolute zero
    ],
)
def test_celsius_to_fahrenheit(celsius, expected_fahrenheit):
    """Test temperature conversion dengan multiple cases."""
    result = convert_celsius_to_fahrenheit(celsius)
    assert abs(result - expected_fahrenheit) < 0.1  # Allow small floating point error


# ==========================================
# PARAMETRIZE - Multiple Parameters
# ==========================================


@pytest.mark.parametrize(
    "email,is_valid",
    [
        # Valid emails
        ("user@example.com", True),
        ("john.doe@company.co.id", True),
        ("admin+tag@site.org", True),
        # Invalid emails
        ("", False),  # Empty
        ("notanemail", False),  # No @
        ("missing@domain", False),  # No dot in domain
        ("@nodomain.com", False),  # No username
        ("noat.com", False),  # No @
        ("double@@domain.com", False),  # Double @
    ],
)
def test_validate_email(email, is_valid):
    """Test email validation dengan berbagai cases."""
    assert validate_email(email) == is_valid


# ==========================================
# PARAMETRIZE - Test Edge Cases
# ==========================================


@pytest.mark.parametrize(
    "age,expected_category",
    [
        # Children
        (0, "child"),
        (5, "child"),
        (12, "child"),
        # Teenagers (boundary testing)
        (13, "teenager"),
        (15, "teenager"),
        (17, "teenager"),
        # Adults (boundary testing)
        (18, "adult"),
        (30, "adult"),
        (59, "adult"),
        # Seniors (boundary testing)
        (60, "senior"),
        (75, "senior"),
        (100, "senior"),
    ],
)
def test_categorize_age(age, expected_category):
    """
    Test age categorization.

    💡 Notice: Kita test boundaries (12, 13, 17, 18, 59, 60)
    Boundary testing sangat penting untuk catch off-by-one errors!
    """
    assert categorize_age(age) == expected_category


# ==========================================
# PARAMETRIZE - String Transformations
# ==========================================


@pytest.mark.parametrize(
    "input_phone,expected_output",
    [
        ("(123) 456-7890", "1234567890"),
        ("+62 812-3456-7890", "+6281234567890"),
        ("123 456 7890", "1234567890"),
        ("+1-800-CALL-NOW", "+1800"),  # Letters removed
        ("", ""),  # Empty string
        ("   ", ""),  # Only spaces
    ],
)
def test_clean_phone_number(input_phone, expected_output):
    """Test phone number cleaning."""
    assert clean_phone_number(input_phone) == expected_output


# ==========================================
# PARAMETRIZE - DataFrames
# ==========================================


@pytest.mark.parametrize(
    "data,filter_category,expected_count",
    [
        # Test case 1: Filter Electronics
        (
            {
                "product": ["Laptop", "Mouse", "Desk"],
                "category": ["Electronics", "Electronics", "Furniture"],
            },
            "Electronics",
            2,
        ),
        # Test case 2: Filter Furniture
        (
            {
                "product": ["Laptop", "Mouse", "Desk"],
                "category": ["Electronics", "Electronics", "Furniture"],
            },
            "Furniture",
            1,
        ),
        # Test case 3: No match
        (
            {
                "product": ["Laptop", "Mouse"],
                "category": ["Electronics", "Electronics"],
            },
            "Furniture",
            0,
        ),
    ],
)
def test_filter_dataframe_by_category(data, filter_category, expected_count):
    """Test filtering DataFrame by category."""
    df = pd.DataFrame(data)
    result = df[df["category"] == filter_category]
    assert len(result) == expected_count


# ==========================================
# PARAMETRIZE - dengan IDs untuk Readability
# ==========================================


@pytest.mark.parametrize(
    "temperature,expected",
    [
        (0, 32),
        (100, 212),
        (-40, -40),
    ],
    ids=["freezing_point", "boiling_point", "equal_point"],
)
def test_temperature_with_ids(temperature, expected):
    """
    Test dengan custom IDs.

    Benefit: Output pytest jadi lebih readable:
    PASSED test_temperature_with_ids[freezing_point]
    PASSED test_temperature_with_ids[boiling_point]

    Instead of:
    PASSED test_temperature_with_ids[0-32]
    PASSED test_temperature_with_ids[100-212]
    """
    result = convert_celsius_to_fahrenheit(temperature)
    assert result == expected


# ==========================================
# PARAMETRIZE - Multiple Parameters
# ==========================================


@pytest.mark.parametrize("category", ["Electronics", "Furniture", "Clothing"])
@pytest.mark.parametrize("min_price", [0, 100, 1000])
def test_filter_products_multi_params(category, min_price):
    """
    Multiple @pytest.mark.parametrize = Cartesian product.

    Ini akan generate 3 x 3 = 9 test cases:
    - Electronics + 0
    - Electronics + 100
    - Electronics + 1000
    - Furniture + 0
    - ... dst
    """
    # Sample test
    products_db = {
        "Electronics": [99, 500, 1500],
        "Furniture": [50, 200, 800],
        "Clothing": [20, 80, 300],
    }

    prices = products_db.get(category, [])
    filtered = [p for p in prices if p >= min_price]

    # Just verify that filtering works
    assert all(p >= min_price for p in filtered)


# ==========================================
# PARAMETRIZE - Marking Expected Failures
# ==========================================


@pytest.mark.parametrize(
    "celsius,expected",
    [
        (0, 32),
        (100, 212),
        pytest.param(
            50, 122.1, marks=pytest.mark.xfail(reason="Known rounding issue")
        ),  # Expected to fail
    ],
)
def test_with_expected_failures(celsius, expected):
    """
    Test dengan expected failures.

    pytest.param() dengan marks=xfail akan mark test sebagai "expected to fail".
    Berguna untuk document known issues.
    """
    result = convert_celsius_to_fahrenheit(celsius)
    assert result == expected


# ==========================================
# REAL-WORLD EXAMPLE - ETL Validation
# ==========================================


def clean_transaction_amount(amount_str):
    """Clean amount string to float."""
    if not amount_str:
        return 0.0

    # Remove currency symbols and spaces
    cleaned = (
        amount_str.replace("$", "").replace("Rp", "").replace(" ", "").replace(",", "")
    )

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


@pytest.mark.parametrize(
    "input_amount,expected_output",
    [
        ("$1234.56", 1234.56),
        ("Rp 1234567", 1234567.0),
        ("$1,234.56", 1234.56),
        ("", 0.0),
        ("invalid", 0.0),
        ("$0", 0.0),
        ("  $  999.99  ", 999.99),
    ],
    ids=[
        "us_currency",
        "idr_currency",
        "with_comma_separator",
        "empty_string",
        "invalid_input",
        "zero_amount",
        "extra_whitespace",
    ],
)
def test_clean_transaction_amount(input_amount, expected_output):
    """
    Real-world example: Test ETL data cleaning.

    Ini adalah contoh typical test untuk data cleaning function.
    """
    assert clean_transaction_amount(input_amount) == expected_output


# ==========================================
# TIPS & BEST PRACTICES
# ==========================================


def test_parametrize_tips():
    """
    💡 KEY POINTS tentang Parametrize:

    1. Use parametrize ketika:
       ✅ Testing same logic dengan different inputs
       ✅ Testing boundary conditions
       ✅ Testing berbagai edge cases

    2. Don't use parametrize ketika:
       ❌ Logic test berbeda untuk tiap case
       ❌ Setup/teardown per case sangat complex

    3. Best Practices:
       - Use descriptive parameter names
       - Add IDs untuk readability
       - Group related test cases
       - Test boundaries (0, negative, max, dll)

    4. Benefits:
       - Less code duplication
       - Easy to add new test cases
       - Clear test coverage
       - Better test reports

    5. Parametrize vs Fixtures:
       - Parametrize: Different inputs, same function
       - Fixtures: Reusable setup/data across tests
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 3-parametrize-tests.py -v")
    print("\n💡 Try also:")
    print("   pytest 3-parametrize-tests.py -v -k temperature")
    print("   pytest 3-parametrize-tests.py -v -k email")
