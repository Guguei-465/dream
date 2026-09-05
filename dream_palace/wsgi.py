"""
WSGI config for Dream Palace project.
"""
import os
import sys  # ✅ Added

# ✅ ADD YOUR PROJECT PATH — SAME AS ABOVE!
sys.path.append("/home/ryacksonfungo/dream_palace_backend")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()