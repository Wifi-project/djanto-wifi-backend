from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # 1. Configuration de la liste d'utilisateurs
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_editable = ('is_active',)
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')

    # 2. Configuration des champs affichés lors de l'ÉDITION d'un utilisateur
    # (Remplace 'username' par 'email')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    # 3. Configuration des champs affichés lors de la CRÉATION d'un utilisateur
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )