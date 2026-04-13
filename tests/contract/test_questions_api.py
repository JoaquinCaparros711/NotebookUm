"""Contract tests for POST /api/v1/preguntas endpoint."""

import io

import pytest

from app import create_app
from app.database import db


QUESTIONS_ENDPOINT = "/api/v1/preguntas"


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
class TestPostQuestions:
    """Contract tests for POST /api/v1/preguntas."""

    def test_create_question_success(self, client):
        """Creating a question with valid payload returns 201 and question data."""
        # Given: A created user
        user_payload = {"email": "qtest@example.com", "nombre": "Question Tester"}
        user_resp = client.post("/api/v1/users", json=user_payload)
        assert user_resp.status_code == 201
        user = user_resp.get_json()
        user_id = user["id"]

        # And: An uploaded document
        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "doc_for_question.pdf",
                "application/pdf",
            )
        }
        doc_resp = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
        )
        assert doc_resp.status_code == 202
        doc_data = doc_resp.get_json()
        assert doc_data is not None
        assert "document_id" in doc_data
        document_id = doc_data["document_id"]

        # When: Posting a valid question
        question_payload = {
            "user_id": user_id,
            "document_id": document_id,
            "pregunta": "¿Cuál es el propósito principal del documento?",
        }
        resp = client.post(QUESTIONS_ENDPOINT, json=question_payload)

        # Then: Returns 201 Created
        assert resp.status_code == 201
        data = resp.get_json()
        assert data is not None
        assert "id" in data
        assert data.get("pregunta") == question_payload["pregunta"]
        # Optional fields: respuesta may be present or empty; created_at should exist
        assert "created_at" in data
        assert data.get("document_id") == document_id
        assert data.get("user_id") == user_id

    def test_create_question_missing_pregunta_returns_400(self, client):
        """Missing 'pregunta' field must return a 400 RFC9457 problem detail."""
        # Given: A created user and uploaded document
        user_payload = {"email": "qval@example.com", "nombre": "Q Validator"}
        user_resp = client.post("/api/v1/users", json=user_payload)
        assert user_resp.status_code == 201
        user_id = user_resp.get_json()["id"]

        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "doc_for_qval.pdf",
                "application/pdf",
            )
        }
        doc_resp = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
        )
        assert doc_resp.status_code == 202
        document_id = doc_resp.get_json()["document_id"]

        # When: Posting a question without 'pregunta'
        invalid_payload = {"user_id": user_id, "document_id": document_id}
        resp = client.post(QUESTIONS_ENDPOINT, json=invalid_payload)

        # Then: Returns 400 Bad Request with RFC 9457 problem details
        assert resp.status_code == 400
        assert resp.content_type == "application/problem+json"
        data = resp.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "pregunta" in data["detail"].lower()
        assert data["instance"] == QUESTIONS_ENDPOINT
