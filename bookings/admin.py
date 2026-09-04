from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "house", "guest_name", "guest_phone", "check_in", "check_out", "status", "total_amount", "expires_at"]
    list_filter = ["status", "house"]
    search_fields = ["guest_name", "guest_phone", "guest_email"]
