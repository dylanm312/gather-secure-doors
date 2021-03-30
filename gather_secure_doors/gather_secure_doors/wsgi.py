"""
WSGI config for gather_secure_doors project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not path in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gather_secure_doors.settings')

application = get_wsgi_application()
