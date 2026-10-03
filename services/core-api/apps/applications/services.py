from django.db import transaction
from apps.applications.models import Application
from common.kafka import publish_event

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
            publish_event("application_events", {
                "event_type": "APPLICATION_SUBMITTED",
                "application_id": str(application.id),
                "listing_id": str(listing.id),
                "applicant_id": str(applicant.id),
                "status": application.status
            })
            return application

    @staticmethod
    def update_status(application, new_status):
        with transaction.atomic():
            application.status = new_status
            application.save()
            publish_event("application_events", {
                "event_type": "APPLICATION_STATUS_UPDATED",
                "application_id": str(application.id),
                "listing_id": str(application.listing.id),
                "applicant_id": str(application.applicant.id),
                "status": application.status
            })
            return application

