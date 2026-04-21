from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.areas.models import Area


@admin.register(Area)
class AreaAdmin(ModelAdmin):
    list_display = ["name", "type", "is_active", "display_order"]
    list_filter = ["type", "is_active"]
    search_fields = ["name", "description"]
    ordering = ["display_order"]