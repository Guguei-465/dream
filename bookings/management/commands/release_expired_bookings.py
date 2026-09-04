from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking


class Command(BaseCommand):
    help = "Releases pending_payment bookings whose hold has expired, freeing those dates back up."

    def handle(self, *args, **options):
        updated = Booking.objects.filter(
            status=Booking.PENDING_PAYMENT,
            expires_at__lt=timezone.now(),
        ).update(status=Booking.EXPIRED)

        self.stdout.write(self.style.SUCCESS(f"Released {updated} expired booking hold(s)."))
