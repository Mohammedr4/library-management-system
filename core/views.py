from rest_framework import viewsets, permissions, filters # Ensure 'filters' is imported
from django_filters.rest_framework import DjangoFilterBackend # NEW: Import DjangoFilterBackend

from .models import Book, Loan, CustomUser # Your models
from .serializers import BookSerializer, LoanSerializer, UserSerializer, UserRegistrationSerializer

# For JWT authentication views (already there)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# --- User Registration, Login, and ViewSets ---

class CustomUserRegistrationView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to register

    # Only allow create action (registration)
    def get_queryset(self):
        return CustomUser.objects.none() # Hide list of users for security via this view

    def list(self, request, *args, **kwargs):
        # Override list method to prevent listing users through the registration endpoint
        from rest_framework.response import Response
        from rest_framework import status
        return Response({'detail': 'Method not allowed for this endpoint.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class MyTokenObtainPairView(TokenObtainPairView):
    # This class uses the default Simple JWT serializer
    pass

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admin can manage users

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('title')
    serializer_class = BookSerializer
    
    # NEW: Add these lines for filtering, searching, and ordering (Bonus Feature)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'isbn', 'availability'] # Fields you can filter by exact match
    search_fields = ['title', 'author', 'isbn'] # Fields you can search by keyword
    ordering_fields = ['title', 'author', 'page_count'] # Fields you can order by

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAdminUser] # Admin can add/edit/delete books
        else:
            self.permission_classes = [permissions.AllowAny] # Anyone can list/retrieve books
        return super().get_permissions()

class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated] # Default to authenticated access

    def get_queryset(self):
        # Admin can see all loans, regular users only see their own
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(borrower=self.request.user)

    def perform_create(self, serializer):
        # When a user borrows a book, set the borrower to the current user
        # And ensure book availability is updated
        book = serializer.validated_data['book']
        if not book.availability:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("This book is currently not available.")
        
        serializer.save(borrower=self.request.user)
        book.availability = False
        book.save()

    def perform_update(self, serializer):
        # If a loan is marked as returned, update book availability
        old_instance = self.get_object()
        serializer.save()
        if serializer.instance.returned_date and not old_instance.returned_date:
            serializer.instance.book.availability = True
            serializer.instance.book.save()

    def perform_destroy(self, instance):
        # If a loan is deleted, mark the book as available again
        book = instance.book
        instance.delete()
        if not book.loan_set.filter(returned_date__isnull=True).exists():
            book.availability = True
            book.save()

# New view for user's personal loans (if you want a dedicated endpoint)
# class MyLoansViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Loan.objects.all()
#     serializer_class = LoanSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Loan.objects.filter(borrower=self.request.user)