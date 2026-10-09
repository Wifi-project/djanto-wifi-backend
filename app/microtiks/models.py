from django.db import models
from app.commone.models import Base
from app.users.models import User
from app.permissions.models import Permissions


class Status(models.TextChoices):
    DISABLE = "disable", "desactiver"
    ACTIVE = "active", "activer et fonctionne"

class RouteurType(models.TextChoices):
    MIKROTIK = "MIKROTIK", "MikroTik RouterOS"
    GDMS = "GDMS", "Grandstream GDMS Cloud"

class Microtik(Base):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, null=True, blank=True)
    device_type = models.CharField(
        max_length=20, 
        choices=RouteurType.choices, 
        default=RouteurType.GDMS
    )
    owners = models.ManyToManyField(
            User, 
            related_name="owners_microtik",
            through="MicrotikOwner"
        )
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    users_count = models.PositiveIntegerField(default=0)
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        help_text="Pourcentage prélevé sur les ventes (ex: 15.00 pour 15%)"
    )
    is_online = models.BooleanField(default=True)
    admin_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
        
    @property
    def amount_available_windrawal(self):
        montant_preleve = self.wallet_balance * (self.commission_rate / 100)
        amount = self.wallet_balance - montant_preleve
        return amount if amount > 0 else 0.0


class MicrotikOwner(Base):
    """Table intermédiaire avec un ManyToMany interne"""
    
    microtik = models.ForeignKey(
        Microtik, 
        on_delete=models.CASCADE, 
        related_name="microtik_owners"
        )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="microtik_owner_trough"
        )
    permissions = models.ManyToManyField(
        Permissions,
        related_name='microtik_owners_permissions',
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [['microtik', 'user']]
        ordering = ['-created_at']


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
    up_rate = models.PositiveIntegerField(
        default=0,
        verbose_name="Débit montant",
        help_text="Débit upload en Kbps",
    )
    down_rate = models.PositiveIntegerField(
        default=0,
        verbose_name="Débit descendant",
        help_text="Débit download en Kbps",
    )
    shared_users = models.IntegerField(
        choices=SharedUsersLimit.choices,
        default=SharedUsersLimit.SOLO
    )
    session_timeout = models.CharField(max_length=50)
    session_timeout_dict = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    microtik = models.ForeignKey(
        Microtik, 
        on_delete=models.CASCADE, 
        related_name='profils', 
        related_query_name='profils'
        )
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.GNF)
    status = models.CharField(max_length=50, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.price} GNF)"


