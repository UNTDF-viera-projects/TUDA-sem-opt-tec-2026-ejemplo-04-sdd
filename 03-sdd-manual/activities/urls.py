from django.urls import path
from django.shortcuts import redirect
from . import views
urlpatterns = [path("", lambda request: redirect("catalog")), path("activities/", views.catalog, name="catalog"), path("activities/<int:pk>/", views.detail, name="activity_detail"), path("activities/<int:pk>/register/", views.enroll, name="register"), path("activities/<int:pk>/cancel/", views.cancel_registration, name="cancel"), path("my-registrations/", views.mine, name="mine")]
