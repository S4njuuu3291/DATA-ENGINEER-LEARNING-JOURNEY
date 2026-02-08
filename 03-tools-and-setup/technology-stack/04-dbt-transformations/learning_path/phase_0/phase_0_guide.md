# Phase 0 — Orientation & Tooling (Profesional & Lengkap)

---

## BAGIAN 1: TEORI MENDALAM

### 1.1 Apa itu dbt?

**dbt (data build tool)** adalah framework untuk **menulis, menguji, dan mendeploy transformasi data** dalam data warehouse. dbt **bukan tool ETL**—dbt adalah tool untuk ELT (Extract-Load-Transform).

**Yang dbt tidak lakukan:**
- Tidak mengekstrak data dari sumber
- Tidak memindahkan data ke warehouse
- Tidak membuat data warehouse

**Yang dbt lakukan:**
- Menulis transformasi SQL yang **modular dan reusable**
- Mengatur **dependensi antar model** (DAG/Directed Acyclic Graph)
- Menjalankan **testing** otomatis pada data
- Menghasilkan **dokumentasi** dari kode dan metadata
- Mengintegrasikan dengan **version control** (Git)
- Mendukung **reproducibility** dan **CI/CD**

**Analogi:** Jika data warehouse adalah database kosong yang sudah full data, dbt adalah yang mengatur bagaimana data tersebut ditransformasi menjadi insights yang siap untuk analytics atau business decision.

### 1.2 ELT vs ETL (Penjelasan Lengkap)

#### ETL (Extract-Transform-Load)
```
[Data Source] --Extract--> [Transformation Engine] --Load--> [Warehouse]
                                 (Ketika: eksternal)
```
- Transformasi terjadi **di luar warehouse** (ETL tool seperti Apache Airflow, Talend, etc.)
- Data di-clean dan di-aggregate **sebelum** masuk warehouse
- **Keuntungan:** warehouse hanya berisi clean data
- **Kerugian:** transformasi kompleks sulit diaudit, maintenance sulit

#### ELT (Extract-Load-Transform)
```
[Data Source] --Extract--> [Warehouse] --Transform (SQL)--> [Clean Data]
                 Load          ^
                           dbt bekerja di sini
```
- Data di-load **mentah** ke warehouse
- Transformasi dilakukan **dalam warehouse** menggunakan SQL
- **Keuntungan:** warehouse modern (BigQuery, Snowflake) mampu transformasi besar dalam hitungan detik; kode SQL mudah diaudit; perubahan logic cepat
- **Kerugian:** storage lebih besar (menyimpan raw + transformed)

**Kenapa industri modern pilih ELT?**
1. Warehouse cloud (BigQuery, Snowflake, Redshift) murah untuk storage dan compute
2. SQL lebih mudah diaudit dibanding black-box ETL
3. Data science & analytics team bisa langsung query raw data untuk eksperimen
4. Faster iteration untuk business logic

### 1.3 dbt Core vs dbt Cloud

| Aspek | dbt Core | dbt Cloud |
|-------|----------|-----------|
| **Format** | CLI (command-line) | Managed SaaS UI + CLI |
| **Setup** | Local machine | Cloud-hosted |
| **Scheduling** | Manual / Cron / External tool | Built-in job scheduling |
| **CI/CD** | Manual integration | Native GitHub integration |
| **Docs Hosting** | Local folder | Cloud-hosted docs.getdbt.com |
| **Cost** | Free | Free tier + paid |
| **Use case** | Development, small team | Production, large org |

**Dalam fase ini kita pakai dbt Core** (CLI lokal) karena cocok untuk belajar dan setup lebih fleksibel.

### 1.4 Konsep Inti: Model, Ref, dan DAG

#### Model
- **1 model = 1 file SQL** (biasanya di `models/` folder)
- Berisi 1 SELECT query
- Materialisasi sebagai view, table, atau incremental model
- Contoh: `models/staging/stg_orders.sql`

#### ref() — Referensi Antar Model
```sql
-- models/marts/fct_orders.sql
SELECT 
    o.order_id,
    c.customer_id
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('dim_customers') }} c USING (customer_id)
```
- `ref()` otomatis membuat **dependency** antar model
- dbt akan menjalankan `stg_orders` dan `dim_customers` **sebelum** `fct_orders`
- Membuat **DAG (lineage)** yang jelas

#### DAG (Directed Acyclic Graph)
```
raw_orders (source)
    |
    v
stg_orders (staging model)
    |    |
    v    v
fct_orders -- dim_customers
    |
    v
analytics_dashboard (exposure)
```
dbt memahami urutan eksekusi secara otomatis.

### 1.5 Struktur Project dbt (Standar Industri)

