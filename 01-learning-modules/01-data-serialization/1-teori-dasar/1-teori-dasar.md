# Tahap 1: Teori Dasar & Filosofi

Untuk memahami Avro, Anda harus "membenci" JSON dalam konteks Data Engineering skala besar.

Di sekolah atau tutorial dasar, kita diajarkan bahwa JSON adalah standar emas karena *human-readable* (bisa dibaca manusia). Namun, bagi sebuah mesin yang memproses jutaan pesan per detik, JSON adalah beban.

Berikut adalah 3 alasan fundamental mengapa JSON "haram" untuk sistem produksi skala *enterprise*:

---

### 1. Masalah *Payload Bloat* (Nama Kolom adalah Polusi)

JSON bersifat **Self-Describing**. Artinya, setiap pesan membawa deskripsinya sendiri.

Bayangkan Anda mengirim 1 juta trade BTC. Setiap pesan JSON akan terlihat seperti ini:

```json
{"symbol": "BTCUSDT", "price": 50000.0, "event_time": 1700000000}

```

Perhatikan teks `"symbol"`, `"price"`, dan `"event_time"`. Kata-kata ini dikirim **berulang-ulang sejuta kali**. Dalam dunia *Big Data*, ini adalah pemborosan *bandwidth* network dan *storage* yang sangat besar.

**Prinsip Avro:** Nama kolom (metadata) dipisahkan dari isi data. Isinya hanya biner mentah. Ibaratnya, JSON adalah surat yang menuliskan judul kolom di setiap baris, sedangkan Avro adalah tabel Excel di mana judulnya cuma ditulis sekali di paling atas.

---

### 2. *Schema Drift* (Si Pembunuh Senyap)

Ini adalah masalah **Governance** (Tata Kelola). Dalam JSON, tidak ada yang menghalangi Produser untuk tiba-tiba mengubah data.

* **Hari ini:** Produser mengirim `price: 50000` (angka).
* **Besok:** Produser mengubahnya menjadi `price: "50.000"` (teks dengan titik).

Sistem Spark Anda akan **crash** karena mengharapkan angka tapi menerima teks. Di industri, ini disebut **Schema Drift**. Tanpa "kontrak" yang kuat, tim Data Engineer akan selalu menjadi "pemadam kebakaran" yang memperbaiki pipeline rusak karena ulah tim Software Engineer (Produser).

---

### 3. Biaya *Parsing* (CPU-Intensive)

Membaca JSON itu berat bagi CPU.

* **JSON:** Komputer harus melakukan *scanning* teks karakter demi karakter, mencari tanda kutip, kurung kurawal, dan koma untuk memahami strukturnya.
* **Binary (Avro):** Komputer langsung membaca blok memori. Karena posisinya sudah pasti (misal: 8 byte pertama adalah ID, 4 byte berikutnya adalah Harga), CPU bekerja jauh lebih ringan.

---

### Perbandingan Paradigma

| Karakteristik | JSON (Textual) | Avro (Binary) |
| --- | --- | --- |
| **Tipe Data** | Lemah (Tergantung parser) | **Kuat (Strictly Typed)** |
| **Deskripsi** | Melekat di setiap data | **Terpisah (Schema File)** |
| **Ukuran** | Besar (Boros) | **Sangat Kecil (Efisien)** |
| **Kontrak** | Tidak ada (Flexible tapi berbahaya) | **Formal (Data Contract)** |

---

### Kesimpulan Tahap 1

JSON diciptakan untuk kemudahan **manusia** (agar bisa di-*debug* dengan mata telanjang), sedangkan format biner seperti Avro diciptakan untuk efisiensi **mesin**.

Di proyek "Mahakarya" Anda, kita ingin berpindah dari sistem yang "semoga data yang datang benar" (JSON) ke sistem yang "data **harus** benar sesuai kontrak, atau sistem menolak" (Avro).

---

### Cek Pemahaman:

Sebelum kita masuk ke **Tahap 2 (Praktik Lokal)**, apakah Anda bisa membayangkan skenario di mana sistem Anda akan hancur jika menggunakan JSON tanpa validasi skema?

----

<br>
<br>
<br>

# Tahap 2: Praktik Lokal — Membedah Anatomi Avro

Di tahap ini, kita akan melihat bagaimana Avro bekerja di balik layar tanpa pusing dengan Kafka. Kita akan membuat sebuah "Kontrak" (Schema) dan menggunakannya untuk membungkus data menjadi biner.

---

### 1. Menulis "Kontrak" (The `.avsc` File)

