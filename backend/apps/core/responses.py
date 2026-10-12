from rest_framework.response import Response


def error_response(code: str, message: str, status_code: int, extra: dict | None = None) -> Response:
    payload = {"error": {"code": code, "message": message}}
    if extra:
        payload["error"].update(extra)
    return Response(payload, status=status_code)
