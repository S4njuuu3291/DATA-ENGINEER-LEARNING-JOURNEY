import json

from confluent_kafka import Consumer

consumer_confs = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "crypto_consumer_group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}

consumer = Consumer(consumer_confs)
consumer.subscribe(["crypto_trades"])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        trade_data = json.loads(msg.value().decode("utf-8"))
        print(
            f"Received event: {trade_data}"
            f"from partition: {msg.partition()}"
            f"at offset: {msg.offset()}"
        )

        consumer.commit(msg)
except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
