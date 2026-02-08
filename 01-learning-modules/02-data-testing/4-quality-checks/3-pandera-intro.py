"""
PANDERA INTRODUCTION

Pandera = Library untuk DataFrame schema validation & data quality checks.

Why Pandera?
✅ Schema-based validation (define once, use everywhere)
✅ Statistical checks (mean, std, min, max)
✅ Type coercion
✅ Detailed error messages
✅ Integration dengan pandas workflow

Cara run:
    pytest 3-pandera-intro.py -v

Note: Install dulu: pip install pandera
"""

import pandas as pd
import pandera.pandas as pa
import pytest
from pandera.pandas import Column, DataFrameSchema, Check


# ==========================================
# BASIC PANDERA SCHEMAS
# ==========================================


# Schema 1: Simple user schema
user_schema = DataFrameSchema(
    {
        "user_id": Column(int, Check.greater_than(0)),
        "name": Column(str, Check.str_length(min_value=1)),
        "email": Column(str, Check.str_matches(r"^[\w\.-]+@[\w\.-]+\.\w+$")),
        "age": Column(int, Check.in_range(0, 150)),
    }
)


# Schema 2: Sales transaction schema
sales_schema = DataFrameSchema(
    {
        "transaction_id": Column(str, unique=True),
        "product": Column(str),
        "quantity": Column(int, Check.greater_than(0)),
        "price": Column(float, Check.greater_than(0)),
        "discount": Column(float, Check.in_range(0, 1), nullable=True),
    },
    strict=True,  # Tidak boleh ada kolom extra
)


# Schema 3: With nullable columns
product_schema = DataFrameSchema(
    {
        "product_id": Column(int, unique=True),
        "name": Column(str),
        "price": Column(float, Check.greater_than(0)),
        "description": Column(str, nullable=True),  # Boleh null
        "stock": Column(int, Check.greater_than_or_equal_to(0)),
    }
)


# ==========================================
# STATISTICAL CHECKS
# ==========================================


# Schema dengan statistical bounds
sensor_data_schema = DataFrameSchema(
    {
        "sensor_id": Column(int),
        "temperature": Column(
            float,
            checks=[
                Check.in_range(-50, 100),  # Physical bounds
                Check.less_than_or_equal_to(50),  # Expected max
            ],
        ),
        "humidity": Column(
            float,
            checks=[
                Check.in_range(0, 100),  # Percentage
                Check(lambda s: s.mean() > 20, error="Mean humidity too low"),
                Check(lambda s: s.mean() < 80, error="Mean humidity too high"),
            ],
        ),
    }
)


# ==========================================
# CUSTOM CHECKS
# ==========================================


def email_must_be_lowercase(series: pd.Series) -> pd.Series:
    """Custom check: email harus lowercase."""
    return series == series.str.lower()


def no_weekends(series: pd.Series) -> pd.Series:
    """Custom check: date tidak boleh weekend."""
    return series.dt.dayofweek < 5  # Monday=0, Friday=4


business_schema = DataFrameSchema(
    {
        "email": Column(str, Check(email_must_be_lowercase, error="Email must be lowercase")),
        "business_date": Column(
            pa.DateTime, Check(no_weekends, error="Business dates cannot be weekends")
        ),
        "revenue": Column(float, Check.greater_than(0)),
    }
)


# ==========================================
# TESTS - Basic Schema Validation
# ==========================================


