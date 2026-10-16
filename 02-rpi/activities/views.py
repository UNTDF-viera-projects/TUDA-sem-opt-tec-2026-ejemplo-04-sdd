from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import RegistrationForm
from .models import Registration
from .services import MESSAGES, can_cancel, cancel as cancel_registration, register, with_availability

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
def mine(request):
    now = timezone.now()  # Un solo reloj por request: badge y botón no pueden contradecirse.
    registrations = Registration.objects.filter(student=request.user).select_related("activity")
    return render(request, "activities/mine.html", {"registrations": registrations, "cancelable": [r.pk for r in registrations if can_cancel(r, now=now)]})

@login_required
def cancel_confirm(request, pk):
    # 404 para ajena e inexistente por igual: la pantalla no revela nada.
    registration = get_object_or_404(Registration.objects.select_related("activity").filter(student=request.user), pk=pk)
    return render(request, "activities/cancel_confirm.html", {"registration": registration, "can_cancel": can_cancel(registration)})

@login_required
@require_POST
def cancel(request, pk):
    result = cancel_registration(student=request.user, registration_id=pk)
    messages.info(request, MESSAGES[result], extra_tags=result)
    return redirect("mine")
