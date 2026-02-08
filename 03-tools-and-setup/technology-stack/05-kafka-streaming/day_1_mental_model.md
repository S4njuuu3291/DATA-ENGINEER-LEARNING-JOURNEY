# 🟦 DAY 1 — KAFKA MENTAL MODEL (PALING KRUSIAL)

> **Tujuan Hari Ini (satu kalimat):**
> Anda memahami **apa itu Kafka sebenarnya**, **kenapa ia diciptakan**, dan **masalah apa yang ia selesaikan** — TANPA menyebut Spark, Flink, atau tool lain.

---

## 1️⃣ MASALAH ASLI YANG MELAHIRKAN KAFKA

Sebelum Kafka ada, perusahaan besar (LinkedIn, Netflix, dll) menghadapi masalah ini:

### Masalah Nyata:

* Banyak sistem menghasilkan data **terus-menerus**
* Banyak sistem lain ingin **membaca data yang sama**
* Sistem bisa **mati kapan saja**
* Data **tidak boleh hilang**

Contoh dunia nyata:

* User activity logs
* Transaction events
* Clickstream
* Price feed

Pertanyaan kuncinya:

> “Bagaimana caranya **mengirim data ke banyak sistem**, TANPA kehilangan data, dan TANPA saling mengganggu?”

---

## 2️⃣ SOLUSI NAIF (DAN KENAPA GAGAL)

### Solusi naif #1 — Database langsung

```
App → INSERT ke DB
Consumer → SELECT dari DB
```

❌ Masalah:

* DB overload
* Sulit scale
* Tidak real-time

---

### Solusi naif #2 — Message Queue biasa

```
Producer → Queue → Consumer
```

❌ Masalah:

* Data **hilang setelah dibaca**
* Consumer mati = data gone
* Tidak bisa replay data

---

## 3️⃣ IDE BESAR KAFKA (INI HARUS NEMPEL DI OTAK)

> **Kafka bukan message queue.**
> Kafka adalah **distributed append-only commit log**.

Mari bedah satu per satu.

---

### 🔹 Append-only

* Data **tidak diubah**
* Data **tidak dihapus setelah dibaca**
* Data hanya **ditambah di belakang**

Bayangkan buku kas:

* Tidak ada edit
* Tidak ada delete
* Hanya tambah baris baru

---

### 🔹 Log

* Data tersimpan **berurutan**
* Setiap record punya **posisi**

Posisi ini namanya: **OFFSET**

---

### 🔹 Distributed

* Data dipecah ke banyak mesin
* Bisa scale horizontal
* Bisa tahan failure

---

## 4️⃣ MENTAL MODEL PALING PENTING (WAJIB DIHAFAL)

Bayangkan Kafka itu seperti:

> **Google Drive untuk data streaming**

* Producer = orang upload file
* Kafka = Drive
* Consumer = orang download file

📌 Kalau satu orang download:

* File **tidak hilang**
* Orang lain tetap bisa download

Ini beda TOTAL dengan queue.

---

## 5️⃣ KONSEP INTI (DIBEDAH DALAM)

### A. Topic

* Seperti folder
* Tempat data dikumpulkan
* Contoh:

  * `user_events`
  * `crypto_trades`

📌 Topic = **kategori data**, bukan pipeline.

---

### B. Partition (INI SUPER PENTING)

* Topic dibagi jadi beberapa part
* Tujuan:

  * **Scale**
  * **Parallelism**
  * **Ordering per key**

Bayangkan:

```
Topic: trades
Partition 0
Partition 1
Partition 2
```

📌 Ordering **HANYA dijamin di dalam satu partition**.

---

### C. Offset (JEBATAN INTERVIEW FAVORIT)

Offset adalah:

* Angka urut data di partition
* Seperti nomor baris di file log

Contoh:

```
Partition 0:
offset 0
offset 1
offset 2
```

📌 Kafka **tidak peduli** apakah data sudah dibaca atau belum.
📌 Kafka **hanya tahu offset ada di disk**.

---

## 6️⃣ PRODUCER vs CONSUMER (SECARA FILOSOFIS)

### Producer

* HANYA kirim data
* Tidak tahu siapa yang baca
* Tidak tahu kapan dibaca

Producer = **tuli**

---

### Consumer

* Datang belakangan pun tidak masalah
* Bisa baca dari offset lama
* Bisa replay data

Consumer = **bebas**

---

## 7️⃣ PERTANYAAN PALING PENTING (STOP DAN PIKIRKAN)

Jawab DI KEPALA dulu:

> ❓ Kenapa Kafka tidak menghapus data setelah dibaca?

**Jawaban inti (jangan dibaca dulu):**

<details>
<summary>Jawaban</summary>

Karena Kafka dirancang agar **banyak consumer bisa membaca data yang sama**, dan agar consumer yang mati bisa **melanjutkan membaca tanpa kehilangan data**. Offset disimpan terpisah dari data, sehingga pembacaan tidak mempengaruhi penyimpanan.

</details>

Kalau jawaban ini masuk akal di kepala Anda → **fondasi sudah benar**.

---

## 8️⃣ LATIHAN WAJIB (TANPA KODING)

### ✍️ Tugas Tulis (WAJIB)

Tulis **1 paragraf pendek** menjawab:

> “Apa perbedaan Kafka dengan message queue biasa?”

Tidak perlu panjang. Yang penting **jujur dan paham**.

---

### 🧠 Mental Checkpoint

Anda **BOLEH lanjut ke Day 2** kalau:

* Bisa menjelaskan Kafka tanpa kata “Spark”
* Bisa menjelaskan offset dengan analogi
* Paham kenapa data tidak langsung dihapus

Kalau belum → baca ulang, jangan lanjut.

---
