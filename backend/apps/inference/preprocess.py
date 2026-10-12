from io import BytesIO

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 18_000_000

MIME_BY_FORMAT = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}


class InvalidImage(ValueError):
    pass


def safely_decode(raw: bytes) -> tuple[Image.Image, str]:
    try:
        with Image.open(BytesIO(raw)) as opened:
            opened.verify()
        with Image.open(BytesIO(raw)) as reopened:
            image = ImageOps.exif_transpose(reopened).convert("RGB")
            mime = MIME_BY_FORMAT.get(reopened.format or "")
            if not mime:
                raise InvalidImage("Unsupported image format.")
            return image.copy(), mime
    except Exception as exc:
        raise InvalidImage("The uploaded file is not a valid chart image.") from exc
