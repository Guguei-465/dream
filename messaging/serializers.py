from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)
    is_from_admin = serializers.BooleanField(source="sender.is_staff", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "sender_name", "is_from_admin", "body", "is_read", "created_at"]
        read_only_fields = ["id", "sender", "sender_name", "is_from_admin", "is_read", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source="guest.username", read_only=True)
    house_name = serializers.CharField(source="house.house_name", read_only=True, default=None)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id", "guest", "guest_name", "house", "house_name", "booking",
            "subject", "status", "created_at", "updated_at",
            "last_message", "unread_count",
        ]
        read_only_fields = ["id", "guest", "guest_name", "house_name", "created_at", "updated_at"]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        return {"body": msg.body, "sender_name": msg.sender.username, "created_at": msg.created_at}

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0
        # Unread messages are ones NOT sent by the person asking, and not yet read.
        return obj.messages.exclude(sender=request.user).filter(is_read=False).count()


class ConversationCreateSerializer(serializers.Serializer):
    house_id = serializers.IntegerField(required=False, allow_null=True)
    booking_id = serializers.IntegerField(required=False, allow_null=True)
    subject = serializers.CharField(max_length=200, required=False, allow_blank=True)
    body = serializers.CharField()
