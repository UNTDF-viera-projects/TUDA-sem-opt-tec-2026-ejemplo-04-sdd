from datetime import timedelta
from django.db import OperationalError, transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from .models import Activity, Registration

CANCELLATION_WINDOW = timedelta(hours=24)

MESSAGES = {
    "registered": "Inscripción confirmada.",
    "already_registered": "Ya estás inscripto en esta actividad.",
    "reinscription_unavailable": "La reinscripción no está disponible en esta versión.",
    "full": "La actividad no tiene cupos disponibles.",
    "started": "La actividad ya comenzó.",
    "disabled": "La actividad está deshabilitada.",
    "not_available": "La actividad no está disponible.",
    "cancelled": "Inscripción cancelada. Se liberó un cupo.",
    "already_cancelled": "La inscripción ya estaba cancelada.",
    "window_closed": "El plazo para cancelar venció: hacen falta 24 horas completas antes del inicio.",
    "unavailable": "No encontramos una inscripción tuya para esa solicitud.",
    "busy": "La base está ocupada. Intentá nuevamente; no se modificaron datos.",
}

def with_availability():
    # Una inscripción cancelada conserva la fila pero no ocupa cupo.
    return Activity.objects.annotate(occupied=Count("registrations", filter=Q(registrations__cancelled_at__isnull=True))).annotate(available=F("capacity") - F("occupied"))

def cancellation_deadline(activity):
    return activity.starts_at - CANCELLATION_WINDOW

def can_cancel(*, registration, now=None):
    if registration.is_cancelled:
        return False
    now = now or timezone.now()
    return now <= cancellation_deadline(registration.activity)

def register(*, student, activity_id, now=None):
    try:
        # SQLite adquiere la reserva de escritura ANTES de leer cupos (IMMEDIATE).
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            existing = Registration.objects.filter(student=student, activity=activity).first()
            if existing is not None:
                # Cancelar no habilita volver a inscribirse (fuera de F1).
                return "reinscription_unavailable" if existing.is_cancelled else "already_registered"
            if not activity.is_active:
                return "disabled"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if activity.starts_at <= now:
                return "started"
            if activity.registrations.filter(cancelled_at__isnull=True).count() >= activity.capacity:
                return "full"
            Registration.objects.create(student=student, activity=activity)
            return "registered"
    except OperationalError as error:
        # Solo la contención conocida se vuelve recuperable; otros errores se propagan.
        if "locked" in str(error).lower():
            return "busy"
        raise

def cancel_registration(*, student, registration_id, now=None):
    try:
        with transaction.atomic():
            # El titular filtra en la misma consulta: ajena e inexistente son indistinguibles.
            registration = Registration.objects.filter(pk=registration_id, student=student).select_related("activity").first()
            if registration is None:
                return "unavailable"
            # Idempotente y consultivo: repetir conserva la fecha original, incluso fuera de plazo.
            if registration.is_cancelled:
                return "already_cancelled"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if now > cancellation_deadline(registration.activity):
                return "window_closed"
            registration.cancelled_at = now
            registration.save(update_fields=["cancelled_at"])
            return "cancelled"
    except OperationalError as error:
        if "locked" in str(error).lower():
            return "busy"
        raise