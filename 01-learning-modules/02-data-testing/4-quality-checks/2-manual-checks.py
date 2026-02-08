"""
MANUAL DATA QUALITY CHECKS

Sebelum pakai library, kita harus paham fundamental checks.
Ini adalah foundation untuk semua data quality testing!

Topics:
- Null checks
- Duplicate detection
- Range validation
- Type checking
- Business rules validation

Cara run:
    pytest 2-manual-checks.py -v
"""

import pandas as pd
import pytest
from datetime import datetime, timedelta


# ==========================================
# DATA QUALITY CHECK FUNCTIONS
# ==========================================


def check_no_nulls(df: pd.DataFrame, columns: list) -> tuple[bool, list]:
    """
    Check that specified columns have no null values.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    for col in columns:
        if col not in df.columns:
            errors.append(f"Column '{col}' not found in DataFrame")
            continue

        null_count = df[col].isna().sum()
        if null_count > 0:
            errors.append(f"Column '{col}' has {null_count} null values")

    return len(errors) == 0, errors


def check_no_duplicates(df: pd.DataFrame, subset: list = None) -> tuple[bool, list]:
    """
    Check for duplicate rows.

    Args:
        df: DataFrame to check
        subset: List of columns to check for duplicates (None = all columns)

    Returns:
        (is_valid, list_of_errors)
    """
    duplicate_count = df.duplicated(subset=subset).sum()

    if duplicate_count > 0:
        return False, [f"Found {duplicate_count} duplicate rows"]

    return True, []


def check_value_range(
    df: pd.DataFrame, column: str, min_value: float = None, max_value: float = None
) -> tuple[bool, list]:
    """
    Check that values in column are within specified range.

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    if column not in df.columns:
        return False, [f"Column '{column}' not found"]

    if min_value is not None:
        below_min = (df[column] < min_value).sum()
        if below_min > 0:
            errors.append(f"{below_min} values in '{column}' are below {min_value}")

    if max_value is not None:
        above_max = (df[column] > max_value).sum()
        if above_max > 0:
            errors.append(f"{above_max} values in '{column}' are above {max_value}")

    return len(errors) == 0, errors


