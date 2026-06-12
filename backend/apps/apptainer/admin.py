from django.contrib import admin
from .models import ApptainerDefinition, ApptainerBuildJob

admin.site.register(ApptainerDefinition)
admin.site.register(ApptainerBuildJob)
