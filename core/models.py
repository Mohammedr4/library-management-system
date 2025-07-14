# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Q 

class CustomUser(AbstractUser):
    # Add any extra fields specific to your library users here if needed.
    # For example:
    # phone_number = models.CharField(max_length=15, blank=True, null=True)
    # address = models.TextField(blank=True, null=True)

    # Just having pass is fine.
    # It still gives you the flexibility to add them later without major migrations.
    pass

    # You can also add custom managers or methods here if necessary later.
    # For now, `pass` is sufficient.

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, help_text="13-digit ISBN number")
    page_count = models.IntegerField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"

class Loan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True) 

    class Meta:
        # Ensures a user can't borrow the same book twice if they haven't returned it
        # This will be enforced at the database level.
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], condition=Q(return_date__isnull=True), name='unique_open_loan')
        ]

    def __str__(self):
        status = "Borrowed" if self.return_date is None else f"Returned on {self.return_date.strftime('%Y-%m-%d')}"
        return f"{self.user.username} borrowed '{self.book.title}' on {self.borrow_date.strftime('%Y-%m-%d')} ({status})"