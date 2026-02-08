import json
import time
from math import prod

from confluent_kafka import Producer


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(
            f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )


producer_confs = {
    "bootstrap.servers": "localhost:9092",
    # Reliability
    "acks": "all",
    "retries": 5,
    # Latency vs Throughput
    "linger.ms": 50,
    "batch.num.messages": 1000,
    # Safety
    "enable.idempotence": True,
}

producer = Producer(producer_confs)

topic = "crypto_trades"

for i in range(20):
    event = {
        "symbol": "BTCUSDT",
        "price": 50000 + i * 100,
        "event_time": int(time.time() * 1000),
    }
    producer.produce(
        topic,
        key=event["symbol"],
        value=json.dumps(event),
        on_delivery=delivery_report,
    )
    producer.poll(0)
    time.sleep(1)

producer.flush()
