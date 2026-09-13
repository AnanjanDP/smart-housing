from rest_framework import viewsets, permissions
from apps.applications.models import Application
from apps.applications.serializers import ApplicationSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'LANDLORD':
            return Application.objects.filter(listing__owner=user)
        return Application.objects.filter(applicant=user)

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
