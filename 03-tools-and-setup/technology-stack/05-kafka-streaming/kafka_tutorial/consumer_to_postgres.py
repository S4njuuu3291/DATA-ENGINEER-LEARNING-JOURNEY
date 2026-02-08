import json

from confluent_kafka import Consumer
from sqlalchemy.orm import sessionmaker

from db import engine
from queries import INSERT_TRADE_SQL

SessionLocal = sessionmaker(
    bind=engine
)  # bind untuk menghubungkan session dengan engine database

consumer_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "crypto-postgres-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}

consumer = Consumer(consumer_conf)
consumer.subscribe(["crypto_trades"])

try:
    while True:
        msg = consumer.poll(1.0)  # timeout 1 detik

        if msg is None:
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue
        event = json.loads(msg.value().decode("utf-8"))
        session = SessionLocal()
        try:
            session.execute(
                INSERT_TRADE_SQL,
                {
                    "symbol": event["symbol"],
                    "price": event["price"],
                    "event_time": event["event_time"],
                    "processed_at": event["processed_at"],
                },
            )
            session.commit()
            consumer.commit(msg)  # commit offset setelah data berhasil disimpan
        except Exception as e:
            session.rollback()
            print(f"Database error: {e}")
        finally:
            session.close()
except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()

# isi dari INSERT_TRADE_SQL = text("""
#        INSERT INTO crypto_trades (symbol,price,event_time,processed_at)
#        VALUES (:symbol, :price, :event_time, :processed_at)
#        ON CONFLICT DO NOTHING
#    """)

# di kode ini, di bagian mana yang mengatur deduplikasi ketika insert ke database?
# Deduplikasi ketika insert ke database diatur oleh bagian "ON CONFLICT DO NOTHING" dalam pernyataan SQL INSERT_TRADE_SQL. Bagian ini memastikan bahwa jika ada konflik (misalnya, duplikat berdasarkan kunci unik), maka perintah insert tidak akan melakukan apa-apa dan tidak akan menimbulkan error, sehingga mencegah duplikasi data di tabel crypto_trades.

# pertanyaan: apa itu poll pada kafka consumer dengan jawaban detil?
# Jawaban: Metode poll pada Kafka Consumer adalah fungsi yang digunakan untuk mengambil pesan dari topik Kafka. Ketika dipanggil, metode ini akan memeriksa apakah ada pesan baru yang tersedia untuk dikonsumsi dari partisi yang telah ditentukan. Jika ada pesan yang tersedia, metode ini akan mengembalikan pesan tersebut; jika tidak, ia akan menunggu hingga timeout yang ditentukan sebelum mengembalikan None. Metode poll biasanya digunakan dalam loop untuk terus memeriksa dan mengambil pesan baru secara berkala.

# pertanyaan: apa itu sessionmaker pada sqlalchemy dengan jawaban detil?
# Jawaban: sessionmaker pada SQLAlchemy adalah sebuah factory yang digunakan untuk membuat objek sesi (session) yang berfungsi sebagai jembatan antara aplikasi dan database. Objek sesi ini digunakan untuk mengelola transaksi, melakukan query, dan menyimpan perubahan ke database. Dengan menggunakan sessionmaker, kita dapat mengonfigurasi bagaimana sesi dibuat, termasuk menghubungkannya ke engine database tertentu. Ketika sessionmaker dipanggil, ia menghasilkan objek sesi baru yang dapat digunakan untuk berinteraksi dengan database. Ini memungkinkan pengelolaan koneksi database yang efisien dan terstruktur dalam aplikasi.

# pertanyaan: apa itu commit pada session sqlalchemy dan bedanya dengan execute dengan jawaban tidak panjang?
# Jawaban: Commit pada session SQLAlchemy adalah tindakan untuk menyimpan semua perubahan yang telah dilakukan dalam sesi ke database secara permanen. Sedangkan execute adalah metode yang digunakan untuk menjalankan perintah SQL atau query terhadap database. Jadi, execute menjalankan perintah, sementara commit menyimpan hasil dari perintah tersebut ke database.

# apakah harus commit baru data muncul di tabel database?
# Ya, dalam SQLAlchemy, setelah melakukan perubahan pada data menggunakan metode seperti execute atau menambahkan objek baru, Anda perlu memanggil commit pada sesi untuk menyimpan perubahan tersebut secara permanen ke database. Tanpa commit, perubahan tersebut hanya akan ada dalam sesi saat ini dan tidak akan tercermin di tabel database.

# pertanyaan: apa itu rollback pada session sqlalchemy dengan jawaban singkat?
# Jawaban: Rollback pada session SQLAlchemy adalah tindakan untuk membatalkan semua perubahan yang telah dilakukan dalam sesi saat ini, mengembalikan sesi ke keadaan sebelum perubahan tersebut dilakukan.

