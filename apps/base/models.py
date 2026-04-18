from django.db import models

from apps.base.constants import OPTIONAL


class BaseModel(models.Model):
    """
    Base model for all models in the project.
    Contains common fields for all models.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(**OPTIONAL)

    class Meta:
        abstract = True