def check_data_types(df: pd.DataFrame, expected_types: dict) -> tuple[bool, list]:
    """
    Check that columns have expected data types.

    Args:
        expected_types: dict of {column_name: expected_dtype}

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    for col, expected_dtype in expected_types.items():
        if col not in df.columns:
            errors.append(f"Column '{col}' not found")
            continue

        actual_dtype = df[col].dtype

        # Handle different dtype representations
        if expected_dtype == "numeric":
            if not pd.api.types.is_numeric_dtype(actual_dtype):
                errors.append(f"Column '{col}' should be numeric, got {actual_dtype}")
        elif expected_dtype == "string":
            if not pd.api.types.is_string_dtype(actual_dtype) and actual_dtype != object:
                errors.append(f"Column '{col}' should be string, got {actual_dtype}")
        elif expected_dtype == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(actual_dtype):
                errors.append(f"Column '{col}' should be datetime, got {actual_dtype}")
        else:
            # Exact dtype match
            if actual_dtype != expected_dtype:
                errors.append(
                    f"Column '{col}' has wrong dtype: expected {expected_dtype}, got {actual_dtype}"
                )

    return len(errors) == 0, errors


def check_unique_values(df: pd.DataFrame, column: str) -> tuple[bool, list]:
    """
    Check that column has only unique values (no duplicates).

    Returns:
        (is_valid, list_of_errors)
    """
    if column not in df.columns:
        return False, [f"Column '{column}' not found"]

    unique_count = df[column].nunique()
    total_count = len(df)

    if unique_count != total_count:
        duplicate_count = total_count - unique_count
        return False, [f"Column '{column}' has {duplicate_count} duplicate values"]

    return True, []


def check_referential_integrity(
    df: pd.DataFrame, foreign_key: str, reference_values: set
) -> tuple[bool, list]:
    """
    Check that foreign key values exist in reference set.

    Args:
        df: DataFrame to check
        foreign_key: Column name of foreign key
        reference_values: Set of valid values

    Returns:
        (is_valid, list_of_errors)
    """
    if foreign_key not in df.columns:
        return False, [f"Column '{foreign_key}' not found"]

    invalid_values = set(df[foreign_key].unique()) - reference_values
    invalid_count = df[foreign_key].isin(invalid_values).sum()

    if invalid_count > 0:
        return False, [
            f"{invalid_count} rows have invalid {foreign_key} values: {invalid_values}"
        ]

    return True, []


def check_freshness(df: pd.DataFrame, timestamp_column: str, max_age_hours: int = 24) -> tuple[bool, list]:
    """
    Check that data is fresh (not too old).

    Args:
        timestamp_column: Column with timestamps
        max_age_hours: Maximum allowed age in hours

    Returns:
        (is_valid, list_of_errors)
    """
    if timestamp_column not in df.columns:
        return False, [f"Column '{timestamp_column}' not found"]

    now = datetime.now()
    df_copy = df.copy()

    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df_copy[timestamp_column]):
        df_copy[timestamp_column] = pd.to_datetime(df_copy[timestamp_column])

    # Check oldest record
    oldest_timestamp = df_copy[timestamp_column].min()
    age_hours = (now - oldest_timestamp).total_seconds() / 3600

    if age_hours > max_age_hours:
        return False, [
            f"Data is stale: oldest record is {age_hours:.1f} hours old (max: {max_age_hours})"
        ]

    return True, []


# ==========================================
# COMPOSITE QUALITY CHECK
# ==========================================


def run_quality_checks(df: pd.DataFrame, checks: list) -> dict:
    """
    Run multiple quality checks dan return summary.

    Args:
        df: DataFrame to validate
        checks: List of (check_function, kwargs, description) tuples

    Returns:
        dict with results: {
            'passed': bool,
            'total_checks': int,
            'passed_checks': int,
            'failed_checks': int,
            'errors': list
        }
    """
    results = {
        "passed": True,
        "total_checks": len(checks),
        "passed_checks": 0,
        "failed_checks": 0,
        "errors": [],
    }

    for check_func, kwargs, description in checks:
        is_valid, errors = check_func(df, **kwargs)

        if is_valid:
            results["passed_checks"] += 1
        else:
            results["failed_checks"] += 1
            results["passed"] = False
            results["errors"].append({"check": description, "errors": errors})

    return results


# ==========================================
# TESTS - Null Checks
# ==========================================


def test_check_no_nulls_pass():
    """Test no nulls - should pass."""
    df = pd.DataFrame({"user_id": [1, 2, 3], "name": ["John", "Alice", "Bob"]})

    is_valid, errors = check_no_nulls(df, ["user_id", "name"])

    assert is_valid
    assert len(errors) == 0


def test_check_no_nulls_fail():
    """Test with nulls - should fail."""
    df = pd.DataFrame({"user_id": [1, None, 3], "name": ["John", "Alice", None]})

    is_valid, errors = check_no_nulls(df, ["user_id", "name"])

    assert not is_valid
    assert len(errors) == 2
    assert any("user_id" in e for e in errors)
    assert any("name" in e for e in errors)


# ==========================================
# TESTS - Duplicate Checks
# ==========================================


def test_check_no_duplicates_pass():
    """Test no duplicates - should pass."""
    df = pd.DataFrame({"user_id": [1, 2, 3], "email": ["a@test.com", "b@test.com", "c@test.com"]})

    is_valid, errors = check_no_duplicates(df)

    assert is_valid


def test_check_no_duplicates_fail():
    """Test with duplicates - should fail."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 1],  # Duplicate!
            "email": ["a@test.com", "b@test.com", "a@test.com"],
        }
    )

    is_valid, errors = check_no_duplicates(df)

    assert not is_valid
    assert "duplicate" in errors[0].lower()


