from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest
from services.serializers import ServiceSerializer, MedicalSpecialtySerializer, EventSerializer, VaccinationSerializer, \
    AnalysisPackageSerializer, AnalysisTestSerializer


class ServiceViewSet(ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class MedicalSpecialtyViewSet(ReadOnlyModelViewSet):
    queryset = MedicalSpecialty.objects.all()
    serializer_class = MedicalSpecialtySerializer
    permission_classes = [AllowAny]

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class VaccinationViewSet(ReadOnlyModelViewSet):
    queryset = Vaccination.objects.all()
    serializer_class = VaccinationSerializer
    permission_classes = [AllowAny]

class AnalysisPackageViewSet(ReadOnlyModelViewSet):
    queryset = AnalysisPackage.objects.all()
    serializer_class = AnalysisPackageSerializer
    permission_classes = [AllowAny]

class AnalysisTestViewSet(ReadOnlyModelViewSet):
    queryset = AnalysisTest.objects.all()
    serializer_class = AnalysisTestSerializer
    permission_classes = [AllowAny]