Dalam Avro, kontrak didefinisikan dalam format JSON dengan ekstensi `.avsc` (*Avro Schema*). Ini adalah aturan mainnya. Jika data tidak sesuai aturan ini, proses akan gagal sejak awal.

Mari kita buat kontrak untuk data trade Binance Anda:

**File: `trade_schema.avsc**`

```json
{
  "type": "record",
  "name": "CryptoTrade",
  "namespace": "com.sanju.crypto",
  "fields": [
    {"name": "symbol", "type": "string"},
    {"name": "price", "type": "double"},
    {"name": "event_time", "type": "long", "logicalType": "timestamp-millis"}
  ]
}

```

**Anatomi Skema:**

* **`record`**: Menandakan ini adalah struktur data (seperti objek/baris tabel).
* **`namespace`**: Agar tidak bentrok dengan skema lain (seperti nama folder/package).
* **`fields`**: Daftar kolom. Di sini kita menentukan tipe data yang sangat spesifik (`double` untuk harga, `long` untuk timestamp).

---

### 2. Simulasi: Mengubah Data Menjadi Biner

Sekarang, kita gunakan library Python untuk melakukan **Serialization** (mengubah objek Python ke biner Avro).

**Persiapan:**

```bash
pip install fastavro

```

**Script Python: `serialize_local.py**`

```python
import json
from fastavro import writer, parse_schema

# 1. Load Kontrak/Schema
with open('trade_schema.avsc', 'r') as f:
    schema = parse_schema(json.load(f))

# 2. Data yang ingin kita kirim (Python Dict)
records = [
    {"symbol": "BTCUSDT", "price": 45000.5, "event_time": 1700000000000},
    {"symbol": "ETHUSDT", "price": 2500.0, "event_time": 1700000001000}
]

# 3. Serialization: Bungkus data ke file biner '.avro'
with open('trades.avro', 'wb') as out:
    writer(out, schema, records)

print("Berhasil membuat file trades.avro!")

```

---

### 3. Eksperimen: Apa yang Berbeda?

Setelah Anda menjalankan script di atas, coba lakukan dua hal ini:

#### A. Cek Ukuran File

Bandingkan jika Anda menyimpan data yang sama dalam format `.json` dan `.avro`. Untuk ribuan data, file `.avro` akan jauh lebih kecil karena Avro menyimpan data dalam format **Biner Kolumnar**.

#### B. Intip Isinya (The "Aha!" Moment)

Coba buka file `trades.avro` menggunakan teks editor (VS Code/Notepad). Anda akan melihat sesuatu seperti ini:

> `Obj...avro.schema...{"type":"record","name":"CryptoTrade"...` diikuti oleh karakter aneh/kotak-kotak biner.

**Poin Penting:**

* **The Header:** Di bagian awal file, Avro menyelipkan seluruh skema JSON-nya.
* **The Body:** Di bawahnya adalah data mentah yang sudah dikompres.
* **Mandiri:** Karena skemanya ada di dalam file, siapa pun yang memegang file ini bisa membacanya tanpa perlu bertanya "Ini kolom apa?".

---

### 4. Mengapa Ini "Ngeri" untuk Data Engineering?

Di industri, jika Anda punya data sebesar 1 Petabyte:

* Pakai JSON: Anda butuh 1000 server untuk menyimpannya.
* Pakai Avro/Parquet: Anda mungkin hanya butuh 200 server karena kompresinya sangat efisien.

Selain itu, jika Anda mencoba memasukkan `price: "MAHAL"` (string) ke dalam script di atas, `fastavro` akan langsung memberikan error **sebelum data itu dikirim**. Ini adalah **Early Warning System** agar data kotor tidak masuk ke pipeline Anda.

---

### Tugas Kecil untuk Anda:

Coba buat satu field baru di `.avsc` (misal: `"quantity": "float"`), lalu jalankan lagi script-nya tanpa memasukkan `quantity` di data Python Anda. Lihat apa yang terjadi.

**Setelah Anda merasakan "gagal karena skema" di lokal, apakah Anda siap lanjut ke Tahap 3: Konsep Schema Evolution (Cara mengubah skema tanpa merusak sistem)?** 

---

# Tahap 3: Schema Evolution — Cara Mengubah Aturan Tanpa Menghancurkan Sistem

Inilah bagian yang paling "ngeri" dan membuat Avro menjadi standar industri. Di dunia nyata, data itu **dinamis**. Hari ini Anda hanya butuh `price`, besok bos Anda minta tambah `quantity`, lusa minta tambah `discount_code`.

