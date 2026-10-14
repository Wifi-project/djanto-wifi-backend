from django.db import models
from app.commone.models import Base


#-------------------Le prix de base -------------------#
class SubscriptioPriceBase(Base):

    price = models.DecimalField(max_digits=10, decimal_places=2, default=15000)
    is_active = models.BooleanField(default=True)

class ConfigurationPrice(Base):
    price = models.DecimalField(max_digits=10, decimal_places=2, default=950000)
    is_active = models.BooleanField(default=True)

#--------------------- Les categories d'abonement --------------------#
class SubscriptionCategorie(Base):
    name = models.CharField(max_length=50)
    days = models.PositiveIntegerField(help_text="Durée en jour")
    discount = models.DecimalField(default=0.0, decimal_places=2,max_digits=5)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Prix de l'abonnement")
    is_active = models.BooleanField(default=True)


