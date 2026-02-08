from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg2://kafka_user:kafka_pass@localhost:5432/kafka_streaming"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,  # echo digunakan untuk menampilkan log SQL yang dihasilkan
    pool_size=5,  # pool digunakan untuk mengatur jumlah koneksi maksimum dalam pool
    max_overflow=10,  # max_overflow digunakan untuk mengatur jumlah koneksi tambahan yang dapat dibuat di luar pool_size
)
