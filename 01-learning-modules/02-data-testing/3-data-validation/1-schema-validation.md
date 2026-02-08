# Schema Validation & Data Contracts

## 🎯 The Problem: Trust Issues

Dalam sistem distributed (Kafka, Microservices, APIs), ada masalah fundamental:

**Producer** (yang kirim data) dan **Consumer** (yang terima data) sering beda team.

### Skenario Tanpa Schema:

**Day 1:**
- Producer kirim: `{"user_id": 123, "email": "john@example.com"}`
- Consumer terima dan process

**Day 30:**
- Producer tiba-tiba kirim: `{"userId": "123", "email": "john@example.com"}`
  - `user_id` → `userId` (rename)
  - `123` (int) → `"123"` (string)
- Consumer **CRASH!** 💥

**Siapa yang salah?**
- Producer: "Kami update schema, harusnya Anda adapt"
- Consumer: "Kami tidak diberi tahu ada perubahan!"

---

## 💡 Solution: Data Contracts dengan Schema Validation

**Data Contract** = perjanjian formal antara Producer dan Consumer tentang struktur data.

Konsepnya seperti:
- **API Contract** (OpenAPI/Swagger) untuk REST APIs
- **Database Schema** untuk relational databases
- **Avro Schema** untuk streaming data

---

## 🔧 Tools untuk Schema Validation

### 1. **Pydantic** (Recommended untuk Pemula)
- Simple, pythonic
- Type hints based
- Great error messages
- Perfect untuk APIs, configs, data models

### 2. **Pandera** (For DataFrames)
- Pandas DataFrame validation
- Statistical checks (min, max, ranges)
- Perfect untuk data quality

### 3. **Great Expectations** (Enterprise)
- Complex data quality checks
- Profiling & documentation
- CI/CD integration

### 4. **Avro/Protobuf** (For Streaming)
- Binary serialization
- Schema evolution
- High performance

---

## 📋 When to Use What?

| Use Case | Tool | Example |
|----------|------|---------|
| API request/response validation | **Pydantic** | FastAPI, data models |
| DataFrame validation | **Pandera** | ETL pipelines, data cleaning |
| Complex data quality checks | **Great Expectations** | Data warehouse ingestion |
| Kafka/streaming data | **Avro** | Real-time data pipelines |

---

## 🎓 What We'll Learn

### Folder 3 (Data Validation):
1. **Manual validation** (if-else checks)
2. **Pydantic** untuk type-safe data models
3. **Schema evolution** strategies
4. Testing validation logic

### Benefits:
- ✅ Catch schema violations early
- ✅ Self-documenting code
- ✅ Type safety
- ✅ Better error messages

---

## 🚀 Real-World Example

Bayangkan Anda punya ETL pipeline yang ingest data dari API external:

```python
# Tanpa validation
def process_user_data(data):
    # Crash di production kalau data berubah format!
    user_id = data['user_id']  # KeyError jika key berubah
    age = data['age'] + 1       # TypeError jika age jadi string
```

```python
# Dengan Pydantic validation
from pydantic import BaseModel

class User(BaseModel):
    user_id: int
    email: str
    age: int

def process_user_data(data):
    # Validation happens here - error jika format salah
    user = User(**data)
    
    # Type-safe from here
    return user.age + 1
```

Kalau data berubah format, error langsung ketahuan di validation step, bukan di tengah-tengah logic!

---

## 💭 Mindset Shift

**Old Way:**
- "Semoga data yang datang benar"
- Debug production errors

**New Way:**
- "Data **harus** sesuai contract, atau reject"
- Fail fast, fail loud

---

**Ready untuk praktik?** Lanjut ke file berikutnya!
