import random
import uuid

from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """
    Handles user lifecycle operations.
    """

    @staticmethod
    def get_or_create_by_email(email: str):
        """
        Retrieve an existing user by *email*, or create a new one.

        New users:
          - Have an auto-generated username (uuid4-based, never exposed)
          - Have an unusable password (passwordless auth only)
          - Are marked active immediately (email is verified via OTP)

        Returns the User instance.
        """
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": UserService._generate_username(),
                "avatar": UserService._get_random_avatar(),
                "is_active": True,
            },
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        return user

    @staticmethod
    def get_profile(user) -> dict:
        """Return a plain dict of profile data for *user*."""
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "avatar": user.avatar,
            "bio": user.bio,
            "timezone": user.timezone,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_username() -> str:
        """Generate a unique internal username that is never shown to users."""
        return f"user_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def _get_random_avatar() -> str:
        """Return a random avatar URL from a predefined list."""
        avatars = [
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix",
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka",
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Jasper",
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Mia",
            "https://api.dicebear.com/7.x/avataaars/svg?seed=Oliver",
        ]
        return random.choice(avatars)
