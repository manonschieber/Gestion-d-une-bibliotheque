from django.contrib import admin

from .models import Client, Livre

admin.site.register(Client)
admin.site.register(Livre)