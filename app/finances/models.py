from django.db import models
from app.commone.models import Base
from app.microtiks.models import Microtik
from app.users.models import User

class GainSysteme(Base):
    microtik = models.ForeignKey(Microtik, related_name="gain_microtik", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)


class Status(models.TextChoices):
    PENDING = "pending", "en attente"
    FAILLED = "failled", "echouer"
    SUCCESS = "success", "success"
    CANCELLED = "cancelled", "annuler"


class Windraw(Base):
    microtik = models.ForeignKey(Microtik, related_name="windraw_microtik", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=10)
    user = models.ForeignKey(User, related_name="user_windraw", on_delete=models.PROTECT)
    status = models.CharField(max_length=20,default=Status.PENDING)