from django.core.exceptions import ValidationError


def validate_non_empty(value: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValidationError("This field cannot be blank.")
    return cleaned
