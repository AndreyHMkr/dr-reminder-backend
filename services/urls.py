from rest_framework.routers import DefaultRouter

from accounts.views import BloodDonationView, DonationCenterViewSet
from services.views import ServiceViewSet, MedicalSpecialtyViewSet, EventViewSet, VaccinationViewSet, \
    AnalysisPackageViewSet, AnalysisTestViewSet, TreatmentPlanViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet, basename='services')
router.register("medical-specialties", MedicalSpecialtyViewSet, basename='medical-specialty')
router.register("events", EventViewSet, basename="events")
router.register("treatment-plans", TreatmentPlanViewSet, basename="treatment-plans")
router.register("donation-centers", DonationCenterViewSet, basename="donation-center")
router.register("blood-donations", BloodDonationView, basename="blood-donations")
router.register("vaccinations", VaccinationViewSet, basename="vaccinations")
router.register("analysis-packages", AnalysisPackageViewSet, basename="analysis-packages")
router.register("analysis-tests", AnalysisTestViewSet, basename="analysis-tests")
urlpatterns = router.urls