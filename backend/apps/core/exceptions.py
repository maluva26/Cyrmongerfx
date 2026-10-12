import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def _code(exc) -> str:
    return getattr(exc, "default_code", None) or exc.__class__.__name__.upper()


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        view = context["view"].__class__.__name__ if context.get("view") else "unknown"
        logger.error("Unhandled server error in %s", view, exc_info=exc)
        return Response(
            {"error": {"code": "SERVER_ERROR", "message": "Something went wrong. Please try again later."}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data.get("detail", response.data) if isinstance(response.data, dict) else response.data
    if isinstance(detail, dict):
        message = "Please correct the highlighted fields."
        payload = {"code": _code(exc), "message": message, "fields": detail}
    elif isinstance(detail, list):
        payload = {"code": _code(exc), "message": " ".join(str(item) for item in detail)}
    else:
        payload = {"code": _code(exc), "message": str(detail)}
    response.data = {"error": payload}
    return response
