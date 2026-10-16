from django.contrib import admin
from django.db import transaction
from .models import Activity, Registration

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_at", "capacity", "is_active"]
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # El mismo IMMEDIATE protege lectura de ocupación, validación y guardado.
        return super().changeform_view(request, object_id, form_url, extra_context)

class EstadoCancelacion(admin.SimpleListFilter):
    title = "estado"
    parameter_name = "estado"
    def lookups(self, request, model_admin):
        return [("vigente", "Vigentes"), ("cancelada", "Canceladas")]
    def queryset(self, request, queryset):
        if self.value() == "vigente":
            return queryset.filter(cancelled_at__isnull=True)
        if self.value() == "cancelada":
            return queryset.filter(cancelled_at__isnull=False)
        return queryset

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["student", "activity", "created_at", "cancelled_at"]
    list_filter = [EstadoCancelacion]
    # Ver el estado sí; alterar el estado no. Toda cancelación pasa por el servicio.
    readonly_fields = ["student", "activity", "created_at", "cancelled_at"]
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
