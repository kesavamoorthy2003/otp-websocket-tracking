from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import serializers

from .models import OTP


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        if len(value) < 8 or len(value) > 20:
            raise serializers.ValidationError("Invalid phone number length.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number", "").strip()
        otp = attrs.get("otp", "").strip()

        if not phone_number or not otp:
            raise serializers.ValidationError("Phone number and OTP are required.")

        try:
            otp_obj = (
                OTP.objects.filter(phone_number=phone_number)
                .order_by("-created_at")
                .first()
            )
        except OTP.DoesNotExist:  # pragma: no cover - defensive
            otp_obj = None

        if not otp_obj:
            raise serializers.ValidationError("OTP not found. Please request a new one.")

        max_attempts = int(getattr(settings, "OTP_MAX_ATTEMPTS", 5))

        if otp_obj.attempt_count >= max_attempts:
            raise serializers.ValidationError(
                f"Maximum OTP attempts exceeded. Please request a new OTP."
            )

        if otp_obj.is_expired():
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        if not check_password(otp, otp_obj.otp_hash):
            otp_obj.attempt_count += 1
            otp_obj.save(update_fields=["attempt_count"])
            raise serializers.ValidationError("Invalid OTP.")

        attrs["otp_obj"] = otp_obj
        return attrs



