from datetime import timedelta
from django.db import OperationalError, transaction
from django.db.models import Count, F
from django.utils import timezone
from .models import Activity, Cancellation, Registration

CANCEL_WINDOW = timedelta(hours=24)

MESSAGES = {
    "registered": "Inscripción confirmada.",
    "already_registered": "Ya estás inscripto en esta actividad.",
    "full": "La actividad no tiene cupos disponibles.",
    "started": "La actividad ya comenzó.",
    "disabled": "La actividad está deshabilitada.",
    "not_available": "La actividad no está disponible.",
    "busy": "La base está ocupada. Intentá nuevamente; no se modificaron datos.",
    "cancelled": "Inscripción cancelada.",
    "not_registered": "No tenés inscripción en esta actividad.",
    "too_late": "El período de cancelación cerró (hasta 24 horas antes del inicio).",
}

def cancellation_message(cancelled_at):
    local = timezone.localtime(cancelled_at)
    return f"Ya cancelaste tu inscripción el {local:%d/%m/%Y} a las {local:%H:%M}"

def with_availability():
    return Activity.objects.annotate(occupied=Count("registrations")).annotate(available=F("capacity") - F("occupied"))

def register(*, student, activity_id, now=None):
    try:
        # SQLite adquiere la reserva de escritura ANTES de leer cupos (IMMEDIATE).
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            if Registration.objects.filter(student=student, activity=activity).exists():
                return "already_registered"
            if Cancellation.objects.filter(student=student, activity=activity).exists():
                return "already_cancelled"
            if not activity.is_active:
                return "disabled"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if activity.starts_at <= now:
                return "started"
            if activity.registrations.count() >= activity.capacity:
                return "full"
            Registration.objects.create(student=student, activity=activity)
            return "registered"
    except OperationalError as error:
        # Solo la contención conocida se vuelve recuperable; otros errores se propagan.
        if "locked" in str(error).lower():
            return "busy"
        raise

def cancel(*, student, activity_id, now=None):
    try:
        # El mismo IMMEDIATE protege lectura, validación de ventana y borrado.
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            if not Registration.objects.filter(student=student, activity=activity).exists():
                if Cancellation.objects.filter(student=student, activity=activity).exists():
                    return "already_cancelled"
                return "not_registered"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if activity.starts_at - now < CANCEL_WINDOW:
                return "too_late"
            Registration.objects.filter(student=student, activity=activity).delete()
            Cancellation.objects.create(student=student, activity=activity)
            return "cancelled"
    except OperationalError as error:
        if "locked" in str(error).lower():
            return "busy"
        raise
