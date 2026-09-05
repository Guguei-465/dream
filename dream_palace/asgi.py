"""
ASGI config for Dream Palace project.
"""
import os
import sys  # ✅ Added
from django.core.asgi import get_asgi_application

# ✅ ADD YOUR PROJECT PATH — THIS IS THE MAGIC LINE!
sys.path.append("/home/ryacksonfungo/dream_palace_backend")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dream_palace.settings")
application = get_asgi_application()