"""
Minimal client for Safaricom's Daraja API (M-Pesa STK Push / Lipa na
M-Pesa Online).

Setup:
1. Create an app at https://developer.safaricom.co.ke/ to get a
   Consumer Key + Consumer Secret (sandbox first, then apply for
   production go-live for a real Paybill/Till).
2. Set these environment variables (see .env.example):
     MPESA_ENV=sandbox|production
     MPESA_CONSUMER_KEY=...
     MPESA_CONSUMER_SECRET=...
     MPESA_SHORTCODE=...          (sandbox default: 174379)
     MPESA_PASSKEY=...            (sandbox passkey is published in the docs)
     MPESA_CALLBACK_URL=https://your-public-domain/api/mpesa/callback/
     (Safaricom must be able to reach this URL over the public internet --
     it will not work with localhost. Use ngrok or your alwaysdata domain.)
"""

import base64
import datetime
import requests
from django.conf import settings

SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE = "https://api.safaricom.co.ke"


class DarajaError(Exception):
    pass


def _base_url():
    return PRODUCTION_BASE if settings.MPESA_ENV == "production" else SANDBOX_BASE


def get_access_token() -> str:
    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    resp = requests.get(
        url,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=15,
    )
    if resp.status_code != 200:
        raise DarajaError(f"Failed to get access token: {resp.status_code} {resp.text}")
    return resp.json()["access_token"]


def _password_and_timestamp():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(*, phone: str, amount, account_reference: str, transaction_desc: str) -> dict:
    """
    Initiates an STK push (a payment prompt on the customer's phone).
    `phone` must be in 2547XXXXXXXX format. Returns Safaricom's response,
    which includes CheckoutRequestID -- store that so the callback can be
    matched back to this payment.
    """
    access_token = get_access_token()
    password, timestamp = _password_and_timestamp()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(round(float(amount))),  # Daraja wants a whole-number amount
        "PartyA": phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference[:12],  # Daraja truncates around here anyway
        "TransactionDesc": transaction_desc[:100],
    }

    resp = requests.post(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )

    data = resp.json()
    if resp.status_code != 200 or data.get("ResponseCode") not in ("0", 0):
        raise DarajaError(data.get("errorMessage") or data.get("ResponseDescription") or "STK push failed")

    return data
