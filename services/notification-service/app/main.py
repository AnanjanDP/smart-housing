import sys
import time
from app.consumers.kafka_consumer import NotificationKafkaConsumerRunner

def main():
    print("=== StayMatch Notification Service Worker Initialized ===")
    runner = NotificationKafkaConsumerRunner()
    try:
        runner.start_listening()
    except KeyboardInterrupt:
        print("Stopping Notification Service Worker...")

if __name__ == '__main__':
    main()
