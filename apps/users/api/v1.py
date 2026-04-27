from rest_framework import status

from apps.base.views import BaseAPIView, UnauthenticatedAPIView
from apps.users.schemas.auth import (
    LogoutSchema,
    SendOTPSchema,
    TokenRefreshSchema,
    VerifyOTPSchema,
)
from apps.users.services.auth import AuthService
from apps.users.services.user import UserService


class SendOTPView(UnauthenticatedAPIView):
    """
    Send a 6-digit OTP to the provided email address.
    Any previously active OTPs for that email are invalidated.
    """

    def post(self, request):
        data = SendOTPSchema.model_validate(request.data)
        AuthService.send_otp(email=data.email)
        return self.success(message="Verification code sent. Please check your inbox.")


class VerifyOTPView(UnauthenticatedAPIView):
    """
    Verify the OTP and return a JWT token pair.
    A new user account is created automatically if none exists for that email.
    """

    def post(self, request):
        data = VerifyOTPSchema.model_validate(request.data)
        tokens = AuthService.verify_otp(email=data.email, code=data.code)
        return self.success(
            data=tokens,
            message="Authentication successful.",
            status_code=status.HTTP_200_OK,
        )


class TokenRefreshView(UnauthenticatedAPIView):
    """
    Rotate a valid refresh token and return a new access + refresh pair.
    """

    def post(self, request):
        data = TokenRefreshSchema.model_validate(request.data)
        tokens = AuthService.refresh_token(refresh_token_str=data.refresh)
        return self.success(data=tokens, message="Token refreshed.")


class LogoutView(BaseAPIView):
    """
    Blacklist the supplied refresh token. The user must be authenticated.
    """

    def post(self, request):
        data = LogoutSchema.model_validate(request.data)
        AuthService.logout(refresh_token_str=data.refresh)
        return self.no_content()


class MeView(BaseAPIView):
    """
    Return the authenticated user's profile.
    """

    def get(self, request):
        data = UserService.get_profile(request.user)
        return self.success(data=data)
