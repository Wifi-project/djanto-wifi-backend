from django.db import models
from app.commone.models import Base
from app.gdms.models import Network
from app.transactions.models import Transaction

class Status(models.TextChoices):
    DISABLE = "disable", "Desactiver"
    ACTIVE = "active", "Activer le compte"


class Client(Base):
    SYSTEME = "systeme"
    OWNER = "owner"

    generate_choice = (
        (SYSTEME,"generer par le systeme",),
        (OWNER, "generer par le owner",),
    )

    phone_number = models.CharField(max_length=10, null=True,blank=True)
    code_username = models.CharField(max_length=50, null=False,blank=False)
    code_password = models.CharField(max_length=50, null=False,blank=False)
    limit_uptime = models.CharField(max_length=50)
    profil_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    network = models.ForeignKey(
        Network, 
        on_delete=models.CASCADE, 
        related_name='clients', 
        related_query_name='clients'
        )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE, 
        related_name="client_transactions",
        null=True
        )
    shared_users = models.IntegerField(default=1)
    generate = models.CharField(max_length=20, choices=generate_choice, default=SYSTEME)

    def __str__(self):
        return self.code_username


class GroupClient(Base):
    name = models.CharField(max_length=250)
    clients = models.ManyToManyField(Client, related_name='group_client')
    number_voucher = models.IntegerField(default=0)
    network = models.ForeignKey(
        Network, 
        on_delete=models.CASCADE, 
        related_name='groups_vouchers', 
        )


