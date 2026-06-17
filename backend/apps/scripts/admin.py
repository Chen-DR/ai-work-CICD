from django.contrib import admin

from .models import ScriptExecutionTask, ScriptFile, ScriptParamPreset


admin.site.register(ScriptFile)
admin.site.register(ScriptParamPreset)
admin.site.register(ScriptExecutionTask)
