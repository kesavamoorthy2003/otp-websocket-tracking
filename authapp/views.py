import logging
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]

        # Generate 4–6 digit OTP (here: 6 digits)
        otp_value = f"{random.randint(0, 999999):06d}"

        # Hash OTP before storing
        otp_hash = make_password(otp_value)

        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 5))
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)

        OTP.objects.create(
            phone_number=phone_number,
            otp_hash=otp_hash,
            expires_at=expires_at,
        )

        # For assignment purposes, just log the OTP instead of sending SMS
        logger.info("Generated OTP %s for %s (expires in %s minutes)", otp_value, phone_number, expiry_minutes)
        print(f"[DEBUG] OTP for {phone_number}: {otp_value}")

        return Response(
            {"detail": "OTP sent successfully."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_obj: OTP = serializer.validated_data["otp_obj"]
        phone_number = serializer.validated_data["phone_number"]

        # OTP is valid at this point; we can delete it to prevent reuse
        otp_obj.delete()

        user, _created = User.objects.get_or_create(phone_number=phone_number)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

