import uuid

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Driver, DriverLocation, Ride
from .serializers import (
    DriverSerializer,
    RideSerializer,
    DriverLocationSerializer,
)


class DriverMeView(APIView):
    """
    Create or fetch a Driver profile for the authenticated user.

    - GET  /tracking/me/driver/   -> return current user's driver profile (if exists)
    - POST /tracking/me/driver/   -> create driver profile for current user
    """

    def get(self, request):
        driver = Driver.objects.filter(user=request.user).first()
        if not driver:
            return Response(
                {"detail": "Driver profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = DriverSerializer(driver).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        driver, created = Driver.objects.get_or_create(user=request.user)
        data = DriverSerializer(driver).data
        return Response(
            data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RideCreateView(APIView):
    """
    Create a ride linking a driver and the current user (rider).

    - POST /tracking/rides/
      body: {"driver_id": 1, "ride_id": "optional-custom-id"}
    """

    def post(self, request):
        driver_id = request.data.get("driver_id")
        if not driver_id:
            return Response(
                {"detail": "driver_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        driver = get_object_or_404(Driver, id=driver_id)

        ride_id = request.data.get("ride_id") or f"RIDE-{uuid.uuid4().hex[:10]}"

        ride, created = Ride.objects.get_or_create(
            ride_id=ride_id,
            defaults={
                "driver": driver,
                "rider": request.user,
            },
        )
        data = RideSerializer(ride).data
        return Response(
            data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RideDetailView(APIView):
    """
    Get basic details of a ride.

    - GET /tracking/rides/<ride_id>/
    """

    def get(self, request, ride_id: str):
        ride = get_object_or_404(Ride, ride_id=ride_id)
        data = RideSerializer(ride).data
        return Response(data, status=status.HTTP_200_OK)


class RideLocationView(APIView):
    """
    Get latest driver location for a ride.

    - GET /tracking/rides/<ride_id>/location/
    """

    def get(self, request, ride_id: str):
        ride = get_object_or_404(Ride, ride_id=ride_id)
        location = getattr(ride.driver, "location", None)
        if not location:
            return Response(
                {"detail": "Location not available for this driver."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = DriverLocationSerializer(location).data
        return Response(data, status=status.HTTP_200_OK)

