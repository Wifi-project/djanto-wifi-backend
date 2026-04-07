from django.db import models
from app.commone.models import Base
from app.users.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class Status(models.TextChoices):
    DISABLE = "disable", "desactiver"
    ACTIVE = "active", "activer et fonctionne"



class SubscriptionCategorie(Base):
    POURCENTAGE = "pourcentage"
    MENSUAL = "mensual"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"

    choice = (
        (POURCENTAGE, "pourcentage",),
        (MENSUAL, "Mensuel",),
        (TRIMESTRIEL, "Trimestiel",),
        (ANNUEL,"Annul",),
    )

    name = models.CharField(max_length=50, default=POURCENTAGE)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Subscription(Base):
    type = models.ForeignKey(
        SubscriptionCategorie,
        on_delete=models.PROTECT
    )
    expire_at = models.DateField(null=True, blank=True)

    def save(self,*args, **kwargs):
        if self.type == SubscriptionCategorie.MENSUAL:
            self.expire_at = timezone.now() + timedelta(days=30)
        elif self.type == SubscriptionCategorie.TRIMESTRIEL:
            self.expire_at = timezone.now() + timedelta(days=90)
        elif self.type == SubscriptionCategorie.ANNUEL:
            self.expire_at = timezone.now() + timedelta(days=360)
        else:
            self.expire_at = None

        return super().save(*args,**kwargs)
    
    def is_active(self):
        if self.type == SubscriptionCategorie.POURCENTAGE:
            return True
        return self.expire_at > timezone.now()



class Microtik(Base):
    VPN = "vpn",
    FREEMIUM = "freemium", 

    FacturationType = (
        (VPN, "abonement vpn",),
        (FREEMIUM, "pas d'abonement type juste pourcentage.",),
    )

    name = models.CharField(max_length=50, null=False)
    description = models.TextField()
    ip = models.CharField(max_length=50, null=False)
    username = models.CharField(max_length=50, null=False)
    password = models.CharField(max_length=50, null=False)
    owner = models.ForeignKey(User,on_delete=models.CASCADE, related_name="microtiks")
    sold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    users = models.BigIntegerField(default=0)
    status = models.CharField(max_length=50, default=Status.ACTIVE)
    admin_blocked = models.CharField(max_length=50, default=Status.ACTIVE)
    # pourcentage = models.FloatField(default=15)
    # facturation_type = models.CharField(max_length=50,choices=FacturationType ,default=FREEMIUM)
    # suscription = models.ForeignKey(
    #     Subscription, 
    #     on_delete=models.PROTECT, 
    #     related_name="suscriptions"
    #     )


    @property
    def get_amount_available_windrawal(self):
        pass
    #     pourcentage = self.pourcentage
    #     return Decimal(self.sold * (pourcentage/100) )


    def __str__(self):
        return self.name



class MikroTikRateLimit(models.TextChoices):
    # Format MikroTik : "Upload/Download"
    BRONZE_MIN  = "256k/512k", "Bronze (256k / 512k)"
    BRONZE_MAX  = "512k/1M",   "Bronze Plus (512k / 1M)"
    SILVER_MIN  = "1M/2M",     "Silver (1M / 2M)"
    SILVER_MAX  = "2M/4M",     "Silver Plus (2M / 4M)"
    GOLD_MIN    = "4M/8M",     "Gold (4M / 8M)"
    GOLD_MAX    = "5M/10M",    "Gold Plus (5M / 10M)"
    PLATINUM    = "10M/20M",   "Platinum (10M / 20M)"
    ULTRA       = "20M/50M",   "Ultra (20M / 50M)"
    BUSINESS    = "50M/100M",  "Business (50M / 100M)"
    UNLIMITED   = "0/0",       "Illimité (No Limit)"


class SharedUsersLimit(models.IntegerChoices):
    SOLO = 1, "1 Utilisateur (Solo)"
    DUO  = 2, "2 Utilisateurs (Duo)"
    TRIO = 3, "3 Utilisateurs (Famille)"
    TEAM = 5, "5 Utilisateurs (Petit Bureau)"
    OPEN = 0, "Illimité (Non recommandé)"

class Currency(models.TextChoices):
    GNF = "gnf", "Franc Guinnen"



class Profil(Base):

    name = models.CharField(max_length=50, null=False)
    rate_limit = models.CharField(
        max_length=20,
        choices=MikroTikRateLimit.choices,
        default=MikroTikRateLimit.SILVER_MIN
    )
    shared_users = models.IntegerField(
        choices=SharedUsersLimit.choices,
        default=SharedUsersLimit.SOLO
    )
    session_timeout = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    microtik = models.ForeignKey(
        Microtik, 
        on_delete=models.CASCADE, 
        related_name='profils', 
        related_query_name='profils'
        )
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.GNF)
    status = models.CharField(max_length=50, default=Status.ACTIVE)

    def __str__(self):
        return self.price


