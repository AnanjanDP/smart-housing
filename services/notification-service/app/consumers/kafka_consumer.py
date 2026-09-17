import json
import logging
import os
import time
from app.consumers.listing_consumer import ListingEventConsumer
from app.consumers.application_consumer import ApplicationEventConsumer
from app.consumers.review_consumer import ReviewEventConsumer

logger = logging.getLogger(__name__)

class NotificationKafkaConsumerRunner:
    def __init__(self):
        self.listing_consumer = ListingEventConsumer()
        self.application_consumer = ApplicationEventConsumer()
        self.review_consumer = ReviewEventConsumer()
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')

    def start_listening(self):
        from kafka import KafkaConsumer
        topics = ['listing_events', 'application_events', 'review_events']
        
        while True:
            try:
                print(f"Connecting to Kafka at {self.bootstrap_servers}...")
                consumer = KafkaConsumer(
                    *topics,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id='notification-service-group',
                    auto_offset_reset='earliest',
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                print("Successfully connected to Kafka. Listening for events...")
                for message in consumer:
                    topic = message.topic
                    payload = message.value
                    print(f"Received message from topic [{topic}]: {payload}")
                    
                    if topic == 'listing_events':
                        self.listing_consumer.handle_message(payload)
                    elif topic == 'application_events':
                        self.application_consumer.handle_message(payload)
                    elif topic == 'review_events':
                        self.review_consumer.handle_message(payload)
            except Exception as err:
                print(f"Kafka consumer encountered error ({err}). Reconnecting in 5 seconds...")
                time.sleep(5)
