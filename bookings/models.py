from django.db import models
from django.utils import timezone
from django.conf import settings

from listings.models import House


class Booking(models.Model):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    STATUS_CHOICES = [
        (PENDING_PAYMENT, "Pending payment"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
        (EXPIRED, "Expired (hold timed out)"),
    ]

    # Bookings that still block the calendar for other guests.
    ACTIVE_STATUSES = (PENDING_PAYMENT, CONFIRMED)

    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )

    guest_name = models.CharField(max_length=200)
    guest_phone = models.CharField(max_length=20)
    guest_email = models.EmailField(blank=True)

    check_in = models.DateField()
    check_out = models.DateField()

    nights = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING_PAYMENT)

    # A pending_payment hold that isn't paid for by this time is released
    # automatically (see bookings/services.py + the release_expired_bookings
    # management command).
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(check_out__gt=models.F("check_in")), name="check_out_after_check_in"),
        ]
        indexes = [
            models.Index(fields=["house", "status", "check_in", "check_out"]),
        ]

    def __str__(self):
        return f"{self.house.house_name}: {self.check_in} -> {self.check_out} ({self.status})"

    def is_active_hold(self):
        return self.status in self.ACTIVE_STATUSES and (
            self.status == self.CONFIRMED or self.expires_at > timezone.now()
        )