# pertanyaan: apa itu bind pada sessionmaker sqlalchemy dengan jawaban singkat?
# Jawaban: Bind pada sessionmaker SQLAlchemy adalah pengaturan yang menghubungkan sesi dengan engine database tertentu, sehingga sesi dapat berinteraksi dengan database tersebut.

# pertanyaan: apa itu engine pada sqlalchemy dengan jawaban singkat?
# Jawaban: Engine pada SQLAlchemy adalah objek yang mengelola koneksi ke database dan menyediakan antarmuka untuk berinteraksi dengan database tersebut.

# tadi barusan saya buat container docker untuk postgres dan engine tersebut, gimana cara membuat user baru atau database baru di dalam container postgres tersebut?
# Anda dapat membuat user baru atau database baru di dalam container PostgreSQL dengan mengikuti langkah-langkah berikut:
# 1. Masuk ke dalam container PostgreSQL menggunakan perintah:
#    docker exec -it <container_name> psql -U <username>
# 2. Setelah masuk ke psql, Anda dapat membuat user baru dengan perintah:
#    CREATE USER new_username WITH PASSWORD 'new_password';
# 3. Untuk membuat database baru, gunakan perintah:
#    CREATE DATABASE new_database_name;
# 4. Jika Anda ingin memberikan hak akses kepada user baru untuk database yang baru dibuat, gunakan perintah:
#    GRANT ALL PRIVILEGES ON DATABASE new_database_name TO new_username;
# 5. Setelah selesai, Anda dapat keluar dari psql dengan perintah:
#    \q

# benarkah pakai sqlalchemy lebih umum di industri dibandingkan psycopg2?
# Ya, SQLAlchemy lebih umum digunakan di industri dibandingkan psycopg2 karena SQLAlchemy menyediakan ORM (Object-Relational Mapping) yang memudahkan pengembang untuk bekerja dengan database menggunakan objek Python, sehingga meningkatkan produktivitas dan mengurangi kompleksitas kode. Psycopg2, di sisi lain, adalah driver database PostgreSQL yang lebih rendah tingkatnya dan memerlukan penulisan SQL secara langsung, yang bisa lebih rumit untuk aplikasi yang kompleks.

# jelaskan tentang ORM ini!
# ORM (Object-Relational Mapping) adalah sebuah teknik pemrograman yang memungkinkan pengembang untuk berinteraksi dengan database relasional menggunakan objek dalam bahasa pemrograman mereka, alih-alih menulis query SQL secara langsung. Dengan ORM, tabel dalam database direpresentasikan sebagai kelas (class) dalam kode, dan baris dalam tabel direpresentasikan sebagai objek dari kelas tersebut. Ini memungkinkan pengembang untuk melakukan operasi CRUD (Create, Read, Update, Delete) pada data menggunakan metode dan atribut objek, yang membuat kode lebih mudah dibaca dan dipelihara. ORM juga mengelola hubungan antar tabel, sehingga pengembang dapat bekerja dengan data yang saling terkait tanpa harus menulis join SQL secara manual. Contoh populer dari ORM di Python adalah SQLAlchemy dan Django ORM.

# kode di file ini itu isinya tentnag apa?
# Kode di file ini adalah sebuah konsumen Kafka yang membaca pesan dari topik "crypto-trades", memproses data perdagangan kripto yang diterima, dan menyimpannya ke dalam database PostgreSQL menggunakan SQLAlchemy. Kode ini mengonfigurasi konsumen Kafka, mengambil pesan, mengurai data JSON, dan menyisipkan data perdagangan ke dalam tabel database. Selain itu, kode ini juga menangani commit offset Kafka setelah data berhasil disimpan, serta mengelola transaksi database dengan commit dan rollback sesuai kebutuhan.

# apakah kode ini commit ke database one row at a time?
# Ya, kode ini melakukan commit ke database satu baris (one row) pada satu waktu. Setiap kali pesan diterima dari Kafka, data perdagangan diurai dan disisipkan ke dalam database, kemudian commit dilakukan segera setelah penyisipan berhasil. Jika terjadi kesalahan selama penyisipan, rollback dilakukan untuk membatalkan perubahan tersebut.

