#!/usr/bin/env bash
set -e

echo "Triggering Kafka topic creation..."
docker-compose exec kafka /bin/sh -c "
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic listing_events
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic application_events
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic review_events
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --topic notification_events
"
echo "Done!"
