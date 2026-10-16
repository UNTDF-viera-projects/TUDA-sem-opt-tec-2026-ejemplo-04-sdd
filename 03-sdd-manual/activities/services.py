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
    "cancelled": "Inscripción cancelada. Se liberó un cupo.",
    "already_cancelled": "Esta inscripción ya estaba cancelada.",
    "window_closed": "No podés cancelar: el plazo venció 24 h antes del inicio.",
    "not_cancellable": "No se pudo cancelar esta inscripción.",
    "not_reenrollable": "Tu inscripción fue cancelada; la reinscripción no está habilitada.",
}

WINDOW = timedelta(hours=24)


def cancellation_deadline(activity):
    return activity.starts_at - WINDOW


def can_cancel(*, registration, now):
    return registration.cancelled_at is None and now <= cancellation_deadline(registration.activity)


def with_availability():
    return Activity.objects.annotate(
        occupied=Count("registrations", filter=Q(registrations__cancelled_at__isnull=True))
    ).annotate(available=F("capacity") - F("occupied"))

def register(*, student, activity_id, now=None):
    try:
        # SQLite adquiere la reserva de escritura ANTES de leer cupos (IMMEDIATE).
        with transaction.atomic():
            activity = Activity.objects.filter(pk=activity_id).first()
            if activity is None:
                return "not_available"
            registration = Registration.objects.filter(student=student, activity=activity).first()
            if registration is not None:
                return "not_reenrollable" if registration.cancelled_at is not None else "already_registered"
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


def cancel(*, student, activity_id, now=None):
    try:
        with transaction.atomic():  # BEGIN IMMEDIATE: toma la reserva de escritura ANTES de leer
            registration = (
                Registration.objects
                .select_related("activity")
                .filter(student=student, activity_id=activity_id)
                .first()
            )
            if registration is None:  # ajena · inexistente · actividad borrada → misma rama
                return "not_cancellable"
            if registration.cancelled_at is not None:  # repetición ANTES que plazo y sin reloj
                return "already_cancelled"
            now = now or timezone.now()  # reloj dentro de la transacción, tras el bloqueo
            if now > cancellation_deadline(registration.activity):  # borde inclusivo
                return "window_closed"
            updated = Registration.objects.filter(
                pk=registration.pk, cancelled_at__isnull=True  # escritura condicional
            ).update(cancelled_at=now)
            if not updated:  # otra transición ya ocurrió → defensa estructural
                return "already_cancelled"
            return "cancelled"
    except OperationalError as error:  # solo contención conocida es recuperable
        if "locked" in str(error).lower():
            return "busy"
        raise
