from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404

from listings.models import House
from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer
from .services import create_booking_hold, BookingUnavailable, _release_expired_holds


@api_view(["POST"])
@permission_classes([AllowAny])
def create_booking(request):
    """
    Creates a pending_payment hold for a house between check_in/check_out.
    Fails with 409 if the dates overlap an existing active booking.
    Frontend should call this BEFORE sending the guest to /api/mpesa_payment.
    """
    serializer = BookingCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    house = get_object_or_404(House, id=data["house_id"])

    try:
        booking = create_booking_hold(
            house_id=house.id,
            check_in=data["check_in"],
            check_out=data["check_out"],
            guest_name=data["guest_name"],
            guest_phone=data["guest_phone"],
            guest_email=data.get("guest_email", ""),
            user=request.user if request.user.is_authenticated else None,
            hold_minutes=settings.BOOKING_HOLD_MINUTES,
        )
    except BookingUnavailable as exc:
        return Response({"success": False, "message": str(exc.detail[0]) if hasattr(exc, "detail") else str(exc)},
                         status=status.HTTP_409_CONFLICT)

    return Response({"success": True, "booking": BookingSerializer(booking).data})


@api_view(["GET"])
@permission_classes([AllowAny])
def booked_dates(request, house_id):
    """
    Returns the date ranges that are already taken for this house, so the
    frontend can grey them out on a date picker instead of letting a guest
    pick a doomed date and find out only after submitting.
    """
    house = get_object_or_404(House, id=house_id)
    _release_expired_holds(house)

    ranges = Booking.objects.filter(
        house=house, status__in=Booking.ACTIVE_STATUSES
    ).values("check_in", "check_out", "status")

    return Response(list(ranges))


@api_view(["GET"])
@permission_classes([AllowAny])
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return Response(BookingSerializer(booking).data)
