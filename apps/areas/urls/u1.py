from django.urls import path
from apps.areas.api.v1 import AreaListAPI


urlpatterns = [
    path("list-areas/", AreaListAPI.as_view(), name="list-areas"),
]