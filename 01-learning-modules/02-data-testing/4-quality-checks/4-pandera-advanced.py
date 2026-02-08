"""
PANDERA ADVANCED - Real-World ETL Patterns

Topics:
- Multi-column validation
- Cross-field checks
- Hypothesis testing
- Schema inheritance & composition
- Real ETL pipeline scenarios

Cara run:
    pytest 4-pandera-advanced.py -v
"""

import pandas as pd
import pandera.pandas as pa
import pytest
from pandera.pandas import Column, DataFrameSchema, Check
from datetime import datetime, timedelta


# ==========================================
# MULTI-COLUMN VALIDATION
# ==========================================


# Cross-field check: end_date must be after start_date
def end_after_start(df: pd.DataFrame) -> pd.Series:
    """Check end_date > start_date."""
    return df["end_date"] > df["start_date"]


# Business rule: discounted_price must be less than original_price
def valid_discount(df: pd.DataFrame) -> pd.Series:
    """Check discounted_price < original_price."""
    return df["discounted_price"] <= df["original_price"]


# Total should equal quantity * price
def total_matches_calculation(df: pd.DataFrame) -> pd.Series:
    """Check total == quantity * price."""
    expected_total = df["quantity"] * df["price"]
    return (df["total"] - expected_total).abs() < 0.01  # Float precision


campaign_schema = DataFrameSchema(
    {
        "campaign_id": Column(int, unique=True),
        "start_date": Column(pa.DateTime),
        "end_date": Column(pa.DateTime),
        "budget": Column(float, Check.greater_than(0)),
    },
    checks=[Check(end_after_start, error="end_date must be after start_date")],
)


product_pricing_schema = DataFrameSchema(
    {
        "product_id": Column(int),
        "original_price": Column(float, Check.greater_than(0)),
        "discounted_price": Column(float, Check.greater_than(0)),
        "discount_percent": Column(float, Check.in_range(0, 100)),
    },
    checks=[Check(valid_discount, error="Discounted price must be <= original price")],
)


transaction_schema = DataFrameSchema(
    {
        "transaction_id": Column(str, unique=True),
        "quantity": Column(int, Check.greater_than(0)),
        "price": Column(float, Check.greater_than(0)),
        "total": Column(float, Check.greater_than(0)),
    },
    checks=[Check(total_matches_calculation, error="Total must equal quantity * price")],
)


# ==========================================
# HYPOTHESIS TESTING
# ==========================================

# Statistical hypothesis: mean should be around a value
def mean_in_expected_range(series: pd.Series, mean_min: float, mean_max: float) -> bool:
    """Check if series mean is within expected range."""
    actual_mean = series.mean()
    return mean_min <= actual_mean <= mean_max


# Check for outliers using IQR method
def no_extreme_outliers(series: pd.Series, multiplier: float = 3.0) -> pd.Series:
    """
    Detect outliers using IQR method.
    
    Points outside [Q1 - multiplier*IQR, Q3 + multiplier*IQR] are outliers.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)
    return series.between(lower_bound, upper_bound)


sales_metrics_schema = DataFrameSchema(
    {
        "date": Column(pa.DateTime),
        "daily_revenue": Column(
            float,
            checks=[
                Check.greater_than(0),
                Check(lambda s: mean_in_expected_range(s, 10000, 50000), 
                      error="Mean daily revenue outside expected range (10k-50k)"),
            ],
        ),
        "transactions_count": Column(
            int,
            checks=[
                Check.greater_than(0),
                Check(no_extreme_outliers, error="Extreme outliers detected in transaction count"),
            ],
        ),
    }
)


# ==========================================
# SCHEMA INHERITANCE & COMPOSITION
# ==========================================


# Base schema for all user types
base_user_schema = DataFrameSchema(
    {
        "user_id": Column(int, unique=True, coerce=True),
        "email": Column(str, Check.str_matches(r"^[\w\.-]+@[\w\.-]+\.\w+$")),
        "created_at": Column(pa.DateTime),
    }
)


# Extend for customer schema
customer_schema = base_user_schema.add_columns(
    {
        "total_purchases": Column(int, Check.greater_than_or_equal_to(0)),
        "loyalty_points": Column(int, Check.greater_than_or_equal_to(0)),
        "tier": Column(str, Check.isin(["bronze", "silver", "gold", "platinum"])),
    }
)


# Extend for admin schema
admin_schema = base_user_schema.add_columns(
    {
        "role": Column(str, Check.isin(["admin", "super_admin", "moderator"])),
        "permissions": Column(str),  # JSON string of permissions
        "last_login": Column(pa.DateTime, nullable=True),
    }
)


# ==========================================
# TESTS - Multi-Column Validation
# ==========================================


def test_campaign_dates_valid():
    """Test campaign dengan valid date range."""
    df = pd.DataFrame(
        {
            "campaign_id": [1, 2],
            "start_date": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "end_date": pd.to_datetime(["2024-01-31", "2024-02-28"]),
            "budget": [10000.0, 20000.0],
        }
    )

    validated_df = campaign_schema.validate(df)
    assert len(validated_df) == 2


def test_campaign_dates_invalid():
    """Test campaign dengan end_date sebelum start_date."""
    df = pd.DataFrame(
        {
            "campaign_id": [1],
            "start_date": pd.to_datetime(["2024-02-01"]),
            "end_date": pd.to_datetime(["2024-01-01"]),  # Invalid!
            "budget": [10000.0],
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        campaign_schema.validate(df)

    assert "end_date must be after start_date" in str(exc_info.value)


def test_product_pricing_valid():
    """Test product pricing dengan valid discount."""
    df = pd.DataFrame(
        {
            "product_id": [1, 2],
            "original_price": [100.0, 200.0],
            "discounted_price": [90.0, 180.0],
            "discount_percent": [10.0, 10.0],
        }
    )

    validated_df = product_pricing_schema.validate(df)
    assert len(validated_df) == 2


def test_product_pricing_invalid_discount():
    """Test invalid discount (discounted > original)."""
    df = pd.DataFrame(
        {
            "product_id": [1],
            "original_price": [100.0],
            "discounted_price": [150.0],  # Higher than original!
            "discount_percent": [10.0],
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        product_pricing_schema.validate(df)

    assert "Discounted price must be" in str(exc_info.value)


def test_transaction_total_calculation_valid():
    """Test transaction dengan correct total."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001", "TXN002"],
            "quantity": [2, 5],
            "price": [100.0, 50.0],
            "total": [200.0, 250.0],  # Correct!
        }
    )

    validated_df = transaction_schema.validate(df)
    assert len(validated_df) == 2


