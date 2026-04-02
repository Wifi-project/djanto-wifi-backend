from django.db import models
from app.commone.models import Base
from app.users.models import User

class OwnerMicrotik(Base):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ownermicrotik",unique=True)
    pourcentage = models.IntegerField(default=20)
    carte = models.ImageField(upload_to='carte/')
    