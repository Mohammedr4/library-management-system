# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2 (if using PostgreSQL)
# This includes build-essential and libpq-dev which are necessary for psycopg2-binary to compile correctly
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Collect static files (important for Django admin CSS/JS)
RUN python manage.py collectstatic --noinput

# Expose the port your Django app will run on
EXPOSE 8000

# Define the command to run your Django application using Gunicorn
# Replace 'library_management.wsgi' with your actual project's WSGI file path
CMD ["gunicorn", "library_management.wsgi:application", "--bind", "0.0.0.0:8000"]