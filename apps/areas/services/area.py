from django.db.models import Q

from apps.areas.models import Area
from apps.areas.choices import AreaType

class AreaService:
    """
    Service layer for Area-related business logic.
    """

    # Fields for area list
    AREA_LIST_FIELDS = (
        "id",
        "name",
        "description",
        "icon",
        "color",
        "image_url",
        "slug",
        "type",
        "display_order",
    )

    @classmethod
    def _base_queryset(cls):
        """
        Base queryset with common filters.
        """
        return Area.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        )

    @classmethod
    def get_area_list(cls, user) -> list[dict]:
        """
        Returns combined list of system areas and user-created areas.
        """
        qs = cls._base_queryset()

        areas = qs.filter(
            Q(type=AreaType.SYSTEM) |
            Q(created_by_id=user.id)
        ).values(*cls.AREA_LIST_FIELDS).order_by("display_order")

        return list(areas)