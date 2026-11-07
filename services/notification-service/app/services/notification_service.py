from app.services.email_service import EmailService


class InvalidEventError(ValueError):
    """The event can never be processed (missing data). Retrying cannot help, so it goes to the dead-letter topic."""
    permanent = True


def _required(event: dict, key: str):
    value = event.get(key)
    if not value:
        raise InvalidEventError(f"event {event.get('event_type', '?')} is missing '{key}'")
    return value


class NotificationService:
    """Turns domain events into emails to the people they concern."""

    def __init__(self, email_service=EmailService):
        self.email = email_service

    def process_listing_event(self, event: dict) -> None:
        owner = _required(event, 'owner_email')
        self.email.send_email(
            owner,
            f"Your listing is live: {event.get('title')}",
            f"Your listing \"{event.get('title')}\" in {event.get('city')} (rent {event.get('price')}) "
            f"has been published on StayMatch.",
        )

    def process_application_event(self, event: dict) -> None:
        kind = event.get('event_type')
        title = event.get('listing_title') or event.get('listing_id')
        if kind == 'APPLICATION_SUBMITTED':
            self.email.send_email(
                _required(event, 'owner_email'),
                f"New application for {title}",
                f"Someone applied for \"{title}\". Open StayMatch to review the application.",
            )
        elif kind == 'APPLICATION_STATUS_UPDATED':
            status = _required(event, 'status')
            self.email.send_email(
                _required(event, 'applicant_email'),
                f"Your application for {title}: {status.replace('_', ' ').title()}",
                f"Your application for \"{title}\" is now {status.replace('_', ' ').lower()}.",
            )
        else:
            raise InvalidEventError(f"unknown application event type '{kind}'")

    def process_review_event(self, event: dict) -> None:
        recipient = _required(event, 'recipient_email')
        about = f" on \"{event['listing_title']}\"" if event.get('listing_title') else ""
        self.email.send_email(
            recipient,
            "You received a new review",
            f"You received a {event.get('rating')}-star review{about}. Open StayMatch to read it.",
        )
