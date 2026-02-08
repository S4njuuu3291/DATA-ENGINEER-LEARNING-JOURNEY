# 🟦 DAY 2 — MENJALANKAN KAFKA PERTAMA KALI (DARI 0 TOTAL)

> **Tujuan besar hari ini:**
> Anda **melihat Kafka hidup**, **mengerti bagian-bagiannya**, dan **paham apa yang sebenarnya sedang berjalan di komputer Anda**.

Hari ini kita jawab 3 pertanyaan besar:

1. Kafka itu *berjalan sebagai apa*?
2. Apa saja komponen minimal Kafka?
3. Bagaimana cara manusia “melihat” Kafka bekerja?

---

## 0️⃣ SEBELUM MULAI — APA YANG SEBENARNYA KITA LAKUKAN?

Kafka **bukan library Python**.
Kafka adalah **server** (lebih tepatnya: *distributed system*).

Artinya:

* Kafka **harus dijalankan dulu**
* Baru aplikasi (Python, dsb) bisa kirim/baca data

Jadi hari ini **kita tidak bikin aplikasi**.
Hari ini kita **menyalakan mesin Kafka**.

Analogi:

> Hari ini kita **nyalakan pabriknya**, belum bikin produknya.

---

## 1️⃣ MASALAH PRAKTIS: “GIMANA CARA JALANIN KAFKA?”

Kafka itu:

* Ditulis pakai Java
* Banyak config
* Ribet kalau install manual

### SOLUSI MODERN:

👉 **Docker**

Docker = cara menjalankan software **tanpa ribet install**.

Kita akan:

* Jalankan Kafka pakai Docker
* Semua config sudah disiapkan
* Fokus ke konsep, bukan setup neraka

---

## 2️⃣ APA ITU KRaft? (JANGAN TAKUT ISTILAH)

### Dulu (versi lama Kafka):

```
Kafka butuh Zookeeper
```

Zookeeper:

* Server tambahan
* Mengatur metadata Kafka
* Ribet, bikin setup makin kompleks

---

### Sekarang (Kafka modern):

```
Kafka pakai KRaft
```

**KRaft = Kafka Raft**

Artinya:

* Kafka **mengatur dirinya sendiri**
* Tidak perlu Zookeeper
* Lebih simpel, lebih modern

📌 **Ini penting secara karier**
Karena perusahaan 2024–2025:

* Mulai migrasi ke KRaft
* Tidak mau dependensi lama

Hari ini kita pakai **cara modern**.

---

## 3️⃣ KOMPONEN MINIMAL KAFKA (INI WAJIB DIPAHAMI)

Kafka **minimal** terdiri dari:

### A. Kafka Broker

Ini **server utama Kafka**.

Tugasnya:

* Menyimpan data
* Menyimpan topic
* Menyimpan partition
* Menyimpan offset

📌 Broker = “mesin penyimpanan data streaming”

---

### B. Topic

Topic = **wadah data**.

Contoh:

* `crypto_trades`
* `user_events`

📌 Topic itu **bukan proses**, tapi **kategori data**.

---

### C. Partition

Partition = **pembagian data di dalam topic**.

Kenapa perlu?

* Supaya bisa parallel
* Supaya bisa scale
* Supaya tidak satu file raksasa

Bayangkan:

```
Topic: crypto_trades
 ├─ Partition 0
 ├─ Partition 1
 └─ Partition 2
```

📌 Data di **satu partition urut**
📌 Data antar partition **tidak dijamin urut**

---

### D. Offset

Offset = **nomor urut data** di partition.

Bayangkan seperti:

```
Partition 0:
offset 0
offset 1
offset 2
```

Kafka **tidak tahu** apakah data sudah dibaca.
Kafka **hanya tahu** offset ini ada di disk.

Ini akan sangat penting nanti.

---

## 4️⃣ KENAPA PERLU KAFKA UI?

Kafka itu **server tanpa tampilan**.

Tanpa UI:

* Anda cuma percaya “katanya jalan”
* Tidak tahu data masuk atau tidak
* Tidak tahu partition terisi atau tidak

👉 **Engineer tidak boleh buta sistem**

Maka kita pakai **Kafka UI**:

* Untuk melihat topic
* Untuk melihat message
* Untuk melihat partition & offset

Ini **bukan mainan**, ini **alat kerja**.

---

## 5️⃣ STRUKTUR SISTEM YANG AKAN JALAN

Hari ini, di laptop Anda, akan berjalan:

```
[ Kafka Broker ]
       ▲
       │
[ Kafka UI ]
```

Belum ada Python, belum ada producer.
Tapi Kafka **SUDAH HIDUP**.

---

