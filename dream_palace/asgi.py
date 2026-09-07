import os
import sys
from django.core.asgi import get_asgi_application
sys.path.append("/home/ryacksonfungo/www/dream")  
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace_backend.settings")

application = get_asgi_application()



 