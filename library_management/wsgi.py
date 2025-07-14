# library_management/wsgi.py (TEMPORARY FOR DEBUGGING)

import os
from django.http import HttpResponse

# This is a dummy application callable.
# It will try to return a simple HTTP response directly, bypassing most of Django.
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b"It works! WSGI is active."]

# You would typically have:
# from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
# application = get_wsgi_application()