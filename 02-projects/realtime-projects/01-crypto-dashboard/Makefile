DB_NAME=crypto-stream-sink
DB_USER=crypto-stream-user
DB_CONTAINER = postgres
.PHONY: setup-kafka run-producer run-consumer run-spark db-shell clean clean-port

stop-compose:
	docker compose down -v

start-compose:
	docker compose up -d

setup-kafka:
	docker exec -it kafka-crypto-stream kafka-topics --create --topic crypto_prices --partitions 20 --replication-factor 1 --bootstrap-server localhost:9092

init-db:
	cat scripts/init-db.sql | docker exec -i $(DB_CONTAINER) psql -U $(DB_USER) $(DB_NAME)

run-producer:
	poetry run python producer/crypto-price-producer.py

run-consumer:
	poetry run python consumer-spark/spark-consume.py

run-spark:
	spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.7.2 main.py

db-shell:
	docker exec -it $(DB_CONTAINER) psql -U ${DB_USER} -d ${DB_NAME}

clean:
	rm -rf checkpoint/*

clean-port:
	sudo systemctl stop postgresql && sudo systemctl disable postgresql


