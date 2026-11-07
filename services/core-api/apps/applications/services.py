from django.db import transaction
from apps.applications.models import Application
from common.kafka import publish_event


def _application_event(event_type, application):
    """What a consumer needs to notify the right people, without calling back into this service."""
    listing = application.listing
    return {
        "event_type": event_type,
        "application_id": str(application.id),
        "listing_id": str(listing.id),
        "listing_title": listing.title,
        "status": application.status,
        "applicant_id": str(application.applicant_id),
        "applicant_email": application.applicant.email,
        "owner_id": str(listing.owner_id),
        "owner_email": listing.owner.email,
    }


class ApplicationService:
    @staticmethod
    def submit_application(applicant, listing, move_in_date, notes=None):
        with transaction.atomic():
            application = Application.objects.create(
                applicant=applicant,
                listing=listing,
                move_in_date=move_in_date,
                notes=notes
            )
            publish_event("application_events", _application_event("APPLICATION_SUBMITTED", application))
            return application

    @staticmethod
    def announce_status_change(application):
        """Record that an already-saved application changed status (call inside the saving transaction)."""
        publish_event("application_events", _application_event("APPLICATION_STATUS_UPDATED", application))

    @staticmethod
    def update_status(application, new_status):
        with transaction.atomic():
            application.status = new_status
            application.save()
            ApplicationService.announce_status_change(application)
            return application
