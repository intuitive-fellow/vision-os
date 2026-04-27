from apps.areas.schemas.area import AreaCreateSchema
from apps.areas.services.area import AreaService
from apps.base.views import BaseAPIView


class AreaListCreateAPI(BaseAPIView):
    def get(self, request):
        """
        Get list of areas (system + user-created).
        """
        areas = AreaService.get_area_list(request.user)
        return self.success(data=areas, message="Listed System + User created areas.")

    def post(self, request):
        """
        Create a new custom area for the user.
        """
        data = AreaCreateSchema.model_validate(request.data)
        area = AreaService.create_area(request.user, data.model_dump())
        return self.created(data=area, message="Area created successfully.")