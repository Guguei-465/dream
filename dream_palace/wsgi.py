import os
import sys 
from django.core.wsgi import get_wsgi_application
sys.path.append("/home/ryacksonfungo/www/dream_palace_backend") 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace_backend.settings")

application = get_wsgi_application()