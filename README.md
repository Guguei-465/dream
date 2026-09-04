# Dream Palace — Django backend

A Django + Django REST Framework backend for the Dream Palace React app,
replacing the previous Flask backend. Endpoints are named to match what
the existing frontend already calls, so you should need **zero or
minimal** frontend changes for houses/menu/products/signup/signin.

Two things beyond a plain CRUD backend, because they were the whole point:

## 1. No double booking

`bookings/services.py` → `create_booking_hold()` is where this happens:

1. It locks the `House` row (`SELECT ... FOR UPDATE`) inside a DB
   transaction. Any other request trying to book the *same* house has to
   wait until this transaction finishes — so "check availability" and
   "create the booking" become one atomic step instead of two separate
   steps that can race each other.
2. It auto-expires stale `pending_payment` holds for that house first
   (see below), so an abandoned checkout doesn't block real guests.
3. It checks whether any `confirmed` or still-live `pending_payment`
   booking overlaps the requested date range. If so, it's rejected with
   a 409 — the frontend should show "these dates are already booked."
4. Only if nothing overlaps does it insert the new booking.

A booking starts as `pending_payment` with a 15-minute hold
(`BOOKING_HOLD_MINUTES`), and only becomes `confirmed` when Safaricom's
payment callback confirms money actually moved (see below). If payment
fails or the hold times out, the dates are released automatically.

Run `python manage.py release_expired_bookings` on a cron job (every
few minutes) to sweep up abandoned holds proactively — it's also
self-cleaning on every new booking attempt for that house.

**Flow the frontend should follow for a house booking:**
```
POST /api/bookings/create   { house_id, check_in, check_out, guest_name, guest_phone }
  -> { success: true, booking: { id, total_amount, expires_at, ... } }
     (or 409 if the dates are taken)

POST /api/mpesa_payment     { booking_id, phone }
  -> triggers the STK push; booking is confirmed only after Safaricom's
     callback hits /api/mpesa/callback/
```

This is a small change from the current React code, which sends the
house straight to `/Mpesa` without asking for dates. `Houses.jsx` needs
a date picker before "Book Now", and `Mpesa.jsx` needs to call
`/api/bookings/create` first and pass the returned `booking_id` instead
of raw `amount`/`product_name` when booking a house. Happy to write
that frontend patch too if you want it — just ask.

## 2. Real Safaricom Daraja integration

`payments/daraja.py` implements STK Push against Safaricom's Daraja API
(sandbox or production). Unlike the previous flow, **the amount is never
trusted from the client** — for house bookings it's pulled straight from
the `Booking.total_amount` your server already computed. A booking is
only marked `confirmed` inside `mpesa_callback()`, i.e. only once
Safaricom itself confirms the payment succeeded. Nothing on the frontend
can fake that.

Setup:
1. Register at https://developer.safaricom.co.ke/ and create an app to
   get a sandbox Consumer Key + Secret immediately (production requires
   Safaricom go-live approval + a real Paybill/Till number).
2. Copy `.env.example` to `.env` and fill in `MPESA_*` values.
3. `MPESA_CALLBACK_URL` **must** be a public HTTPS URL Safaricom can
   reach — localhost won't work. Use `ngrok http 8000` while developing,
   or your alwaysdata domain once deployed.

## 3. Contact / messaging (guest ↔ admin)

Deliberately **not** a real-time websocket chat — see reasoning below.
It's a simple threaded-message system (`messaging` app):

- `Conversation` — a thread between one guest and the admin/owner,
  optionally tied to a `House` (a pre-booking question) or a `Booking`
  (e.g. "I'll check in around 6pm tomorrow").
- `Message` — belongs to a conversation, tracks `is_read`.
- Requires login (`IsAuthenticated`) — prevents anonymous spam and ties
  every message to a real account, which you already have via signup/signin.
- Any user with `is_staff=True` (set in Django admin) can see and reply
  to *every* conversation — that's your admin/owner inbox. A guest can
  only see their own.
- New messages trigger an email notification (console backend by
  default — swap in real SMTP via the `EMAIL_*` env vars when ready).
  Guest messages notify `ADMIN_NOTIFY_EMAIL`; admin replies notify the
  guest's account email.

**Why not real-time websockets:** this is occasional, asynchronous
messaging (a guest saying they'll arrive tomorrow, an owner replying
later) — not a dense back-and-forth chat. A polling REST thread gets
you 95% of the value with none of the extra infrastructure (Channels +
Redis, persistent connections, scaling concerns). If usage later shows
people genuinely chatting live, this can be upgraded to Django Channels
without changing the data model — `Conversation`/`Message` stay the same,
only the transport changes.

Note: the frontend must send `Authorization: Token <token>` (the token
`/api/signin` already returns) on these requests — the current React
code stores the user object in localStorage but not the token, so that
needs to be added when the messaging UI is built.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

python manage.py runserver
```

The API is now at `http://localhost:8000/api/...` and the Django admin
at `http://localhost:8000/admin/`.

## Endpoints

| Method | Path                              | Notes |
|--------|------------------------------------|-------|
| GET    | /api/get_houses                    | list houses |
| GET    | /api/get_house                     | alias, used by admin ViewHouse.jsx |
| POST   | /api/add_house                     | multipart: house_name, house_description, house_price, house_location, house_photo |
| DELETE | /api/delete_house/\<id\>           | |
| GET    | /api/get_menu                      | |
| POST   | /api/add_menu                      | multipart: menu_name, menu_description, menu_price, menu_photo |
| GET    | /api/get_product_details           | |
| POST   | /api/add_product                   | multipart: product_name, product_description, product_photo |
| POST   | /api/signup                        | multipart: username, email, phone, password |
| POST   | /api/signin                        | email, password → { user, token } |
| POST   | /api/bookings/create                | house_id, check_in, check_out, guest_name, guest_phone → creates a hold, 409 if dates taken |
| GET    | /api/houses/\<id\>/booked_dates     | date ranges already taken, for a calendar UI |
| GET    | /api/bookings/\<id\>                | |
| POST   | /api/mpesa_payment                  | { booking_id, phone } for a house, or { phone, amount, product_name } for menu/products |
| POST   | /api/mpesa/callback/                | Safaricom calls this — not for the frontend |
| GET    | /api/payments/\<id\>                | poll payment/booking status after STK push |
| GET/POST | /api/messages/conversations       | GET: mine (or all, if staff, `?status=open`). POST: `{ house_id?, booking_id?, subject?, body }` starts a thread |
| GET/POST | /api/messages/conversations/\<id\>/messages | GET marks the other side's messages read. POST `{ body }` replies |
| PATCH  | /api/messages/conversations/\<id\>/status | staff-only: `{ status: "open" \| "closed" }` |

Uploaded photos are served at `/static/images/<filename>` to match the
frontend's existing `img_url` pattern — no change needed there. In
production, put nginx or WhiteNoise in front instead of Django serving
files directly.

## Notes / things to decide before going to production

- Switch `DB_ENGINE` to MySQL/Postgres (alwaysdata offers both) — SQLite
  is fine for development but doesn't give real row-level locking.
- Set `DJANGO_DEBUG=False` and a real `DJANGO_SECRET_KEY` in production.
- Lock down `add_house` / `add_menu` / `add_product` / `delete_house`
  behind authentication (currently open like the old Flask routes were)
  — recommend requiring a staff/admin token via DRF permissions once
  you're ready.
#   d r e a m  
 