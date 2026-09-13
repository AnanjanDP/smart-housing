import time

def main():
    print("=== StayMatch Notification Service Worker Initialized ===")
    print("Listening for Kafka events on topics: listing_events, application_events, review_events...")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping Notification Service Worker...")

if __name__ == '__main__':
    main()
