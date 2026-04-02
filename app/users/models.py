from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from app.users.managers import UserManager
from app.commone.models import Base
from django.utils import timezone

class User(AbstractBaseUser,Base):

    OWNERSYSTEME = "supervisor"
    ADMIN = "admin"
    OWNERMICROTIK = "ownermicrotik"

    users_choices = (
        (ADMIN, "admin",),
        (OWNERMICROTIK, "owner microtik",),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True,null=False)
    phone_number = models.CharField(max_length=10)
    address = models.CharField(max_length=50,null=True)
    username = None
    user_type = models.CharField(max_length=20, default=OWNERMICROTIK, choices=users_choices)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

