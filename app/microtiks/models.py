from django.db import models
from app.commone.models import Base
from app.users.models import User
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from app.subscriptions.models import SubscriptionVpn


class Status(models.TextChoices):
    DISABLE = "disable", "desactiver"
    ACTIVE = "active", "activer et fonctionne"



class Microtik(Base):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="microtiks")
    
    subscription = models.OneToOneField(
        SubscriptionVpn, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="suscription_vpn"
        )
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    users_count = models.BigIntegerField(default=0)
    
    commission_rate = models.FloatField(default=15.0, help_text="Pourcentage prélevé sur les ventes")

    is_online = models.BooleanField(default=True)
    admin_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
    
    @property
    def amount_available_windrawal(self):
        return float(00.0)



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


