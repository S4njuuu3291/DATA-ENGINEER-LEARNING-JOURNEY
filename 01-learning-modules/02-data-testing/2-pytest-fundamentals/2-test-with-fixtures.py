"""
PYTEST FIXTURES

Fixtures = reusable test data/setup yang bisa dipakai di banyak tests.

Kenapa pakai fixtures?
- DRY principle (Don't Repeat Yourself)
- Centralized test data
- Easy to maintain
- Auto cleanup

Cara run:
    pytest 2-test-with-fixtures.py -v
"""

import pandas as pd
import pytest


# ==========================================
# FIXTURES - Reusable Test Data
# ==========================================


@pytest.fixture
def sample_users():
    """Fixture: Sample user data untuk testing."""
    return [
        {"id": 1, "name": "John", "email": "john@example.com", "age": 25},
        {"id": 2, "name": "Alice", "email": "alice@test.com", "age": 30},
        {"id": 3, "name": "Bob", "email": "bob@shop.com", "age": 22},
    ]


@pytest.fixture
def sample_transactions():
    """Fixture: Sample transaction data."""
    return [
        {"product": "Laptop", "price": 1000, "quantity": 2},
        {"product": "Mouse", "price": 50, "quantity": 5},
        {"product": "Laptop", "price": 1000, "quantity": 1},
    ]


@pytest.fixture
def sample_dataframe():
    """Fixture: Pandas DataFrame untuk testing."""
    return pd.DataFrame(
        {
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
            "price": [1299.99, 29.99, 179.99, 399.99],
            "category": ["Electronics", "Electronics", "Electronics", "Electronics"],
            "stock": [10, 50, 30, 15],
        }
    )


@pytest.fixture
def empty_dataframe():
    """Fixture: Empty DataFrame (untuk test edge case)."""
    return pd.DataFrame(columns=["product", "price", "category", "stock"])


# ==========================================
# FUNCTIONS TO TEST
# ==========================================


def filter_users_by_age(users, min_age):
    """Filter users yang age >= min_age."""
    return [u for u in users if u["age"] >= min_age]


def get_user_by_email(users, email):
    """Cari user by email."""
    for user in users:
        if user["email"] == email:
            return user
    return None


def calculate_total_value(transactions):
    """Calculate total value dari semua transactions."""
    total = 0
    for txn in transactions:
        total += txn["price"] * txn["quantity"]
    return total


def filter_expensive_products(df, min_price):
    """Filter products dengan price >= min_price."""
    return df[df["price"] >= min_price]


def add_discount_column(df, discount_percent):
    """Add kolom discounted_price ke DataFrame."""
    df = df.copy()
    df["discounted_price"] = df["price"] * (1 - discount_percent / 100)
    return df


# ==========================================
# TESTS - Menggunakan Fixtures
# ==========================================


def test_filter_users_by_age(sample_users):
    """Test filter users - pakai fixture sample_users."""
    # Min age 25: harus return John (25) dan Alice (30)
    result = filter_users_by_age(sample_users, min_age=25)

    assert len(result) == 2
    assert result[0]["name"] == "John"
    assert result[1]["name"] == "Alice"


def test_filter_users_all_match(sample_users):
    """Test filter: semua users match."""
    result = filter_users_by_age(sample_users, min_age=18)
    assert len(result) == 3  # semua users age > 18


def test_filter_users_no_match(sample_users):
    """Test filter: tidak ada yang match."""
    result = filter_users_by_age(sample_users, min_age=100)
    assert len(result) == 0


def test_get_user_by_email_found(sample_users):
    """Test cari user by email - found."""
    user = get_user_by_email(sample_users, "alice@test.com")

    assert user is not None
    assert user["name"] == "Alice"
    assert user["age"] == 30


def test_get_user_by_email_not_found(sample_users):
    """Test cari user by email - not found."""
    user = get_user_by_email(sample_users, "notfound@example.com")
    assert user is None


def test_calculate_total_value(sample_transactions):
    """Test calculate total value - pakai fixture."""
    total = calculate_total_value(sample_transactions)

    # Expected: (1000*2) + (50*5) + (1000*1) = 2000 + 250 + 1000 = 3250
    assert total == 3250


def test_calculate_total_value_empty():
    """Test dengan empty list (tanpa fixture)."""
    total = calculate_total_value([])
    assert total == 0


def test_filter_expensive_products(sample_dataframe):
    """Test filter expensive products."""
    result = filter_expensive_products(sample_dataframe, min_price=100)

    # Products >= 100: Laptop, Keyboard, Monitor
    assert len(result) == 3
    assert "Mouse" not in result["product"].values


