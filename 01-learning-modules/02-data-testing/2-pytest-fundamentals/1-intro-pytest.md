# Kenapa Pytest > Unittest (Python Built-in)

## 🥊 Battle: pytest vs unittest

Python punya built-in testing framework namanya `unittest`. Tapi kenapa hampir semua Data Engineer pakai **pytest**?

### Unittest (Built-in Python)

```python
import unittest

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)

if __name__ == '__main__':
    unittest.main()
```

**Masalahnya:**
- ❌ Harus bikin class (boilerplate code)
- ❌ Pakai `self.assertEqual`, `self.assertTrue`, dll (banyak hafalan)
- ❌ Kurang flexible untuk data testing

### Pytest (Modern Way)

```python
def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2
```

**Keuntungannya:**
- ✅ Simple, pakai `assert` biasa
- ✅ Tidak perlu class
- ✅ Auto-discover tests (cukup nama fungsi pakai prefix `test_`)
- ✅ Error messages lebih informatif
- ✅ Ekosistem plugin yang kaya (pytest-cov, pytest-benchmark, dll)

---

## 🎯 Core Features Pytest

### 1. Auto-Discovery

Pytest otomatis cari files yang:
- Nama file: `test_*.py` atau `*_test.py`
- Nama function: `test_*()`
- Nama class: `Test*`

Cukup run `pytest` di terminal, dia akan cari semua tests!

### 2. Assert Introspection

Kalau test fail, pytest kasih info detail:

```python
def test_example():
    expected = {"name": "John", "age": 30}
    actual = {"name": "John", "age": 25}
    assert expected == actual
```

Output:
```
AssertionError: assert {'age': 30, '...hn'} == {'age': 25, '...hn'}
  Omitting 1 identical items, use -vv to show
  Differing items:
  {'age': 30} != {'age': 25}
```

Sangat helpful untuk debug!

### 3. Fixtures (Reusable Data)

Fixtures = data atau setup yang bisa dipakai berulang kali.

```python
import pytest

@pytest.fixture
def sample_dataframe():
    """Fixture: DataFrame untuk testing."""
    return pd.DataFrame({
        'product': ['A', 'B', 'C'],
        'price': [100, 200, 300]
    })

def test_filter_expensive_products(sample_dataframe):
    # Pakai fixture sebagai parameter
    result = filter_by_price(sample_dataframe, min_price=150)
    assert len(result) == 2
```

### 4. Parametrize (Test Banyak Case)

Test dengan berbagai input tanpa copy-paste code:

```python
@pytest.mark.parametrize("input,expected", [
    (0, 32),      # 0°C = 32°F
    (100, 212),   # 100°C = 212°F
    (-40, -40),   # -40°C = -40°F (same!)
])
def test_celsius_to_fahrenheit(input, expected):
    assert convert_temp(input) == expected
```

Run sekali, test 3 cases!

---

## 🚀 Pytest Commands

### Basic Commands

```bash
# Run all tests
pytest

# Run dengan verbose output
pytest -v

# Run specific file
pytest test_my_module.py

# Run specific function
pytest test_my_module.py::test_my_function

# Run tests yang match keyword
pytest -k "email"  # run semua test yang ada kata "email"
```

### Useful Options

```bash
# Stop at first failure
pytest -x

# Show print statements
pytest -s

# Show detailed diff
pytest -vv

# Run only failed tests from last run
pytest --lf

# Coverage report
pytest --cov=mymodule
```

---

## 💡 Best Practices

### 1. Test Naming Convention

```python
# ✅ GOOD
def test_calculate_discount_returns_correct_value():
    ...

def test_clean_email_handles_whitespace():
    ...

# ❌ BAD
def test1():  # Tidak jelas test apa
    ...

def check_email():  # Tidak pakai prefix "test_"
    ...
```

### 2. One Assert Per Test (Ideally)

```python
# ✅ GOOD - focused
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, 1) == 0

# ⚠️ OK - related assertions
def test_email_cleaning():
    assert clean_email("  TEST@GMAIL.COM  ") == "test@gmail.com"
    assert clean_email("") == ""
```

### 3. Arrange-Act-Assert Pattern

```python
def test_aggregate_sales():
    # ARRANGE: Setup test data
    transactions = [
        {'product': 'A', 'amount': 100},
        {'product': 'A', 'amount': 200},
    ]
    
    # ACT: Execute function
    result = aggregate_by_product(transactions)
    
    # ASSERT: Verify result
    assert result['A'] == 300
```

---

## 🎓 Next Step

Sekarang kita akan praktik:
1. Convert unittest ke pytest
2. Pakai fixtures untuk reusable data
3. Parametrize tests
4. Handle exceptions

**Ready? Lanjut ke file berikutnya!**

---

## 📚 Resources

- [Pytest Official Docs](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parametrize](https://docs.pytest.org/en/stable/parametrize.html)
