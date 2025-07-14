# core/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, Book, Loan

# --- User Serializers ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Remove password2 as it's not a model field
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    # This serializer can be used to display user details (e.g., for admin or profile)
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'is_staff', 'is_superuser') # Include relevant user fields

# --- Book Serializers ---

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__' # Include all fields from the Book model

# --- Loan Serializers ---

class LoanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Nested serializer to show user details
    book = BookSerializer(read_only=True) # Nested serializer to show book details
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book') # For creating/updating loan

    class Meta:
        model = Loan
        fields = ('id', 'user', 'book', 'book_id', 'borrow_date', 'return_date')
        read_only_fields = ('borrow_date',) # borrow_date is auto_now_add

    def validate(self, data):
        # Custom validation for borrowing a book
        if self.instance is None: # Only for creation (borrowing)
            book = data.get('book')
            if not book:
                raise serializers.ValidationError({"book_id": "Book ID is required to borrow a book."})

            if not book.availability:
                raise serializers.ValidationError({"book": "This book is currently not available."})

            # Check for existing unreturned loans by the same user for the same book
            user = self.context['request'].user
            if Loan.objects.filter(user=user, book=book, return_date__isnull=True).exists():
                raise serializers.ValidationError({"book": "You already have an unreturned loan for this book."})

        return data

    def create(self, validated_data):
        # Set the user to the current authenticated user
        validated_data['user'] = self.context['request'].user
        # Mark the book as unavailable upon successful loan creation
        book = validated_data['book']
        book.availability = False
        book.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # This serializer will also be used for returning a book.
        # Ensure return_date is set only once and book availability is updated.
        if 'return_date' in validated_data and instance.return_date is None:
            instance.return_date = validated_data['return_date']
            # Mark the book as available upon return
            instance.book.availability = True
            instance.book.save()
        elif 'return_date' in validated_data and instance.return_date is not None:
            raise serializers.ValidationError({"return_date": "This loan has already been returned."})

        return super().update(instance, validated_data)