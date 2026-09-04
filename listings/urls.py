from django.urls import path
from . import views

urlpatterns = [
    path("get_houses", views.get_houses, name="get_houses"),
    path("get_house", views.get_houses, name="get_house"),  # alias used by admin ViewHouse.jsx
    path("add_house", views.add_house, name="add_house"),
    path("delete_house/<int:house_id>", views.delete_house, name="delete_house"),

    path("get_menu", views.get_menu, name="get_menu"),
    path("add_menu", views.add_menu, name="add_menu"),

    path("get_product_details", views.get_product_details, name="get_product_details"),
    path("add_product", views.add_product, name="add_product"),
]
