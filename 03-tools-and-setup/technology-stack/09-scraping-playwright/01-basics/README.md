# Modul 1 - The Foundation & Isolation

## Teori Singkat Playwright

- Playwright adalah framework automasi browser modern berbasis Node yang menyediakan API lintas browser (Chromium, Firefox, WebKit).
- Ia mengontrol browser seperti user nyata dan mengandalkan event loop async untuk orkestrasi tindakan (navigate, click, screenshot).
- Playwright menunggu kondisi siap secara otomatis (auto-waiting), sehingga script lebih tahan terhadap halaman dinamis.
- Model isolasi utama ada di `BrowserContext`: sesi yang terpisah tanpa harus memulai proses browser baru.

## Ringkasan Teori

### Mengapa kita menggunakan Context daripada langsung memakai Browser? [cite: 2026-02-14]
- `Browser` adalah proses besar yang menampung banyak state dan resource.
- `BrowserContext` memberi isolasi sesi (cookies, localStorage, cache) seperti mode incognito.
- Context lebih ringan dibuat/dihancurkan, sehingga workflow scraping lebih stabil dan mudah diulang.

### Apa bedanya `page.locator()` dengan `page.query_selector()` dan kenapa locator lebih disukai? [cite: 2026-02-14]
- `query_selector()` melakukan snapshot sekali; jika DOM berubah setelahnya, hasilnya mudah menjadi stale.
- `locator()` bersifat lazy dan auto-waiting, sehingga lebih tahan terhadap elemen yang muncul terlambat.
- Locator memberikan API yang konsisten untuk aksi berulang, tanpa harus re-query DOM manual.

### Tips efisiensi: Cara menutup browser dengan benar agar tidak terjadi memory leak. [cite: 2026-01-19]
- Tutup `BrowserContext` lebih dulu, lalu `Browser`.
- Gunakan `async with async_playwright()` agar proses driver ditutup otomatis.
- Hindari membiarkan event loop hidup dengan browser terbuka; selalu `await browser.close()`.

## Cara Menjalankan

```bash
python main.py
```

## Output
- Screenshot disimpan di folder `screenshots/`.
- Terminal akan menampilkan judul halaman dan isi elemen `h1`.
