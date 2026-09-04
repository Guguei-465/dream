from django.db import models


class House(models.Model):
    house_name = models.CharField(max_length=200)
    house_description = models.TextField(blank=True)
    house_price = models.DecimalField(max_digits=12, decimal_places=2)
    house_location = models.CharField(max_length=200, blank=True)
    house_photo = models.ImageField(upload_to="")  # stored directly under MEDIA_ROOT
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.house_name


class MenuItem(models.Model):
    menu_name = models.CharField(max_length=200)
    menu_description = models.TextField(blank=True)
    menu_price = models.DecimalField(max_digits=10, decimal_places=2)
    menu_photo = models.ImageField(upload_to="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.menu_name


class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(blank=True)
    product_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_photo = models.ImageField(upload_to="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name
