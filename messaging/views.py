from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from listings.models import House
from bookings.models import Booking
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationCreateSerializer, MessageSerializer
from .permissions import notify_new_message


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def conversations(request):
    if request.method == "GET":
        # Staff see every conversation (their inbox); guests see only their own.
        if request.user.is_staff:
            qs = Conversation.objects.all()
            status_filter = request.query_params.get("status")
            if status_filter:
                qs = qs.filter(status=status_filter)
        else:
            qs = Conversation.objects.filter(guest=request.user)

        serializer = ConversationSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    # POST -- start a new conversation with a first message.
    serializer = ConversationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    house = None
    if data.get("house_id"):
        house = get_object_or_404(House, id=data["house_id"])

    booking = None
    if data.get("booking_id"):
        booking = get_object_or_404(Booking, id=data["booking_id"])
        if not request.user.is_staff and booking.user_id != request.user.id:
            return Response({"message": "That booking doesn't belong to you."}, status=status.HTTP_403_FORBIDDEN)

    conversation = Conversation.objects.create(
        guest=request.user,
        house=house,
        booking=booking,
        subject=data.get("subject", ""),
    )
    message = Message.objects.create(conversation=conversation, sender=request.user, body=data["body"])
    notify_new_message(message)

    return Response(ConversationSerializer(conversation, context={"request": request}).data, status=status.HTTP_201_CREATED)


def _get_conversation_or_403(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if not request.user.is_staff and conversation.guest_id != request.user.id:
        return None
    return conversation


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    conversation = _get_conversation_or_403(request, conversation_id)
    if conversation is None:
        return Response({"message": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # Mark the other side's messages as read now that this user opened the thread.
        conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response(MessageSerializer(conversation.messages.all(), many=True).data)

    # POST -- reply.
    body = request.data.get("body", "").strip()
    if not body:
        return Response({"message": "Message body is required."}, status=status.HTTP_400_BAD_REQUEST)

    if conversation.status == Conversation.CLOSED:
        # A new guest message reopens a closed thread; a staff reply on a
        # closed thread is unusual but allowed (e.g. following up).
        conversation.status = Conversation.OPEN

    message = Message.objects.create(conversation=conversation, sender=request.user, body=body)
    conversation.save(update_fields=["status", "updated_at"])
    notify_new_message(message)

    return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def conversation_status(request, conversation_id):
    """Staff-only: mark a conversation resolved/closed, or reopen it."""
    if not request.user.is_staff:
        return Response({"message": "Staff only."}, status=status.HTTP_403_FORBIDDEN)

    conversation = get_object_or_404(Conversation, id=conversation_id)
    new_status = request.data.get("status")
    if new_status not in (Conversation.OPEN, Conversation.CLOSED):
        return Response({"message": "status must be 'open' or 'closed'."}, status=status.HTTP_400_BAD_REQUEST)

    conversation.status = new_status
    conversation.save(update_fields=["status", "updated_at"])
    return Response(ConversationSerializer(conversation, context={"request": request}).data)
