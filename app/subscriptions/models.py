from django.db import models
from app.commone.models import Base
from django.utils import timezone
from datetime import timedelta


class SubscriptionCategorieVpn(Base):
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    ANNUEL = "annuel"

    CHOICES = [
        (MENSUEL, "Mensuel"),
        (TRIMESTRIEL, "Trimestriel"),
        (ANNUEL, "Annuel"),
    ]

    name = models.CharField(max_length=50, choices=CHOICES, default=MENSUEL)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de l'abonnement")
    is_active = models.BooleanField(default=True)


class SubscriptionVpn(Base):
    """ 
        pour la suscription a un abonement ou garder le standard de facturation par pourcentage.
    """
    
    vpn_username = models.CharField(max_length=50, unique=True, null=True)
    vpn_password = models.CharField(max_length=50, null=True)
    vpn_ip = models.GenericIPAddressField(null=True, blank=True)

    category = models.ForeignKey(SubscriptionCategorieVpn, on_delete=models.PROTECT)
    expire_at = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expire_at or self.expire_at is None:
            durations = {
                SubscriptionCategorieVpn.MENSUEL: 30,
                SubscriptionCategorieVpn.TRIMESTRIEL: 90,
                SubscriptionCategorieVpn.ANNUEL: 360,
            }
            days = durations.get(self.category.name)
            if days:
                self.expire_at = timezone.now().date() + timedelta(days=days)
        super().save(*args, **kwargs)

    @property
    def validation(self):
        return self.expire_at >= timezone.now().date()
