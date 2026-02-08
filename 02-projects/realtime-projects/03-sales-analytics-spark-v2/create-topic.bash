kafka-topics --create \
  --topic sales_events \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
