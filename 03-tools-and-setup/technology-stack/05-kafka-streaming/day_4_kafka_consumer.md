# 🟦 DAY 4 — KAFKA CONSUMER (OFFSET, CONSUMER GROUP, & FAILURE)

> **Tujuan besar hari ini:**
> Anda memahami **bagaimana Kafka membaca data**, **bagaimana offset bekerja**, dan **kenapa Kafka tidak kehilangan data walaupun consumer mati**.

Kalau Day 3 = *cara data masuk*,
Day 4 = *cara data dibaca dengan aman*.

---

## 0️⃣ APA ITU CONSUMER (SECARA FILOSOFI)

Consumer **bukan “penerima pesan”**.

Consumer adalah:

> **pembaca log Kafka dengan posisi (offset) yang bisa maju, berhenti, atau mundur**

📌 Ini beda total dengan queue biasa:

* Queue → pesan dihapus setelah dibaca
* Kafka → **data tetap ada**, consumer cuma **menggeser pointer**

Ingat ini baik-baik.

---

## 1️⃣ MENTAL MODEL PALING PENTING (WAJIB NEMPEL)

Bayangkan Kafka seperti **file log besar**:

```
[ record 0 ][ record 1 ][ record 2 ][ record 3 ]
```

Consumer itu **bukan mengambil record**.
Consumer hanya bilang:

> “Saya sudah membaca sampai record ke-2”

Angka “2” itulah **OFFSET**.

📌 Kafka **tidak peduli** Anda membaca atau tidak.
Kafka **tidak peduli** consumer hidup atau mati.
Kafka **hanya menyimpan data**.

---

## 2️⃣ OFFSET ITU DISIMPAN DI MANA?

Ini penting secara engineering.

Offset:

* ❌ **TIDAK disimpan di consumer**
* ❌ **TIDAK disimpan di kode Python**
* ✅ **Disimpan di Kafka (internal topic)**

Nama topic internal:

```
__consumer_offsets
```

Artinya:

* Consumer mati → offset tetap aman
* Consumer hidup lagi → lanjut dari posisi terakhir

Inilah **alasan utama Kafka tahan failure**.

---

## 3️⃣ APA ITU CONSUMER GROUP?

Sekarang kita naik level.

### Definisi sederhana:

> **Consumer group = sekumpulan consumer yang bekerja sama membaca satu topic**

Tujuan:

* Parallel processing
* Scalability
* Fault tolerance

---

### Aturan emas consumer group (WAJIB HAFAL):

1. **Satu partition hanya dibaca oleh satu consumer dalam satu group**
2. Banyak consumer ≠ selalu lebih cepat
3. Scaling dibatasi jumlah partition

Contoh:

```
Topic: crypto_trades (3 partitions)

Consumer group A:
- consumer-1 → partition 0
- consumer-2 → partition 1
- consumer-3 → partition 2
```

Kalau:

* consumer mati → partition di-reassign
* data **tidak hilang**

---

## 4️⃣ KENAPA CONSUMER GROUP PENTING DI INDUSTRI?

Karena:

* Microservices
* Multiple downstream systems
* Horizontal scaling

Kafka **dirancang dari awal** untuk ini.

---

## 5️⃣ KITA MULAI PRAKTIK — CONSUMER DENGAN CONFLUENT

Masuk ke folder Kafka Anda.

Buat file baru:

```bash
consumer_confluent.py
```

---

## 6️⃣ IMPORT & CALLBACK DASAR

```python
from confluent_kafka import Consumer
import json
```

---

## 7️⃣ KONFIGURASI CONSUMER (INI JANTUNG DAY 4)

```python
consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "crypto-consumer-group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
}
```

Sekarang kita bedah **SATU PER SATU**.

---

### `group.id`

* Identitas consumer group
* Offset disimpan per group
* Ganti group → baca ulang dari awal

📌 Ini sering dipakai untuk:

* Reprocessing
* Backfill

