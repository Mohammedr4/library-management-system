# core/admin.py
from django.contrib import admin
from .models import CustomUser, Book, Loan

admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(Loan)