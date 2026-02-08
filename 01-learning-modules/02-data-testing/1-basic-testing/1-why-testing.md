# Mengapa Testing Penting untuk Data Engineer?

## 🎭 Analogi: Restoran vs Data Pipeline

Bayangkan Anda punya restoran. Ada 2 chef:

### Chef A (Tanpa Testing):
- Masak langsung serve ke customer
- "Semoga rasanya enak" 🤞
- Kalau ada komplain, baru tahu ada yang salah
- Customer sudah kecewa, review jelek

### Chef B (Dengan Testing):
- Setiap masak, icip dulu sebelum serve
- Cek suhu, rasa, presentasi
- Kalau ada yang salah, perbaiki sebelum ke customer
- Customer selalu puas

**Anda mau jadi chef yang mana?**

Di Data Engineering, "customer" Anda adalah:
- Business Analyst yang pakai data Anda untuk dashboard
- Data Scientist yang pakai data untuk ML model
- CEO yang buat keputusan based on data Anda

Kalau data salah? Keputusan bisnis salah. Bisa rugi jutaan.

---

## 🔥 Skenario Real: Kenapa Pipeline Rusak

### Skenario 1: Bug di Production

**Situasi:**
Anda bikin ETL pipeline untuk hitung total penjualan per hari.

```python
def calculate_daily_sales(transactions):
    # Bug: tidak handle null price
    total = sum([t['price'] * t['quantity'] for t in transactions])
    return total
```

**Yang Terjadi:**
- Development: Semua berjalan lancar (kebetulan test data tidak ada null)
- Production: **CRASH!** Ada 1 transaksi yang price-nya null
- Dashboard CEO kosong
- Boss telpon Anda jam 2 pagi 😱

**Kalau ada testing:**
```python
def test_calculate_daily_sales_with_null_price():
    transactions = [
        {'price': 100, 'quantity': 2},
        {'price': None, 'quantity': 1},  # ini yang bikin crash!
    ]
    
    # Test akan FAIL, bug ketahuan sebelum deploy
    result = calculate_daily_sales(transactions)
```

---

### Skenario 2: Refactor Code Rusak yang Lain

**Situasi:**
Anda perbaiki 1 fungsi, tapi tanpa sadar ngerusak fungsi lain.

```python
# Dulu
def clean_email(email):
    return email.strip().lower()

# Refactor (untuk fix bug whitespace)
def clean_email(email):
    return email.replace(" ", "").lower()  # Bug: ini rusak format email!
```

**Yang Terjadi:**
- Email "user @gmail.com" jadi "user@gmail.com" ✅
- Tapi email yang valid "user.name@gmail.com" jadi "user.name@gmail.com" ✅
- Tunggu... email "my email@test.com" (invalid) jadi "myemail@test.com" (jadi valid!) ❌

**Kalau ada testing:**
Test akan langsung fail, Anda tahu ada side effect.

---

## 🧪 Apa Itu Testing?

Testing = **Menulis kode untuk mengecek kode**

Strukturnya sederhana:

```python
def test_something():
    # 1. ARRANGE: Persiapkan data test
    input_data = "dirty data  "
    
    # 2. ACT: Jalankan fungsi yang mau di-test
    result = clean_data(input_data)
    
    # 3. ASSERT: Cek apakah hasilnya sesuai ekspektasi
    assert result == "dirty data"  # harusnya clean (trim whitespace)
```

**Analogi:** Seperti guru yang bikin soal ujian untuk murid.
- Guru (Anda) tahu jawaban yang benar
- Kalau murid (kode Anda) jawab salah → fail

---

## 📊 Tipe Testing dalam Data Engineering

### 1. **Unit Testing** (Most Common)
Test 1 fungsi secara terpisah.

```python
def test_convert_celsius_to_fahrenheit():
    assert convert_temperature(0) == 32
    assert convert_temperature(100) == 212
```

### 2. **Integration Testing**
Test beberapa komponen sekaligus.

```python
def test_full_etl_pipeline():
    # Extract dari API
    data = extract_from_api()
    
    # Transform
    cleaned = transform_data(data)
    
    # Load ke database
    load_to_db(cleaned)
    
    # Verify data ada di database
    assert count_records_in_db() == len(cleaned)
```

### 3. **Data Quality Testing**
Test kualitas data (bukan kode).

```python
def test_no_duplicate_users():
    df = load_users_from_db()
    assert df['user_id'].nunique() == len(df)  # tidak ada duplikat
```

---

## ✅ Kapan Harus Nulis Test?

**Wajib test kalau:**
- ✅ Fungsi transformasi data (cleaning, aggregation)
- ✅ Business logic (calculation, validation)
- ✅ Kode yang sering berubah
- ✅ Kode yang critical (kalau salah, impact besar)

**Tidak perlu test kalau:**
- ❌ Kode yang hanya print/log
- ❌ Kode throw-away (temporary script)
- ❌ Kode yang sangat simple (getter/setter)

**Prinsip:** Kalau kode Anda crash, apakah ada orang lain yang kena impact? Kalau ya, **wajib test**.

---

## 🎯 Manfaat Testing

1. **Confidence** - Deploy tanpa deg-degan
2. **Documentation** - Test = contoh cara pakai
3. **Faster Debugging** - Tau persis mana yang rusak
4. **Refactor Safely** - Ubah kode tanpa takut rusak
5. **Better Code Quality** - Kode yang testable = kode yang well-designed

---

## 🚀 Next Step

Sekarang kita akan praktik langsung:
1. Nulis test paling sederhana
2. Run test pakai pytest
3. Test transformasi data sederhana

**Ready? Lanjut ke file `2-first-test.py`!**

---

## 💭 Renungan

> "Testing doesn't just find bugs. It prevents bugs from existing in the first place by forcing you to think about edge cases."

Pertanyaan untuk Anda:
- Pernah tidak deploy kode yang ternyata ada bug?
- Berapa lama waktu Anda untuk debug issue di production?
- Kalau ada test, apakah itu bisa dicegah?
