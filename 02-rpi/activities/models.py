from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# Definición única de inscripción activa. Una inscripción cancelada conserva la fila y
# su fecha, pero no ocupa cupo: los tres conteos del proyecto salen de este filtro.
# El prefijo permite reutilizar la misma definición en consultas sobre Activity, donde
# el filtro de una anotación se resuelve contra Activity y no contra Registration.
def active_registrations_q(prefix: str = "") -> models.Q:
    return models.Q(**{f"{prefix}cancelled_at__isnull": True})

class Activity(models.Model):
    title = models.CharField("título", max_length=160)
    description = models.TextField("descripción")
    starts_at = models.DateTimeField("inicio")
    capacity = models.PositiveIntegerField("capacidad")
    is_active = models.BooleanField("habilitada", default=True)
    seed_key = models.CharField(max_length=40, null=True, blank=True, unique=True, editable=False)
    class Meta:
        ordering = ["starts_at", "pk"]
        constraints = [models.CheckConstraint(condition=models.Q(capacity__gt=0), name="positive_capacity")]
        verbose_name = "actividad"
    def __str__(self):
        return self.title
    @property
    def active_registrations(self):
        return self.registrations.filter(active_registrations_q())
    def clean(self):
        if self.pk and self.capacity < self.active_registrations.count():
            raise ValidationError({"capacity": "No puede reducir la capacidad por debajo de las inscripciones confirmadas."})

class Registration(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="registrations")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField("cancelación", null=True, blank=True, default=None)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "activity"], name="one_registration_per_student_activity")]
        ordering = ["-created_at", "-pk"]
        verbose_name = "inscripción"
    def __str__(self):
        return f"{self.student} — {self.activity}"

class DemoSeed(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    reference_time = models.DateTimeField()
