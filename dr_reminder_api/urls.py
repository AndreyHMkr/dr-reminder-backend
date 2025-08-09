"""
URL configuration for dr_reminder_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from dr_reminder_api import settings
import debug_toolbar
from django.conf.urls.static import static
from django.http import JsonResponse



def root_view(request):
    return JsonResponse({"message": "Backend is alive."})


urlpatterns = [
                  path("api/services/", include("services.urls")),

                  path('', root_view),
                  path("__debug__/", include(debug_toolbar.urls)),
                  path("api/telegram/", include("telegram_notifications.urls")),
                  path("api/accounts/", include("accounts.urls")),
                  path("__debug__/", include(debug_toolbar.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

