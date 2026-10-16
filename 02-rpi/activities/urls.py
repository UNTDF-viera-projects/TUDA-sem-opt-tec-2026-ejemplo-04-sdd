from django.urls import path
from django.shortcuts import redirect
from . import views
urlpatterns = [path("", lambda request: redirect("catalog")), path("activities/", views.catalog, name="catalog"), path("activities/<int:pk>/", views.detail, name="activity_detail"), path("activities/<int:pk>/register/", views.enroll, name="register"), path("my-registrations/", views.mine, name="mine"), path("my-registrations/<int:pk>/cancel/", views.cancel_confirm, name="cancel_confirm"), path("my-registrations/<int:pk>/cancel/confirm/", views.cancel, name="cancel")]
