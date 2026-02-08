"""
EXCEPTION TESTING - Testing Error Handling

Dalam Data Engineering, error handling sama pentingnya dengan happy path.
Kita harus test bahwa code kita handle error dengan benar.

Topics:
1. Test exceptions dengan pytest.raises
2. Test error messages
3. Test validation errors
4. Real-world data quality scenarios

Cara run:
    pytest 4-test-exceptions.py -v
"""

import pytest
import pandas as pd


# ==========================================
# FUNCTIONS WITH ERROR HANDLING
# ==========================================


def divide(a, b):
    """
    Divide a by b.
    Raises ZeroDivisionError if b is 0.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def validate_user_age(age):
    """
    Validate user age.

    Raises:
        ValueError: If age < 0 or age > 150
        TypeError: If age is not a number
    """
    if not isinstance(age, (int, float)):
        raise TypeError(f"Age must be a number, got {type(age).__name__}")

    if age < 0:
        raise ValueError("Age cannot be negative")

    if age > 150:
        raise ValueError("Age cannot be more than 150")

    return True


def load_csv_with_validation(filepath, required_columns):
    """
    Load CSV and validate required columns exist.

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns missing
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df


def parse_json_strict(json_string):
    """
    Parse JSON with strict validation.

    Raises:
        ValueError: If json_string is empty or invalid
    """
    import json

    if not json_string:
        raise ValueError("JSON string cannot be empty")

    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


# ==========================================
# BASIC EXCEPTION TESTING
# ==========================================