# apa keuntungan dan kelemahan commit one row at a time ini?
# Keuntungan commit one row at a time:
# 1. Konsistensi Data: Setiap baris data disimpan secara independen, sehingga jika terjadi kesalahan, hanya baris tersebut yang terpengaruh.
# 2. Sederhana: Implementasi lebih sederhana karena tidak perlu mengelola batch atau kumpulan data.
# 3. Responsif: Data dapat segera tersedia di database setelah setiap commit.
# Kelemahan commit one row at a time:
# 1. Kinerja: Commit satu per satu dapat menyebabkan overhead yang signifikan, terutama pada volume data yang besar, karena setiap commit memerlukan interaksi dengan database.
# 2. Latensi: Waktu yang dibutuhkan untuk menyimpan setiap baris dapat menambah latensi keseluruhan dalam pemrosesan data.
# 3. Beban pada Database: Dapat meningkatkan beban pada database karena banyaknya transaksi kecil yang harus ditangani.

# bagaimana jika saya commit database dalam batch, sedangkan commit offset kafka satu per satu?
# Jika Anda melakukan commit database dalam batch sementara commit offset Kafka satu per satu, ada beberapa hal yang perlu diperhatikan:
# 1. Konsistensi Data: Ada risiko inkonsistensi antara data yang disimpan di database dan offset Kafka. Jika terjadi kegagalan setelah beberapa baris disimpan tetapi sebelum offset Kafka di-commit, Anda mungkin kehilangan data yang telah disimpan.
# 2. Kompleksitas: Anda perlu mengelola logika tambahan untuk memastikan bahwa offset Kafka hanya di-commit setelah batch database berhasil disimpan, yang dapat menambah kompleksitas kode.
# 3. Kinerja: Meskipun commit database dalam batch dapat meningkatkan kinerja penyimpanan, commit offset satu per satu dapat memperlambat pemrosesan karena setiap offset harus di-commit secara terpisah.
# 4. Pemulihan: Dalam kasus kegagalan, pemulihan data menjadi lebih rumit karena Anda harus memastikan bahwa offset Kafka sesuai dengan data yang telah disimpan di database.
# Secara keseluruhan, penting untuk menyelaraskan strategi commit antara database dan Kafka untuk memastikan konsistensi dan keandalan data.

# berarti cadence commit offset kafka harus mengikuti cadence commit database, ya?
# Ya, cadence commit offset Kafka sebaiknya mengikuti cadence commit database untuk memastikan konsistensi data. Dengan menyelaraskan kedua proses commit ini, Anda dapat menghindari situasi di mana offset Kafka di-commit tetapi data belum disimpan di database, atau sebaliknya. Hal ini membantu menjaga integritas data dan memudahkan pemulihan jika terjadi kegagalan. Idealnya, Anda harus memastikan bahwa offset Kafka hanya di-commit setelah data berhasil disimpan di database.

# berarti kalau satu satu, kedua commit satu satu, kalau batch, kedua commit batch, ya?
# Ya, benar. Jika Anda memilih untuk melakukan commit satu per satu, maka baik commit database maupun commit offset Kafka harus dilakukan satu per satu. Sebaliknya, jika Anda memilih untuk melakukan commit dalam batch, maka kedua commit tersebut harus dilakukan dalam batch juga. Menyelaraskan cadence commit antara database dan Kafka membantu memastikan konsistensi data dan mengurangi risiko inkonsistensi antara data yang disimpan di database dan offset yang di-commit di Kafka.

# pertanyaan: apa itu idempotent consumer dan hubungannya dengan ON CONFLICT DO NOTHING?
# Jawaban: Idempotent consumer adalah konsep dalam pemrosesan pesan di mana konsumen dapat memproses pesan yang sama berulang kali tanpa menyebabkan efek samping atau perubahan yang tidak diinginkan pada sistem. Ini berarti bahwa jika pesan yang sama diterima lebih dari sekali, hasil akhir tetap konsisten dan tidak berubah.

