from apps.areas.services.area import AreaService
from apps.base.views import BaseAPIView


class AreaListAPI(BaseAPIView):
    def get(self, request):
        """
        Get list of areas (system + user-created).
        """
        areas = AreaService.get_area_list(request.user)
        return self.success(data=areas, message="Listed System + User created areas.")