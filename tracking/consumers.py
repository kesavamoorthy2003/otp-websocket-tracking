import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.utils import timezone

from .models import Driver, DriverLocation, Ride

logger = logging.getLogger(__name__)
jwt_auth = JWTAuthentication()


class TrackingConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles both driver and rider WebSocket connections.

    - Drivers:
        * Connect with ?token=<JWT>
        * Send:
            {"event": "driver_identify", "driver_id": 1}
            {"event": "driver_location", "latitude": 12.34, "longitude": 56.78, "timestamp": "..."}
    - Riders:
        * Connect with ?token=<JWT>
        * Send:
            {"event": "subscribe_ride", "ride_id": "RIDE123"}
    """

    async def connect(self):
        user = await self._authenticate_user()
        if not user:
            await self.close(code=4001)
            return

        self.user = user
        self.driver = None
        self.ride_id = None
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "ride_id", None):
            await self.channel_layer.group_discard(
                self._ride_group_name(self.ride_id),
                self.channel_name,
            )

        if getattr(self, "driver", None):
            # No persistent "online" flag here, but this is where it could be handled.
            logger.info("Driver %s disconnected", self.driver.id)

    async def receive_json(self, content, **kwargs):
        event = content.get("event")

        if event == "driver_identify":
            await self._handle_driver_identify(content)
        elif event == "driver_location":
            await self._handle_driver_location(content)
        elif event == "subscribe_ride":
            await self._handle_subscribe_ride(content)
        else:
            await self.send_json({"error": "Unknown event type."})

    async def _handle_driver_identify(self, content):
        driver_id = content.get("driver_id")
        if not driver_id:
            await self.send_json({"error": "driver_id is required."})
            return

        driver = await self._get_driver(driver_id)
        if not driver:
            await self.send_json({"error": "Driver not found."})
            return

        self.driver = driver
        await self.send_json({"status": "driver_registered", "driver_id": driver_id})

    async def _handle_driver_location(self, content):
        if not self.driver:
            await self.send_json({"error": "Driver not identified."})
            return

        try:
            latitude = float(content.get("latitude"))
            longitude = float(content.get("longitude"))
        except (TypeError, ValueError):
            await self.send_json({"error": "Invalid latitude/longitude."})
            return

        timestamp = content.get("timestamp") or timezone.now().isoformat()

        await self._update_location(self.driver, latitude, longitude)

        # Broadcast to any riders subscribed to this driver's active ride
        ride = await self._get_latest_ride_for_driver(self.driver)
        if ride:
            await self.channel_layer.group_send(
                self._ride_group_name(ride.ride_id),
                {
                    "type": "location_update",
                    "data": {
                        "driver_id": self.driver.id,
                        "ride_id": ride.ride_id,
                        "latitude": latitude,
                        "longitude": longitude,
                        "timestamp": timestamp,
                    },
                },
            )

        await self.send_json({"status": "location_updated"})

    async def _handle_subscribe_ride(self, content):
        ride_id = content.get("ride_id")
        if not ride_id:
            await self.send_json({"error": "ride_id is required."})
            return

        ride_exists = await self._ride_exists(ride_id)
        if not ride_exists:
            await self.send_json({"error": "Ride not found."})
            return

        self.ride_id = ride_id
        await self.channel_layer.group_add(
            self._ride_group_name(ride_id),
            self.channel_name,
        )
        await self.send_json({"status": "subscribed", "ride_id": ride_id})

    async def location_update(self, event):
        await self.send_json(event["data"])

    # Helper methods

    async def _authenticate_user(self):
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token")
        if not token_list:
            return None

        raw_token = token_list[0]
        try:
            validated_token = jwt_auth.get_validated_token(raw_token)
            user = jwt_auth.get_user(validated_token)
            return user
        except AuthenticationFailed:
            return None

    @database_sync_to_async
    def _get_driver(self, driver_id: int):
        try:
            return Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return None

    @database_sync_to_async
    def _update_location(self, driver: Driver, latitude: float, longitude: float):
        DriverLocation.objects.update_or_create(
            driver=driver,
            defaults={
                "latitude": latitude,
                "longitude": longitude,
                "updated_at": timezone.now(),
            },
        )

    @database_sync_to_async
    def _get_latest_ride_for_driver(self, driver: Driver):
        return (
            Ride.objects.filter(driver=driver)
            .order_by("-created_at")
            .first()
        )

    @database_sync_to_async
    def _ride_exists(self, ride_id: str) -> bool:
        return Ride.objects.filter(ride_id=ride_id).exists()

    @staticmethod
    def _ride_group_name(ride_id: str) -> str:
        return f"ride_{ride_id}"