Jika pakai JSON, setiap kali ada perubahan, tim Consumer (Anda) harus janjian dengan tim Producer agar kode tidak *crash*. Di Avro, ini diatur oleh **Compatibility Rules**.

---

### 1. Konsep Reader vs Writer Schema

Dalam Avro, ada dua pihak:

1. **Writer Schema**: Skema yang dipakai si Producer saat mengirim data.
2. **Reader Schema**: Skema yang dipegang si Consumer (Anda) saat membaca data.

Avro sangat sakti karena **Writer dan Reader tidak harus punya skema yang identik 100%**, selama mereka memenuhi aturan evolusi.

---

### 2. Tiga Jenis Evolusi (Compatibility)

Anda harus paham 3 istilah ini saat *interview* Data Engineer:

#### A. Backward Compatibility (Paling Sering)

* **Definisi:** Konsumer dengan skema **baru** bisa membaca data yang ditulis dengan skema **lama**.
* **Contoh:** Anda menambah kolom `quantity` di Spark, tapi di Kafka masih ada data lama yang tidak punya `quantity`.
* **Syarat:** Kolom baru **wajib** punya nilai `default`. Jadi saat Spark baca data lama, dia akan mengisi `quantity` dengan nilai default tersebut. Tidak ada *crash*.

#### B. Forward Compatibility

* **Definisi:** Konsumer dengan skema **lama** bisa membaca data yang ditulis dengan skema **baru**.
* **Contoh:** Producer sudah kirim data pakai kolom `discount_code`, tapi Spark Anda belum di-update dan masih pakai skema lama.
* **Hasil:** Spark akan mengabaikan kolom `discount_code` dan tetap memproses kolom yang dia tahu saja.

#### C. Full Compatibility

* **Definisi:** Gabungan keduanya. Data lama bisa dibaca kode baru, data baru bisa dibaca kode lama. Ini adalah standar emas untuk sistem yang sangat aman.

---

### 3. Eksperimen Praktik: Mencoba "Kekuatan" Default

Mari kita modifikasi skema yang Anda buat di Tahap 2. Bayangkan kita ingin menambah kolom `volume`.

**Skema Baru (V2): `trade_schema_v2.avsc**`

```json
{
  "type": "record",
  "name": "CryptoTrade",
  "namespace": "com.sanju.crypto",
  "fields": [
    {"name": "symbol", "type": "string"},
    {"name": "price", "type": "double"},
    {"name": "event_time", "type": "long"},
    {"name": "volume", "type": "float", "default": 0.0} 
  ]
}

```

**Skenario "Ngeri":**

1. Si Producer masih pakai **Skema V1** (hanya ada symbol, price, event_time).
2. Si Consumer (Anda) sudah upgrade pakai **Skema V2** (mengharapkan volume).

**Hasilnya?**
Saat Anda menjalankan Reader di Python, Avro akan melihat: *"Oh, data ini nggak punya volume, tapi di skema saya volume wajib ada. Untungnya ada nilai default 0.0, jadi saya pakai itu saja."*

**Sistem tetap jalan (No Crash!).**

---

### 4. Kenapa Ini "Mahakarya"?

Bayangkan Anda punya 100 mikroservis yang saling kirim data. Tanpa Schema Evolution, saat satu tim mengubah struktur data, 99 tim lainnya harus ikut ganti kode di hari yang sama. Itu kiamat bagi tim *engineering*.

Dengan Avro, tim Producer bisa *deploy* duluan, atau tim Consumer bisa *deploy* duluan, sistem tetap harmonis. Ini yang disebut **Decoupling** (Pemisahan ketergantungan) secara teknis.

---

### Tugas Analisis:

Menurut Anda, apa yang akan terjadi jika saya **menghapus** sebuah kolom yang tidak punya nilai `default` di skema lama, padahal si Reader masih mengharapkan kolom itu ada?

---

# Tahap 4: Schema Registry — "Buku Telepon" Otomatis untuk Kafka Anda?

---

Kita masuk ke **Tahap 4: Schema Registry — "Buku Telepon" Otomatis untuk Kafka.**

Di Tahap 2, Anda belajar bahwa file `.avro` menyimpan skema di dalam *header*-nya. Tapi di Kafka, kita mengirim pesan satu per satu (misal: 1 baris trade). Kalau setiap 1 baris trade kita selipkan skema JSON yang berat itu, maka keuntungan "biner yang kecil" akan hilang. Kita malah balik lagi ke masalah JSON (overhead besar).

