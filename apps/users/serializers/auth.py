from rest_framework import serializers
from apps.base.serializers import BaseInputSerializer


class SendOTPSerializer(BaseInputSerializer):
    """Validate the email address for OTP dispatch."""

    email = serializers.EmailField(
        help_text="The email address to send the one-time verification code to."
    )

    def validate_email(self, value: str) -> str:
        return value.lower().strip()


class VerifyOTPSerializer(BaseInputSerializer):
    """Validate email + OTP code pair for authentication."""

    email = serializers.EmailField(help_text="The email address the OTP was sent to.")
    code = serializers.CharField(
        min_length=6,
        max_length=6,
        help_text="The 6-digit one-time code received via email.",
    )

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def validate_code(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain digits only.")
        return value


class TokenRefreshSerializer(BaseInputSerializer):
    """Validate a JWT refresh token for rotation."""

    refresh = serializers.CharField(
        help_text="The refresh token obtained from a previous authentication."
    )


class LogoutSerializer(BaseInputSerializer):
    """Validate a JWT refresh token for blacklisting."""

    refresh = serializers.CharField(help_text="The refresh token to invalidate.")
