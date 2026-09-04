from django.conf import settings
from django.db import models

from listings.models import House
from bookings.models import Booking


class Conversation(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    STATUS_CHOICES = [(OPEN, "Open"), (CLOSED, "Closed")]

    # The guest who started the conversation. Admin/staff can see every
    # conversation; a guest can only see their own.
    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations"
    )

    # Optional context -- what is this conversation about? Both are
    # optional so a guest can also send a general enquiry.
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations")
    booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations"
    )

    subject = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation #{self.id} with {self.guest}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField()

    # Whether the *other* side of the conversation has read this message
    # yet (if sender is the guest, this means "an admin has read it";
    # if sender is staff, this means "the guest has read it").
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message #{self.id} in conversation #{self.conversation_id}"
