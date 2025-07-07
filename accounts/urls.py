from django.urls import path

from accounts.views import CreateUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
]