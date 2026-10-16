from datetime import timedelta
from django.db import OperationalError, transaction
from django.db.models import Count, F
from django.utils import timezone
from .models import Activity, Registration, active_registrations_q

# Ventana de cancelación acordada: al menos 24 horas exactas antes del inicio, sin redondear.
CANCELLATION_LEAD = timedelta(hours=24)

MESSAGES = {
    "registered": "Inscripción confirmada.",
    "already_registered": "Ya estás inscripto en esta actividad.",
    "full": "La actividad no tiene cupos disponibles.",
    "started": "La actividad ya comenzó.",
    "disabled": "La actividad está deshabilitada.",
    "not_available": "La actividad no está disponible.",
    "busy": "La base está ocupada. Intentá nuevamente; no se modificaron datos.",
    "cancelled": "Inscripción cancelada. El cupo quedó disponible.",
    "already_cancelled": "Esta inscripción ya estaba cancelada.",
    "too_late": "No se puede cancelar: el plazo de 24 horas antes del inicio venció.",
    "not_found": "No encontramos esa inscripción en tu cuenta.",
    "cancelled_no_reenrollment": "Tu inscripción está cancelada y la reinscripción no está disponible en esta demo.",
}

def with_availability():
    return Activity.objects.annotate(occupied=Count("registrations", filter=active_registrations_q("registrations__"))).annotate(available=F("capacity") - F("occupied"))

def can_cancel(registration, *, now=None):
    # Una actividad deshabilitada SÍ se puede cancelar: el plazo es la única condición.
    if registration.cancelled_at is not None:
        return False
    return registration.activity.starts_at - (now or timezone.now()) >= CANCELLATION_LEAD

def register(*, student, activity_id, now=None):
    try:
        # SQLite adquiere la reserva de escritura ANTES de leer cupos (IMMEDIATE).
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            existing = Registration.objects.filter(student=student, activity=activity).first()
            if existing is not None:
                # La fila cancelada se conserva: la reinscripción queda fuera de alcance.
                return "already_registered" if existing.cancelled_at is None else "cancelled_no_reenrollment"
            if not activity.is_active:
                return "disabled"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if activity.starts_at <= now:
                return "started"
            if activity.active_registrations.count() >= activity.capacity:
                return "full"
            Registration.objects.create(student=student, activity=activity)
            return "registered"
    except OperationalError as error:
        # Solo la contención conocida se vuelve recuperable; otros errores se propagan.
        if "locked" in str(error).lower():
            return "busy"
        raise

def cancel(*, student, registration_id, now=None):
    try:
        with transaction.atomic():
            # Filtrar por titular hace que ajena e inexistente sean indistinguibles.
            registration = (Registration.objects
                            .select_related("activity")
                            .filter(pk=registration_id, student=student).first())
            if registration is None:
                return "not_found"
            # Idempotencia antes del plazo: repetir es no-op incluso fuera de la ventana.
            if registration.cancelled_at is not None:
                return "already_cancelled"
            now = now or timezone.now()  # Instante real después de adquirir IMMEDIATE.
            if registration.activity.starts_at - now < CANCELLATION_LEAD:
                return "too_late"
            # El propio WHERE es la transición única: compare-and-swap, no lectura+escritura.
            updated = (Registration.objects
                       .filter(pk=registration_id, cancelled_at__isnull=True)
                       .update(cancelled_at=now))
            return "cancelled" if updated == 1 else "already_cancelled"
    except OperationalError as error:
        if "locked" in str(error).lower():
            return "busy"
        raise
