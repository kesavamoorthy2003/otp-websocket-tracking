from django.urls import path

from .views import (
    DriverMeView,
    RideCreateView,
    RideDetailView,
    RideLocationView,
)

urlpatterns = [
    path("me/driver/", DriverMeView.as_view(), name="driver-me"),
    path("rides/", RideCreateView.as_view(), name="ride-create"),
    path("rides/<str:ride_id>/", RideDetailView.as_view(), name="ride-detail"),
    path("rides/<str:ride_id>/location/", RideLocationView.as_view(), name="ride-location"),
]


