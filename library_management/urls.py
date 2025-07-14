# library_management/urls.py

from django.contrib import admin
from django.urls import path, include

# No drf_yasg imports as it's not in settings.py for now

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')), # Include URLs from your core app
]