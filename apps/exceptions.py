from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, PermissionDenied
import datetime


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "PM-GEN-000"  # General error code as default

        # TODO: Add more error codes
        if isinstance(exc, ValidationError):
            error_code = "PM-VAL-001"
        elif isinstance(exc, PermissionDenied):
            error_code = "PM-AUTH-001"

        custom_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "status": response.status_code,
            "error": response.reason_phrase,
            "code": error_code,
            "message": str(exc),
            "path": context['request'].path,
        }
        response.data = custom_data

    return response
