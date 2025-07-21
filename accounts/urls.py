from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import CreateUserView, ResetPasswordView, ResetPasswordConfirmView, UserProfileView

urlpatterns = [
                  path("register/", CreateUserView.as_view(), name="register"),
                  path("profile/", UserProfileView.as_view(), name="profile"),
                  path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
                  path("reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),
                  path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
                  path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
                  path("token/verify/", TokenVerifyView.as_view(), name="token_verify")
              ] + debug_toolbar_urls()
