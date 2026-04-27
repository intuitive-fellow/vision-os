from django.urls import path
from apps.areas.api.v1 import AreaListCreateAPI


urlpatterns = [
    path("", AreaListCreateAPI.as_view(), name="list-create-areas"),
]