```
my_dbt_project/
├── dbt_project.yml           # Konfigurasi utama
├── models/
│   ├── staging/              # Cleaning & standardization
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── marts/                # Business logic
│   │   ├── fct_orders.sql
│   │   └── dim_customers.sql
│   └── intermediate/         # Optional, internal models
├── macros/                   # Reusable SQL/Jinja logic
├── seeds/                    # Static data (CSV)
├── snapshots/                # Slowly Changing Dimension (SCD)
├── tests/                    # Custom tests
├── analyses/                 # One-off analysis
├── data/                     # Data files
└── README.md
```

**Penjelasan:**
- **staging**: model pertama yang clean raw data
- **marts**: model akhir untuk analytics/BI
- **intermediate**: model internal (jarang diakses langsung)

### 1.6 dbt_project.yml (Konfigurasi Penting)

```yaml
name: 'my_analytics_project'
version: '1.0.0'
config-version: 2

profile: 'my_project'  # Nama profile di ~/.dbt/profiles.yml
model-paths: ['models']
macro-paths: ['macros']
seed-paths: ['seeds']
test-paths: ['tests']

models:
  my_analytics_project:
    staging:
      materialized: view
    marts:
      materialized: table
```

**Arti:**
- `profile`: koneksi ke warehouse (BigQuery, PostgreSQL, etc.)
- `materialized`: default materialization (bisa override per model)

### 1.7 Reproducibility & Best Practices

**Reproducible = Bisa di-run ulang dengan hasil sama**

```sql
-- ✅ BAIK (reproducible)
SELECT 
    customer_id,
    COUNT(*) as order_count
FROM raw_orders
GROUP BY customer_id
```

```sql
-- ❌ BURUK (tidak reproducible, date berubah setiap hari)
SELECT 
    customer_id,
    COUNT(*) as order_count,
    CURRENT_DATE as run_date
FROM raw_orders
WHERE order_date > CURRENT_DATE - 7
GROUP BY customer_id
```

**Prinsip reproducibility:**
- Query harus deterministic (output sama untuk input sama)
- Harus bisa di-run di machine/warehouse lain dan hasil sama
- Semua dependency harus explicit (via ref/source)

---

## BAGIAN 2: SETUP WAREHOUSE

**Pilih salah satu: PostgreSQL lokal atau BigQuery**

### 2.1 Setup PostgreSQL Lokal

#### Prerequisites
- PostgreSQL terinstall (versi 12+)
- PostgreSQL CLI (`psql`) accessible dari terminal

#### Step 1: Validasi PostgreSQL sudah installed
```bash
psql --version
```
Jika tidak ada, install via:
- **MacOS**: `brew install postgresql@15`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`
- **Windows**: download dari https://www.postgresql.org/download/windows/

#### Step 2: Start PostgreSQL service
```bash
# MacOS
brew services start postgresql@15

# Linux
sudo service postgresql start

# Windows
net start postgresql-15
```

#### Step 3: Buat database untuk dbt
```bash
# Connect ke postgres default
psql -U postgres

# Di dalam psql shell
CREATE DATABASE analytics_dev;
CREATE USER dbt_user WITH PASSWORD 'dbt_password_123';
GRANT ALL PRIVILEGES ON DATABASE analytics_dev TO dbt_user;

# Exit
\q
```

#### Step 4: Validasi koneksi
```bash
psql -U dbt_user -d analytics_dev -h localhost
```
Jika berhasil, Anda akan masuk ke shell PostgreSQL.

#### Step 5: Setup profiles.yml
Buat atau edit file `~/.dbt/profiles.yml`:
```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: dbt_user
      password: dbt_password_123
      port: 5432
      dbname: analytics_dev
      schema: dbt_dev
      threads: 4
      keepalives_idle: 0
```

**Penjelasan:**
- `target: dev`: profile ini bernama "dev"
- `type: postgres`: koneksi ke PostgreSQL
- `schema: dbt_dev`: dbt akan membuat schema ini otomatis
- `threads: 4`: jalankan 4 model secara parallel (jika ada dependency)

---

### 2.2 Setup BigQuery Cloud

#### Prerequisites
- Google Cloud Project (GCP) dibuat
- Service account dibuat dengan BigQuery Admin role

#### Step 1: Buat GCP Project
1. Buka https://console.cloud.google.com/
2. Klik "Select a project" → "NEW PROJECT"
3. Nama: `dbt-learning`
4. Tunggu project selesai dibuat

#### Step 2: Aktifkan BigQuery API
1. Di GCP Console, search "BigQuery API"
2. Klik "Enable"

#### Step 3: Buat Service Account
1. Di GCP Console, buka "Service Accounts" (Search bar atas)
2. Klik "CREATE SERVICE ACCOUNT"
3. Nama: `dbt-sa`
4. Klik "CREATE AND CONTINUE"
5. Role: "BigQuery Admin"
6. Klik "CONTINUE" → "DONE"

#### Step 4: Generate JSON key
1. Di halaman Service Accounts, klik service account `dbt-sa`
2. Tab "Keys" → "ADD KEY" → "Create new key"
3. Format: JSON
4. Klik "CREATE"
5. File JSON auto-download. **Simpan di tempat aman** (ex: `~/.dbt/keys/`)

```bash
mkdir -p ~/.dbt/keys
mv ~/Downloads/dbt-learning-*.json ~/.dbt/keys/bq_key.json
```

#### Step 5: Setup profiles.yml
Edit `~/.dbt/profiles.yml`:
```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: dbt-learning  # Ganti dengan project ID Anda
      keyfile: /Users/yourname/.dbt/keys/bq_key.json
      dataset: dbt_dev
      threads: 4
      timeout_seconds: 300
      priority: interactive
