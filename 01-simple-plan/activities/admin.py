from django.contrib import admin
from django.db import transaction
from django.utils.timezone import localtime
from .models import Activity, Registration

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_at", "capacity", "is_active"]
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # El mismo IMMEDIATE protege lectura de ocupación, validación y guardado.
        return super().changeform_view(request, object_id, form_url, extra_context)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["student", "activity", "created_at", "cancelled_at", "state"]
    readonly_fields = ["student", "activity", "created_at", "cancelled_at"]
    @admin.display(description="Estado")
    def state(self, obj):
        # La cancelación es un dato de la fila; el admin no la ejecuta ni la revierte.
        return f"Inscripción cancelada el {localtime(obj.cancelled_at):%d/%m/%Y %H:%M}" if obj.is_cancelled else "Inscripción confirmada"
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False