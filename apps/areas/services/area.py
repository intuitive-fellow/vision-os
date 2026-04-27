from django.db.models import Q
from django.utils.text import slugify

from apps.areas.choices import AreaType
from apps.areas.models import Area
from apps.base.exceptions import ConflictException


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

    @classmethod
    def create_area(cls, user, validated_data: dict) -> dict:
        name = validated_data["name"]

        name_conflict = cls._base_queryset().filter(
            Q(type=AreaType.SYSTEM) | Q(created_by_id=user.id),
            name__iexact=name,
        ).exists()
        if name_conflict:
            raise ConflictException("An area with this name already exists.")

        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Area.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        area = Area.objects.create(
            name=name,
            slug=slug,
            type=AreaType.CUSTOM,
            created_by=user,
            description=validated_data.get("description"),
            icon=validated_data.get("icon"),
            image_url=validated_data.get("image_url"),
            color=validated_data.get("color"),
            display_order=validated_data.get("display_order"),
        )

        return Area.objects.filter(id=area.id).values(*cls.AREA_LIST_FIELDS).first()