def test_check_no_duplicates_subset():
    """Test duplicates on specific columns."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
            "email": ["a@test.com", "a@test.com", "c@test.com"],  # Email duplicate
        }
    )

    # Check duplicates on email only
    is_valid, errors = check_no_duplicates(df, subset=["email"])

    assert not is_valid


# ==========================================
# TESTS - Range Checks
# ==========================================


def test_check_value_range_pass():
    """Test range check - should pass."""
    df = pd.DataFrame({"age": [25, 30, 45, 60]})

    is_valid, errors = check_value_range(df, "age", min_value=0, max_value=150)

    assert is_valid


def test_check_value_range_fail_min():
    """Test range check - below minimum."""
    df = pd.DataFrame({"age": [-5, 25, 30]})  # -5 is invalid

    is_valid, errors = check_value_range(df, "age", min_value=0)

    assert not is_valid
    assert "below" in errors[0]


def test_check_value_range_fail_max():
    """Test range check - above maximum."""
    df = pd.DataFrame({"age": [25, 30, 200]})  # 200 is invalid

    is_valid, errors = check_value_range(df, "age", max_value=150)

    assert not is_valid
    assert "above" in errors[0]


# ==========================================
# TESTS - Data Type Checks
# ==========================================


def test_check_data_types_pass():
    """Test data type check - should pass."""
    df = pd.DataFrame({"user_id": [1, 2, 3], "price": [10.5, 20.0, 30.0], "name": ["A", "B", "C"]})

    expected_types = {"user_id": "numeric", "price": "numeric", "name": "string"}

    is_valid, errors = check_data_types(df, expected_types)

    assert is_valid


def test_check_data_types_fail():
    """Test data type check - should fail."""
    df = pd.DataFrame({"user_id": ["1", "2", "3"]})  # String instead of int

    expected_types = {"user_id": "numeric"}

    is_valid, errors = check_data_types(df, expected_types)

    assert not is_valid
    assert "numeric" in errors[0]


# ==========================================
# TESTS - Unique Values
# ==========================================


def test_check_unique_values_pass():
    """Test unique values - should pass."""
    df = pd.DataFrame({"user_id": [1, 2, 3]})

    is_valid, errors = check_unique_values(df, "user_id")

    assert is_valid


def test_check_unique_values_fail():
    """Test unique values - should fail."""
    df = pd.DataFrame({"user_id": [1, 2, 2, 3]})  # 2 appears twice

    is_valid, errors = check_unique_values(df, "user_id")

    assert not is_valid
    assert "duplicate" in errors[0]


# ==========================================
# TESTS - Referential Integrity
# ==========================================


def test_check_referential_integrity_pass():
    """Test foreign key validation - should pass."""
    df = pd.DataFrame({"order_id": [1, 2, 3], "user_id": [10, 20, 30]})

    valid_user_ids = {10, 20, 30, 40}  # All exist

    is_valid, errors = check_referential_integrity(df, "user_id", valid_user_ids)

    assert is_valid


def test_check_referential_integrity_fail():
    """Test foreign key validation - should fail."""
    df = pd.DataFrame({"order_id": [1, 2, 3], "user_id": [10, 20, 999]})  # 999 invalid

    valid_user_ids = {10, 20, 30}

    is_valid, errors = check_referential_integrity(df, "user_id", valid_user_ids)

    assert not is_valid
    assert "invalid" in errors[0]


# ==========================================
# TESTS - Freshness Check
# ==========================================


def test_check_freshness_pass():
    """Test data freshness - should pass."""
    now = datetime.now()
    df = pd.DataFrame({"timestamp": [now - timedelta(hours=1), now - timedelta(hours=2)]})

    is_valid, errors = check_freshness(df, "timestamp", max_age_hours=24)

    assert is_valid


def test_check_freshness_fail():
    """Test data freshness - should fail."""
    old_date = datetime.now() - timedelta(days=10)
    df = pd.DataFrame({"timestamp": [old_date]})

    is_valid, errors = check_freshness(df, "timestamp", max_age_hours=24)

    assert not is_valid
    assert "stale" in errors[0].lower()


# ==========================================
# TESTS - Composite Quality Checks
# ==========================================


def test_run_quality_checks_all_pass():
    """Test running multiple checks - all pass."""
    df = pd.DataFrame(
        {"user_id": [1, 2, 3], "age": [25, 30, 35], "email": ["a@test.com", "b@test.com", "c@test.com"]}
    )

    checks = [
        (check_no_nulls, {"columns": ["user_id", "age"]}, "No nulls in critical columns"),
        (check_no_duplicates, {}, "No duplicate rows"),
        (check_value_range, {"column": "age", "min_value": 0, "max_value": 150}, "Age in valid range"),
    ]

    results = run_quality_checks(df, checks)

    assert results["passed"]
    assert results["passed_checks"] == 3
    assert results["failed_checks"] == 0


def test_run_quality_checks_some_fail():
    """Test running multiple checks - some fail."""
    df = pd.DataFrame(
        {"user_id": [1, None, 3], "age": [25, 200, 35]}  # Null!  # Invalid!
    )

    checks = [
        (check_no_nulls, {"columns": ["user_id"]}, "No nulls"),
        (check_value_range, {"column": "age", "min_value": 0, "max_value": 150}, "Age range"),
    ]

    results = run_quality_checks(df, checks)

    assert not results["passed"]
    assert results["failed_checks"] == 2
    assert len(results["errors"]) == 2


# ==========================================
# REAL-WORLD SCENARIO
# ==========================================


def test_real_world_etl_quality_gates():
    """
    Real-world: ETL pipeline dengan quality gates.

    Scenario:
    - Load data dari source
    - Run quality checks
    - Only load to warehouse if all checks pass
    """
    # Simulate data dari API
    raw_data = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN002", "TXN003"],
            "user_id": [123, 456, 789],
            "amount": [100.0, 250.0, 75.5],
            "currency": ["USD", "USD", "USD"],
            "timestamp": [
                datetime.now() - timedelta(hours=1),
                datetime.now() - timedelta(hours=2),
                datetime.now() - timedelta(hours=3),
            ],
        }
    )

    # Define quality checks
    checks = [
        (check_no_nulls, {"columns": ["transaction_id", "user_id", "amount"]}, "No nulls in critical fields"),
        (check_unique_values, {"column": "transaction_id"}, "Unique transaction IDs"),
        (check_value_range, {"column": "amount", "min_value": 0}, "Positive amounts"),
        (check_freshness, {"timestamp_column": "timestamp", "max_age_hours": 24}, "Data is fresh"),
    ]

    # Run quality checks
    results = run_quality_checks(raw_data, checks)

    # Assert all checks pass
    assert results["passed"], f"Quality checks failed: {results['errors']}"

    # If we reach here, data is good to load!
    print(f"\n✅ All {results['total_checks']} quality checks passed!")
    print("Data is safe to load to warehouse.")


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 2-manual-checks.py -v")
