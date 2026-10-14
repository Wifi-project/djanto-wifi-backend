from django.db import models
from app.commone.models import Base


class Permissions(Base):
    name = models.CharField(max_length=250,blank=False,null=False)
    code = models.CharField(max_length=250, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    
class PermissionGroup(Base):
    name = models.CharField(max_length=250,blank=False,null=False)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(Permissions, related_name="permissionsGroup")
    users = models.ManyToManyField("users.User", related_name="custom_permission_groups")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name