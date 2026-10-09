from django.contrib import admin
from .models import PermissionGroup, Permissions


@admin.register(Permissions)
class PermissionsAdmin(admin.ModelAdmin):  #  Utiliser admin.ModelAdmin
    list_display = ('name', 'code', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):  #  Utiliser admin.ModelAdmin
    list_display = ('name',)  #  Ajout de la virgule pour former un tuple valide
    search_fields = ('name',)