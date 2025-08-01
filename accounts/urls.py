from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import CreateUserView, ResetPasswordView, ResetPasswordConfirmView, UserProfileView, LogoutView, \
    UserDetailView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("me/", UserDetailView.as_view(), name="me"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify")
]
