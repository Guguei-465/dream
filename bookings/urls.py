from django.urls import path
from . import views

urlpatterns = [
    path("bookings/create", views.create_booking, name="create_booking"),
    path("bookings/<int:booking_id>", views.booking_detail, name="booking_detail"),
    path("houses/<int:house_id>/booked_dates", views.booked_dates, name="booked_dates"),
]
