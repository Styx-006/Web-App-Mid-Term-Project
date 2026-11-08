from django.contrib import admin
from .models import Business, OwnedBusiness, PlayerProgress

admin.site.register(PlayerProgress)
admin.site.register(Business)
admin.site.register(OwnedBusiness)