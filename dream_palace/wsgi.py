import os
import sys 
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace_backend.settings")

application = get_wsgi_application()