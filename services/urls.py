from rest_framework.routers import DefaultRouter

from services.views import ServiceViewSet, MedicalSpecialtyViewSet

router = DefaultRouter()
router.register('services', ServiceViewSet, basename='services')
router.register("medical-specialties", MedicalSpecialtyViewSet, basename='medical-specialty')
urlpatterns = router.urls