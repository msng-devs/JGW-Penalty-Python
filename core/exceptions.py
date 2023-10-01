import datetime

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
)


def _check_error_code(exc):
    match exc:
        # VALIDATION ERRORS
        case ValidationError():
            error_code = "PM-VALD-001"
        # SQL ERRORS
        case IntegrityError():
            error_code = "PM-SQL-001"
        case ObjectDoesNotExist():
            error_code = "PM-SQL-002"
        # VALUE ERRORS
        case ValueError():
            error_code = "PM-VAL-001"
        case TypeError():
            error_code = "PM-VAL-002"
        case KeyError():
            error_code = "PM-VAL-003"
        case IndexError():
            error_code = "PM-VAL-004"
        # AUTHENTICATION ERRORS
        case PermissionDenied():
            error_code = "PM-AUTH-001"
        case NotAuthenticated():
            error_code = "PM-AUTH-002"
        case AttributeError():
            error_code = "PM-AUTH-003"
        # DATABASE ERRORS
        case ConnectionError():
            error_code = "PM-DB-001"
        case TimeoutError():
            error_code = "PM-DB-002"
        case ConnectionRefusedError():
            error_code = "PM-DB-003"
        case ConnectionAbortedError():
            error_code = "PM-DB-004"
        case ConnectionResetError():
            error_code = "PM-DB-005"
        case BrokenPipeError():
            error_code = "PM-DB-006"
        case _:
            error_code = "PM-GEN-000"  # General error code as default

    return error_code


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_code = _check_error_code(exc=exc)

        custom_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "status": response.status_code,
            "error": response.reason_phrase,
            "code": error_code,
            "message": str(exc),
            "path": context["request"].path,
        }
        response.data = custom_data

    return response
