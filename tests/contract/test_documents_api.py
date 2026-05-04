"""Contract tests for document API endpoints (upload, list, patch, delete)."""

import io
from datetime import datetime

import pytest

from app import create_app
from app.database import db
from app.models.summary import Summary


UPLOAD_ENDPOINT = "/api/v1/documento/upload"
LIST_ENDPOINT = "/api/v1/documentos"
USERS_ENDPOINT = "/api/v1/users"
PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


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


def _create_user(client, email, nombre):
    response = client.post(USERS_ENDPOINT, json={"email": email, "nombre": nombre})
    assert response.status_code == 201
    data = response.get_json()
    assert data is not None
    return data["id"]


def _upload_document_for_user(client, user_id, filename):
    response = client.post(
        UPLOAD_ENDPOINT,
        data={"file": (io.BytesIO(PDF_BYTES), filename, "application/pdf")},
        headers={"X-User-ID": str(user_id)},
        content_type="multipart/form-data",
    )
    assert response.status_code == 202
    data = response.get_json()
    assert data is not None
    return data["document_id"]


def _document_endpoint(document_id):
    return f"/api/v1/documento/{document_id}"


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


@pytest.mark.contract
class TestListDocuments:
    """Contract tests for GET /api/v1/documentos."""

    def test_list_all_documents_for_authenticated_user(self, client):
        """The endpoint must return only documents owned by the requesting user."""
        owner_id = _create_user(client, "docs_owner@example.com", "Docs Owner")
        other_id = _create_user(client, "docs_other@example.com", "Docs Other")

        _upload_document_for_user(client, owner_id, "owner_doc_1.pdf")
        _upload_document_for_user(client, owner_id, "owner_doc_2.pdf")
        _upload_document_for_user(client, other_id, "other_doc_1.pdf")

        response = client.get(LIST_ENDPOINT, headers={"X-User-ID": str(owner_id)})

        assert response.status_code == 200
        assert response.content_type == "application/json"
        payload = response.get_json()
        assert payload is not None

        items = payload["items"] if isinstance(payload, dict) and "items" in payload else payload
        assert isinstance(items, list)
        assert len(items) >= 2
        assert all(item.get("usuario_id") == owner_id for item in items)

    def test_list_documents_supports_pagination_when_available(self, client):
        """If pagination is implemented, contract validates shape and page size."""
        user_id = _create_user(client, "docs_page@example.com", "Docs Page")
        for idx in range(3):
            _upload_document_for_user(client, user_id, f"paged_doc_{idx}.pdf")

        response = client.get(f"{LIST_ENDPOINT}?page=1&per_page=2", headers={"X-User-ID": str(user_id)})

        assert response.status_code == 200
        assert response.content_type == "application/json"
        payload = response.get_json()
        assert payload is not None

        if isinstance(payload, dict) and "items" in payload:
            assert isinstance(payload["items"], list)
            assert len(payload["items"]) <= 2
            assert any(key in payload for key in ("page", "per_page", "total", "pages", "has_next"))
        else:
            assert isinstance(payload, list)
            assert len(payload) >= 1

    def test_list_documents_returns_empty_array_for_new_user(self, client):
        """A newly created user with no uploads must receive an empty list payload."""
        new_user_id = _create_user(client, "docs_new@example.com", "Docs New")

        response = client.get(LIST_ENDPOINT, headers={"X-User-ID": str(new_user_id)})

        assert response.status_code == 200
        assert response.content_type == "application/json"
        payload = response.get_json()
        assert payload is not None

        items = payload["items"] if isinstance(payload, dict) and "items" in payload else payload
        assert isinstance(items, list)
        assert items == []


