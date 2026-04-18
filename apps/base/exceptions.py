import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

from rest_framework import exceptions, status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exception Classes
# ---------------------------------------------------------------------------


class AppException(APIException):
    """
    Base exception for all custom application exceptions.
    Raise this (or a subclass) anywhere in the codebase.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred."
    default_code = "error"

    def __init__(self, message=None, errors=None, status_code=None):
        self.detail = message or self.default_detail
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code


class ValidationException(AppException):
    """Raise for invalid input / bad request."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation error."
    default_code = "validation_error"


class NotFoundException(AppException):
    """Raise when a requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionException(AppException):
    """Raise when the user does not have permission."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class UnauthorizedException(AppException):
    """Raise when the user is not authenticated."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication required."
    default_code = "unauthorized"


class ConflictException(AppException):
    """Raise for duplicate / conflict situations."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "A conflict occurred."
    default_code = "conflict"


class ServerException(AppException):
    """Raise for unexpected server-side errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unexpected error occurred."
    default_code = "server_error"


# ---------------------------------------------------------------------------
# Custom Exception Handler
# ---------------------------------------------------------------------------


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    Returns all errors in the standard format:
        {
            "success": false,
            "message": "...",
            "errors": {...} | null
        }

    Register in settings:
        REST_FRAMEWORK = {
            'EXCEPTION_HANDLER': 'apps.base.exceptions.custom_exception_handler',
        }
    """

    # --- Convert Django native exceptions to DRF equivalents ---
    # DRF's built-in handler doesn't know about these Django exceptions,
    # so we normalise them first (inspired by HackSoft's approach).
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    # Let DRF handle it first to get the default response (sets status codes etc.)
    response = exception_handler(exc, context)

    # --- Custom AppException ---
    if isinstance(exc, AppException):
        return Response(
            {
                "success": False,
                "message": exc.detail,
                "errors": exc.errors,
            },
            status=exc.status_code,
        )

    # --- DRF Built-in Exceptions ---
    if response is not None:
        message, errors = _extract_drf_exception(exc, response)
        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
        }
        return response

    # --- Unhandled / Unexpected Exceptions ---
    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {
            "success": False,
            "message": "An unexpected error occurred.",
            "errors": None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_drf_exception(exc, response):
    """Map DRF built-in exceptions to a (message, errors) pair."""

    if isinstance(exc, ValidationError):
        return "Validation error.", response.data

    if isinstance(exc, NotFound):
        return "Resource not found.", None

    if isinstance(exc, PermissionDenied):
        return "You do not have permission to perform this action.", None

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return "Authentication required.", None

    # Any other DRF APIException
    detail = (
        response.data.get("detail")
        if isinstance(response.data, dict)
        else str(response.data)
    )
    return str(detail) if detail else "An error occurred.", None
