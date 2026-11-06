from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

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
    def clean(self):
        active = self.registrations.filter(status=Registration.STATUS_ACTIVE).count() if self.pk else 0
        if self.pk and self.capacity < active:
            raise ValidationError({"capacity": "No puede reducir la capacidad por debajo de las inscripciones confirmadas."})

class Registration(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [(STATUS_ACTIVE, "activa"), (STATUS_CANCELLED, "cancelada")]
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="registrations")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "activity"], name="one_registration_per_student_activity")]
        ordering = ["-created_at", "-pk"]
        verbose_name = "inscripción"
    def __str__(self):
        return f"{self.student} — {self.activity}"
    @property
    def is_cancelled(self):
        return self.status == self.STATUS_CANCELLED
    def clean(self):
        if self.status == self.STATUS_CANCELLED and self.cancelled_at is None:
            raise ValidationError({"cancelled_at": "La cancelación requiere momento de cancelación."})
        if self.status == self.STATUS_ACTIVE and self.cancelled_at is not None:
            raise ValidationError({"cancelled_at": "Una inscripción activa no tiene momento de cancelación."})

class DemoSeed(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    reference_time = models.DateTimeField()
