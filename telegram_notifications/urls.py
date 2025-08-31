from django.urls import path
from . import views


urlpatterns = [
    path("link-token/", views.create_link_token, name="create_link_token"),
    path("link/",       views.link_by_token,     name="link_by_token"),
    path("status/",     views.me_status,         name="me_status"),
    path("toggle/", views.toggle_active, name="toggle_active"),

]