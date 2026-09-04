from rest_framework import serializers
from .models import House, MenuItem, Product


class HouseSerializer(serializers.ModelSerializer):
    # Frontend does `img_url + house.house_photo`, so we return just the
    # stored filename (not a full URL) to stay compatible.
    house_photo = serializers.SerializerMethodField()
    # The admin pages (ViewHouse.jsx) read `house.house_id` while the
    # public pages read `house.id` -- expose both so neither breaks.
    house_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = House
        fields = [
            "id",
            "house_id",
            "house_name",
            "house_description",
            "house_price",
            "house_location",
            "house_photo",
        ]

    def get_house_photo(self, obj):
        return obj.house_photo.name if obj.house_photo else ""


class HouseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = ["house_name", "house_description", "house_price", "house_location", "house_photo"]


class MenuItemSerializer(serializers.ModelSerializer):
    menu_photo = serializers.SerializerMethodField()

    class Meta:
        model = MenuItem
        fields = ["id", "menu_name", "menu_description", "menu_price", "menu_photo"]

    def get_menu_photo(self, obj):
        return obj.menu_photo.name if obj.menu_photo else ""


class MenuItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["menu_name", "menu_description", "menu_price", "menu_photo"]


class ProductSerializer(serializers.ModelSerializer):
    product_photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "product_name", "product_description", "product_cost", "product_photo"]

    def get_product_photo(self, obj):
        return obj.product_photo.name if obj.product_photo else ""


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_name", "product_description", "product_cost", "product_photo"]
