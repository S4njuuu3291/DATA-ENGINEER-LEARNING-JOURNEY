import asyncio
import json
import time

import websockets
import yaml
from confluent_kafka import Producer, SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from models import CryptoPrice


async def send_message(symbol: str):
    ws_url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
    while True:
        try:
            print("Connecting to WebSocket for symbol:", symbol)
            async with websockets.connect(ws_url) as websocket:
                print("✅ Connected to WebSocket for symbol:", symbol)
                while True:
                    message = await websocket.recv()
                    raw_events = json.loads(message)
                    try:
                        crypto_price = CryptoPrice.from_kafka_message(raw_events)
                    except Exception as e:
                        print("⚠️ Error parsing message:", e)
                        continue

                    avro_record = crypto_price.model_dump()
                    # state deduplikasi
                    current_fingerprint = (
                        f"{crypto_price.symbol}-{crypto_price.event_time}"
                    )
                    if last_prices.get(symbol) == current_fingerprint:
                        continue
                    last_prices[symbol] = current_fingerprint

                    producer.produce(
                        KAFKA_TOPIC,
                        value=avro_record,
                    )
                    producer.poll(0)
                    print(
                        f"Produced message for {crypto_price.symbol} at price {crypto_price.price}"
                    )
        except Exception as e:
            print("⚠️ Error connecting to WebSocket for symbol:", symbol, e)
            await asyncio.sleep(5)


if __name__ == "__main__":
    config = yaml.safe_load(open(".//config//settings.yml", "r"))
    symbols = config["symbols"]
    KAFKA_TOPIC = config["kafka"]["topic"]
    BOOTSTRAP_SERVERS = config["kafka"]["bootstrap_servers"]
    last_prices = {}

    sr_config = {
        "url": config["schema_registry"]["url"],
    }
    schema_registry_client = SchemaRegistryClient(sr_config)

    with open("avro_schema/producer_schema_v1.avsc") as f:
        schema_str = f.read()

    avro_serializer = AvroSerializer(schema_registry_client, schema_str)

    producer_config = {
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "client.id": "crypto-price-producer",
        "acks": "all",
        "retries": 2,
        "enable.idempotence": True,
        "batch.size": 16384,
        "linger.ms": 100,
        "value.serializer": avro_serializer,
    }

    producer = SerializingProducer(producer_config)

    try:
        loop = asyncio.get_event_loop()
        tasks = [send_message(symbol) for symbol in symbols]
        loop.run_until_complete(asyncio.gather(*tasks))
    except KeyboardInterrupt:
        print("⚠️ Keyboard interrupt received, exiting...")
    finally:
        producer.flush()
        print("✅ Producer flushed and closed.")
