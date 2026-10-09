from django.contrib import admin
from app.clients.models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "code_username", "phone_number", "profil_name",)
    search_fields = ("code_username", "phone_number", "profil_name",)
    # list_filter = ("microtik",)