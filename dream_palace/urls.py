from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as serve_static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/bookings", include("accounts.urls")),
    path("api/media", include("listings.urls")),
    path("api/listings", include("bookings.urls")),
    path("api/payments", include("payments.urls")),
    path("api/messaging", include("messaging.urls")),
    path("api/accounts", include("accounts.urls")),
    path("api/payments", include("payments.urls")),
    path("api/messaging", include("messaging.urls")),
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
