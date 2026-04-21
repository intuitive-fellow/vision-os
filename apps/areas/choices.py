from django.db import models


class AreaType(models.TextChoices):
        SYSTEM = "system", "System"
        CUSTOM = "custom", "Custom"