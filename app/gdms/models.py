from django.db import models
from app.commone.models import Base
from app.users.models import User
from app.permissions.models import Permissions,PermissionGroup
from django.utils import timezone


class Status(models.TextChoices):
    DISABLE = "disable", "desactiver"
    ACTIVE = "active", "activer et fonctionne"


class Network(Base):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250, null=True, blank=True)
    network_id = models.IntegerField(
        null=True, 
        blank=True, 
        )
    owners = models.ManyToManyField(
        User, 
        related_name="owners_network",
        through="NetworkOwner"
    )
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        help_text="Pourcentage prélevé sur les ventes (ex: 15.00 pour 15%)"
    )
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    admin_blocked = models.BooleanField(default=False)

    subscription_expire_at = models.DateField(null=True, blank=True)
    subscription_at = models.DateField(null=True, blank=True)
    configuration_paid = models.BooleanField(default=False)

    @property
    def subscription(self):
        if not self.subscription_expire_at:
            return False
        return self.subscription_expire_at >= timezone.now().date()
    
    @property
    def days_remaining(self):
        if not self.subscription_expire_at:
            return 0
        delta = self.subscription_expire_at - timezone.now().date()
        return max(delta.days, 0)



class NetworkOwner(Base):
    """Table intermédiaire avec un ManyToMany interne"""
    
    network = models.ForeignKey(
        Network, 
        on_delete=models.CASCADE, 
        related_name="network_owners"
        )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="network_owner_trough"
        )
    permissions = models.ManyToManyField(
        Permissions,
        related_name='network_owners_permissions',
        blank=True,
    )
    group_permissions = models.ManyToManyField(
        PermissionGroup,
        related_name='network_owners_group_permissions'
    )
    status = models.CharField(choices=Status, default=Status.ACTIVE)
    
    class Meta:
        unique_together = [['network', 'user']]
        ordering = ['-created_at']



class Gdms(Base):
    """le routeur gdms"""
    description = models.CharField(max_length=250, null=True, blank=True)
    network = models.ForeignKey(
        Network, on_delete=models.CASCADE,
        related_name="gdms_network"
        )
    gdms_site_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        )
    mac_address = models.CharField(
        max_length=17, 
        unique=True,
        null=True
        )
    password = models.CharField(max_length=50,null=True)    
    device_add = models.BooleanField(default=False)
    is_online = models.BooleanField(default=True)
    set_isloation = models.BooleanField(default=False)
    status = models.CharField(choices=Status, default=Status.ACTIVE)




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
    network = models.ForeignKey(
        Network, 
        on_delete=models.CASCADE, 
        related_name='profils', 
        related_query_name='profils'
        )
    currency = models.CharField(max_length=10, choices=Currency.choices, default=Currency.GNF)
    status = models.CharField(max_length=50, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.price} GNF)"


