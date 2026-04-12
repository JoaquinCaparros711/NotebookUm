"""Unit tests for file validation helpers."""

import io
import json

import pytest
from werkzeug.datastructures import FileStorage

from app import create_app
from app.services.validation import (
    create_rfc9457_error,
    validate_file_size,
    validate_pdf_content_type,
)


@pytest.fixture
def app():
    """Create Flask application for testing."""
    return create_app("testing")


@pytest.fixture
def app_context(app):
    """Create application context for tests."""
    with app.app_context():
        yield app


def _make_file(filename: str, content_type: str, size_bytes: int) -> FileStorage:
    """Build an in-memory uploaded file for validation tests."""
    stream = io.BytesIO(b"a" * size_bytes)
    return FileStorage(stream=stream, filename=filename, content_type=content_type)


@pytest.mark.unit
class TestValidatePDFContentType:
    """Tests for validate_pdf_content_type."""

    def test_accepts_application_pdf(self):
        """Accept PDF files with content-type application/pdf."""
        file = _make_file("doc.pdf", "application/pdf", 64)

        validate_pdf_content_type(file)

    def test_rejects_non_pdf_content_type_with_descriptive_message(self):
        """Reject non-PDF files and provide descriptive error message."""
        file = _make_file("doc.txt", "text/plain", 64)

        with pytest.raises(ValueError) as exc_info:
            validate_pdf_content_type(file)

        message = str(exc_info.value).lower()
        assert "application/pdf" in message or "pdf" in message


@pytest.mark.unit
class TestValidateFileSize:
    """Tests for validate_file_size."""

    def test_accepts_file_size_up_to_25mb(self):
        """Accept files with size <= 25MB."""
        max_size = 25 * 1024 * 1024
        file = _make_file("doc.pdf", "application/pdf", max_size)

        validate_file_size(file, max_size=max_size)

    def test_rejects_file_size_over_25mb_with_descriptive_message(self):
        """Reject files larger than max_size and provide descriptive message."""
        max_size = 25 * 1024 * 1024
        file = _make_file("too_large.pdf", "application/pdf", max_size + 1)

        with pytest.raises(ValueError) as exc_info:
            validate_file_size(file, max_size=max_size)

        message = str(exc_info.value).lower()
        assert "25mb" in message or "size" in message or "tama" in message


@pytest.mark.unit
class TestCreateRFC9457Error:
    """Tests for create_rfc9457_error."""

    def test_builds_problem_details_400_response(self, app_context):
        """Create RFC 9457 error response with 400 status."""
        response = create_rfc9457_error(
            detail="Only PDF files are allowed",
            instance="/api/v1/documento/upload",
        )

        assert response.status_code == 400
        assert response.content_type == "application/problem+json"

        data = json.loads(response.data)
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "pdf" in data["detail"].lower()
        assert data["instance"] == "/api/v1/documento/upload"

