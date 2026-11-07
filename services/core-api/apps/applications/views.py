from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from apps.applications.models import Application
from apps.applications.serializers import ApplicationSerializer, ACTIVE_STATUSES


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # You see the applications you made and the applications made to your listings, nothing else.
        user = self.request.user
        return (
            Application.objects.filter(Q(applicant=user) | Q(listing__owner=user))
            .select_related('listing', 'listing__owner', 'applicant')
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def perform_destroy(self, instance):
        # Applicants may withdraw an open application; a landlord cannot delete the applicant's record
        # and a decided application is kept as history.
        if instance.applicant_id != self.request.user.id:
            raise PermissionDenied('Only the applicant can withdraw an application.')
        if instance.status not in ACTIVE_STATUSES:
            raise PermissionDenied('A decided application cannot be withdrawn.')
        instance.delete()
