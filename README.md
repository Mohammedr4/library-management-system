# Library Management System API

A robust RESTful API for managing books, users, and loans within a library system. Built with Django and Django REST Framework, featuring authentication, permissions, filtering, searching, ordering, and interactive API documentation.

## Features

* **User Management:**
    * User registration (`/api/users/register/`)
    * User authentication (JWT Tokens) (`/api/token/`, `/api/token/refresh/`)
    * Password change (`/api/users/<id>/change-password/`)
    * Admin access to manage all users.
* **Book Management:**
    * CRUD operations for books.
    * Publicly viewable book listings.
    * Admin-only access for creating, updating, and deleting books.
    * Filtering by author, genre, published date, and available copies.
    * Searching by title, author, ISBN, and genre.
    * Ordering by various fields.
* **Loan Management:**
    * CRUD operations for loans.
    * Users can view and manage their own loans.
    * Admins can view and manage all loans.
    * Filtering by user, book, loan date, and return date.
    * Searching by user email, book title, and author.
    * Ordering by loan date and return date.
* **API Documentation:** Interactive Swagger UI and Redoc documentation.

## Technologies Used

* Python 3.x
* Django
* Django REST Framework
* Django REST Framework Simple JWT (for token authentication)
* drf-yasg (for Swagger/OpenAPI documentation)
* django-filter (for advanced filtering)
* WhiteNoise (for serving static files in production)
* PostgreSQL (recommended for production via Railway)

## Setup Instructions (Local Development)

Follow these steps to get a development copy of the project running on your local machine.

### Prerequisites

* Python 3.9+
* pip (Python package installer)

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/library_management_system.git](https://github.com/your-username/library_management_system.git)
cd library_management_system