from django.db import models
from app.commone.models import Base
from django.utils import timezone
from datetime import timedelta
from app.microtiks.models import Microtik


#-------------------Le prix de base -------------------#
class SubscriptioPriceBase(Base):

    price = models.DecimalField(max_digits=10, decimal_places=2, default=15000)
    is_active = models.BooleanField(default=True)

class ConfigurationPrice(Base):
    price = models.DecimalField(max_digits=10, decimal_places=2, default=950000)
    is_active = models.BooleanField(default=True)

#--------------------- Les categories d'abonement --------------------#
class SubscriptionCategorieWg(Base):
    name = models.CharField(max_length=50)
    days = models.PositiveIntegerField(help_text="Durée en jour")
    discount = models.DecimalField(default=0.0, decimal_places=2,max_digits=5)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de l'abonnement")
    is_active = models.BooleanField(default=True)


#----------------------- Paiement d'abonnement ---------------------#


class SubscriptionWG(Base):
    """Abonnement WireGuard d'un point de vente / MikroTik"""
    
    microtik = models.OneToOneField(
        Microtik,
        on_delete=models.CASCADE,
        null=True,
        related_name="subscriptionwg"
    )
    wg_client_id = models.CharField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True, 
        verbose_name="ID Client wg-easy"
    )
    wg_ip = models.GenericIPAddressField(
        null=True, 
        blank=True, 
        verbose_name="IP du Tunnel WireGuard"
    )
    wg_private_key = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Clé Privée du MikroTik"
    )
    wg_public_key = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Clé Publique du MikroTik"
    )
    
    mikrotik_username = models.CharField(
        max_length=50, 
        default="admin", 
        verbose_name="User Winbox/API"
    )
    mikrotik_password = models.CharField(
        max_length=50, 
        default="", 
        blank=True, 
        verbose_name="Pass Winbox/API"
    )

    gdms_site_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        )
    gdms_network_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        )
    mac_address = models.CharField(
        max_length=17, 
        unique=True,
        null=True
        )
    serial_number = models.CharField(max_length=50,null=True)
    device_name = models.CharField(max_length=250,null=True)
    
    expire_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    
    @property
    def validation(self):
        if not self.expire_at:
            return False
        return self.expire_at >= timezone.now().date()
    
    @property
    def days_remaining(self):
        if not self.expire_at:
            return 0
        delta = self.expire_at - timezone.now().date()
        return max(delta.days, 0)
    
    def __str__(self):
        return f"Abonnement - IP: {self.wg_ip} (Actif: {self.validation})"