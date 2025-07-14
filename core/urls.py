from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomUserRegistrationView,
    MyTokenObtainPairView,
    CustomUserViewSet,
    BookViewSet,
    LoanViewSet,
)

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'books', BookViewSet, basename='book')
router.register(r'loans', LoanViewSet, basename='loan')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', CustomUserRegistrationView.as_view({'post': 'create'}), name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]