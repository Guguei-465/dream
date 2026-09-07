import os
import sys

sys.path.append("/home/ryackson/www/ryackson_dream")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace_backend.settings")

from django.core.asgi import get_asgi_application
application = get_asgi_application()