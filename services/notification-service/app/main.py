import logging
import os
from app.consumers.kafka_consumer import NotificationKafkaConsumerRunner

def main():
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO'),
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    logging.getLogger(__name__).info('StayMatch notification worker starting')
    runner = NotificationKafkaConsumerRunner()
    try:
        runner.start_listening()
    except KeyboardInterrupt:
        logging.getLogger(__name__).info('Stopping notification worker')

if __name__ == '__main__':
    main()
