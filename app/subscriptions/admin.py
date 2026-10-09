from django.contrib import admin
from app.subscriptions.models import ConfigurationPrice



@admin.register(ConfigurationPrice)
class Configuration(admin.ModelAdmin): 
    list_display = ('price',)  
    search_fields = ('price',)
    