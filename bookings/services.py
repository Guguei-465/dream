"""
This module is where double-booking is actually prevented.

The core idea:
1. Lock the House row (SELECT ... FOR UPDATE) for the duration of the
   transaction. Any other request trying to book the *same* house has to
   wait for this transaction to finish before it can even check
   availability. This turns "check then insert" into an atomic operation
   instead of two separate steps that can race each other.
2. Auto-expire any stale pending_payment holds for this house before
   checking availability, so an abandoned checkout doesn't block real
   guests forever.
3. Check for any CONFIRMED or still-live PENDING_PAYMENT booking whose
   date range overlaps the requested range. If one exists, reject.
4. Only if no overlap exists, create the new booking inside the same
   transaction/lock.

On Postgres or MySQL (InnoDB) this gives a real guarantee under
concurrent requests. On SQLite (fine for local dev) writes are already
serialized by the database file lock, so the same logic still holds,
just without genuine row-level locking.
"""

from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from listings.models import House
from .models import Booking


class BookingUnavailable(ValidationError):
    pass


def _release_expired_holds(house: House):
    """Flip stale pending_payment bookings for this house to 'expired'."""
    Booking.objects.filter(
        house=house,
        status=Booking.PENDING_PAYMENT,
        expires_at__lt=timezone.now(),
    ).update(status=Booking.EXPIRED)


def _has_overlap(house: House, check_in, check_out, exclude_booking_id=None) -> bool:
    qs = Booking.objects.filter(
        house=house,
        status__in=Booking.ACTIVE_STATUSES,
        check_in__lt=check_out,
        check_out__gt=check_in,
    )
    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)
    return qs.exists()


@transaction.atomic
def create_booking_hold(*, house_id, check_in, check_out, guest_name, guest_phone, guest_email="", user=None,
                         hold_minutes=15) -> Booking:
    """
    Create a pending_payment booking, or raise BookingUnavailable if the
    dates are already taken. Safe to call concurrently for the same house.
    """
    if check_out <= check_in:
        raise ValidationError("Check-out date must be after check-in date.")

    if check_in < timezone.now().date():
        raise ValidationError("Check-in date can't be in the past.")

    # select_for_update() on the House row is the mutex: only one request
    # per house can be inside this block at a time.
    house = House.objects.select_for_update().get(id=house_id)

    _release_expired_holds(house)

    if _has_overlap(house, check_in, check_out):
        raise BookingUnavailable(
            "This house is already booked for one or more of the selected dates. "
            "Please choose different dates."
        )

    nights = (check_out - check_in).days
    total_amount = (Decimal(house.house_price) * nights).quantize(Decimal("0.01"))

    booking = Booking.objects.create(
        house=house,
        user=user,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guest_email=guest_email,
        check_in=check_in,
        check_out=check_out,
        nights=nights,
        total_amount=total_amount,
        status=Booking.PENDING_PAYMENT,
        expires_at=timezone.now() + timedelta(minutes=hold_minutes),
    )
    return booking


@transaction.atomic
def confirm_booking(booking_id):
    booking = Booking.objects.select_for_update().get(id=booking_id)
    if booking.status != Booking.CONFIRMED:
        booking.status = Booking.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
    return booking


@transaction.atomic
def release_booking(booking_id, reason_status=Booking.CANCELLED):
    booking = Booking.objects.select_for_update().get(id=booking_id)
    if booking.status == Booking.PENDING_PAYMENT:
        booking.status = reason_status
        booking.save(update_fields=["status", "updated_at"])
    return booking
