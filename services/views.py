from django.db.models import Prefetch
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from services.models import Service, MedicalSpecialty, Event, Vaccination, AnalysisPackage, AnalysisTest, TreatmentPlan, \
    TreatmentIntake
from services.serializers import ServiceSerializer, MedicalSpecialtySerializer, EventSerializer, VaccinationSerializer, \
    AnalysisPackageSerializer, AnalysisTestSerializer, EventRetrySerializer, TreatmentPlanCreateSerializer, \
    TreatmentPlanReadSerializer


class ServiceViewSet(ReadOnlyModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class MedicalSpecialtyViewSet(ReadOnlyModelViewSet):
    queryset = MedicalSpecialty.objects.all()
    serializer_class = MedicalSpecialtySerializer
    permission_classes = [AllowAny]

class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventRetrySerializer
        return EventSerializer
    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

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

class TreatmentPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TreatmentPlan.objects.filter(
            user=self.request.user,
        ).prefetch_related(
            Prefetch(
                "intakes",
                queryset=TreatmentIntake.objects.order_by("time")
            )
        ).order_by("-id")
    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TreatmentPlanCreateSerializer
        return TreatmentPlanReadSerializer