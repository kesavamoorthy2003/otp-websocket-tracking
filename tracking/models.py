from django.conf import settings
from django.db import models
from django.utils import timezone


class Driver(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_profile",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Driver {self.user.phone_number}"


class DriverLocation(models.Model):
    driver = models.OneToOneField(
        Driver,
        on_delete=models.CASCADE,
        related_name="location",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.driver} @ {self.latitude},{self.longitude}"


class Ride(models.Model):
    ride_id = models.CharField(max_length=64, unique=True)
    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="rides",
    )
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rides",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Ride {self.ride_id}"