Di sinilah **Schema Registry** berperan sebagai pahlawan.

---

### 1. Masalah: Kegendutan Data di Kafka

Bayangkan Anda mengirim data trade BTC.

* **Data (Biner):** 20 byte.
* **Skema (JSON):** 500 byte.

Kalau Anda kirim keduanya sekaligus, 95% *bandwidth* Anda habis cuma buat kirim skema yang sama berulang-ulang. Itu bodoh.

**Solusinya:** Simpan skemanya di suatu tempat (Registry), dan di Kafka kita cukup kirim "ID"-nya saja.

---

### 2. Cara Kerja Schema Registry (The Workflow)

Schema Registry adalah server terpisah (di luar Kafka) yang berfungsi sebagai pustaka skema.

1. **Producer (Pendaftaran):** Sebelum kirim data, Producer lapor ke Registry: *"Ini skema trade saya."*
2. **Registry (Pemberian ID):** Registry menyimpan skema itu dan membalas: *"Oke, itu skema ID nomor 5."*
3. **Producer (Pengiriman):** Producer membungkus data biner dengan **ID nomor 5** di depannya, lalu dikirim ke Kafka. (Sangat ringan!)
4. **Consumer (Pencarian):** Consumer menerima data, melihat ada ID nomor 5. Dia bertanya ke Registry: *"Eh, skema ID nomor 5 itu strukturnya gimana?"*
5. **Registry (Jawaban):** Registry memberikan skema aslinya. Consumer pun bisa membaca datanya dengan sempurna.

---

### 3. "The Magic Byte" (Anatomi Pesan Kafka Avro)

Di industri, Anda akan sering mendengar istilah **Wire Format**. Saat Anda menggunakan Avro dengan Schema Registry, setiap pesan di Kafka memiliki struktur biner yang sangat spesifik (5 byte pertama adalah kuncinya):

* **Byte 0:** Magic Byte (Selalu `0`). Ini penanda bahwa ini adalah format Confluent Avro.
* **Byte 1-4:** **Schema ID** (4 byte). Inilah ID unik dari Registry.
* **Byte 5-dst:** Data biner aslinya.

**Kenapa ini "Ngeri"?** Karena dengan hanya menambah 5 byte, Anda mendapatkan validasi skema tingkat tinggi tanpa membebani performa.

---

### 4. Centralized Governance: "Polisi" Data

Schema Registry bukan cuma buku telepon, tapi juga **"Polisi"**.

Jika Anda mengeset *Compatibility Mode* ke `BACKWARD`, dan ada Producer nakal yang mencoba mendaftarkan skema baru yang merusak (misal: menghapus kolom wajib), **Schema Registry akan menolak pendaftaran itu** dengan error HTTP 409.

Artinya: **Data kotor tidak akan pernah bisa menyentuh Kafka.** Pipeline Anda di sisi Spark akan aman dari *crash* karena Registry sudah menghadangnya di depan.

---

### 5. Teori Prasyarat untuk Praktek

Sebelum masuk ke tahap akhir (implementasi ke kodingan), Anda harus paham bahwa Schema Registry berkomunikasi lewat **REST API**.

* Registry punya *endpoint* seperti `/subjects/crypto-price-value/versions`.
* Artinya, Spark dan Producer Anda harus punya koneksi jaringan (network) ke server Registry ini.

---

### Ringkasan Intuisi Tahap 4

| Tanpa Schema Registry | Dengan Schema Registry |
| --- | --- |
| Skema dikirim di setiap pesan (Boros). | Skema disimpan di pusat (Efisien). |
| Tidak ada yang menjaga perubahan skema. | Registry menolak perubahan yang merusak. |
| Consumer harus punya file skema manual. | Consumer mendownload skema otomatis via ID. |

---

### Pertanyaan Refleksi:

Jika Schema Registry tiba-tiba mati, apakah Consumer masih bisa membaca data baru yang masuk ke Kafka?

**Setelah Anda merenungkan risiko ini, apakah kita siap untuk Tahap 5: Implementasi Kode (The "Grand Finale")?** Di sini kita akan mengubah Producer Python dan Spark Streaming Anda untuk berbicara dengan Schema Registry.

<br>

---
<br>

Sekarang kita akan menyatukan semua teori tadi ke dalam kode. Kita akan mengubah pipeline Anda yang tadinya mengirim "pesan mentah" (JSON) menjadi "pesan kontrak" (Avro).

---

### 1. Update Infrastruktur (Docker Compose)

