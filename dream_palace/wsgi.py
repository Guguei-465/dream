import os
import sys

# ✅ Path to where your project FOLDER lives (CONTAINS dream_palace/)
sys.path.append("/home/ryacksonfungo/www/dream")

# ✅ NAME OF THE FOLDER THAT HAS settings.py → dream_palace.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()