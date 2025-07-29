from debug_toolbar.toolbar import debug_toolbar_urls
from django.http import JsonResponse
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, TokenBlacklistView,
)
from accounts.views import CreateUserView, ResetPasswordView, ResetPasswordConfirmView, UserProfileView, LogoutView


def accounts_root(request):
    return JsonResponse({"message": "Accounts API root"})


urlpatterns = [
                  path("", accounts_root),
                  path("register/", CreateUserView.as_view(), name="register"),
                  path("login/", TokenObtainPairView.as_view(), name="login"),
                  path("logout/", LogoutView.as_view(), name="logout"),
                  path("profile/", UserProfileView.as_view(), name="profile"),
                  path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
                  path("reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),
                  path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
                  path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
                  path("token/verify/", TokenVerifyView.as_view(), name="token_verify")
              ] + debug_toolbar_urls()
