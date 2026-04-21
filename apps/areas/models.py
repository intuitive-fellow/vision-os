from django.db import models
from django.conf import settings

from apps.base.models import BaseModel
from apps.base.constants import OPTIONAL, SET_NULL
from apps.areas.choices import AreaType


class Area(BaseModel):
    """
    Represents a high-level life domain (e.g., fitness, career, finance) used to
    organize goals, tasks, and activities. Supports system-defined and user-created
    areas, with optional ownership, ordering, and soft deletion.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(**OPTIONAL)
    type = models.CharField(max_length=20, choices=AreaType.choices)
    icon = models.CharField(max_length=50, **OPTIONAL)
    image_url = models.URLField(**OPTIONAL)
    color = models.CharField(max_length=20, **OPTIONAL)
    display_order = models.IntegerField(**OPTIONAL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, **SET_NULL, **OPTIONAL, related_name="areas"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "areas"
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ["display_order"]

    def __str__(self):
        return self.name
