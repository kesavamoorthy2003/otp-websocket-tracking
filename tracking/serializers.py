from rest_framework import serializers

from .models import Driver, DriverLocation, Ride


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ("id", "user", "is_active")
        read_only_fields = ("id", "user")


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ("ride_id", "driver", "rider", "created_at")
        read_only_fields = ("ride_id", "rider", "created_at")


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ("driver", "latitude", "longitude", "updated_at")
        read_only_fields = ("driver", "updated_at")


