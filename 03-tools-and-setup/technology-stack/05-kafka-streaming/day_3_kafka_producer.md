# 🟦 DAY 3 (REVISI FINAL) — KAFKA PRODUCER DENGAN CONFLUENT KAFKA

**Level: Intern → Junior-ready**

> **Tujuan besar hari ini:**
> Anda memahami **bagaimana Producer Kafka bekerja secara internal**, **menulis producer Python yang benar-benar mendekati produksi**, dan **mengerti reliability, ordering, dan failure behavior**.

Hari ini **panjang** karena memang **inilah jantung Kafka**.

---

## 0️⃣ KENAPA `confluent-kafka` LEBIH BENAR?

### Perbandingan singkat (JUJUR):

| Library             | Cocok untuk    | Catatan                                  |
| ------------------- | -------------- | ---------------------------------------- |
| kafka-python        | belajar cepat  | Pure Python, lebih lambat                |
| **confluent-kafka** | **real-world** | Binding C (librdkafka), dipakai industri |

📌 **Fakta industri**:

* Banyak company **tidak pakai Java**
* Tapi tetap pakai **Kafka client Confluent**
* Python + Confluent Kafka = **valid produksi**

Kalau Anda pakai ini di portofolio:

> Recruiter tahu Anda **tidak main-main**

---

## 1️⃣ APA SEBENARNYA PRODUCER KAFKA LAKUKAN?

Sebelum koding, pahami **alur internal sesungguhnya**:

```
Python Event
   ↓
Serializer
   ↓
Producer Buffer (Client-side)
   ↓
Batching
   ↓
Partitioner
   ↓
Network I/O
   ↓
Kafka Broker
   ↓
Append ke Commit Log (disk)
   ↓
ACK
```

📌 **Producer itu asynchronous by default**
📌 `produce()` ≠ data sudah aman
📌 Data aman **hanya setelah ACK**

Ini **harus nempel di kepala**.

---

## 2️⃣ INSTALLASI YANG BENAR (PELAn, TIDAK ASAL)

Masuk virtualenv Anda:

```bash
pip install confluent-kafka
```

Jika error:

* Pastikan Python ≥ 3.8
* Di Windows/WSL biasanya aman

Cek install:

```bash
python -c "from confluent_kafka import Producer; print('OK')"
```

---

## 3️⃣ FILE PRODUCER — STRUKTUR PROFESIONAL

Buat file:

```bash
producer_confluent.py
```

---

## 4️⃣ KONFIGURASI PRODUCER (INI SANGAT PENTING)

```python
from confluent_kafka import Producer
import json
import time
```

---

### 4.1️⃣ CALLBACK DELIVERY REPORT (ENGINEERING CORE)

Ini **yang tidak ada di kafka-python secara natural**.

```python
def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        print(
            f"✅ Record delivered to {msg.topic()} "
            f"[partition {msg.partition()}] @ offset {msg.offset()}"
        )
```

📌 **Inilah ACK Kafka**
📌 Tanpa ini → Anda **buta reliability**

---

### 4.2️⃣ PRODUCER CONFIG (DIBEDAH SATU-SATU)

```python
producer_conf = {
    "bootstrap.servers": "localhost:9092",

    # Reliability
    "acks": "all",
    "retries": 5,

    # Latency vs throughput
    "linger.ms": 50,
    "batch.num.messages": 1000,

    # Safety
    "enable.idempotence": True,
}
```

#### Penjelasan perlahan:

##### `acks = all`

* Tunggu semua replica
* Data **tidak hilang**
* Cocok untuk financial / event penting

##### `retries`

* Kalau network glitch → retry
* Tanpa retry → silent data loss

##### `linger.ms`

* Tunggu sebentar untuk batching
* Lebih efisien
* Ini **engineering trade-off**

##### `enable.idempotence`

🔥 **INI KEREN DAN MODERN**

* Kafka menjamin **no duplicate on retry**
* Wajib disebut di README

---

### 4.3️⃣ INISIALISASI PRODUCER

```python
producer = Producer(producer_conf)
```

---

## 5️⃣ PRODUCE DATA (SECARA SADAR, BUKAN COPY-PASTE)

```python
topic = "crypto_trades"

for i in range(10):
    event = {
        "symbol": "BTCUSDT",
        "price": 68000 + i,
        "event_time": int(time.time())
    }

    producer.produce(
        topic=topic,
        key=event["symbol"],
        value=json.dumps(event),
        on_delivery=delivery_report
    )

    producer.poll(0)  # trigger callbacks
    time.sleep(1)
```

📌 **`poll(0)` WAJIB**

* Tanpa ini → callback tidak dipanggil
* Ini sering dilewatkan pemula

---

## 6️⃣ FLUSH = “PASTIKAN SEMUA DATA TERKIRIM”

Di akhir file:

```python
producer.flush()
```

Artinya:

> “Tunggu sampai semua message benar-benar terkirim atau gagal”

---

## 7️⃣ JALANKAN & OBSERVASI (WAJIB)

```bash
python producer_confluent.py
```

Buka Kafka UI:

* Lihat partition
* Lihat offset naik
* Perhatikan **semua masuk ke 1 partition** (karena key sama)

---

## 8️⃣ EKSPERIMEN WAJIB (INI YANG MEMBUAT ANDA JAGO)

### Eksperimen 1 — Matikan Kafka

```bash
docker stop kafka
python producer_confluent.py
```

Perhatikan:

* Error muncul
* Tidak silent failure

---

### Eksperimen 2 — Hidupkan Kafka Lagi

```bash
docker start kafka
```

Jalankan ulang producer.

📌 **Idempotence memastikan tidak duplikat**

---

## 9️⃣ HAL YANG ANDA HARUS PAHAM (BISA JELASIN TANPA KODE)

1. Producer asynchronous
2. ACK = tanda data aman
3. Key → partition
4. Retry bisa bikin duplikat (kecuali idempotent)
5. Producer buffer ≠ Kafka disk

Kalau ini bisa dijelaskan → **Anda SUDAH DI LEVEL ENGINEER**

---

## 🔟 TUGAS WAJIB (INI BUKAN OPSIONAL)

Jawab tertulis:

1. Kenapa `enable.idempotence=True` penting?
2. Kenapa `producer.produce()` tidak menjamin data sudah masuk Kafka?
3. Apa fungsi `producer.poll()`?

Kalau bisa jawab **tanpa buka kode**, Anda benar-benar paham.

---
