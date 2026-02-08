import json

from fastavro import parse_schema, writer

with open("1-teori-dasar//trade_schema.avsc", "r") as f:
    schema = parse_schema(json.load(f))

records = [
    {"symbol": "BTCUSDT", "price": 45005, "event_time": 1689000000000},
    {"symbol": "ETHUSDT", "price": 3200, "event_time": 1689000001000},
]

with open("1-teori-dasar//trades.avro", "wb") as out:
    writer(out, schema, records)

print("Berhasil menulis data ke trades.avro!")
