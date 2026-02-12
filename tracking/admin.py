from django.contrib import admin

from .models import Driver, DriverLocation, Ride


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active")
    search_fields = ("user__phone_number",)
    list_filter = ("is_active",)


@admin.register(DriverLocation)
class DriverLocationAdmin(admin.ModelAdmin):
    list_display = ("driver", "latitude", "longitude", "updated_at")
    search_fields = ("driver__user__phone_number",)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("ride_id", "driver", "rider", "created_at")
    search_fields = ("ride_id", "driver__user__phone_number", "rider__phone_number")
