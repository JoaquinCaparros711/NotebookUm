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


@pytest.mark.contract
class TestGetQuestions:
    """Contract tests for GET /api/v1/preguntas (listing and filtering)."""

    def test_list_questions_for_user(self, client):
        """Listing questions for a user returns only their questions."""
        # Arrange: create two users and two documents
        u1 = client.post("/api/v1/users", json={"email": "list_user1@example.com", "nombre": "List One"})
        assert u1.status_code == 201
        user1_id = u1.get_json()["id"]

        u2 = client.post("/api/v1/users", json={"email": "list_user2@example.com", "nombre": "List Two"})
        assert u2.status_code == 201
        user2_id = u2.get_json()["id"]

        # upload two documents
        file_data1 = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "list_doc1.pdf",
                "application/pdf",
            )
        }
        d1 = client.post("/api/v1/documento/upload", data=file_data1, content_type="multipart/form-data")
        assert d1.status_code == 202
        doc1_id = d1.get_json()["document_id"]

        file_data2 = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "list_doc2.pdf",
                "application/pdf",
            )
        }
        d2 = client.post("/api/v1/documento/upload", data=file_data2, content_type="multipart/form-data")
        assert d2.status_code == 202
        doc2_id = d2.get_json()["document_id"]

        # Create questions: two for user1 (one per document), one for user2
        q1 = client.post(QUESTIONS_ENDPOINT, json={"user_id": user1_id, "document_id": doc1_id, "pregunta": "Pregunta A"})
        assert q1.status_code == 201
        q2 = client.post(QUESTIONS_ENDPOINT, json={"user_id": user1_id, "document_id": doc2_id, "pregunta": "Pregunta B"})
        assert q2.status_code == 201
        q3 = client.post(QUESTIONS_ENDPOINT, json={"user_id": user2_id, "document_id": doc1_id, "pregunta": "Otra pregunta"})
        assert q3.status_code == 201

        # Act: List questions as user1 using X-User-ID header (mock auth)
        resp = client.get(QUESTIONS_ENDPOINT, headers={"X-User-ID": str(user1_id)})

        # Assert
        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert isinstance(data, list)
        # should contain only the two questions created by user1
        assert any(q.get("pregunta") == "Pregunta A" for q in data)
        assert any(q.get("pregunta") == "Pregunta B" for q in data)
        assert all(q.get("user_id") == user1_id for q in data)

    def test_filter_questions_by_document_id(self, client):
        """Filtering questions by document_id returns only questions for that document."""
        # Arrange: create a user and two documents
        u = client.post("/api/v1/users", json={"email": "filter_user@example.com", "nombre": "Filter User"})
        assert u.status_code == 201
        user_id = u.get_json()["id"]

        file_data1 = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "filter_doc1.pdf",
                "application/pdf",
            )
        }
        d1 = client.post("/api/v1/documento/upload", data=file_data1, content_type="multipart/form-data")
        assert d1.status_code == 202
        doc1_id = d1.get_json()["document_id"]

        file_data2 = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "filter_doc2.pdf",
                "application/pdf",
            )
        }
        d2 = client.post("/api/v1/documento/upload", data=file_data2, content_type="multipart/form-data")
        assert d2.status_code == 202
        doc2_id = d2.get_json()["document_id"]

        # Create questions for both documents
        q1 = client.post(QUESTIONS_ENDPOINT, json={"user_id": user_id, "document_id": doc1_id, "pregunta": "Doc1 pregunta"})
        assert q1.status_code == 201
        q2 = client.post(QUESTIONS_ENDPOINT, json={"user_id": user_id, "document_id": doc2_id, "pregunta": "Doc2 pregunta"})
        assert q2.status_code == 201

        # Act: Filter by document_id for doc1
        resp = client.get(f"{QUESTIONS_ENDPOINT}?document_id={doc1_id}", headers={"X-User-ID": str(user_id)})

        # Assert: only the question for doc1 is returned
        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(q.get("document_id") == doc1_id for q in data)


@pytest.mark.contract
class TestPatchQuestion:
    """Contract tests for PATCH /api/v1/pregunta/{id} (update pregunta/respuesta)."""

    def test_update_question_and_answer_success(self, client):
        """PATCH updates pregunta and respuesta and returns 200 with updated resource."""
        # Arrange: create user, upload document and create question
        u = client.post("/api/v1/users", json={"email": "patch_user@example.com", "nombre": "Patch User"})
        assert u.status_code == 201
        user_id = u.get_json()["id"]

        file_data = {
            "file": (
                io.BytesIO(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"),
                "patch_doc.pdf",
                "application/pdf",
            )
        }
        d = client.post("/api/v1/documento/upload", data=file_data, content_type="multipart/form-data")
        assert d.status_code == 202
        document_id = d.get_json()["document_id"]

        q = client.post(QUESTIONS_ENDPOINT, json={"user_id": user_id, "document_id": document_id, "pregunta": "Pregunta inicial"})
        assert q.status_code == 201
        question = q.get_json()
        question_id = question["id"]

        # Act: Patch the question to update pregunta and respuesta
        patch_payload = {"pregunta": "Pregunta actualizada", "respuesta": "Respuesta generada"}
        resp = client.patch(f"/api/v1/pregunta/{question_id}", json=patch_payload)

        # Assert: 200 OK and fields updated
        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert data is not None
        assert data.get("id") == question_id
        assert data.get("pregunta") == "Pregunta actualizada"
        assert data.get("respuesta") == "Respuesta generada"
        assert data.get("user_id") == user_id
        assert data.get("document_id") == document_id
        assert "updated_at" in data

    def test_update_nonexistent_question_returns_404(self, client):
        """PATCH to a non-existent question id returns 404 RFC 9457 problem detail."""
        # Act: attempt to patch a non-existent question
        resp = client.patch("/api/v1/pregunta/999999", json={"pregunta": "x"})

        # Assert: 404 Not Found with problem details
        assert resp.status_code == 404
        assert resp.content_type == "application/problem+json"
        data = resp.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert data["instance"] == "/api/v1/pregunta/999999"
