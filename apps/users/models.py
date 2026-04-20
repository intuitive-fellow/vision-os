import secrets
import string

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.base.constants import OPTIONAL
from apps.base.models import BaseModel
from apps.users.constants import OTP_EXPIRY_MINUTES, OTP_LENGTH
from apps.users.managers import CustomUserManager


class User(AbstractUser, BaseModel):
    """
    Custom user model.
    """

    # Override to make email unique and required.
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    objects = CustomUserManager()

    # username is kept but hidden from users; auto-generated on creation.
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Auto-generated internal identifier. Not shown to users."),
    )

    # ------------------------------------------------------------------
    # Profile fields
    # ------------------------------------------------------------------

    avatar = models.URLField(
        _("avatar URL"),
        **OPTIONAL,
        help_text=_("URL to the user's profile picture."),
    )

    bio = models.TextField(
        _("bio"),
        **OPTIONAL,
        max_length=500,
        help_text=_("Short description about the user."),
    )

    timezone = models.CharField(
        _("timezone"),
        max_length=64,
        default="UTC",
        help_text=_("User's local timezone (e.g. 'Asia/Kolkata')."),
    )

    # ------------------------------------------------------------------
    # Many-to-many overrides (resolve reverse accessor clashes)
    # ------------------------------------------------------------------

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        related_name="custom_user_groups",
        help_text=_(
            "The groups this user belongs to. "
            "A user will get all permissions granted to each of their groups."
        ),
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_user_permissions",
        help_text=_("Specific permissions for this user."),
    )

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # No prompts beyond email when using createsuperuser

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        db_table = "users"


    def __str__(self):
        return self.email

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email.split("@")[0]


def _generate_otp():
    """Return a cryptographically secure numeric OTP string."""
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(OTP_LENGTH))


def _otp_expiry():
    """Return the expiry datetime for a freshly generated OTP."""
    return timezone.now() + timezone.timedelta(minutes=OTP_EXPIRY_MINUTES)


class EmailOTP(models.Model):
    """
    Stores a one-time password sent to a user's email address.

    A new record is created each time an OTP is requested.
    Old/unused records for the same email are invalidated on new requests.
    """

    email = models.EmailField(_("email address"), db_index=True)
    code = models.CharField(
        _("OTP code"),
        max_length=OTP_LENGTH,
        default=_generate_otp,
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        default=_otp_expiry,
    )
    is_used = models.BooleanField(_("is used"), default=False)
    attempts = models.PositiveSmallIntegerField(
        _("failed attempts"),
        default=0,
        help_text=_("Number of failed verification attempts for this OTP."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("email OTP")
        verbose_name_plural = _("email OTPs")
        ordering = ["-created_at"]
        db_table = "email_otps"

    def __str__(self):
        return f"OTP({self.email}, used={self.is_used})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
