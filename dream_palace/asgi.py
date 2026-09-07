import os
import sys
sys.path.append("/home/ryacksonfungo/www/dream")  # ✅ SAME PATH!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")
from django.core.asgi import get_asgi_application
application = get_asgi_application()