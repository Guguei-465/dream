from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extends Django's built-in user with a phone number, since the
    frontend's signup form collects one and Mpesa needs it later.
    Email is required and used to sign in (frontend sends email+password).
    """
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username