---

### `auto.offset.reset = earliest`

Artinya:

* Kalau **belum ada offset**
* Mulai baca dari **data paling awal**

Alternatif:

* `latest` → hanya data baru

📌 Ini sangat penting saat testing.

---

### `enable.auto.commit = False`

🔥 **INI PENTING**

Artinya:

* Kita **mengontrol kapan offset disimpan**
* Offset baru disimpan setelah kita yakin data sudah diproses

Kalau auto-commit:

* Consumer bisa commit offset
* Tapi processing gagal
* Data hilang secara logis

📌 Manual commit = **engineering practice yang benar**

---

## 8️⃣ SUBSCRIBE KE TOPIC

```python
consumer = Consumer(consumer_conf)
consumer.subscribe(["crypto_trades"])
```

Artinya:

* Consumer ini join group
* Kafka assign partition otomatis

---

## 9️⃣ LOOP CONSUME (PELAn, SADAR)

```python
try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        event = json.loads(msg.value().decode("utf-8"))
        print(
            f"Received event: {event} "
            f"from partition {msg.partition()} "
            f"offset {msg.offset()}"
        )

        # Commit offset setelah processing sukses
        consumer.commit(msg)

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    consumer.close()
```

---

## 🔟 BACA INI PER BARIS (INI PENTING)

### `poll()`

* Ambil message dari Kafka
* Tidak blocking selamanya
* Kafka **tidak push**, consumer **pull**

---

### `consumer.commit(msg)`

Artinya:

> “Saya sudah berhasil memproses message sampai offset ini.”

📌 Offset disimpan di Kafka
📌 Kalau consumer mati setelah commit → aman
📌 Kalau mati sebelum commit → data akan dibaca ulang

Ini **inti reliability Kafka**.

---

## 1️⃣1️⃣ JALANKAN CONSUMER

```bash
python consumer_confluent.py
```

Sambil consumer jalan:

* Jalankan producer (Day 3)
* Lihat data masuk real-time

---

## 1️⃣2️⃣ EKSPERIMEN WAJIB (INI YANG MEMBUAT ANDA JAGO)

### Eksperimen 1 — MATIKAN CONSUMER

* Jalankan consumer
* Stop pakai `Ctrl+C`
* Jalankan lagi

❓Pertanyaan:

* Apakah data lama dibaca ulang?
* Atau lanjut dari offset terakhir?

---

### Eksperimen 2 — MATIKAN TANPA COMMIT

* Comment `consumer.commit(msg)`
* Jalankan consumer
* Stop
* Jalankan ulang

❓Apa yang terjadi?

📌 Ini membuktikan:

> Offset = kunci data safety

---

### Eksperimen 3 — GANTI GROUP ID

Ubah:

```python
"group.id": "crypto-consumer-group-v2"
```

Jalankan lagi.

❓Kenapa data lama muncul lagi?

---

## 1️⃣3️⃣ KESALAHAN UMUM PEMULA (HINDARI INI)

❌ Auto-commit tanpa sadar
❌ Mengira Kafka push data
❌ Mengira offset disimpan di kode
❌ Mengira data hilang kalau consumer mati

Kalau Anda paham ini → **Anda di atas rata-rata**.

---

## 1️⃣4️⃣ RANGKUMAN DAY 4 (HAFALKAN)

1. Kafka menyimpan data, bukan consumer
2. Offset adalah pointer, bukan data
3. Offset disimpan di Kafka
4. Consumer group = scaling unit
5. Commit menentukan data safety

---

## 1️⃣5️⃣ TUGAS WAJIB (TANPA KODE)

Jawab dengan kata-kata sendiri:

1. Kenapa offset harus di-commit setelah processing?
2. Apa yang terjadi kalau consumer mati sebelum commit?
3. Kenapa satu partition hanya boleh satu consumer per group?

Kalau bisa jawab **tanpa lihat kode** → Anda benar-benar paham Kafka.

---