def test_user_schema_valid():
    """Test valid user DataFrame."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2, 3],
            "name": ["John", "Alice", "Bob"],
            "email": ["john@example.com", "alice@test.com", "bob@shop.com"],
            "age": [25, 30, 28],
        }
    )

    # Validate
    validated_df = user_schema.validate(df)

    # Should pass without errors
    assert len(validated_df) == 3


def test_user_schema_invalid_age():
    """Test invalid age (out of range)."""
    df = pd.DataFrame(
        {
            "user_id": [1],
            "name": ["John"],
            "email": ["john@example.com"],
            "age": [200],  # Invalid!
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        user_schema.validate(df)

    # Check error message
    assert "age" in str(exc_info.value).lower()


def test_user_schema_invalid_email():
    """Test invalid email format."""
    df = pd.DataFrame(
        {
            "user_id": [1],
            "name": ["John"],
            "email": ["not-an-email"],  # Invalid!
            "age": [25],
        }
    )

    with pytest.raises(pa.errors.SchemaError):
        user_schema.validate(df)


# ==========================================
# TESTS - Nullable Columns
# ==========================================


def test_product_schema_with_null_description():
    """Test nullable column (description can be null)."""
    df = pd.DataFrame(
        {
            "product_id": [1, 2],
            "name": ["Laptop", "Mouse"],
            "price": [1000.0, 50.0],
            "description": ["Gaming laptop", None],  # None is OK!
            "stock": [10, 50],
        }
    )

    validated_df = product_schema.validate(df)
    assert len(validated_df) == 2


def test_product_schema_null_in_required_column():
    """Test null in required column (should fail)."""
    df = pd.DataFrame(
        {
            "product_id": [1, 2],
            "name": ["Laptop", None],  # NULL not allowed!
            "price": [1000.0, 50.0],
            "description": ["Gaming laptop", "Wireless mouse"],
            "stock": [10, 50],
        }
    )

    with pytest.raises(pa.errors.SchemaError):
        product_schema.validate(df)


# ==========================================
# TESTS - Uniqueness
# ==========================================


def test_sales_schema_unique_transaction_id():
    """Test unique constraint on transaction_id."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN002"],
            "product": ["Laptop", "Mouse"],
            "quantity": [1, 2],
            "price": [1000.0, 50.0],
            "discount": [0.1, None],
        }
    )

    validated_df = sales_schema.validate(df)
    assert len(validated_df) == 2


def test_sales_schema_duplicate_transaction_id():
    """Test duplicate transaction_id (should fail)."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN001"],  # Duplicate!
            "product": ["Laptop", "Mouse"],
            "quantity": [1, 2],
            "price": [1000.0, 50.0],
            "discount": [0.1, None],
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        sales_schema.validate(df)

    assert "duplicate" in str(exc_info.value).lower()


# ==========================================
# TESTS - Strict Mode
# ==========================================


def test_sales_schema_strict_mode_extra_column():
    """Test strict mode (no extra columns allowed)."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001"],
            "product": ["Laptop"],
            "quantity": [1],
            "price": [1000.0],
            "discount": [0.1],
            "extra_column": ["should fail"],  # Extra column!
        }
    )

    with pytest.raises(pa.errors.SchemaError):
        sales_schema.validate(df)


# ==========================================
# TESTS - Statistical Checks
# ==========================================


def test_sensor_data_within_bounds():
    """Test sensor data dengan statistical checks."""
    df = pd.DataFrame(
        {
            "sensor_id": [1, 1, 1, 1],
            "temperature": [20.0, 22.0, 21.5, 23.0],
            "humidity": [45.0, 50.0, 48.0, 52.0],  # Mean ~49
        }
    )

    validated_df = sensor_data_schema.validate(df)
    assert len(validated_df) == 4