def test_transaction_total_calculation_invalid():
    """Test transaction dengan wrong total."""
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN001"],
            "quantity": [2],
            "price": [100.0],
            "total": [150.0],  # Should be 200!
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        transaction_schema.validate(df)

    assert "Total must equal" in str(exc_info.value)


# ==========================================
# TESTS - Hypothesis Testing
# ==========================================


def test_sales_metrics_within_expected_range():
    """Test sales metrics dalam expected range."""
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "daily_revenue": [25000.0] * 30,  # Mean = 25k (dalam range 10k-50k)
            "transactions_count": [100] * 30,
        }
    )

    validated_df = sales_metrics_schema.validate(df)
    assert len(validated_df) == 30


def test_sales_metrics_mean_too_low():
    """Test mean revenue terlalu rendah."""
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "daily_revenue": [5000.0] * 30,  # Mean = 5k (< 10k minimum)
            "transactions_count": [50] * 30,
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        sales_metrics_schema.validate(df)

    assert "outside expected range" in str(exc_info.value)


def test_sales_metrics_with_outliers():
    """Test detection of extreme outliers."""
    # Normal values + 1 extreme outlier
    normal_txns = [100] * 29
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "daily_revenue": [25000.0] * 30,
            "transactions_count": normal_txns + [10000],  # Extreme outlier!
        }
    )

    with pytest.raises(pa.errors.SchemaError) as exc_info:
        sales_metrics_schema.validate(df)

    assert "outlier" in str(exc_info.value).lower()


# ==========================================
# TESTS - Schema Inheritance
# ==========================================


def test_customer_schema():
    """Test customer schema (extends base_user_schema)."""
    df = pd.DataFrame(
        {
            "user_id": [1, 2],
            "email": ["john@example.com", "alice@test.com"],
            "created_at": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "total_purchases": [10, 25],
            "loyalty_points": [100, 500],
            "tier": ["bronze", "gold"],
        }
    )

    validated_df = customer_schema.validate(df)
    assert len(validated_df) == 2


def test_customer_schema_invalid_tier():
    """Test invalid tier value."""
    df = pd.DataFrame(
        {
            "user_id": [1],
            "email": ["john@example.com"],
            "created_at": pd.to_datetime(["2024-01-01"]),
            "total_purchases": [10],
            "loyalty_points": [100],
            "tier": ["diamond"],  # Invalid!
        }
    )

    with pytest.raises(pa.errors.SchemaError):
        customer_schema.validate(df)


def test_admin_schema():
    """Test admin schema (extends base_user_schema)."""
    df = pd.DataFrame(
        {
            "user_id": [1],
            "email": ["admin@example.com"],
            "created_at": pd.to_datetime(["2024-01-01"]),
            "role": ["super_admin"],
            "permissions": ['["read", "write", "delete"]'],
            "last_login": pd.to_datetime(["2024-01-24"]),
        }
    )

    validated_df = admin_schema.validate(df)
    assert len(validated_df) == 1


# ==========================================
# REAL-WORLD: ETL QUALITY GATES
# ==========================================


