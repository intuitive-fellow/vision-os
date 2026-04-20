from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.users.models import User

from django.contrib.auth.models import Group
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

# Unregister default models
admin.site.unregister(Group)
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["email", "first_name", "last_name", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