Agar sistem ini jalan, Anda butuh server **Schema Registry**. Jika Anda menggunakan Confluent Kafka di lokal, tambahkan servis ini di `docker-compose.yml`.

```yaml
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    depends_on:
      - broker
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: 'broker:29092'
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081

```

---

### 2. Update Producer (Python)

Di sisi Producer, kita tidak lagi menggunakan `json.dumps()`. Kita akan menggunakan `AvroSerializer` yang secara otomatis akan mendaftarkan skema ke Registry jika belum ada.

**Prasyarat:** `pip install confluent-kafka fastavro`

```python
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# 1. Setup Client Schema Registry
sr_config = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(sr_config)

# 2. Load Skema .avsc
with open("trade_schema.avsc") as f:
    schema_str = f.read()

# 3. Setup Serializer
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

# 4. Setup Producer
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'value.serializer': avro_serializer # Di sini "saktinya"
}
producer = SerializingProducer(producer_config)

# 5. Kirim Data
data = {"symbol": "BTCUSDT", "price": 50000.0, "event_time": 1700000000000}
producer.produce(topic='crypto_prices', value=data)
producer.flush()

```

**Apa yang terjadi di balik layar?**
Saat `produce()` dipanggil, library ini akan:

1. Mengecek ke `localhost:8081` apakah skema ini sudah punya ID.
2. Jika belum, dia mendaftarkannya dan mendapat ID (misal: ID #1).
3. Mengonversi `data` menjadi biner, lalu menempelkan ID #1 di depannya (5 byte pertama).
4. Mengirimkan total biner tersebut ke Kafka.

---

### 3. Update Consumer (Spark Structured Streaming)

Di sisi Spark, ini bagian yang paling menantang. Spark bawaan (`spark-avro`) didesain untuk membaca file Avro statis, bukan streaming dari Kafka yang punya *header* 5-byte dari Confluent.

Di industri, kita biasanya menggunakan library **ABRiS** (paling populer untuk Spark + Confluent Avro) atau menggunakan fungsi bawaan Spark dengan sedikit trik pada *binary handling*.

**Logika di Spark:**

```python
from pyspark.sql.functions import col, inline
# Anda butuh package: org.apache.spark:spark-avro_2.12

# 1. Baca mentah dari Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "crypto_prices") \
    .load()

# 2. Proses Deserialization
# Karena 5 byte pertama adalah Magic Byte + Schema ID, 
# kita harus membuangnya jika menggunakan format standar Spark from_avro
binary_df = raw_df.selectExpr("substring(value, 6) as avro_value")

# 3. Gunakan skema untuk mengubah biner ke kolom
# (Di industri, kita akan mengambil skema langsung dari Registry via API)
from pyspark.sql.avro.functions import from_avro

json_schema = open("trade_schema.avsc").read()
decoded_df = binary_df.select(from_avro(col("avro_value"), json_schema).alias("data")).select("data.*")

```

---

### 4. Cara Membuktikan Ini "Mahakarya"

Setelah Anda mengimplementasikan ini, lakukan tes ini saat demo atau di depan rekruter:

1. **Efisiensi:** Tunjukkan ukuran pesan di Kafka. Avro akan jauh lebih kecil daripada JSON.
2. **Strictness:** Coba ubah Producer untuk mengirim field `price` sebagai `string`. Lihat bagaimana Producer akan **error bahkan sebelum data keluar dari laptop Anda**.
3. **Registry Check:** Buka browser ke `http://localhost:8081/subjects/crypto_prices-value/versions/latest`. Tunjukkan bahwa skema Anda tersimpan secara resmi di sana.

---

### Kesimpulan Besar Tahap 1-5

Anda baru saja naik kelas dari **"Seseorang yang bisa memindahkan data"** menjadi **"Seseorang yang membangun ekosistem data yang teratur"**.

Anda sekarang paham:

* **Kenapa** JSON buruk untuk skala besar.
* **Bagaimana** biner bekerja menghemat biaya.
* **Cara** Schema Evolution menjaga pipeline agar tidak crash di tengah malam.
* **Fungsi** Schema Registry sebagai "polisi" kualitas data.

---

### Apa Selanjutnya?

Aspek 1 (Data Serialization) sudah selesai kita bedah secara teori dan praktik. Apakah Anda ingin:

1. **Istirahat sejenak** dan mencoba mengimplementasikan ini ke repo Anda?
2. Atau **Lanjut ke Aspek 4: Observability** (Melihat "jantung" sistem Anda lewat metrik *Consumer Lag* di Grafana)?