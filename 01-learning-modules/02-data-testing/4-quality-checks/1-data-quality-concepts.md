# Data Quality Testing

## 🎯 The Silent Killer: Bad Data Quality

### Skenario Real yang Bikin Rugi Perusahaan

**Case 1: E-commerce Dashboard Salah**
- CEO lihat dashboard: "Penjualan naik 300%! 🎉"
- Ternyata: Ada duplikat data, setiap transaksi tercatat 3x
- Keputusan: Expand bisnis agresif → burn cash
- Reality: Sales flat, company hampir bankrupt

**Case 2: ML Model Rusak**
- Data Scientist train model untuk predict churn
- Accuracy 95% di training!
- Production: Prediksi acak, customer marah
- Root cause: Training data ada 50% null di kolom penting
- Model belajar pattern dari garbage

**Case 3: Regulatory Fine**
- Bank wajib report customer data ke regulator
- Data ada typo, format salah, missing values
- Regulator: Fine $1M + audit 6 bulan

---

## 💰 Cost of Bad Data Quality

Research Gartner: **Bad data costs companies $15 MILLION per year** on average.

Breakdown:
- **40%** - Wrong business decisions
- **30%** - Operational inefficiencies  
- **20%** - Lost revenue opportunities
- **10%** - Compliance/legal issues

---

## 🔍 6 Dimensions of Data Quality

### 1. **Completeness** - Tidak ada missing values
```
❌ BAD: {'user_id': 123, 'email': None}
✅ GOOD: {'user_id': 123, 'email': 'user@example.com'}
```

### 2. **Accuracy** - Data sesuai reality
```
❌ BAD: {'age': 250}  # Impossible!
✅ GOOD: {'age': 25}
```

### 3. **Consistency** - Sama di berbagai sistem
```
❌ BAD: 
   System A: {'country': 'USA'}
   System B: {'country': 'United States'}
✅ GOOD: Both use ISO codes: 'US'
```

### 4. **Validity** - Sesuai format/rules
```
❌ BAD: {'email': 'not-an-email'}
✅ GOOD: {'email': 'user@example.com'}
```

### 5. **Uniqueness** - Tidak ada duplikat
```
❌ BAD: 
   user_id: 1, email: john@example.com
   user_id: 1, email: john@example.com  # Duplikat!
✅ GOOD: Setiap record unique
```

### 6. **Timeliness** - Data masih fresh
```
❌ BAD: {'last_updated': '2020-01-01'}  # 6 tahun lalu!
✅ GOOD: {'last_updated': '2026-01-24'}
```

---

## 🛠️ Tools untuk Data Quality Testing

### **Pandera** (Recommended untuk Pemula)
- DataFrame schema validation
- Statistical checks (min, max, mean)
- Custom checks
- Perfect untuk pandas workflows

**When to use:**
- ✅ ETL pipelines dengan pandas
- ✅ Data cleaning workflows
- ✅ Quick data quality checks

### **Great Expectations** (Enterprise Level)
- Profiling & auto-documentation
- Rich validation library
- Integration dengan Airflow, dbt
- Dashboard untuk monitoring

**When to use:**
- ✅ Large-scale data warehouses
- ✅ Multiple data sources
- ✅ Need documentation & reporting
- ✅ Production data pipelines

### **Manual Checks** (Always Useful)
- Custom business logic
- Quick debugging
- Learning fundamentals

---

## 📊 Data Quality Checks - Checklist

### Basic Checks (Must Have)
- [ ] No null values in critical columns
- [ ] No duplicate records
- [ ] Data types are correct
- [ ] Ranges are valid (age 0-150, prices > 0)

### Intermediate Checks
- [ ] Referential integrity (foreign keys exist)
- [ ] Format consistency (email, phone, dates)
- [ ] Statistical bounds (mean, std within expected range)
- [ ] Business rules (discounted_price < original_price)

### Advanced Checks
- [ ] Distribution checks (is data normal/skewed?)
- [ ] Outlier detection
- [ ] Cross-field validation (end_date > start_date)
- [ ] Historical comparison (today's data similar to yesterday?)

---

## 🎓 Learning Path untuk Folder 4

**File 1:** Manual data quality checks
- Null checks, duplicates, ranges
- Foundation yang penting!

**File 2:** Pandera introduction
- Schema-based validation
- Statistical checks
- Custom validators

**File 3:** Pandera advanced
- Hypothesis testing
- Multi-column checks
- Real-world ETL scenarios

**File 4:** Great Expectations intro (Optional)
- Enterprise patterns
- Expectations suites
- Data docs

---

## 💡 Philosophy: Fail Fast, Fail Loud

**Bad Practice:**
```python
# Silent failures
df = load_data()
# No checks, just assume it's good
df.to_sql('production_table')  # 💥 Bad data in production
```

**Good Practice:**
```python
# Fail fast with clear errors
df = load_data()

# Quality checks
assert df['user_id'].notna().all(), "Found nulls in user_id!"
assert df['age'].between(0, 150).all(), "Invalid age values!"
assert len(df) > 0, "DataFrame is empty!"

# Only load if all checks pass
df.to_sql('production_table')  # ✅ Data quality guaranteed
```

---

## 🚀 Ready?

Sekarang kita akan praktik:
1. Manual quality checks (foundation)
2. Pandera untuk automated validation
3. Real ETL scenarios dengan quality gates

**Lanjut ke file berikutnya!**

---

## 📚 Resources

- [Pandera Documentation](https://pandera.readthedocs.io/)
- [Great Expectations](https://greatexpectations.io/)
- [Data Quality Dimensions (Wikipedia)](https://en.wikipedia.org/wiki/Data_quality)

---

**Quote:**
> "Garbage in, garbage out. No amount of fancy ML can fix bad data quality."
> — Every Data Scientist Ever
