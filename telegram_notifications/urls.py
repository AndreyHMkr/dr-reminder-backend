from django.urls import path
from .views import SaveChatIdView

urlpatterns = [path("save-chat-id/", SaveChatIdView.as_view())]
