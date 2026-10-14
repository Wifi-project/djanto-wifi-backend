from django.contrib import admin
from app.gdms.models import Gdms,Network

@admin.register(Network)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", )
    # search_fields = ("slug", "phone_number", "profil_name",)



@admin.register(Gdms)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("slug", "network__name", )
