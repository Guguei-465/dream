import os
import sys  # ✅ MUST HAVE — JUST LIKE LUMA!

# ✅ THIS LINE IS THE MAGIC — TELLS PYTHON WHERE YOUR FILES ARE
sys.path.append("/home/ryacksonfungo/dream_palace_backend")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()