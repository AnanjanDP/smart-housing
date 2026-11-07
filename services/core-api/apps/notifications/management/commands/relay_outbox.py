import logging
import time

from django.core.management.base import BaseCommand

from common.kafka import dispatch_pending

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Publish pending outbox events to Kafka. Runs until stopped unless --once is given."

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='Send what is pending and exit.')
        parser.add_argument('--interval', type=float, default=2.0, help='Seconds to wait when idle (default 2).')

    def handle(self, *args, **options):
        interval = options['interval']
        while True:
            try:
                sent = dispatch_pending()
            except Exception:
                logger.exception("Outbox relay iteration failed")
                sent = 0
            if sent:
                self.stdout.write(f"Published {sent} event(s)")
            if options['once']:
                return
            if not sent:
                time.sleep(interval)
