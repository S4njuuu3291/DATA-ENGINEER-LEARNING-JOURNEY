"""
TEST PERTAMA ANDA!

Ini adalah test paling sederhana yang bisa Anda buat.
Tidak pakai library apapun, hanya pure Python.

Cara run:
    python 2-first-test.py
"""


# ==========================================
# FUNGSI YANG MAU DI-TEST
# ==========================================


def add(a, b):
    """Fungsi sederhana untuk menjumlahkan 2 angka."""
    return a + b


def clean_text(text):
    """
    Membersihkan text:
    - Remove whitespace di awal/akhir
    - Convert ke lowercase
    """
    return text.strip().lower()


def calculate_discount(price, discount_percent):
    """
    Hitung harga setelah diskon.

    Args:
        price: Harga original
        discount_percent: Persen diskon (0-100)

    Returns:
        Harga setelah diskon
    """
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount harus antara 0-100")

    discount_amount = price * (discount_percent / 100)
    return price - discount_amount


# ==========================================
# TESTS - Pakai Assert Statement
# ==========================================


def test_add():
    """Test fungsi add."""
    # Test case 1: Angka positif
    assert add(2, 3) == 5

    # Test case 2: Angka negatif
    assert add(-1, 1) == 0

    # Test case 3: Angka decimal
    assert add(2.5, 2.5) == 5.0

    print("✅ test_add PASSED")


def test_clean_text():
    """Test fungsi clean_text."""
    # Test case 1: Text dengan whitespace
    assert clean_text("  Hello World  ") == "hello world"

    # Test case 2: Text uppercase
    assert clean_text("PYTHON") == "python"

    # Test case 3: Text mixed case dengan spasi
    assert clean_text("  DaTa EnGiNeEr  ") == "data engineer"

    print("✅ test_clean_text PASSED")


def test_calculate_discount():
    """Test fungsi calculate_discount."""
    # Test case 1: Diskon 10%
    result = calculate_discount(100, 10)
    assert result == 90

    # Test case 2: Diskon 50%
    result = calculate_discount(200, 50)
    assert result == 100

    # Test case 3: Tanpa diskon
    result = calculate_discount(100, 0)
    assert result == 100

    # Test hasil salah:
    result = calculate_discount(100, 10)
    assert result == 93 # Ini harusnya fail

    print("✅ test_calculate_discount PASSED")


def test_calculate_discount_invalid_input():
    """Test error handling untuk input invalid."""
    # Test case: Diskon > 100 harus raise error
    try:
        calculate_discount(100, 150)
        # Kalau sampai sini, berarti error tidak di-raise (test fail)
        assert False, "Seharusnya raise ValueError"
    except ValueError as e:
        assert "Discount harus antara 0-100" in str(e)
        print("✅ test_calculate_discount_invalid_input PASSED")


# ==========================================
# ANALOGIES & LEARNING POINTS
# ==========================================


def demonstrate_why_testing_matters():
    """
    Demonstrasi: Apa yang terjadi tanpa testing.
    """
    print("\n" + "=" * 50)
    print("DEMONSTRASI: KENAPA TESTING PENTING")
    print("=" * 50 + "\n")

    # Scenario 1: Bug yang tidak ketahuan
    print("Scenario 1: Bug di fungsi (sebelum di-test)")
    print("-" * 50)

    def buggy_average(numbers):
        """Fungsi berisi bug - tidak handle list kosong."""
        return sum(numbers) / len(numbers)  # Crash kalau list kosong!

    # Tanpa test, kita tidak tahu ada bug
    print("Memanggil buggy_average([1, 2, 3]):", buggy_average([1, 2, 3]))
    print("Tampak normal...")

    # Tapi kalau ada edge case:
    try:
        print("Memanggil buggy_average([])...")
        result = buggy_average([])
        print(f"Result: {result}")
    except ZeroDivisionError:
        print("❌ CRASH! Division by zero")
        print("Bug baru ketahuan setelah production crash!\n")

    # Scenario 2: Dengan testing
    print("\nScenario 2: Kalau ada test")
    print("-" * 50)

    def safe_average(numbers):
        """Fungsi yang sudah di-fix."""
        if len(numbers) == 0:
            return 0
        return sum(numbers) / len(numbers)

    # Test akan catch bug sebelum production
    def test_safe_average():
        assert safe_average([1, 2, 3]) == 2
        assert safe_average([]) == 0  # Edge case tertangkap!
        print("✅ All tests passed - aman deploy ke production\n")

    test_safe_average()


# ==========================================
# RUNNER
# ==========================================

if __name__ == "__main__":
    print("\n🧪 Running Tests...\n")

    # Run semua tests
    test_add()
    test_clean_text()
    test_calculate_discount()
    test_calculate_discount_invalid_input()

    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)

    # Demonstrasi kenapa testing penting
    demonstrate_why_testing_matters()

    print("\n💡 KEY TAKEAWAYS:")
    print("1. Test = kode yang mengecek kode Anda")
    print("2. Struktur: ARRANGE → ACT → ASSERT")
    print("3. Test edge cases (empty, null, negative, dll)")
    print("4. Test mencegah bug masuk ke production")
    print("\n🚀 Next: Lanjut ke 3-test-data-transformation.py")
