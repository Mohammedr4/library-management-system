# core/views.py
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import CustomUser, Book, Loan
from .serializers import UserRegistrationSerializer, UserSerializer, BookSerializer, LoanSerializer

# --- Authentication Views ---

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny] # Allow anyone to register

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# --- Book Views ---

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        # Anonymous users can list/retrieve (browse)
        # Authenticated users (registered) can list/retrieve (browse)
        # Admins can create, update, delete
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser] # For create, update, destroy
        return super().get_permissions()

    # Bonus: Filtering and Pagination will be applied via settings.py or custom filter backends later.

# --- Loan Views ---

class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated] # Only registered users can borrow

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        # Pass the book instance to the serializer for validation
        serializer = LoanSerializer(data={'book_id': book.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)

        try:
            # The create method in LoanSerializer handles setting user, book availability
            loan = serializer.save()
            return Response(LoanSerializer(loan, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated] # Only registered users can return

    def post(self, request, pk):
        # Find the specific loan by the current user for the given book that is not yet returned
        loan = get_object_or_404(
            Loan,
            book__pk=pk,
            user=request.user,
            return_date__isnull=True
        )

        serializer = LoanSerializer(loan, data={'return_date': timezone.now()}, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)

        try:
            # The update method in LoanSerializer handles setting return_date and book availability
            loan = serializer.save()
            return Response(LoanSerializer(loan, context={'request': request}).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only loans belonging to the authenticated user
        return Loan.objects.filter(user=self.request.user).order_by('-borrow_date')