@pytest.mark.contract
class TestPatchDocumentMetadata:
    """Contract tests for PATCH /api/v1/documento/{id}."""

    def test_patch_document_updates_metadata(self, client):
        """Owner must be able to update document metadata."""
        owner_id = _create_user(client, "patch_owner@example.com", "Patch Owner")
        document_id = _upload_document_for_user(client, owner_id, "before_name.pdf")

        response = client.patch(
            _document_endpoint(document_id),
            json={"nombre_archivo": "after_name.pdf"},
            headers={"X-User-ID": str(owner_id)},
        )

        assert response.status_code == 200
        assert response.content_type == "application/json"
        payload = response.get_json()
        assert payload is not None
        assert payload["id"] == document_id
        assert payload["usuario_id"] == owner_id
        assert payload["nombre_archivo"] == "after_name.pdf"

    def test_patch_document_returns_404_when_not_found(self, client):
        """PATCH must return 404 when the document does not exist."""
        user_id = _create_user(client, "patch_not_found@example.com", "Patch Not Found")
        response = client.patch(
            _document_endpoint(999999),
            json={"nombre_archivo": "missing.pdf"},
            headers={"X-User-ID": str(user_id)},
        )

        assert response.status_code == 404
        assert response.content_type in ("application/problem+json", "application/json")

    def test_patch_document_returns_403_for_non_owner(self, client):
        """PATCH must return 403 when user tries to update foreign document."""
        owner_id = _create_user(client, "patch_doc_owner@example.com", "Patch Doc Owner")
        intruder_id = _create_user(client, "patch_intruder@example.com", "Patch Intruder")
        document_id = _upload_document_for_user(client, owner_id, "owner_only.pdf")

        response = client.patch(
            _document_endpoint(document_id),
            json={"nombre_archivo": "hacked_name.pdf"},
            headers={"X-User-ID": str(intruder_id)},
        )

        assert response.status_code == 403
        assert response.content_type in ("application/problem+json", "application/json")


@pytest.mark.contract
class TestDeleteDocument:
    """Contract tests for DELETE /api/v1/documento/{id}."""

    def test_delete_document_success(self, client):
        """Owner DELETE removes document; list and status endpoints reflect removal."""
        owner_id = _create_user(client, "del_doc_owner@example.com", "Del Doc Owner")
        document_id = _upload_document_for_user(client, owner_id, "to_delete.pdf")

        resp = client.delete(
            _document_endpoint(document_id),
            headers={"X-User-ID": str(owner_id)},
        )

        assert resp.status_code in (200, 204)

        list_resp = client.get(LIST_ENDPOINT, headers={"X-User-ID": str(owner_id)})
        assert list_resp.status_code == 200
        payload = list_resp.get_json()
        assert payload is not None
        items = payload["items"] if isinstance(payload, dict) and "items" in payload else payload
        ids = [item["id"] for item in items]
        assert document_id not in ids

        status_resp = client.get(f"{_document_endpoint(document_id)}/status")
        assert status_resp.status_code == 404

    def test_delete_document_cascades_summaries(self, client, app):
        """DELETE removes linked summaries (verified via GET /api/v1/summaries/document/{id})."""
        owner_id = _create_user(client, "del_cascade@example.com", "Del Cascade")
        document_id = _upload_document_for_user(client, owner_id, "cascade.pdf")

        with app.app_context():
            summary = Summary(
                document_id=document_id,
                summary_text="Resumen ligado al documento.",
                status="completed",
                user_id=owner_id,
                created_at=datetime(2026, 5, 1, 12, 0, 0),
                updated_at=datetime(2026, 5, 1, 12, 0, 0),
            )
            db.session.add(summary)
            db.session.commit()

        sum_resp = client.get(f"/api/v1/summaries/document/{document_id}")
        assert sum_resp.status_code == 200

        del_resp = client.delete(
            _document_endpoint(document_id),
            headers={"X-User-ID": str(owner_id)},
        )
        assert del_resp.status_code in (200, 204)

        sum_after = client.get(f"/api/v1/summaries/document/{document_id}")
        assert sum_after.status_code == 404
        assert sum_after.content_type == "application/problem+json"

    def test_delete_document_returns_404_when_not_found(self, client):
        """DELETE for a non-existent document returns 404 RFC 9457 problem detail."""
        user_id = _create_user(client, "del_nf@example.com", "Del Not Found")
        endpoint = _document_endpoint(999999)
        resp = client.delete(
            endpoint,
            headers={"X-User-ID": str(user_id)},
        )

        assert resp.status_code == 404
        assert resp.content_type == "application/problem+json"
        data = resp.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert data["instance"] == endpoint

