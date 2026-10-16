from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import RegistrationForm
from .models import Cancellation, Registration
from .services import MESSAGES, cancel, cancellation_message, register, with_availability

def _cancelled_text(request, activity_id):
    cancellation = Cancellation.objects.filter(activity_id=activity_id, student=request.user).first()
    if cancellation is None:
        return MESSAGES["not_available"]
    return cancellation_message(cancellation.cancelled_at)

@login_required
def catalog(request):
    return render(request, "activities/catalog.html", {"activities": with_availability().filter(is_active=True, starts_at__gt=timezone.now())})

@login_required
def detail(request, pk):
    activity = get_object_or_404(with_availability(), pk=pk)
    registration = Registration.objects.filter(activity=activity, student=request.user).first()
    cancellation = Cancellation.objects.filter(activity=activity, student=request.user).first()
    open_for_registration = activity.is_active and activity.starts_at > timezone.now() and activity.available > 0
    return render(request, "activities/detail.html", {"activity": activity, "registration": registration, "cancellation": cancellation, "can_register": open_for_registration and registration is None and cancellation is None, "form": RegistrationForm()})

@login_required
@require_POST
def enroll(request, pk):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        result = register(student=request.user, activity_id=pk)
        text = _cancelled_text(request, pk) if result == "already_cancelled" else MESSAGES[result]
        messages.info(request, text, extra_tags=result)
    return redirect("activity_detail", pk=pk)

@login_required
@require_POST
def cancel_registration(request, pk):
    result = cancel(student=request.user, activity_id=pk)
    if result in ("cancelled", "already_cancelled"):
        text = _cancelled_text(request, pk)
    else:
        text = MESSAGES[result]
    messages.info(request, text, extra_tags=result)
    return redirect("activity_detail", pk=pk)

@login_required
def mine(request):
    return render(request, "activities/mine.html", {"registrations": Registration.objects.filter(student=request.user).select_related("activity"), "cancellations": Cancellation.objects.filter(student=request.user).select_related("activity")})
