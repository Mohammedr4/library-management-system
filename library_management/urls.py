# library_management/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import routers

# Imports for DRF-YASG (Swagger/Redoc)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# IMPORTANT: Import your ViewSets from core.views directly here
from core.views import CustomUserViewSet, BookViewSet, LoanViewSet

# Define schema_view for Swagger/Redoc
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management API",
        default_version='v1',
        description="API for managing library books, users, and loans.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourproject.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Initialize the router and register your ViewSets
router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet) # This will handle /api/users/, /api/users/register/, /api/users/<pk>/change-password/
router.register(r'books', BookViewSet)
router.register(r'loans', LoanViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # This includes all URLs from your registered ViewSets
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # DRF-YASG (Swagger/Redoc) URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]