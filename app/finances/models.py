from django.db import models
from app.commone.models import Base
from app.microtiks.models import Microtik
from app.users.models import User
import secrets
from datetime import datetime

class GainSysteme(Base):
    microtik = models.ForeignKey(Microtik, related_name="gain_microtik", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Status(models.TextChoices):
    PENDING = "pending", "en attente"
    FAILLED = "failled", "echouer"
    SUCCESS = "success", "success"
    CANCELLED = "cancelled", "annuler"
    IN_CHECKING = "en cours de verification"


def slug_genenration():
    now = datetime.now()
    date_string = now.strftime("%d-%m-%y")
    slug = secrets.token_hex(4).upper()

    return f"R-{date_string}-{slug}"

class Windraw(Base):
    reference = models.CharField(max_length=50,null=False, editable=False, unique=True, default=slug_genenration)
    microtik = models.ForeignKey(Microtik, related_name="windraw_microtik", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=10)
    user = models.ForeignKey(User, related_name="user_windraw", on_delete=models.PROTECT)
    status = models.CharField(max_length=20,default=Status.PENDING)

    def __str__(self):
        return self.reference