from sqlalchemy import text

INSERT_TRADE_SQL = text("""
        INSERT INTO crypto_trades (symbol,price,event_time,processed_at)
        VALUES (:symbol, :price, :event_time, :processed_at)
        ON CONFLICT DO NOTHING
    """)
# pertanyaan: apakah sintaks ini aman sql injection dan kenapa?
# jawaban: Ya, sintaks ini aman dari SQL injection karena menggunakan parameterized queries. Dalam kode tersebut, nilai-nilai yang akan dimasukkan ke dalam query (seperti :symbol, :price, :event_time, dan :processed_at) adalah parameter yang akan diisi secara terpisah dari pernyataan SQL itu sendiri. Dengan cara ini, input pengguna tidak langsung disisipkan ke dalam pernyataan SQL, sehingga mencegah kemungkinan injeksi kode berbahaya. SQLAlchemy akan menangani pengamanan input tersebut secara otomatis.

# contoh sintaks yang tidak aman dibanding sintaks di atas:
UNSAFE_INSERT_TRADE_SQL = text("""
        INSERT INTO crypto_trades (symbol,price,event_time,processed_at)
        VALUES ('{symbol}', {price}, '{event_time}', '{processed_at}')
    """)
# sintaks di atas tidak aman karena menggunakan format string untuk menyisipkan nilai-nilai langsung ke dalam pernyataan SQL. Jika nilai-nilai tersebut berasal dari input pengguna, seorang penyerang dapat menyisipkan kode SQL berbahaya yang dapat mengubah perilaku query, seperti menghapus data atau mengakses informasi sensitif.

# apa itu cadence dalam data engineering
# jawaban: Cadence dalam data engineering merujuk pada frekuensi atau interval waktu di mana proses-proses data dijalankan atau diulang. Ini bisa mencakup jadwal untuk ekstraksi data, transformasi, pemuatan (ETL), atau proses lainnya yang terkait dengan pengelolaan data. Cadence yang tepat penting untuk memastikan bahwa data selalu up-to-date dan tersedia sesuai kebutuhan bisnis. Misalnya, sebuah pipeline data mungkin memiliki cadence harian, mingguan, atau bahkan real-time tergantung pada kebutuhan aplikasi atau analisis yang dilakukan.

# apakah autcomplete anda bisa di file .txt, lebih ke untuk tanya jawab seputar teori tools data engineering?
# jawaban: Ya, saya dapat memberikan jawaban dan penjelasan seputar teori tools data engineering dalam format teks biasa (.txt). Anda dapat menyimpan percakapan atau informasi yang saya berikan dalam file .txt untuk referensi di masa mendatang. Jika Anda memiliki pertanyaan spesifik tentang tools data engineering, silakan ajukan, dan saya akan berusaha memberikan jawaban yang informatif.

# apa itu teori tools data engineering?
# jawaban: Teori tools data engineering merujuk pada konsep, prinsip, dan metodologi yang mendasari penggunaan berbagai alat dan teknologi dalam bidang data engineering. Data engineering adalah disiplin yang fokus pada desain, pembangunan, dan pemeliharaan infrastruktur data yang memungkinkan pengumpulan, penyimpanan, dan pemrosesan data dalam skala besar. Teori tools data engineering mencakup pemahaman tentang berbagai alat seperti database, sistem pemrosesan data, alat ETL (Extract, Transform, Load), platform big data, dan teknologi cloud yang digunakan untuk mengelola data secara efisien. Selain itu, teori ini juga mencakup praktik terbaik dalam pengelolaan data, keamanan data, dan optimasi kinerja sistem data.
