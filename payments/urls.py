from django.urls import path
from . import views

urlpatterns = [
    path("mpesa_payment", views.mpesa_payment, name="mpesa_payment"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path("payments/<int:payment_id>", views.payment_status, name="payment_status"),
]
