from django.db import models
from bookings.models import Booking


class Payment(models.Model):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCESS, "Success"),
        (FAILED, "Failed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")

    # What was being paid for, in plain text -- used for non-booking
    # payments too (e.g. a menu order), where there's no Booking row.
    description = models.CharField(max_length=255, blank=True)

    phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    result_desc = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.phone} - {self.amount} ({self.status})"
