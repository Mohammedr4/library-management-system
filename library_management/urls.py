# library_management/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers # Ensure this is imported

# ... other imports ...

# Define your ViewSets from core.views
from core.views import CustomUserViewSet, BookViewSet, LoanViewSet, frontend_view

# DRF-YASG Schema View (already there)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# --- ENSURE THIS 'router' DEFINITION IS PRESENT AND BEFORE urlpatterns ---
router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'books', BookViewSet)
router.register(r'loans', LoanViewSet)
# --- END router DEFINITION ---


# DRF-YASG Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Library Management API",
      default_version='v1',
      description="API for managing books, users, and loans in a library system.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@library.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Frontend Root
    path('', frontend_view, name='home'),

    # API Endpoints
    path('api/', include(router.urls)), # This line requires 'router' to be defined above
    path('api/users/register/', CustomUserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('api/users/<int:pk>/change-password/', CustomUserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # DRF-YASG Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]