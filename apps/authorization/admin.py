from django.contrib import admin

from .models import HabrUser, HabrUserProfile

admin.site.register(HabrUser)
admin.site.register(HabrUserProfile)
