import asyncio
import json
from math import prod

import websockets
from confluent_kafka import Producer

from models import TradeEvent

producer_confs = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
    "retries": 5,
    "linger.ms": 100,
    "batch.size": 16384,
    "enable.idempotence": True,
}

BINANCE_WS = "wss://stream.binance.com:9443/ws/btcusdt@trade"
TOPIC = "crypto_trades"


import asyncio
import json

import websockets
from confluent_kafka import Producer

from models import TradeEvent

producer_confs = {
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
    "retries": 5,
    "linger.ms": 100,
    "batch.size": 16384,
    "enable.idempotence": True,
}

BINANCE_WS = "wss://stream.binance.com:9443/ws/btcusdt@trade"
TOPIC = "crypto_trades"


async def stream_trades():
    producer = Producer(producer_confs)

    # Bungkus dalam loop supaya kalau putus bisa nyambung lagi otomatis
    while True:
        try:
            print(f"Connecting to Binance WebSocket...")
            # TAMBAHKAN: open_timeout agar lebih sabar saat koneksi awal
            async with websockets.connect(
                BINANCE_WS, open_timeout=20, ping_interval=20
            ) as ws:
                print("✅ Connected to Binance WebSocket")

                while True:
                    msg = await ws.recv()
                    raw_event = json.loads(msg)

                    try:
                        trade = TradeEvent.from_binance(raw_event)
                    except Exception as e:
                        print(f"⚠️ Invalid event skipped: {e}")
                        continue

                    # Kirim ke Kafka
                    producer.produce(
                        TOPIC,
                        key=trade.symbol,
                        value=trade.model_dump_json(),
                    )

                    # Trigger pengiriman batch
                    producer.poll(0)

                    print(f"🚀 Produced: {trade.symbol} at {trade.price}")

                    # Opsional: Jangan terlalu lama sleep kalau mau real-time
                    # await asyncio.sleep(0.1)

        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
            print(f"❌ Connection error: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"🔥 Unexpected error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(stream_trades())
    except KeyboardInterrupt:
        print("\nStopping Producer...")
