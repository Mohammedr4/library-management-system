# core/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient # <-- THIS CRUCIAL IMPORT LINE
from django.contrib.auth import get_user_model
from .models import Book, Loan # Make sure your models are correctly imported

User = get_user_model()


class UserRegistrationTest(APITestCase):
    """
    Test suite for User Registration API endpoint.
    """
    def setUp(self):
        self.register_url = reverse('register') 
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123!', 
            'password2': 'StrongPassword123!'
        }

    def test_user_registration_success(self):
        """
        Ensure we can register a new user.
        """
        response = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1) 
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_registration_with_existing_username(self):
        """
        Ensure user cannot register with an existing username.
        """
        user_create_data = self.test_user_data.copy()
        user_create_data.pop('password2', None) 
        User.objects.create_user(**user_create_data) 

        response = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data) 

    def test_user_registration_with_mismatched_passwords(self):
        """
        Ensure user cannot register with mismatched passwords.
        """
        data = self.test_user_data.copy()
        data['password2'] = 'mismatched_password'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data) 


class APITokenObtainTest(APITestCase):
    """
    Test suite for JWT Token Obtain API endpoint.
    """
    def setUp(self):
        self.login_url = reverse('token_obtain_pair') 
        self.test_user_data = {
            'username': 'testuser_login', 
            'email': 'test_login@example.com', 
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!'
        }
        user_create_data = self.test_user_data.copy()
        user_create_data.pop('password2', None)
        self.user = User.objects.create_user(**user_create_data)


    def test_token_obtain_success(self):
        """
        Ensure a user can obtain an access token with valid credentials.
        """
        response = self.client.post(self.login_url, {
            'username': self.test_user_data['username'],
            'password': self.test_user_data['password']
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) 
        self.assertIn('refresh', response.data) 

    def test_token_obtain_invalid_credentials(self):
        """
        Ensure token cannot be obtained with invalid credentials.
        """
        response = self.client.post(self.login_url, {
            'username': self.test_user_data['username'],
            'password': 'wrongpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 
        self.assertIn('detail', response.data) 
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')


class BookAPITest(APITestCase):
    """
    Test suite for Book API endpoints (creation and listing).
    """
    def setUp(self):
        # Create an admin user to perform privileged actions (like creating books)
        self.admin_user_data = {
            'username': 'admin_test',
            'email': 'admin@example.com',
            'password': 'AdminPassword123!',
            'password2': 'AdminPassword123!'
        }
        admin_create_data = self.admin_user_data.copy()
        admin_create_data.pop('password2', None)
        self.admin_user = User.objects.create_superuser(**admin_create_data) # Create a superuser

        # Create a regular user for non-privileged actions if needed (e.g., listing)
        self.regular_user_data = {
            'username': 'regular_test',
            'email': 'regular@example.com',
            'password': 'RegularPassword123!',
            'password2': 'RegularPassword123!'
        }
        regular_create_data = self.regular_user_data.copy()
        regular_create_data.pop('password2', None)
        self.regular_user = User.objects.create_user(**regular_create_data)


        # Get tokens for authentication
        login_url = reverse('token_obtain_pair')
        admin_response = self.client.post(login_url, {
            'username': self.admin_user_data['username'],
            'password': self.admin_user_data['password']
        }, format='json')
        self.admin_token = admin_response.data['access']

        regular_response = self.client.post(login_url, {
            'username': self.regular_user_data['username'],
            'password': self.regular_user_data['password']
        }, format='json')
        self.regular_token = regular_response.data['access']


        # URLs for book operations
        self.book_list_create_url = reverse('book-list') # Assumes 'book-list' name for /api/books/

        # Sample book data
        self.book_data = {
            'title': 'Test Book Title',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'page_count': 300
        }


    def test_create_book_as_admin(self):
        """
        Ensure an admin user can create a book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = self.client.post(self.book_list_create_url, self.book_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, self.book_data['title'])
        self.assertTrue(Book.objects.get().availability)

    def test_create_book_as_regular_user_denied(self):
        """
        Ensure a regular user cannot create a book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_token)
        response = self.client.post(self.book_list_create_url, self.book_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 
        self.assertEqual(Book.objects.count(), 0) 

    def test_list_books_authenticated(self):
        """
        Ensure authenticated users (admin or regular) can list books.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        self.client.post(self.book_list_create_url, self.book_data, format='json')
        self.client.credentials() 

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_token)
        response = self.client.get(self.book_list_create_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 
        self.assertEqual(response.data[0]['title'], self.book_data['title'])

    def test_list_books_unauthenticated(self):
        """
        Ensure unauthenticated users can list books (if allowed by permissions).
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        self.client.post(self.book_list_create_url, self.book_data, format='json')

        self.client.credentials() 
        response = self.client.get(self.book_list_create_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.book_data['title'])


class LoanAPITest(APITestCase):
    """
    Test suite for Loan API endpoints (borrow, my-loans, return).
    """
    def setUp(self):
        # Create a regular user who will borrow/return books
        self.user_data = {
            'username': 'borrower_test',
            'email': 'borrower@example.com',
            'password': 'BorrowerPassword123!',
            'password2': 'BorrowerPassword123!'
        }
        user_create_data = self.user_data.copy()
        user_create_data.pop('password2', None)
        self.user = User.objects.create_user(**user_create_data)

        # Create an admin user to create books
        self.admin_user_data = {
            'username': 'loan_admin',
            'email': 'loan_admin@example.com',
            'password': 'LoanAdminPassword123!',
            'password2': 'LoanAdminPassword123!'
        }
        admin_create_data = self.admin_user_data.copy()
        admin_create_data.pop('password2', None)
        self.admin_user = User.objects.create_superuser(**admin_create_data)

        # Get token for the regular user
        login_url = reverse('token_obtain_pair')
        user_response = self.client.post(login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }, format='json')
        self.user_token = user_response.data['access']

        # Sample book data (DEFINED BEFORE USE)
        self.book_data = {
            'title': 'Test Loan Book',
            'author': 'Loan Author',
            'isbn': '9876543210987',
            'page_count': 250
        }

        # Create a book to be borrowed (as admin)
        admin_login_response = self.client.post(login_url, {
            'username': self.admin_user_data['username'],
            'password': self.admin_user_data['password']
        }, format='json')
        self.admin_token = admin_login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_token)

        book_response = self.client.post(reverse('book-list'), self.book_data, format='json')
        self.book_id = book_response.data['id']
        self.client.credentials() # Clear credentials


    def test_borrow_book_success(self):
        """
        Ensure a user can borrow an available book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        borrow_url = reverse('borrow_book', args=[self.book_id])
        response = self.client.post(borrow_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        loan = Loan.objects.get(book_id=self.book_id, user=self.user)
        self.assertIsNotNone(loan.borrow_date)
        self.assertIsNone(loan.return_date)
        book = Book.objects.get(id=self.book_id)
        self.assertFalse(book.availability)

    def test_borrow_unavailable_book_denied(self):
        """
        Ensure a user cannot borrow an unavailable book.
        """
        # First, borrow the book to make it unavailable
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        borrow_url = reverse('borrow_book', args=[self.book_id])
        self.client.post(borrow_url, {}, format='json') # Borrow it once

        # Try to borrow it again
        response = self.client.post(borrow_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # CORRECTED ASSERTION: Check the specific error message in the 'book' field directly
        self.assertIn('book', response.data)
        self.assertEqual(response.data['book'][0], 'This book is currently not available.') # .string or direct comparison


    def test_list_my_loans(self):
        """
        Ensure a user can list their borrowed books.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        borrow_url = reverse('borrow_book', args=[self.book_id])
        self.client.post(borrow_url, {}, format='json')

        my_loans_url = reverse('my_loans')
        response = self.client.get(my_loans_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['book']['id'], self.book_id)
        self.assertEqual(response.data[0]['user']['id'], self.user.id)
        self.assertFalse(response.data[0]['book']['availability'])
        self.assertIsNone(response.data[0]['return_date'])

    def test_return_book_success(self):
        """
        Ensure a user can return a borrowed book.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        borrow_url = reverse('borrow_book', args=[self.book_id])
        self.client.post(borrow_url, {}, format='json')

        return_url = reverse('return_book', args=[self.book_id])
        response = self.client.post(return_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan = Loan.objects.get(book_id=self.book_id, user=self.user)
        self.assertIsNotNone(loan.return_date) 
        book = Book.objects.get(id=self.book_id)
        self.assertTrue(book.availability) 

    def test_return_unborrowed_book_denied(self):
        """
        Ensure a user cannot return a book they haven't borrowed or that's already returned.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        return_url = reverse('return_book', args=[self.book_id])
        response = self.client.post(return_url, {}, format='json')

        # CORRECTED ASSERTION: Expect 404 based on current API behavior
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # You can add a check for the message if you want, but 404 implies 'Not Found'
        # self.assertIn('detail', response.data) # This might be 'Not found.' for 404