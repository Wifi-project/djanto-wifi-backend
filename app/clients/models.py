from django.db import models
from app.commone.models import Base
from app.microtiks.models import Microtik,Profil


class Status(models.TextChoices):
    DISABLE = "disable", "Desactiver"
    ACTIVE = "active", "Activer le compte"


class Client(Base):
    phone_number = models.CharField(max_length=10, null=True,blank=True)
    code_username = models.CharField(max_length=50, null=False,blank=False)
    code_password = models.CharField(max_length=50, null=False,blank=False)
    microtik = models.ForeignKey(Microtik, on_delete=models.CASCADE, related_name='clients', related_query_name='clients')
    limit_uptime = models.CharField(max_length=50)
    profil_name = models.CharField(max_length=50)
    status = models.BooleanField(default=Status.ACTIVE, choices=Status)

    def __str__(self):
        return self.phone_number
    

class InfoDeposit(Base):
    PENDING = 'pending'
    FAILED = 'failed'
    SUCCESS = 'success'

    phone_number = models.CharField(max_length=10, null=False,blank=False)
    number_receve_code = models.CharField(max_length=10, null=False,blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    status = models.CharField(default=PENDING, max_length=15)
    profil_name = models.CharField(max_length=50)
    limit_uptime = models.CharField(max_length=50)
    microtik = models.ForeignKey(
        Microtik, on_delete=models.CASCADE, 
        related_name='info_deposit', 
        related_query_name='info_deposit'
        )
    eventId = models.CharField(max_length=250)
    paymentMethod = models.CharField(max_length=20)

    def __str__(self):
        return self.phone_number
