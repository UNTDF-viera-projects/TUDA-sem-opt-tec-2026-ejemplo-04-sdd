from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from .forms import RegistrationForm
from .models import Registration
from .services import CANCELLATION_WINDOW, MESSAGES, cancel_registration, can_cancel, cancellation_deadline, register, with_availability

@login_required
def catalog(request):
    return render(request, "activities/catalog.html", {"activities": with_availability().filter(is_active=True, starts_at__gt=timezone.now())})

@login_required
def detail(request, pk):
    activity = get_object_or_404(with_availability(), pk=pk)
    registration = Registration.objects.filter(activity=activity, student=request.user).first()
    open_for_registration = activity.is_active and activity.starts_at > timezone.now() and activity.available > 0
    return render(request, "activities/detail.html", {"activity": activity, "registration": registration, "can_register": open_for_registration and registration is None, "form": RegistrationForm()})

@login_required
@require_POST
def enroll(request, pk):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        result = register(student=request.user, activity_id=pk)
        messages.info(request, MESSAGES[result], extra_tags=result)
    return redirect("activity_detail", pk=pk)

@login_required
@require_http_methods(["GET", "POST"])
def cancel(request, pk):
    registration = Registration.objects.filter(pk=pk, student=request.user).select_related("activity").first()
    if registration is None:
        # Respuesta genérica: no distingue ajena de inexistente.
        messages.info(request, MESSAGES["unavailable"], extra_tags="unavailable")
        return redirect("mine")
    if request.method == "POST":
        # El reloj del servicio se evalúa dentro de IMMEDIATE, no en la vista.
        result = cancel_registration(student=request.user, registration_id=pk)
        messages.info(request, MESSAGES[result], extra_tags=result)
        return redirect("mine")
    now = timezone.now()  # Solo para mostrar el plazo; no decide la transición.
    return render(request, "activities/cancel_confirm.html", {"registration": registration, "activity": registration.activity, "deadline": cancellation_deadline(registration.activity), "can_cancel": can_cancel(registration=registration, now=now), "window_hours": int(CANCELLATION_WINDOW.total_seconds() // 3600)})

@login_required
def mine(request):
    now = timezone.now()  # Un solo instante para toda la pantalla.
    registrations = Registration.objects.filter(student=request.user).select_related("activity")
    entries = [{"registration": registration, "deadline": cancellation_deadline(registration.activity), "can_cancel": can_cancel(registration=registration, now=now)} for registration in registrations]
    return render(request, "activities/mine.html", {"entries": entries})