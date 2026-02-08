# Why Spark Exists — The Problem with Single-Machine Processing

> **Learning Objective:** Understand the fundamental limitations of single-machine data processing and why distributed computing frameworks like Spark are necessary.

---

## The Problem: Why Pandas Is Not Enough?

Bayangkan kamu punya DataFrame Pandas dengan 100 juta baris. Kamu mau:
- Filter berdasarkan kondisi
- Join dengan tabel lain (50 juta baris)
- Agregasi per kategori
- Simpan hasilnya

**Apa yang terjadi?**

```
RAM laptop/server kamu: 16 GB
Data mentah: ~8 GB
Pandas perlu load SEMUA data ke memory
Join operation: butuh ~20 GB (temporary objects)
Result: 💥 MemoryError atau swap disk (super lambat)
```

---

## Fundamental Limitations of Pandas

### 1. **Single-Machine Processing**
- Semua komputasi di 1 mesin
- Terbatas oleh RAM mesin tersebut
- Tidak bisa leverage multiple machines

### 2. **Eager Execution**
- Setiap operasi langsung dieksekusi
- Hasilnya disimpan di memory
- No optimization opportunity

### 3. **No Horizontal Scaling**
- Nambah mesin lain tidak membantu
- Hanya bisa vertical scaling (nambah RAM)
- Limited by single machine capacity

---

## The Need for Distributed Computing

**Key Insight:** When data exceeds single machine capacity, we need to:
1. **Distribute data** across multiple machines
2. **Parallelize processing** across those machines
3. **Coordinate execution** efficiently

**This is where Apache Spark comes in!**

---

## Mental Model: Factory Worker Analogy

**Pandas = 1 Super Fast Worker**
- Works alone
- Has limited desk space (RAM)
- When desk is full → stuck

**Spark = 1 Manager + Many Workers**
- **Manager (Driver)**: Plans and coordinates
- **Workers (Executors)**: Execute tasks in parallel
- **Distributed desks**: Each worker has their own RAM

**Key Intuition:**
- Data doesn't need to be in one place
- Work is split into small tasks executed in parallel
- Results are collected by the manager

---

## When to Consider Spark?

### ✅ Use Spark When:
- Data > single machine RAM (100 GB+)
- Need horizontal scaling
- Processing can be parallelized
- Data in distributed storage (HDFS, S3, GCS)

### ❌ Pandas is Better When:
- Data < 10 GB (fits in RAM)
- Quick prototyping
- Sequential operations
- Small team/simple requirements

---

## Summary

- **Problem:** Single machine can't handle data beyond its RAM
- **Solution:** Distribute data and processing across cluster
- **Spark:** Framework for distributed, parallel data processing
- **Key advantage:** Scale horizontally by adding machines

---

**Next:** [Spark Ecosystem →](02-spark-ecosystem.md)