# jika ada N partisi dan M consumer (N > M, tapi N != kelipatan N oleh M), apakah kafka nya yang dinamis mengatur pembagian partisi ke consumer?
# Ya, Kafka secara dinamis mengatur pembagian partisi ke konsumen dalam sebuah grup konsumen. Ketika ada N partisi dan M konsumen (dengan N > M dan N tidak merupakan kelipatan dari M), Kafka akan mendistribusikan partisi secara merata di antara konsumen yang tersedia. Beberapa konsumen mungkin mendapatkan lebih dari satu partisi, sementara yang lain mungkin hanya mendapatkan satu partisi. Kafka memastikan bahwa setiap partisi hanya dikonsumsi oleh satu konsumen dalam grup konsumen pada waktu tertentu, sehingga menghindari duplikasi pemrosesan pesan. Jika jumlah konsumen berubah (misalnya, konsumen baru ditambahkan atau dihapus), Kafka akan secara otomatis menyeimbangkan ulang pembagian partisi di antara konsumen yang tersisa.
# jadi kalau ada 10 partisi dan 3 consumer, pembagiannya gimana?
# Jika ada 10 partisi dan 3 konsumen, Kafka akan mendistribusikan partisi secara merata di antara ketiga konsumen tersebut. Pembagian partisi bisa terjadi sebagai berikut:
# - Konsumen 1: Partisi 0, Partisi 1, Partisi 2, Partisi 3
# - Konsumen 2: Partisi 4, Partisi 5, Partisi 6
# - Konsumen 3: Partisi 7, Partisi 8, Partisi 9
# Dalam contoh ini, Konsumen 1 mendapatkan 4 partisi, sementara Konsumen 2 dan Konsumen 3 masing-masing mendapatkan 3 partisi. Kafka memastikan bahwa setiap partisi hanya dikonsumsi oleh satu konsumen dalam grup konsumen pada waktu tertentu, sehingga menghindari duplikasi pemrosesan pesan. Jika jumlah konsumen berubah, Kafka akan menyeimbangkan ulang pembagian partisi sesuai dengan jumlah konsumen yang tersedia.

# berarti consumer ini bukan "pihak" kaku yang cuma melakukan satu identitas tugas saja, tetapi apa yang diminta oleh "manager"? misal ada partisi berisi koin BTC, ada partisi koin ETH, dan koin koin lain?
# Ya, konsumen Kafka bukanlah entitas yang kaku dengan satu identitas tugas saja. Konsumen dapat dikonfigurasi untuk menangani berbagai partisi yang berisi data berbeda, seperti partisi untuk koin BTC, ETH, dan koin lainnya. Manajer grup konsumen Kafka akan mengatur pembagian partisi di antara konsumen yang tersedia berdasarkan jumlah konsumen dan partisi yang ada. Setiap konsumen dapat menangani beberapa partisi sekaligus, memungkinkan fleksibilitas dalam pemrosesan data. Dengan demikian, konsumen dapat menyesuaikan tugasnya sesuai dengan kebutuhan aplikasi dan beban kerja yang dihadapi.

# berarti apakah di tengah proses consumer group, kafka bisa saja merevisi pembagian partisi ke consumer?
# Ya, Kafka dapat merevisi pembagian partisi ke konsumen di tengah proses konsumen group. Proses ini dikenal sebagai rebalancing. Rebalancing terjadi ketika ada perubahan dalam grup konsumen, seperti ketika konsumen baru ditambahkan, konsumen yang ada dihapus, atau ketika partisi baru ditambahkan ke topik. Saat rebalancing terjadi, Kafka akan mendistribusikan ulang partisi di antara konsumen yang tersedia untuk memastikan bahwa setiap partisi hanya dikonsumsi oleh satu konsumen pada waktu tertentu. Rebalancing ini memungkinkan Kafka untuk menyesuaikan pembagian beban kerja secara dinamis dan memastikan efisiensi dalam pemrosesan pesan. Namun, rebalancing juga dapat menyebabkan jeda singkat dalam pemrosesan pesan karena konsumen harus menyesuaikan diri dengan pembagian partisi yang baru.

# apakah skenario yang sangat umum di industri jika kecepatan producer jauh lebih tinggi daripada consumer memprosesnya, misal producer harga koin jauh lebih cepat dibanding consumer?
# Ya, skenario di mana kecepatan producer jauh lebih tinggi daripada kecepatan consumer adalah hal yang umum terjadi di industri, terutama dalam sistem yang menangani data real-time seperti harga koin kripto. Dalam situasi ini, beberapa pendekatan dapat digunakan untuk mengatasi ketidakseimbangan tersebut:
# 1. Scaling Out Consumers: Menambahkan lebih banyak konsumen ke dalam grup konsumen untuk meningkatkan kapasitas pemrosesan.
# 2. Batch Processing: Mengubah cara konsumen memproses pesan dengan mengambil beberapa pesan sekaligus dalam satu batch, sehingga mengurangi overhead pemrosesan per pesan.
# 3. Backpressure Handling: Mengimplementasikan mekanisme backpressure untuk mengatur aliran data dari producer ke consumer, sehingga mencegah overload pada konsumen.
# 4. Optimizing Consumer Logic: Meningkatkan efisiensi logika pemrosesan pada konsumen untuk mempercepat waktu pemrosesan.
# 5. Using Faster Storage: Memanfaatkan penyimpanan yang lebih cepat atau caching untuk mempercepat akses data selama pemrosesan.
# Dengan pendekatan-pendekatan ini, sistem dapat lebih efektif menangani situasi di mana producer menghasilkan data lebih cepat daripada yang dapat diproses oleh consumer.
