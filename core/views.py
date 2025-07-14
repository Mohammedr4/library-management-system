# core/views.py

from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django_filters.rest_framework import DjangoFilterBackend # Re-added for filtering
from rest_framework.filters import SearchFilter, OrderingFilter # For search and ordering

from .models import CustomUser, Book, Loan
from .serializers import (
    CustomUserSerializer, RegisterSerializer,
    BookSerializer, LoanSerializer
)

# Custom Token Obtain Pair Serializer to include user data
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# User Registration View
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,) # Allow unauthenticated users to register
    serializer_class = RegisterSerializer

# User ViewSet (for listing, retrieving users - typically admin-only)
class CustomUserViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnly because creation/update is via register/profile update
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can view/list users
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'date_joined']


# Book ViewSet
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Authenticated users can create/update, others read
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter] # Re-added filter backends
    filterset_fields = ['genre', 'author'] # Filter books by genre and author
    search_fields = ['title', 'author', 'isbn'] # Search by title, author, ISBN
    ordering_fields = ['title', 'author', 'published_date', 'available_copies']


# Loan ViewSet
class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can access loans
    filter_backends = [DjangoFilterBackend, OrderingFilter] # Re-added filter backends
    filterset_fields = ['user', 'book', 'return_date'] # Filter loans by user, book, return status
    ordering_fields = ['loan_date', 'return_date']

    def get_queryset(self):
        # Allow users to only see their own loans unless they are staff/admin
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # When a loan is created, decrement available_copies of the book
        book = serializer.validated_data['book']
        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()
            serializer.save(user=self.request.user) # Assign the current user to the loan
        else:
            raise serializers.ValidationError("No copies of this book are available for loan.")

    def perform_update(self, serializer):
        # If return_date is being set, increment available_copies
        old_loan = self.get_object()
        new_return_date = serializer.validated_data.get('return_date')
        if new_return_date and not old_loan.return_date: # Only increment if it's being marked as returned
            book = old_loan.book
            book.available_copies += 1
            book.save()
        serializer.save()