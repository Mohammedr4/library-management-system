# core/views.py

from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Removed filtering imports for stability
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter, OrderingFilter

from .models import CustomUser, Book, Loan
from .serializers import (
    CustomUserSerializer, RegisterSerializer,
    BookSerializer, LoanSerializer
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]
    # Removed filtering backends
    # filter_backends = [SearchFilter, OrderingFilter]
    # search_fields = ['email', 'first_name', 'last_name']
    # ordering_fields = ['email', 'first_name', 'date_joined']


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # Removed filtering backends
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['genre', 'author']
    # search_fields = ['title', 'author', 'isbn']
    # ordering_fields = ['title', 'author', 'published_date', 'available_copies']


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Removed filtering backends
    # filter_backends = [DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ['user', 'book', 'return_date']
    # ordering_fields = ['loan_date', 'return_date']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        if book.available_copies > 0:
            book.available_copies -= 1
            book.save()
            serializer.save(user=self.request.user)
        else:
            raise serializers.ValidationError("No copies of this book are available for loan.")

    def perform_update(self, serializer):
        old_loan = self.get_object()
        new_return_date = serializer.validated_data.get('return_date')
        if new_return_date and not old_loan.return_date:
            book = old_loan.book
            book.available_copies += 1
            book.save()
        serializer.save()