def test_divide_by_zero():
    """Test that divide raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)


def test_divide_by_zero_with_message():
    """Test exception AND the error message."""
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        divide(10, 0)


def test_divide_normal_operation():
    """Test that divide works normally when no error."""
    result = divide(10, 2)
    assert result == 5.0


# ==========================================
# TESTING MULTIPLE EXCEPTION TYPES
# ==========================================


def test_validate_age_negative():
    """Test ValueError for negative age."""
    with pytest.raises(ValueError, match="Age cannot be negative"):
        validate_user_age(-5)


def test_validate_age_too_old():
    """Test ValueError for age > 150."""
    with pytest.raises(ValueError, match="cannot be more than 150"):
        validate_user_age(200)


def test_validate_age_wrong_type():
    """Test TypeError for non-numeric age."""
    with pytest.raises(TypeError, match="Age must be a number"):
        validate_user_age("twenty five")


def test_validate_age_valid():
    """Test that valid age passes."""
    assert validate_user_age(25) is True
    assert validate_user_age(0) is True  # Boundary
    assert validate_user_age(150) is True  # Boundary


# ==========================================
# TESTING EXCEPTION DETAILS
# ==========================================


def test_exception_with_detailed_check():
    """
    Test exception dengan check detail message.

    Berguna untuk verify bahwa error message informatif.
    """
    with pytest.raises(ValueError) as exc_info:
        validate_user_age(-10)

    # exc_info.value adalah exception instance
    error_message = str(exc_info.value)
    assert "negative" in error_message.lower()


def test_parse_json_empty_string():
    """Test error untuk empty JSON string."""
    with pytest.raises(ValueError) as exc_info:
        parse_json_strict("")

    assert "cannot be empty" in str(exc_info.value)


def test_parse_json_invalid_format():
    """Test error untuk invalid JSON."""
    with pytest.raises(ValueError) as exc_info:
        parse_json_strict("{invalid json}")

    # Error message harus contain "Invalid JSON"
    assert "Invalid JSON" in str(exc_info.value)


# ==========================================
# PARAMETRIZE + EXCEPTIONS
# ==========================================


@pytest.mark.parametrize(
    "invalid_age,expected_error,error_pattern",
    [
        (-1, ValueError, "negative"),
        (-100, ValueError, "negative"),
        (151, ValueError, "more than 150"),
        (999, ValueError, "more than 150"),
        ("abc", TypeError, "must be a number"),
        (None, TypeError, "must be a number"),
        ([25], TypeError, "must be a number"),
    ],
)
def test_validate_age_invalid_inputs(invalid_age, expected_error, error_pattern):
    """
    Test berbagai invalid inputs dengan parametrize.

    Efficient: 1 test function untuk banyak error cases.
    """
    with pytest.raises(expected_error, match=error_pattern):
        validate_user_age(invalid_age)


# ==========================================
# REAL-WORLD: DATA QUALITY CHECKS
# ==========================================


def validate_dataframe_schema(df, schema):
    """
    Validate DataFrame against schema.

    Args:
        df: Pandas DataFrame
        schema: dict of {column_name: expected_dtype}

    Raises:
        ValueError: If columns missing or wrong dtype
    """
    # Check missing columns
    missing_cols = set(schema.keys()) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    # Check data types
    for col, expected_dtype in schema.items():
        actual_dtype = df[col].dtype
        if actual_dtype != expected_dtype:
            raise ValueError(
                f"Column '{col}' has wrong dtype: expected {expected_dtype}, got {actual_dtype}"
            )

    return True


def test_validate_dataframe_missing_columns():
    """Test error ketika columns missing."""
    df = pd.DataFrame({"name": ["John"], "age": [25]})

    schema = {"name": object, "age": int, "email": object}  # email missing!

    with pytest.raises(ValueError, match="Missing columns"):
        validate_dataframe_schema(df, schema)


def test_validate_dataframe_wrong_dtype():
    """Test error ketika dtype salah."""
    # Age as string instead of int
    df = pd.DataFrame({"name": ["John"], "age": ["25"]})

    schema = {"name": object, "age": int}

    with pytest.raises(ValueError, match="wrong dtype"):
        validate_dataframe_schema(df, schema)


def test_validate_dataframe_success():
    """Test validation success."""
    df = pd.DataFrame({"name": ["John"], "age": [25]})

    schema = {"name": str, "age": int}

    assert validate_dataframe_schema(df, schema) is True


# ==========================================
# TESTING FILE OPERATIONS
# ==========================================


def test_load_csv_file_not_found():
    """Test FileNotFoundError ketika file tidak ada."""
    with pytest.raises(FileNotFoundError, match="File not found"):
        load_csv_with_validation("/nonexistent/file.csv", ["col1"])


def test_load_csv_missing_columns(tmp_path):
    """
    Test ValueError ketika required columns missing.

    Uses tmp_path fixture untuk create temporary CSV.
    """
    # Create temporary CSV
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age\nJohn,25\n")

    # Try load dengan required column yang tidak ada
    with pytest.raises(ValueError, match="Missing required columns"):
        load_csv_with_validation(csv_file, ["name", "email"])  # email missing!


def test_load_csv_success(tmp_path):
    """Test successful CSV load."""
    # Create temporary CSV
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age,email\nJohn,25,john@test.com\n")

    df = load_csv_with_validation(csv_file, ["name", "age"])

    assert len(df) == 1
    assert "name" in df.columns


# ==========================================
# TESTING CUSTOM EXCEPTIONS
# ==========================================


class DataQualityError(Exception):
    """Custom exception untuk data quality issues."""

    pass


def check_no_nulls(df, column):
    """
    Check that column has no null values.

    Raises:
        DataQualityError: If nulls found
    """
    null_count = df[column].isna().sum()
    if null_count > 0:
        raise DataQualityError(f"Column '{column}' has {null_count} null values")
    return True


def test_check_no_nulls_with_nulls():
    """Test error ketika ada nulls."""
    df = pd.DataFrame({"name": ["John", None, "Alice"]})

    with pytest.raises(DataQualityError, match="has 1 null values"):
        check_no_nulls(df, "name")


def test_check_no_nulls_success():
    """Test success ketika tidak ada nulls."""
    df = pd.DataFrame({"name": ["John", "Alice"]})
    assert check_no_nulls(df, "name") is True


# ==========================================
# EDGE CASE: Testing No Exception Raised
# ==========================================


def test_function_does_not_raise():
    """
    Kadang kita mau verify bahwa function TIDAK raise exception.

    Ini implicitly tested di normal tests, tapi bisa explicit juga.
    """
    # This should not raise any exception
    try:
        result = divide(10, 2)
        assert result == 5.0
    except Exception as e:
        pytest.fail(f"Function raised unexpected exception: {e}")


# ==========================================
# TIPS & BEST PRACTICES
# ==========================================


def test_exception_testing_tips():
    """
    💡 KEY POINTS tentang Exception Testing:

    1. Always test error paths:
       - "Happy path" aja tidak cukup
       - Error handling sama pentingnya

    2. Use pytest.raises():
       - Test that exception is raised
       - Test exception message (with match)
       - Access exception details (exc_info.value)

    3. Test multiple error scenarios:
       - Different inputs that cause errors
       - Different exception types
       - Boundary conditions

    4. Real-world importance:
       - Data quality checks harus raise clear errors
       - ETL failures harus informatif
       - Validation errors guide users

    5. Don't just test that it raises:
       - Also test error messages are helpful
       - Test that correct exception type is raised

    6. Use custom exceptions:
       - More specific than generic ValueError
       - Better for error handling in production
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 4-test-exceptions.py -v")
    print("\n💡 Try also:")
    print("   pytest 4-test-exceptions.py -v -k age")
    print("   pytest 4-test-exceptions.py -v -k csv")
