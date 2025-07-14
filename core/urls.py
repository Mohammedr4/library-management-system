# core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, CustomTokenObtainPairView,
    CustomUserViewSet, BookViewSet, LoanViewSet
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'books', BookViewSet)
router.register(r'loans', LoanViewSet)


urlpatterns = [
    # JWT Authentication paths
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),

    # API endpoints from router
    path('', include(router.urls)),
]