from django.db import models

OPTIONAL = {"null": True, "blank": True}
CASCADE = {"on_delete": models.CASCADE}
SET_NULL = {"on_delete": models.SET_NULL, "null": True}
