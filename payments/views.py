from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from bookings.models import Booking
from bookings.services import confirm_booking, release_booking
from .models import Payment
from .daraja import stk_push, DarajaError


def _normalize_phone(raw: str) -> str:
    phone = (raw or "").strip().replace(" ", "")
    if phone.startswith("+254"):
        phone = phone[1:]
    elif phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("7") or phone.startswith("1"):
        phone = "254" + phone
    return phone


@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_payment(request):
    """
    Initiates an M-Pesa STK push.

    Two modes, matching how the frontend already calls this endpoint:

    1. Booking payment (houses): body includes `booking_id`. The amount is
       taken from the server-side Booking record -- NOT from whatever the
       client sends -- so a tampered request can't pay less than the real
       price or "confirm" a booking that has already expired.

    2. Simple payment (menu/products, no booking involved): body includes
       `product_name` and `amount`, same shape the existing Mpesa.jsx
       already sends.
    """
    phone = _normalize_phone(request.data.get("phone"))
    if not phone.startswith("254") or len(phone) != 12:
        return Response({"errorMessage": "Enter a valid Safaricom number, e.g. 0712345678."},
                         status=status.HTTP_400_BAD_REQUEST)

    booking_id = request.data.get("booking_id")
    booking = None

    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.status == Booking.CONFIRMED:
            return Response({"errorMessage": "This booking has already been paid for."},
                             status=status.HTTP_400_BAD_REQUEST)

        if booking.status != Booking.PENDING_PAYMENT or booking.expires_at < timezone.now():
            return Response(
                {"errorMessage": "This booking hold has expired. Please book again."},
                status=status.HTTP_409_CONFLICT,
            )

        amount = booking.total_amount
        account_reference = f"DreamPalace-{booking.house.house_name}"[:12]
        description = f"Booking of {booking.house.house_name} ({booking.check_in} to {booking.check_out})"

    else:
        product_name = request.data.get("product_name", "Order")
        try:
            amount = Decimal(str(request.data.get("amount")))
        except Exception:
            return Response({"errorMessage": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"errorMessage": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        account_reference = "DreamPalace"
        description = str(product_name)[:100]

    payment = Payment.objects.create(
        booking=booking,
        description=description,
        phone=phone,
        amount=amount,
        status=Payment.PENDING,
    )

    try:
        result = stk_push(
            phone=phone,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=description,
        )
    except DarajaError as exc:
        payment.status = Payment.FAILED
        payment.result_desc = str(exc)
        payment.save(update_fields=["status", "result_desc", "updated_at"])
        return Response({"errorMessage": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    payment.merchant_request_id = result.get("MerchantRequestID", "")
    payment.checkout_request_id = result.get("CheckoutRequestID", "")
    payment.save(update_fields=["merchant_request_id", "checkout_request_id", "updated_at"])

    # Shape matches what Mpesa.jsx already expects
    # (response.data.CustomerMessage / ResponseDescription).
    return Response(
        {
            **result,
            "payment_id": payment.id,
        }
    )


def _extract_metadata(items):
    values = {}
    for item in items or []:
        values[item.get("Name")] = item.get("Value")
    return values


@api_view(["POST"])
@permission_classes([AllowAny])
def mpesa_callback(request):
    """
    Safaricom POSTs the payment result here after the customer enters
    their M-Pesa PIN (or cancels / times out). This is the ONLY place a
    booking is ever confirmed -- the frontend can't fake a success.
    """
    body = request.data.get("Body", {}).get("stkCallback", {})
    checkout_request_id = body.get("CheckoutRequestID", "")
    result_code = body.get("ResultCode")
    result_desc = body.get("ResultDesc", "")

    try:
        payment = Payment.objects.get(checkout_request_id=checkout_request_id)
    except Payment.DoesNotExist:
        # Nothing we can match this to; acknowledge anyway so Safaricom
        # doesn't keep retrying.
        return Response({"ResultCode": 0, "ResultDesc": "Accepted"})

    if result_code == 0:
        metadata = _extract_metadata(body.get("CallbackMetadata", {}).get("Item", []))
        payment.status = Payment.SUCCESS
        payment.mpesa_receipt_number = str(metadata.get("MpesaReceiptNumber", ""))
        payment.result_desc = result_desc
        payment.save(update_fields=["status", "mpesa_receipt_number", "result_desc", "updated_at"])

        if payment.booking_id:
            confirm_booking(payment.booking_id)

    else:
        payment.status = Payment.FAILED
        payment.result_desc = result_desc
        payment.save(update_fields=["status", "result_desc", "updated_at"])

        if payment.booking_id:
            # Free the dates immediately instead of waiting for the hold to expire.
            release_booking(payment.booking_id, reason_status="cancelled")

    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


@api_view(["GET"])
@permission_classes([AllowAny])
def payment_status(request, payment_id):
    """Lets the frontend poll for whether the STK push was completed."""
    payment = get_object_or_404(Payment, id=payment_id)
    return Response(
        {
            "status": payment.status,
            "mpesa_receipt_number": payment.mpesa_receipt_number,
            "result_desc": payment.result_desc,
            "booking_status": payment.booking.status if payment.booking_id else None,
        }
    )