## 6️⃣ MULAI PRAKTIK — SIAPKAN FOLDER

Di terminal:

```bash
mkdir kafka-day2
cd kafka-day2
```

Folder ini = **laboratorium Kafka Anda**.

---

## 7️⃣ FILE PALING PENTING: `docker-compose.yml`

Docker Compose = cara mendeskripsikan:

* Service apa saja yang jalan
* Port apa
* Config apa

### Bikin file:

```bash
touch docker-compose.yml
```

Isi **PELAn-PELAn**:

```yaml
version: "3.8"
```

Artinya:

* Versi format docker compose
* Tidak terlalu penting, tapi wajib ada

---

### 🧠 SERVICE 1 — Kafka Broker

Tambahkan:

```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    container_name: kafka
```

Artinya:

* Kita pakai image Kafka resmi dari Confluent
* Versi modern
* Nama container = kafka

---

### 🧠 KONFIGURASI KRaft (INTI)

Tambahkan di bawah `kafka:`:

```yaml
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
```

Maknanya:

* Kafka ini punya ID = 1
* Dia berperan sebagai:

  * broker (penyimpan data)
  * controller (pengatur metadata)

Karena kita **single-node**, satu Kafka melakukan dua peran.

---

### 🧠 QUORUM (JANGAN PANIK)

```yaml
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
```

Artinya:

* Siapa yang berhak mengambil keputusan metadata
* Dalam kasus kita: Kafka itu sendiri

Ini bagian **internal**, tidak perlu hafal, cukup tahu:

> “Ini config KRaft supaya Kafka bisa jalan sendiri.”

---

### 🧠 LISTENER (INI PENTING)

Tambahkan:

```yaml
      KAFKA_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://0.0.0.0:9092,CONTROLLER://kafka:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
```

Makna sederhana:

* Kafka buka beberapa “pintu”
* `9092` = pintu untuk aplikasi di laptop
* `29092` = pintu antar container

📌 Anda **tidak perlu hafal**, cukup tahu:

> “Ini supaya Kafka bisa diakses dari luar Docker.”

---

### 🧠 CONFIG TAMBAHAN

```yaml
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_LOG_DIRS: /tmp/kraft-combined-logs
```

Maknanya:

* Karena single node, replication = 1
* Topic bisa auto dibuat
* Data disimpan di folder internal Kafka

---

## 8️⃣ TAMBAHKAN KAFKA UI

Di bawah service kafka:

```yaml
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local-kafka
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
    depends_on:
      - kafka
```

Artinya:

* Kafka UI jalan
* Terhubung ke Kafka
* Bisa diakses di browser

---

## 9️⃣ JALANKAN SEMUANYA

Di terminal:

```bash
docker compose up -d
```

Tunggu ±20–30 detik.

Cek:

```bash
docker ps
```

Harus muncul:

* kafka
* kafka-ui

---

## 🔟 LIHAT KAFKA DENGAN MATA SENDIRI

Buka browser:

```
http://localhost:8080
```

Yang Anda lihat:

* Cluster: `local-kafka`
* Menu: Topics, Brokers, Consumers

📌 **Ini momen penting**
Kafka sekarang **bukan teori lagi**.

---

## 1️⃣1️⃣ BUAT TOPIC PERTAMA (SECARA SADAR)

Masuk:

* Topics → Create Topic

Isi:

* Name: `crypto_trades`
* Partitions: `3`
* Replication factor: `1`

### BERHENTI SEBENTAR

Jawab di kepala:

> “Kenapa 3 partition?”

Jawaban benar:

* Parallel processing
* Scaling consumer
* Ordering per key

---

## 1️⃣2️⃣ KIRIM DATA MANUAL (TANPA KODE)

Masuk topic `crypto_trades` → Produce Message

Value:

```json
{
  "symbol": "BTCUSDT",
  "price": 68000,
  "timestamp": 1700000000
}
```

Key:

```
BTCUSDT
```

Klik send.

Perhatikan:

* Partition mana terisi
* Offset bertambah

---

## 1️⃣3️⃣ APA YANG WAJIB ANDA PAHAMI HARI INI

Jika Anda lupa semuanya, INGAT 3 HAL INI:

1. Kafka = server penyimpan data
2. Data **tidak hilang setelah dikirim**
3. Offset itu **penunjuk**, bukan datanya

---

## 1️⃣4️⃣ LATIHAN WAJIB (TANPA LOMPAT)

Jawab dengan jujur (boleh di notes):

1. Kalau tidak ada consumer, apakah data hilang?
2. Kalau consumer datang besok, apakah data hari ini bisa dibaca?
3. Apa fungsi Kafka UI?

Kalau bisa jawab → **DAY 2 LULUS**.

---
