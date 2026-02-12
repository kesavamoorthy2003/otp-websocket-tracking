from django.contrib import admin

from .models import User, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "created_at", "is_active", "is_staff")
    search_fields = ("phone_number",)
    list_filter = ("is_active", "is_staff")


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "expires_at", "attempt_count", "created_at")
    search_fields = ("phone_number",)
    list_filter = ("expires_at",)
