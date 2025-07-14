# Library Management System API

This project implements a RESTful API for a simple library management system using Django and Django REST Framework.

## Features

* **User Management:**
    * User registration and login (JWT authenticated).
    * Extended Django User model.
* **Book Management:**
    * Browse/search books (anonymous and registered users).
    * Add/remove books (administrators only).
* **Loan Management:**
    * Borrow books (registered users).
    * Return books (registered users).
    * View personal loan history.
* **Authentication:** JWT (JSON Web Token) based authentication.
* **Admin Panel:** Simple Django Admin interface for managing users, books, and loans.
* **Automated Testing:** Comprehensive unit and integration tests for core functionalities.
* **API Documentation:** Interactive API documentation using Swagger UI and Redoc.

## Technologies Used

* **Backend:** Python 3.x, Django 5.x, Django REST Framework
* **Authentication:** `djangorestframework-simplejwt`
* **Database:** SQLite (development), PostgreSQL (production)
* **API Documentation:** `drf-yasg` (Swagger/Redoc)
* **Deployment Tools:** Gunicorn, Whitenoise, dj-database-url (for Heroku/Docker)
* **Containerization:** Docker
* **Version Control:** Git

## Setup and Local Development

Follow these steps to get the project up and running on your local machine.

### Prerequisites

* Python 3.9+
* `pip` (Python package installer)
* Git
* (Optional but Recommended) Postman or Insomnia for API testing

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPO_URL_HERE>
cd library_management