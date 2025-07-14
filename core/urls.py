# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegistrationView,
    BookViewSet,
    BorrowBookView,
    ReturnBookView,
    UserLoansView
)

router = DefaultRouter()
router.register(r'books', BookViewSet) # Register BookViewSet for CRUD operations

urlpatterns = [
    # Authentication URLs
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Book & Loan URLs
    path('', include(router.urls)), # Includes /books/ and /books/<pk>/
    path('books/<int:pk>/borrow/', BorrowBookView.as_view(), name='borrow_book'),
    path('books/<int:pk>/return/', ReturnBookView.as_view(), name='return_book'),
    path('my-loans/', UserLoansView.as_view(), name='my_loans'),
]