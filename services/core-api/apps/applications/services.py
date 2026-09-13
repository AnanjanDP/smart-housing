from apps.applications.models import Application

class ApplicationService:
    @staticmethod
    def submit_application(applicant, listing, move_in_date, notes=None):
        application = Application.objects.create(
            applicant=applicant,
            listing=listing,
            move_in_date=move_in_date,
            notes=notes
        )
        return application

    @staticmethod
    def update_status(application, new_status):
        application.status = new_status
        application.save()
        return application
