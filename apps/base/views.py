from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


class BaseAPIView(APIView):
    """
    Base API view for all authenticated endpoints.

    Defaults:
    - Authentication: JWT + Session
    - Permission: IsAuthenticated

    Error responses are handled globally by the custom exception handler.
    Raise exceptions from apps.base.exceptions instead of returning error responses.

    Inherit from this for any protected endpoint.
    """

    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def success(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    def created(self, data=None, message="Created successfully"):
        return self.success(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    def no_content(self):
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnauthenticatedAPIView(BaseAPIView):
    """
    Base API view for public/unauthenticated endpoints.

    Overrides permissions to allow any request without authentication.
    Use this for login, register, password reset, and other public endpoints.
    """

    authentication_classes = []
    permission_classes = [AllowAny]


class HealthCheckView(UnauthenticatedAPIView):
    """
    Health check API to verify the service is running.
    """

    def get(self, request):
        return self.success(message="Service is healthy")
