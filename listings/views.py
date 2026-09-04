from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import House, MenuItem, Product
from .serializers import (
    HouseSerializer,
    HouseWriteSerializer,
    MenuItemSerializer,
    MenuItemWriteSerializer,
    ProductSerializer,
    ProductWriteSerializer,
)


# ---------------------------------------------------------------- Houses --
@api_view(["GET"])
@permission_classes([AllowAny])
def get_houses(request):
    houses = House.objects.all().order_by("-created_at")
    return Response(HouseSerializer(houses, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_house(request):
    serializer = HouseWriteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    house = serializer.save()
    return Response({"success": "House added successfully!", "house": HouseSerializer(house).data})


@api_view(["DELETE"])
@permission_classes([AllowAny])
def delete_house(request, house_id):
    try:
        house = House.objects.get(id=house_id)
    except House.DoesNotExist:
        return Response({"message": "House not found."}, status=status.HTTP_404_NOT_FOUND)
    house.delete()
    return Response({"success": "House deleted successfully."})


# ------------------------------------------------------------------ Menu --
@api_view(["GET"])
@permission_classes([AllowAny])
def get_menu(request):
    items = MenuItem.objects.all().order_by("-created_at")
    return Response(MenuItemSerializer(items, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_menu(request):
    serializer = MenuItemWriteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"message": "Failed to add menu. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
    item = serializer.save()
    return Response({"message": "Menu added successfully!", "item": MenuItemSerializer(item).data})


# -------------------------------------------------------------- Products --
@api_view(["GET"])
@permission_classes([AllowAny])
def get_product_details(request):
    products = Product.objects.all().order_by("-created_at")
    return Response(ProductSerializer(products, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_product(request):
    serializer = ProductWriteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    product = serializer.save()
    return Response({"success": "Product added successfully!", "product": ProductSerializer(product).data})