def test_sensor_data_mean_too_high():
    """Test sensor data dengan mean humidity terlalu tinggi."""
    df = pd.DataFrame(
        {
            "sensor_id": [1, 1, 1],
            "temperature": [20.0, 22.0, 21.0],
            "humidity": [85.0, 90.0, 88.0],  # Mean > 80!
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        sensor_data_schema.validate(df)

    assert "humidity too high" in str(exc_info.value).lower()


# ==========================================
# TESTS - Custom Checks
# ==========================================


def test_business_schema_valid():
    """Test business schema dengan custom checks."""
    df = pd.DataFrame(
        {
            "email": ["john@example.com", "alice@test.com"],
            "business_date": pd.to_datetime(["2024-01-15", "2024-01-16"]),  # Monday, Tuesday
            "revenue": [1000.0, 1500.0],
        }
    )

    validated_df = business_schema.validate(df)
    assert len(validated_df) == 2


def test_business_schema_uppercase_email():
    """Test email must be lowercase."""
    df = pd.DataFrame(
        {
            "email": ["JOHN@EXAMPLE.COM"],  # Uppercase!
            "business_date": pd.to_datetime(["2024-01-15"]),
            "revenue": [1000.0],
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        business_schema.validate(df)

    assert "lowercase" in str(exc_info.value).lower()


def test_business_schema_weekend_date():
    """Test business date cannot be weekend."""
    df = pd.DataFrame(
        {
            "email": ["john@example.com"],
            "business_date": pd.to_datetime(["2024-01-13"]),  # Saturday!
            "revenue": [1000.0],
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        business_schema.validate(df)

    assert "weekend" in str(exc_info.value).lower()


# ==========================================
# DECORATOR-BASED VALIDATION
# ==========================================


@pa.check_input(user_schema)
def process_users(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process user data.

    Pandera automatically validates input!
    If validation fails, error is raised before function runs.
    """
    # Add computed column
    df["age_group"] = pd.cut(df["age"], bins=[0, 18, 30, 50, 150], labels=["child", "young", "adult", "senior"])
    return df


@pa.check_output(
    DataFrameSchema(
        {
            "user_id": Column(int),
            "total_spent": Column(float, Check.greater_than_or_equal_to(0)),
        }
    )
)
def calculate_user_spending(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total spending per user.

    Pandera validates OUTPUT of this function!
    """
    return df.groupby("user_id").agg(total_spent=("amount", "sum")).reset_index()


# ==========================================
# TESTS - Decorator Validation
# ==========================================


def test_decorator_input_validation_pass():
    """Test @check_input decorator - valid data."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2],
            "name": ["John", "Alice"],
            "email": ["john@example.com", "alice@test.com"],
            "age": [25, 30],
        }
    )

    result = process_users(df)

    assert "age_group" in result.columns
    assert len(result) == 2


def test_decorator_input_validation_fail():
    """Test @check_input decorator - invalid data."""
    df = pd.DataFrame(
        {
            "user_id": [1],
            "name": ["John"],
            "email": ["invalid-email"],  # Bad!
            "age": [25],
        }
    )

    with pytest.raises(pa.errors.SchemaError):
        process_users(df)


def test_decorator_output_validation_pass():
    """Test @check_output decorator."""
    df = pd.DataFrame({"user_id": [1, 1, 2], "amount": [100.0, 200.0, 150.0]})

    result = calculate_user_spending(df)

    assert len(result) == 2
    assert result.loc[result["user_id"] == 1, "total_spent"].iloc[0] == 300.0


# ==========================================
# TYPE COERCION
# ==========================================


schema_with_coercion = DataFrameSchema(
    {"user_id": Column(int, coerce=True), "price": Column(float, coerce=True)}, coerce=True
)


def test_type_coercion():
    """
    Test type coercion (auto convert types).

    Pandera can automatically convert compatible types.
    """
    df = pd.DataFrame(
        {
            "user_id": ["1", "2", "3"],  # String → int
            "price": ["100.5", "200.0", "50.25"],  # String → float
        }
    )

    validated_df = schema_with_coercion.validate(df)

    # Types should be coerced
    assert validated_df["user_id"].dtype == int
    assert validated_df["price"].dtype == float


# ==========================================
# COMPARISON: Manual vs Pandera
# ==========================================


def test_comparison_manual_vs_pandera():
    """
    💡 COMPARISON: Manual Checks vs Pandera

    Manual (dari file sebelumnya):
    ------------------------------------------------
    def validate_df(df):
        # Check nulls
        assert df['user_id'].notna().all()
        # Check range
        assert df['age'].between(0, 150).all()
        # Check types
        assert df['user_id'].dtype == int
        # Check unique
        assert df['user_id'].nunique() == len(df)
        # ... banyak lagi ...

    Pandera:
    ------------------------------------------------
    schema = DataFrameSchema({
        'user_id': Column(int, unique=True),
        'age': Column(int, Check.in_range(0, 150))
    })
    schema.validate(df)

    Benefits Pandera:
    ✅ Deklaratif (define schema, not imperative checks)
    ✅ Reusable (1 schema, many DataFrames)
    ✅ Better error messages (shows exact failures)
    ✅ Statistical checks built-in
    ✅ Type coercion
    ✅ Decorator support

    When to use Manual:
    - Very custom logic
    - Learning fundamentals

    When to use Pandera:
    - Production pipelines
    - Reusable schemas
    - Statistical validation
    - 90% of real-world cases
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 3-pandera-intro.py -v")
    print("\n💡 Install Pandera first:")
    print("   pip install pandera")
