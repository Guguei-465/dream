from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "phone", "amount", "status", "mpesa_receipt_number", "booking", "created_at"]
    list_filter = ["status"]
    search_fields = ["phone", "mpesa_receipt_number", "checkout_request_id"]