```

**Penjelasan:**
- `project`: GCP project ID (lihat di dashboard GCP)
- `keyfile`: path ke JSON key
- `dataset`: BigQuery dataset (otomatis dibuat)

---

## BAGIAN 3: FIRST RUN dbt

### 3.1 Validasi koneksi
```bash
cd /home/sanju3291/DATA-ENGINEER/tools/phase5-dbt/weatherflow_dbt
dbt debug
```

**Output sukses terlihat seperti:**
```
Configuration:
  profiles.yml file: ~/.dbt/profiles.yml
  dbt_project.yml file: /path/to/dbt_project.yml
  dbt version: 1.5.0
  ...
  
Connection:
  type: postgres (atau bigquery)
  schema: dbt_dev
  ...
  
All checks passed!
```

Jika error, troubleshoot:
1. Pastikan PostgreSQL/BigQuery running
2. Pastikan password benar di profiles.yml
3. Pastikan network connectivity OK

### 3.2 Eksekusi model pertama
```bash
dbt run --select example_table
```

**Output sukses:**
```
Running with dbt=1.5.0
Found 1 model, 0 tests, 0 snapshots, 0 analyses, 0 macros, 0 operations...
Completed successfully
```

### 3.3 Jalankan test
```bash
dbt test --select example_table
```

**Output sukses:**
```
1 test passed
```

---

## BAGIAN 4: UJIAN PHASE 0

**Durasi:** 2 jam

### Ujian Bagian A: Praktik (60 poin)

**Deliverable:**
1. Output `dbt debug` (screenshot atau copy-paste)
2. Output `dbt run --select <model_name>` (minimal 1 model)
3. Output `dbt test --select <model_name>` (minimal 1 test)
4. Screenshot atau file `.sql` dari 1 model yang Anda jalankan

**Kriteria penilaian:**
- dbt debug all checks passed: 20 poin
- dbt run sukses (minimal 1 model): 20 poin
- dbt test sukses (minimal 1 test): 20 poin

### Ujian Bagian B: Teori (40 poin)

**Jawab masing-masing pertanyaan dalam 3-5 kalimat:**

1. **Jelaskan perbedaan ETL dan ELT. Mengapa industri modern lebih memilih ELT?** (10 poin)
2. **Apa peran dbt dalam arsitektur data modern? Apa yang dbt lakukan dan apa yang tidak dbt lakukan?** (10 poin)
3. **Jelaskan konsep DAG (Directed Acyclic Graph) dalam konteks dbt dan bagaimana `ref()` membantu membangun DAG.** (10 poin)
4. **Apa yang dimaksud "reproducible" dalam konteks dbt model? Berikan contoh query yang reproducible dan tidak reproducible.** (10 poin)

---

## Checklist Kelulusan
- [ ] PostgreSQL / BigQuery sudah tersetup
- [ ] `dbt debug` lulus (all checks passed)
- [ ] Minimal 1 model berhasil di-run
- [ ] Minimal 1 test berhasil
- [ ] Jawaban teori sudah disiapkan

---

## Cara Submit
1. Kirim output praktik (Bagian A) berupa screenshot atau teks
2. Kirim jawaban teori (Bagian B) dalam format txt atau markdown
3. Saya akan nilai berdasarkan rubrik di bawah

---

## Rubrik Penilaian

**Total skor: 100**

### Praktik (60 poin)
- dbt debug all checks passed: **20 poin**
- dbt run sukses: **20 poin**
- dbt test sukses: **20 poin**

### Teori (40 poin)
- Soal 1 (ETL vs ELT): **10 poin**
  - Dijelaskan perbedaan dengan akurat: 5 poin
  - Dijelaskan kenapa modern pilih ELT: 5 poin
- Soal 2 (Peran dbt): **10 poin**
  - Explained correctly apa dbt lakukan: 5 poin
  - Explained correctly apa dbt tidak lakukan: 5 poin
- Soal 3 (DAG & ref): **10 poin**
  - Defined DAG dengan jelas: 5 poin
  - Dijelaskan peran ref() dengan tepat: 5 poin
- Soal 4 (Reproducibility): **10 poin**
  - Defined reproducibility dengan akurat: 5 poin
  - Contoh query benar dan berguna: 5 poin

**Kelulusan:** Minimum **75 poin**. Praktik wajib 100% (semua 3 bagian harus lulus).