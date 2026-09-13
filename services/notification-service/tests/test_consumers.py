import unittest
from app.consumers.listing_consumer import ListingEventConsumer
from app.consumers.application_consumer import ApplicationEventConsumer

class TestConsumers(unittest.TestCase):
    def test_listing_consumer(self):
        consumer = ListingEventConsumer()
        payload = {"title": "Test Apartment", "city": "SF", "price": 2000}
        consumer.handle_message(payload)

    def test_application_consumer(self):
        consumer = ApplicationEventConsumer()
        payload = {"listing_id": "123", "status": "APPROVED"}
        consumer.handle_message(payload)

if __name__ == '__main__':
    unittest.main()
