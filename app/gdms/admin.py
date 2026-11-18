from django.contrib import admin
from app.gdms.models import Gdms,Network,NetworkOwner

@admin.register(Network)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", )
    # search_fields = ("slug", "phone_number", "profil_name",)



@admin.register(Gdms)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("slug", "network__name", )


@admin.register(NetworkOwner)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("slug", "network__name","user__first_name","user__last_name" )
