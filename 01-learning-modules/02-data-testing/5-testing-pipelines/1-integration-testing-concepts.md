# Integration Testing untuk Data Pipelines

## 🎯 Kenapa Integration Testing?

### Analogi: Resep Masakan

**Unit Testing:**
- Test: "Pisau tajam?" ✅
- Test: "Bawang sudah dicincang?" ✅
- Test: "Bumbu sudah tercampur?" ✅

**Integration Testing:**
- Tapi... Hasil masakan jadi aneh? 🤔
- Ternyata: Urutan masuknya tidak benar!
- Atau: Takaran tidak sesuai saat dikombinasikan

### Real-World Data Engineering Scenario:

**Unit tests pass ✅**
- `extract()` function: ✅ Return data yang benar
- `transform()` function: ✅ Clean data dengan benar
- `load()` function: ✅ Insert ke database dengan benar

**Tapi pipeline gagal di production 💥**
- Extract: API timeout, tidak di-retry
- Transform: Assume data selalu valid (tidak)
- Load: Unique constraint violation, tidak di-handle
- Urutan eksekusi salah
- Configuration salah di production

---

## 🏗️ Testing Pyramid

```
      /\          E2E Tests
     /  \         (Slow, complex, few)
    /    \
   /______\

   /        \     Integration Tests
  /          \   (Medium speed, real deps)
 /____________\

 /              \  Unit Tests
/________________\ (Fast, isolated, many)
```

### Jumlah Tests:
- **Unit:** 70% (banyak, cepat)
- **Integration:** 20% (sedang)
- **E2E:** 10% (sedikit, lambat)

---

## 🔀 Unit vs Integration vs E2E

| Aspek | Unit | Integration | E2E |
|-------|------|-------------|-----|
| **Scope** | 1 fungsi | Module/component | Full pipeline |
| **Dependencies** | Mock | Real/Semi-real | All real |
| **Speed** | Milliseconds | Seconds | Minutes |
| **When** | Always | Before deploy | Scheduled |
| **Cost** | Cheap | Medium | Expensive |
| **Confidence** | Low | High | Highest |

---

## 🛠️ Mocking Strategies

### Strategy 1: Full Mock (Fastest)
```python
@patch('requests.get')
def test_extract(mock_get):
    mock_get.return_value.json.return_value = {'data': [...]}
    # API completely mocked
```

**Pros:** Cepat, deterministic, tidak butuh API
**Cons:** Tidak test actual API behavior

### Strategy 2: Real Service + Test Database
```python
def test_with_real_api():
    # Real API call (might be slow/flaky)
    data = requests.get('https://api.example.com/test')
    # But load ke test database (isolated)
```

**Pros:** Test actual API
**Cons:** Lambat, dependent on external service

### Strategy 3: Hybrid (Best!)
```python
@pytest.fixture(scope="session")
def api_responses():
    # Load real API responses once, cache them
    return load_cached_responses()

def test_with_cached_responses(api_responses):
    # Use cached real responses
    # Fast + realistic
```

---

## ✅ Integration Test Checklist

Sebelum write integration test, check:

- [ ] Mocking strategy jelas (full mock, partial, real?)
- [ ] External resources isolated (test DB, test files)
- [ ] Cleanup after test (no side effects)
- [ ] Test data realistic (similar to production)
- [ ] Error scenarios covered
- [ ] Retry logic tested
- [ ] Data validation at each step
- [ ] Performance acceptable (<5s ideally)

---

## 🚀 Patterns yang Akan Kita Pelajari

### 1. **Mocking External APIs**
```python
# Mock requests.get()
# Simulate different responses (success, 404, 500, timeout)
```

### 2. **Test Database Setup**
```python
# Use sqlite in-memory (:memory:)
# Fast, isolated, auto-cleanup
```

### 3. **Full ETL Pipeline**
```python
# Extract (mock API) → Transform → Load (test DB) → Verify
```

### 4. **Error Handling**
```python
# Test retry logic
# Test error recovery
# Test data integrity on failure
```

### 5. **Real-World Scenarios**
```python
# Idempotency testing
# Partial failure recovery
# Data reconciliation
```

---

## 💡 Real-World Use Cases

### **Use Case 1: Cryptocurrency Price ETL**
```
Hourly job:
1. Extract prices dari CoinGecko API
2. Transform: normalize, add calculations
3. Load: upsert ke PostgreSQL
4. Alert: kalau ada anomaly

Integration test:
- Mock API response
- Test transform logic
- Verify database state
- Check alert triggering
```

### **Use Case 2: E-commerce Order Processing**
```
Real-time:
1. Extract: consume dari Kafka queue
2. Validate: check order data
3. Enrich: add customer info dari API
4. Load: insert ke data warehouse

Integration test:
- Mock Kafka consumer
- Mock customer API
- Verify DW structure
```

### **Use Case 3: Data Sync**
```
Daily job:
1. Extract: dari source database
2. Transform: handle schema differences
3. Load: ke target database
4. Reconcile: verify counts match

Integration test:
- Setup source DB dengan data
- Run sync
- Verify target DB
- Check reconciliation
```

---

## 🎯 Folder 5 akan cover:

**File 1:** Teori & konsep (file ini)
**File 2:** Mocking basics (API, database, files)
**File 3:** Full ETL pipeline test
**File 4:** Error handling & retry logic
**File 5:** Real-world crypto ETL scenario

---

## 📚 Learning Philosophy untuk Folder 5

1. **Start Simple** - Single mock, simple pipeline
2. **Build Gradually** - Add more complexity
3. **Real Data** - Use realistic sample data
4. **Error Scenarios** - Always test failures
5. **Performance Check** - Make sure tests are fast

---

**Siap untuk practical examples?** Lanjut ke file 2! 🚀
