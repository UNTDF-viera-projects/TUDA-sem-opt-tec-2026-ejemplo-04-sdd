from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import RegistrationForm
from .models import Registration
from .services import MESSAGES, can_cancel, cancel, register, with_availability

@login_required
def catalog(request):
    return render(request, "activities/catalog.html", {"activities": with_availability().filter(is_active=True, starts_at__gt=timezone.now())})

@login_required
def detail(request, pk):
    activity = get_object_or_404(with_availability(), pk=pk)
    registration = Registration.objects.filter(activity=activity, student=request.user).select_related("activity").first()
    now = timezone.now()
    open_for_registration = activity.is_active and activity.starts_at > now and activity.available > 0
    return render(request, "activities/detail.html", {"activity": activity, "registration": registration, "can_register": open_for_registration and registration is None, "form": RegistrationForm(), "can_cancel": registration is not None and can_cancel(registration=registration, now=now)})

@login_required
@require_POST
def enroll(request, pk):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        result = register(student=request.user, activity_id=pk)
        messages.info(request, MESSAGES[result], extra_tags=result)
    return redirect("activity_detail", pk=pk)

@login_required
@require_POST
def cancel_registration(request, pk):
    result = cancel(student=request.user, activity_id=pk)
    messages.info(request, MESSAGES[result], extra_tags=result)
    return redirect("mine")

@login_required
def mine(request):
    now = timezone.now()
    registrations = list(Registration.objects.filter(student=request.user).select_related("activity"))
    cancellable_ids = {r.pk for r in registrations if can_cancel(registration=r, now=now)}
    return render(request, "activities/mine.html", {"registrations": registrations, "cancellable_ids": cancellable_ids})
