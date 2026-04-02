from django.db import models
import uuid,secrets

def generate_slug():
    return secrets.token_urlsafe(16)

class Base(models.Model):
    slug = models.CharField(max_length=40, default=generate_slug, unique=True)
    created_at = models.DateField(auto_now=True)
    update_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True

