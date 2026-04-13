"""File validation helpers for document upload workflows."""

from flask import Response
from werkzeug.datastructures import FileStorage

from app.utils.errors import bad_request


def validate_pdf_content_type(file: FileStorage) -> None:
    """Validate that the uploaded file is a PDF."""
    content_type = (file.content_type or "").lower()
    if content_type != "application/pdf":
        raise ValueError("Invalid content type. Only application/pdf files are allowed.")


def validate_file_size(file: FileStorage, max_size: int = 25 * 1024 * 1024) -> None:
    """Validate that the uploaded file size does not exceed max_size bytes."""
    size = file.content_length
    if size is None or size <= 0:
        current_pos = file.stream.tell()
        file.stream.seek(0, 2)
        size = file.stream.tell()
        file.stream.seek(current_pos)

    if size > max_size:
        raise ValueError("File size exceeds 25MB maximum allowed size.")


def create_rfc9457_error(detail: str, instance: str) -> Response:
    """Create an RFC 9457 (Problem Details) error response for bad requests."""
    return bad_request(detail=detail, instance=instance)
