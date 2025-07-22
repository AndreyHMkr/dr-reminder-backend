from rest_framework.routers import DefaultRouter

from services.views import ServiceViewSet, SpecialityViewSet

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="services")
router.register("speciality", SpecialityViewSet, basename="speciality")
urlpatterns = router.urls