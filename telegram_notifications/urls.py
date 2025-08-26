from django.urls import path
from .views import create_link_token, link_by_token, me_status, toggle_active, unlink

urlpatterns = [
    path("link-token/", create_link_token),  # фронт генерит токен
    path("link/", link_by_token),            # бот связывает
    path("status/", me_status),
    path("toggle/", toggle_active),          # PATCH {is_active: true/false}
    path("unlink/", unlink),                 # DELETE
]