class ETLPipeline:
    """
    Real-world ETL pipeline dengan quality gates.
    
    Pattern:
    1. Extract (raw data)
    2. Validate raw (basic checks)
    3. Transform
    4. Validate transformed (strict checks)
    5. Load
    """

    # Schema untuk raw data (loose validation)
    raw_schema = DataFrameSchema(
        {
            "user_id": Column(str),  # Masih string dari source
            "purchase_date": Column(str),  # Masih string
            "amount": Column(str),  # Masih string
            "product_category": Column(str, nullable=True),
        },
        strict=False,  # Allow extra columns
    )

    # Schema untuk transformed data (strict validation)
    transformed_schema = DataFrameSchema(
        {
            "user_id": Column(int, Check.greater_than(0)),
            "purchase_date": Column(pa.DateTime),
            "amount": Column(float, Check.greater_than(0)),
            "product_category": Column(str),
            "year": Column(int),
            "month": Column(int, Check.in_range(1, 12)),
        },
        strict=True,
        checks=[
            Check(
                lambda df: (df["amount"] > 0).all(),
                error="All amounts must be positive",
            )
        ],
    )

    @staticmethod
    @pa.check_output(raw_schema)
    def extract(source_file: str = None)->pd.DataFrame:
        """Stage 1: Extract raw data."""
        # Simulate extracting from source
        return pd.DataFrame(
            {
                "user_id": ["123", "456", "789"],
                "purchase_date": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "amount": ["100.50", "200.00", "75.25"],
                "product_category": ["Electronics", None, "Books"],
                "extra_column": ["ignore", "me", "please"],
            }
        )

    @staticmethod
    @pa.check_output(transformed_schema)
    def transform(df: pd.DataFrame) -> pd.DataFrame:
        """Stage 2: Transform & clean data."""
        result = df.copy()

        # Type conversions
        result["user_id"] = result["user_id"].astype(int)
        result["purchase_date"] = pd.to_datetime(result["purchase_date"])
        result["amount"] = result["amount"].astype(float)

        # Fill nulls
        result["product_category"] = result["product_category"].fillna("Unknown")

        # Add derived columns
        result["year"] = result["purchase_date"].dt.year.astype("int64")
        result["month"] = result["purchase_date"].dt.month.astype("int64")

        # Remove extra columns
        result = result[
            ["user_id", "purchase_date", "amount", "product_category", "year", "month"]
        ]

        return result

    @classmethod
    def run(cls) -> pd.DataFrame:
        """Run full ETL pipeline with quality gates."""
        # Extract
        raw_data = cls.extract()
        print("✅ Extract complete & validated")

        # Transform
        clean_data = cls.transform(raw_data)
        print("✅ Transform complete & validated")

        # Load (simulated)
        print(f"✅ Ready to load {len(clean_data)} records")

        return clean_data


def test_etl_pipeline_success():
    """Test successful ETL pipeline run."""
    result = ETLPipeline.run()

    # Verify output
    assert len(result) == 3
    assert result["user_id"].dtype == int
    assert pd.api.types.is_datetime64_any_dtype(result["purchase_date"])
    assert result["amount"].dtype == float
    assert "extra_column" not in result.columns


def test_etl_pipeline_raw_validation_fails():
    """Test ETL fails if raw data invalid."""

    # Override extract to return bad data
    @pa.check_output(ETLPipeline.raw_schema)
    def bad_extract(df=None) -> pd.DataFrame:
        return pd.DataFrame(
            {
                # Missing required column: user_id
                "purchase_date": ["2024-01-15"],
                "amount": ["100.50"],
            }
        )

    with pytest.raises(pa.errors.SchemaError):
        bad_extract()


def test_etl_pipeline_transform_validation_fails():
    """Test ETL fails if transformed data invalid."""
    # Create raw data that passes raw schema but fails after transform
    raw_data = pd.DataFrame(
        {
            "user_id": ["abc"],  # Can't convert to int!
            "purchase_date": ["2024-01-15"],
            "amount": ["100.50"],
            "product_category": ["Books"],
        }
    )

    with pytest.raises((ValueError, pa.errors.SchemaError)):
        ETLPipeline.transform(raw_data)


# ==========================================
# ADVANCED PATTERNS
# ==========================================


def test_advanced_patterns_summary():
    """
    💡 ADVANCED PANDERA PATTERNS:

    1. MULTI-COLUMN VALIDATION
       - Cross-field checks (end_date > start_date)
       - Business rules (discount < original)
       - Calculated fields (total = qty * price)

    2. HYPOTHESIS TESTING
       - Mean/std within expected range
       - Outlier detection (IQR method)
       - Distribution checks

    3. SCHEMA COMPOSITION
       - Base schemas untuk reuse
       - Inheritance (add_columns)
       - Schema per data source

    4. ETL QUALITY GATES
       - Validate at each stage
       - Loose → strict validation
       - Fail fast if quality bad

    5. DECORATOR PATTERNS
       - @check_input for function arguments
       - @check_output for return values
       - Type safety + runtime validation

    REAL-WORLD BENEFITS:
    ✅ Catch data quality issues early
    ✅ Self-documenting schemas
    ✅ Prevent bad data in production
    ✅ Easy to maintain & extend

    USE CASES:
    - ETL pipelines
    - API data validation
    - ML feature engineering
    - Data warehouse ingestion
    - Microservice communication
    """
    assert True


if __name__ == "__main__":
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 4-pandera-advanced.py -v")
    print("\n💡 Key concepts:")
    print("   - Multi-column validation")
    print("   - Statistical hypothesis testing")
    print("   - Schema inheritance")
    print("   - ETL quality gates")