def test_filter_expensive_products_no_match(sample_dataframe):
    """Test filter dengan threshold tinggi."""
    result = filter_expensive_products(sample_dataframe, min_price=10000)
    assert len(result) == 0


def test_add_discount_column(sample_dataframe):
    """Test add discount column."""
    result = add_discount_column(sample_dataframe, discount_percent=10)

    # Check kolom baru ada
    assert "discounted_price" in result.columns

    # Check nilai discount (Laptop: 1299.99 * 0.9 = 1169.991)
    laptop_row = result[result["product"] == "Laptop"].iloc[0]
    assert abs(laptop_row["discounted_price"] - 1169.991) < 0.01


def test_empty_dataframe_handling(empty_dataframe):
    """Test dengan empty DataFrame."""
    result = filter_expensive_products(empty_dataframe, min_price=100)

    assert len(result) == 0
    assert list(result.columns) == ["product", "price", "category", "stock"]


# ==========================================
# FIXTURE SCOPES
# ==========================================


@pytest.fixture(scope="module")
def expensive_setup():
    """
    Fixture dengan scope="module".

    Ini hanya di-execute SEKALI per module (file).
    Berguna untuk setup yang expensive (load big file, connect DB, dll).
    """
    print("\n🔧 Expensive setup running...")
    # Simulate expensive operation
    data = {"initialized": True}
    return data


def test_with_expensive_setup_1(expensive_setup):
    """Test 1 yang pakai expensive_setup."""
    assert expensive_setup["initialized"] is True


def test_with_expensive_setup_2(expensive_setup):
    """Test 2 yang pakai expensive_setup (reuse fixture)."""
    assert expensive_setup["initialized"] is True


# ==========================================
# FIXTURE dengan TEARDOWN
# ==========================================


@pytest.fixture
def temp_file(tmp_path):
    """
    Fixture yang create temp file dan cleanup setelahnya.

    tmp_path adalah built-in pytest fixture untuk temporary directory.
    """
    # Setup: create file
    file_path = tmp_path / "test_data.txt"
    file_path.write_text("sample data")

    yield file_path  # Return file path ke test

    # Teardown (after test): cleanup
    # tmp_path akan auto-cleanup oleh pytest, tapi bisa manual juga
    print(f"\n🗑️  Cleanup temp file: {file_path}")


def test_with_temp_file(temp_file):
    """Test yang pakai temp file."""
    # File sudah di-create oleh fixture
    assert temp_file.exists()
    assert temp_file.read_text() == "sample data"

    # Bisa modify file di test
    temp_file.write_text("modified data")
    assert temp_file.read_text() == "modified data"

    # Setelah test selesai, fixture akan cleanup


# ==========================================
# MULTIPLE FIXTURES
# ==========================================


@pytest.fixture
def user_data():
    """Fixture: User data."""
    return {"name": "John", "email": "john@example.com"}


@pytest.fixture
def product_data():
    """Fixture: Product data."""
    return {"product": "Laptop", "price": 1000}


def test_with_multiple_fixtures(user_data, product_data):
    """Test yang pakai multiple fixtures sekaligus."""
    # Bisa pakai multiple fixtures sebagai parameters
    assert user_data["name"] == "John"
    assert product_data["price"] == 1000


# ==========================================
# FIXTURE YANG PAKAI FIXTURE LAIN
# ==========================================


@pytest.fixture
def user_df(sample_users):
    """Fixture yang build on top of fixture lain."""
    # Convert list of dicts → DataFrame
    return pd.DataFrame(sample_users)


def test_user_dataframe(user_df):
    """Test yang pakai fixture composite."""
    assert len(user_df) == 3
    assert "name" in user_df.columns
    assert "email" in user_df.columns


# ==========================================
# TIPS & TRICKS
# ==========================================


def test_fixture_tips():
    """
    💡 KEY POINTS tentang Fixtures:

    1. Fixtures bisa return anything: dict, list, DataFrame, object, dll
    2. Fixtures bisa pakai fixtures lain (composable)
    3. Fixtures bisa punya scope:
       - function (default): run per test
       - class: run per test class
       - module: run per file
       - session: run sekali untuk semua tests

    4. Fixtures bisa punya teardown (cleanup) pakai yield
    5. Built-in fixtures: tmp_path, tmpdir, monkeypatch, capsys, dll

    6. Fixtures make tests:
       - More readable (clear test data)
       - More maintainable (change fixture = change all tests)
       - Faster (scope optimization)
    """
    assert True


if __name__ == "__main__":
    # Run dengan pytest, bukan python
    print("❌ Don't run with python!")
    print("✅ Run dengan: pytest 2-test-with-fixtures.py -v")
