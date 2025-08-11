from debug_toolbar.toolbar import debug_toolbar_urls
from django.http import JsonResponse
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import CreateUserView, ResetPasswordView, ResetPasswordConfirmView, UserProfileView, LogoutView, \
    UserDetailView, HealthIndicatorsView


def accounts_root(request):
    return JsonResponse({"message": "Accounts API root"})

router = DefaultRouter()
router.register(r'health-indicators', HealthIndicatorsView, basename='health-indicators')
urlpatterns = [
                  path("", accounts_root),
                  path("register/", CreateUserView.as_view(), name="register"),
                  path("login/", TokenObtainPairView.as_view(), name="login"),
                  path("logout/", LogoutView.as_view(), name="logout"),
                  path("profile/", UserProfileView.as_view(), name="profile"),
                  path("me/", UserDetailView.as_view(), name="me"),
                  path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
                  path("reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),
                  path("token/verify/", TokenVerifyView.as_view(), name="token_verify")
              ] + debug_toolbar_urls() + router.urls
