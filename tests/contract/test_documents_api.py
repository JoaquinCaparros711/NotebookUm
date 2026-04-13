"""Contract tests for POST /api/v1/documento/upload endpoint."""

import io

import pytest

from app import create_app
from app.database import db


UPLOAD_ENDPOINT = "/api/v1/documento/upload"


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    flask_app = create_app("testing")

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.mark.contract
class TestUploadDocuments:
    """Contract tests for POST /api/v1/documento/upload."""

    def test_upload_valid_pdf_returns_202(self, client):
        """A valid PDF file under 25MB must be accepted."""
        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "documento.pdf",
                "application/pdf",
            )
        }

        response = client.post(
            UPLOAD_ENDPOINT,
            data=file_data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 202
        assert response.content_type == "application/json"

        data = response.get_json()
        assert data is not None
        assert "document_id" in data
        assert "status" in data

    def test_upload_non_pdf_returns_400_problem_details(self, client):
        """A non-PDF file must be rejected with RFC 9457 error."""
        file_data = {
            "file": (
                io.BytesIO(b"This is plain text, not a PDF."),
                "documento.txt",
                "text/plain",
            )
        }

        response = client.post(
            UPLOAD_ENDPOINT,
            data=file_data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        assert response.content_type == "application/problem+json"

        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "pdf" in data["detail"].lower()
        assert data["instance"] == UPLOAD_ENDPOINT

    def test_upload_pdf_over_25mb_returns_400_problem_details(self, client, app):
        """A PDF larger than 25MB must be rejected with RFC 9457 error."""
        max_size = app.config["MAX_UPLOAD_SIZE"]
        oversized_pdf = b"%PDF-1.4\n" + (b"0" * max_size)
        file_data = {
            "file": (
                io.BytesIO(oversized_pdf),
                "muy_grande.pdf",
                "application/pdf",
            )
        }

        response = client.post(
            UPLOAD_ENDPOINT,
            data=file_data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        assert response.content_type == "application/problem+json"

        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "25mb" in data["detail"].lower() or "size" in data["detail"].lower()
        assert data["instance"] == UPLOAD_ENDPOINT

    def test_upload_returns_async_confirmation_payload(self, client):
        """A successful upload must confirm asynchronous processing details."""
        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "async_documento.pdf",
                "application/pdf",
            )
        }

        response = client.post(
            UPLOAD_ENDPOINT,
            data=file_data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 202
        data = response.get_json()
        assert data is not None
        assert "job_id" in data
        assert data["status"] in {"pending", "processing"}
        assert "status_url" in data

    def test_upload_processing_error_returns_500_problem_details(self, client, monkeypatch):
        """Queue/processing enqueue failures must return RFC 9457 500 response."""
        from app.routes.documents import process_document_task

        def _raise_enqueue_error(*args, **kwargs):
            raise RuntimeError("queue unavailable")

        monkeypatch.setattr(process_document_task, "delay", _raise_enqueue_error)

        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "enqueue_error.pdf",
                "application/pdf",
            )
        }

        response = client.post(
            UPLOAD_ENDPOINT,
            data=file_data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 500
        assert response.content_type == "application/problem+json"

        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Internal Server Error"
        assert data["status"] == 500
        assert data["instance"] == UPLOAD_ENDPOINT

