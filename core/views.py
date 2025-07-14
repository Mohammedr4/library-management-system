# core/views.py

from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render

# Import filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import CustomUser, Book, Loan
from .serializers import (
    CustomUserSerializer, BookSerializer, LoanSerializer,
    RegisterSerializer, ChangePasswordSerializer
)

# core/views.py
from django.shortcuts import render

def frontend_view(request):
    """
    Renders the main frontend HTML page.
    """
    return render(request, 'index.html')

# ... (your existing ViewSets for API) ...

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAdminUser] # Only admins can manage users

    # Filtering, Searching, Ordering for CustomUser
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined']

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated], url_path='change-password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()] # Anyone can view books
        return [IsAdminUser()] # Only admin can create, update, delete books

    # Filtering, Searching, Ordering for Book
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['author', 'genre', 'published_date', 'available_copies']
    search_fields = ['title', 'author', 'isbn', 'genre']
    ordering_fields = ['title', 'author', 'published_date', 'available_copies']

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    # Filtering, Searching, Ordering for Loan
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'book', 'loan_date', 'return_date']
    search_fields = ['user__email', 'book__title', 'book__author']
    ordering_fields = ['loan_date', 'return_date']

    def perform_create(self, serializer):
        # Automatically set the user for a new loan to the requesting user
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Allow admin to see all loans, but regular users only their own loans
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)