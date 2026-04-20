import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.base.exceptions import (
    UnauthorizedException,
    ValidationException,
)
from apps.users.constants import OTP_MAX_ATTEMPTS
from apps.users.models import EmailOTP
from apps.users.services.user import UserService

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles all authentication-related logic:
      - OTP generation and email dispatch
      - OTP verification and JWT issuance
      - Token refresh and logout (blacklist)
    """

    # ------------------------------------------------------------------
    # OTP
    # ------------------------------------------------------------------

    @staticmethod
    def send_otp(email: str) -> None:
        """
        Generate a fresh OTP for *email*, invalidate any previous unused OTPs
        for that address, and send the code via email.
        """
        # Invalidate all previous un-used OTPs for this email so only the
        # latest code is ever valid.
        EmailOTP.objects.filter(email=email, is_used=False).update(is_used=True)

        otp = EmailOTP.objects.create(email=email)

        AuthService._send_otp_email(email=email, code=otp.code)
        logger.info("OTP sent to %s", email)

    @staticmethod
    def verify_otp(email: str, code: str):
        """
        Verify the submitted OTP code for *email*.

        On success:
          - Marks the OTP as used
          - Gets or creates the User for *email*
          - Returns a dict with ``access`` and ``refresh`` JWT strings

        Raises:
          ValidationException – invalid, expired, or too-many-attempts OTP
        """
        try:
            otp = (
                EmailOTP.objects.filter(email=email, is_used=False)
                .order_by("-created_at")
                .first()
            )
        except EmailOTP.DoesNotExist:
            otp = None

        if otp is None:
            raise ValidationException("No active OTP found for this email. Please request a new one.")

        if otp.is_expired:
            raise ValidationException("OTP has expired. Please request a new one.")

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            raise ValidationException("Too many failed attempts. Please request a new OTP.")

        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            remaining = max(OTP_MAX_ATTEMPTS - otp.attempts, 0)
            raise ValidationException(
                f"Invalid OTP. {remaining} attempt(s) remaining."
            )

        # Mark as used
        otp.is_used = True
        otp.save(update_fields=["is_used"])

        # Get or create user
        user = UserService.get_or_create_by_email(email)

        tokens = AuthService._generate_tokens(user)
        logger.info("User %s authenticated via OTP", user.email)
        return tokens

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    @staticmethod
    def refresh_token(refresh_token_str: str) -> dict:
        """
        Rotate the refresh token and return a new token pair.

        Raises:
          UnauthorizedException – if the token is invalid or blacklisted
        """
        try:
            refresh = RefreshToken(refresh_token_str)
            # Access new access token (triggers rotation if ROTATE_REFRESH_TOKENS=True)
            new_access = str(refresh.access_token)
            # Rotate produces a new refresh token
            refresh.set_jti()
            refresh.set_exp()
            new_refresh = str(refresh)
            return {"access": new_access, "refresh": new_refresh}
        except TokenError as exc:
            raise UnauthorizedException(str(exc)) from exc

    @staticmethod
    def logout(refresh_token_str: str) -> None:
        """
        Blacklist the provided refresh token, effectively logging the user out.

        Raises:
          UnauthorizedException – if the token is invalid
        """
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
            logger.info("Refresh token blacklisted")
        except TokenError as exc:
            raise UnauthorizedException(str(exc)) from exc

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_tokens(user) -> dict:
        """Return a dict with ``access`` and ``refresh`` JWT strings for *user*."""
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def _send_otp_email(email: str, code: str) -> None:
        """Dispatch the OTP email. Raises nothing – caller handles logging."""
        subject = "Your VisionOS verification code"
        message = (
            f"Your VisionOS one-time verification code is:\n\n"
            f"    {code}\n\n"
            f"This code expires in 10 minutes. Do not share it with anyone."
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
