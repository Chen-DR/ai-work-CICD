from django.contrib import admin
from .models import BenchmarkScript, BenchmarkJob

admin.site.register(BenchmarkScript)
admin.site.register(BenchmarkJob)
