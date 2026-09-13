from app.services.email_service import EmailService

class NotificationService:
    @staticmethod
    def process_listing_event(event_data):
        subject = f"New Listing Alert: {event_data.get('title')}"
        body = f"A new listing was published in {event_data.get('city')} for ${event_data.get('price')}."
        EmailService.send_email("subscribers@staymatch.com", subject, body)

    @staticmethod
    def process_application_event(event_data):
        subject = f"Application Update: Status is {event_data.get('status')}"
        body = f"Your application for listing {event_data.get('listing_id')} has been updated to {event_data.get('status')}."
        EmailService.send_email("applicant@staymatch.com", subject, body)
