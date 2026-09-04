from django.conf import settings
from django.core.mail import send_mail

from rest_framework.permissions import BasePermission


class IsConversationParticipant(BasePermission):
    """Only the guest who owns the conversation, or any staff user, may access it."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.guest_id == request.user.id


def notify_new_message(message):
    """
    Sends a simple notification email. Uses the console email backend by
    default (prints to the server log) -- swap EMAIL_BACKEND in settings
    for real SMTP when you're ready to actually deliver these.
    """
    conversation = message.conversation

    if message.sender.is_staff:
        # Admin replied -- notify the guest.
        recipient = conversation.guest.email
        subject = f"Dream Palace: reply to your message"
    else:
        # Guest sent a message -- notify the admin/owner.
        recipient = settings.ADMIN_NOTIFY_EMAIL
        subject = f"Dream Palace: new message from {message.sender.username}"

    if not recipient:
        return

    try:
        send_mail(
            subject=subject,
            message=message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        # Never let a notification failure break the API response.
        pass
