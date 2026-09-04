from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as serve_static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("listings.urls")),
    path("api/", include("bookings.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("messaging.urls")),
]

# Serve uploaded house/menu/product photos at /static/images/<filename>
# so the existing frontend (img_url = ".../static/images/") needs no changes.
# In production, put nginx/whitenoise in front of this instead of Django.
urlpatterns += [
    path(
        "static/images/<path:path>",
        serve_static,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
