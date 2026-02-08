import json
import random
import time
from datetime import datetime, timedelta

from confluent_kafka import Producer

producer_config = {
    "bootstrap.servers": "localhost:9092",
    "client.id": "sales_data_generator",
}

# APA ITU BOOTSTRAP SERVERS DISINI?
# Bootstrap servers adalah daftar host/port pasangan yang digunakan oleh klien Kafka untuk terhubung ke cluster Kafka. Ini adalah titik masuk awal untuk klien agar dapat menemukan broker Kafka lainnya dalam cluster.

producer = Producer(producer_config)

categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# Fungsi ini dipanggil untuk melaporkan status pengiriman pesan ke Kafka.


def generate_transaction():
    """Generate realistic transaction event"""
    # Event time: mostly current, 10% late (2-8 minutes ago)
    if random.random() < 0.1:
        # Late event
        delay_seconds = random.randint(120, 480)  # 2-8 minutes
        event_time = datetime.now() - timedelta(seconds=delay_seconds)
    else:
        # On-time event
        event_time = datetime.now()

    transaction = {
        "transaction_id": f"TXN{random.randint(100000, 999999)}",
        "category": random.choice(categories),
        "amount": round(random.uniform(10.0, 500.0), 2),
        "quantity": random.randint(1, 10),
        "event_timestamp": event_time.isoformat(),  # ISO format
        "customer_id": f"CUST{random.randint(1000, 9999)}",
    }
    return transaction


# Fungsi diatas menghasilkan data transaksi penjualan yang realistis dengan kemungkinan 10% untuk menjadi event terlambat.

# Generate 1000 events
print("Generating transactions to Kafka...")
while True:
    transaction = generate_transaction()

    # Serialize ke JSON
    message = json.dumps(transaction).encode("utf-8")

    # Produce ke Kafka
    producer.produce(
        topic="sales_events",
        key=transaction["transaction_id"].encode("utf-8"),
        value=message,
        callback=delivery_report,
    )

    # Trigger callbacks
    producer.poll(0)

    # Simulate streaming (10 events/sec)
    time.sleep(0.1)

# Fungsi diatas menghasilkan 1000 event transaksi penjualan dan mengirimkannya ke topik Kafka "sales_events" dengan kecepatan sekitar 10 event per detik.

producer.flush()
print("Data generation complete!")
# .flush() memastikan semua pesan yang tertunda telah dikirim ke Kafka sebelum program berakhir.
