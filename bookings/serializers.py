from rest_framework import serializers
from .models import Booking


class BookingCreateSerializer(serializers.Serializer):
    house_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guest_name = serializers.CharField(max_length=200)
    guest_phone = serializers.CharField(max_length=20)
    guest_email = serializers.EmailField(required=False, allow_blank=True)


class BookingSerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(source="house.house_name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "house",
            "house_name",
            "guest_name",
            "guest_phone",
            "guest_email",
            "check_in",
            "check_out",
            "nights",
            "total_amount",
            "status",
            "expires_at",
            "created_at",
        ]
        read_only_fields = fields
