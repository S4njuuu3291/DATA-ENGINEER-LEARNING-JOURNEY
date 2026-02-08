# 🧪 Data Testing Framework

Framework lengkap untuk belajar testing dalam konteks **Data Engineering** - dari pemula sampai advanced.

## 🎯 Kenapa Testing Penting untuk Data Engineer?

Bayangkan Anda bikin ETL pipeline yang:
- Extract data dari API
- Transform datanya (cleaning, aggregation)
- Load ke database/data warehouse

**Tanpa testing:**
- ❌ Bug baru ketahuan setelah production (data sudah salah di dashboard CEO)
- ❌ Refactor code = deg-degan, takut rusak yang lain
- ❌ Deploy cuma bisa "semoga berhasil" 🤞

**Dengan testing:**
- ✅ Bug ketahuan sebelum deploy
- ✅ Refactor dengan percaya diri
- ✅ Dokumentasi hidup (test = contoh cara pakai)

---

## 📚 Learning Path (Bertahap)

### 🟢 **LEVEL 1: PEMULA** (Mulai dari sini!)

#### **Folder 1: Basic Testing**
- Konsep testing paling dasar
- Assert statements
- Test transformasi data sederhana
- **Goal:** Paham kenapa testing itu penting

#### **Folder 2: Pytest Fundamentals**  
- Kenapa pytest > unittest
- Fixtures (reusable test data)
- Parametrize (test banyak case sekaligus)
- **Goal:** Mahir pakai pytest untuk daily testing

**🎓 Setelah Level 1:** Anda sudah bisa produktif! Bisa test fungsi-fungsi transformasi data Anda.

---

### 🟡 **LEVEL 2: INTERMEDIATE**

#### **Folder 3: Data Validation**
- Schema validation
- Pydantic models untuk data contracts
- **Goal:** Pastikan data sesuai kontrak

#### **Folder 4: Quality Checks**
- Null checks, duplicate detection
- Range validation, business rules
- Pandera untuk data quality
- **Goal:** Detect data quality issues otomatis

**🎓 Setelah Level 2:** Anda bisa bikin robust data pipelines dengan validasi lengkap.

---

### 🟠 **LEVEL 3: ADVANCED**

#### **Folder 5: Testing Pipelines** ✅ COMPLETE
- **1-integration-testing-concepts.md:** Unit vs Integration vs E2E, testing pyramid
- **2-mocking-basics.py:** Mock API calls, test DB setup, mock files (18+ tests)
- **3-test-etl-pipeline.py:** Full ETL pipeline testing (11 tests)
- **4-error-handling-retry.py:** Retry logic, graceful error handling, idempotency (16 tests)
- **5-real-world-crypto-etl.py:** Complete production-like pipeline (11 tests)
- **Status:** 56 tests, ALL PASSING ✅
- **Goal:** Test pipeline secara menyeluruh dengan mocking & error handling

#### **Folder 6: Production Patterns**
- CI/CD integration (GitHub Actions)
- Performance testing & benchmarking
- Great Expectations (enterprise-level)
- **Goal:** Production-ready testing practices

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
# Untuk pemula (Level 1)
cd Data_Testing_Framework
# Jika pakai poetry
poetry install

# Jika pakai pip
pip install pytest pandas faker
```

### 2️⃣ Mulai dari Folder 1

```bash
cd 1-basic-testing
# Baca teorinya dulu
cat 1-why-testing.md

# Coba run test pertama
pytest 2-first-test.py -v
```

### 3️⃣ Lanjut Bertahap

Jangan skip folder! Setiap folder build on top of previous folder.

---

## 📖 Struktur Folder

```
Data_Testing_Framework/
├── 1-basic-testing/           # 🟢 START HERE
├── 2-pytest-fundamentals/     # 🟢 Core skills
├── 3-data-validation/         # 🟡 Validation patterns
├── 4-quality-checks/          # 🟡 Quality assurance
├── 5-testing-pipelines/       # 🟠 Integration testing
└── 6-production-patterns/     # 🟠 Advanced practices
```

---

## 💡 Tips Belajar

1. **Jangan buru-buru** - Pahami setiap konsep sebelum lanjut
2. **Run semua code** - Jangan cuma baca, eksekusi!
3. **Modifikasi examples** - Coba ubah-ubah untuk paham lebih dalam
4. **Praktek dengan project sendiri** - Apply ke ETL pipeline Anda

---

## 🔗 Resources

- [Pytest Official Docs](https://docs.pytest.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pandera Documentation](https://pandera.readthedocs.io/)

---

**Happy Testing! 🚀**

*"Code without tests is broken by design" - Jacob Kaplan-Moss*
