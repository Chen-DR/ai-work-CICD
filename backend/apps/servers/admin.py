from django.contrib import admin
from .models import Server, ServerCredential, ServerAllowedDir

admin.site.register(Server)
admin.site.register(ServerCredential)
admin.site.register(ServerAllowedDir)
