import os
import sys  # ✅ MUST HAVE

# ✅ THIS IS THE CORRECT PATH — FROM YOUR SSH SCREEN!
sys.path.append("/home/ryacksonfungo/www/dream")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()