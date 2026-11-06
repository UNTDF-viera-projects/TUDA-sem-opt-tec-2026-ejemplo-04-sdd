from datetime import timedelta

from django.db import OperationalError, transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from .models import Activity, Registration

MESSAGES = {
    "registered": "Inscripción confirmada.",
    "already_registered": "Ya estás inscripto en esta actividad.",
    "full": "La actividad no tiene cupos disponibles.",
    "started": "La actividad ya comenzó.",
    "disabled": "La actividad está deshabilitada.",
    "not_available": "La actividad no está disponible.",
    "busy": "La base está ocupada. Intentá nuevamente; no se modificaron datos.",
    "cancelled": "Inscripción cancelada.",
    "too_late": "El plazo de cancelación terminó (24 horas antes del inicio).",
    "already_cancelled": "La inscripción ya está cancelada.",
    "no_resubscribe": "Ya tuviste una inscripción en esta actividad; en esta versión no podés reinscribirte.",
}

def with_availability():
    active = Count("registrations", filter=Q(registrations__status=Registration.STATUS_ACTIVE))
    return Activity.objects.annotate(occupied=active).annotate(available=F("capacity") - F("occupied"))

def cancel_deadline(activity):
    """Último instante en que se puede cancelar: inicio − 24h (inclusive)."""
    return activity.starts_at - timedelta(hours=24)

def cancel_block_reason(registration, now):
    """Clave de mensaje que impide cancelar, o None si la cancelación es posible."""
    if registration.status == Registration.STATUS_CANCELLED:
        return "already_cancelled"
    if registration.activity.starts_at <= now:
        return "started"
    if now > cancel_deadline(registration.activity):
        return "too_late"
    return None

def can_cancel(registration, now):
    return cancel_block_reason(registration, now) is None

def register(*, student, activity_id, now=None):
    try:
        # SQLite adquiere la reserva de escritura ANTES de leer cupos (IMMEDIATE).
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            if Registration.objects.filter(student=student, activity=activity, status=Registration.STATUS_CANCELLED).exists():
                return "no_resubscribe"
            if Registration.objects.filter(student=student, activity=activity).exists():
                return "already_registered"
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
        # La misma disciplina que register(): reserva de escritura ANTES de leer.
        with transaction.atomic():
            registration = Registration.objects.filter(
                activity_id=activity_id,
                student=student,
            ).select_related("activity").first()
            if registration is None:
                return "not_available"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            reason = cancel_block_reason(registration, now)
            if reason:
                return reason
            registration.status = Registration.STATUS_CANCELLED
            registration.cancelled_at = now
            registration.save(update_fields=["status", "cancelled_at"])
            return "cancelled"
    except OperationalError as error:
        # Solo la contención conocida se vuelve recuperable; otros errores se propagan.
        if "locked" in str(error).lower():
            return "busy"
        raise
