"""Contract tests for POST /api/v1/preguntas endpoint."""

import io

import pytest

from app import create_app
from app.database import db


QUESTIONS_ENDPOINT = "/api/v1/preguntas"
QUESTION_DETAIL_ENDPOINT = "/api/v1/pregunta"
USERS_ENDPOINT = "/api/v1/users"
DOCUMENT_UPLOAD_ENDPOINT = "/api/v1/documento/upload"
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


def _pdf_upload_data(filename):
    return {"file": (io.BytesIO(PDF_BYTES), filename, "application/pdf")}


def _create_user(client, email, nombre):
    response = client.post(USERS_ENDPOINT, json={"email": email, "nombre": nombre})
    assert response.status_code == 201
    data = response.get_json()
    assert data is not None
    return data["id"]


def _upload_document(client, filename):
    response = client.post(
        DOCUMENT_UPLOAD_ENDPOINT,
        data=_pdf_upload_data(filename),
        content_type="multipart/form-data",
    )
    assert response.status_code == 202
    data = response.get_json()
    assert data is not None
    return data["document_id"]


def _create_question(client, user_id, document_id, pregunta):
    response = client.post(
        QUESTIONS_ENDPOINT,
        json={
            "user_id": user_id,
            "document_id": document_id,
            "pregunta": pregunta,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data is not None
    return data


def _assert_problem_details(response, expected_status, expected_title, expected_instance):
    assert response.status_code == expected_status
    assert response.content_type == "application/problem+json"
    data = response.get_json()
    assert data is not None
    assert data["type"] == "about:blank"
    assert data["title"] == expected_title
    assert data["status"] == expected_status
    assert data["instance"] == expected_instance
    return data


@pytest.mark.contract
class TestPostQuestions:
    """Contract tests for POST /api/v1/preguntas."""

    def test_create_question_success(self, client):
        """Creating a question with valid payload returns 201 and question data."""
        user_id = _create_user(client, "qtest@example.com", "Question Tester")
        document_id = _upload_document(client, "doc_for_question.pdf")

        question_payload = {
            "user_id": user_id,
            "document_id": document_id,
            "pregunta": "¿Cuál es el propósito principal del documento?",
        }
        resp = client.post(QUESTIONS_ENDPOINT, json=question_payload)

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
        user_id = _create_user(client, "qval@example.com", "Q Validator")
        document_id = _upload_document(client, "doc_for_qval.pdf")

        invalid_payload = {"user_id": user_id, "document_id": document_id}
        resp = client.post(QUESTIONS_ENDPOINT, json=invalid_payload)

        data = _assert_problem_details(resp, 400, "Bad Request", QUESTIONS_ENDPOINT)
        assert "pregunta" in data["detail"].lower()


@pytest.mark.contract
class TestGetQuestions:
    """Contract tests for GET /api/v1/preguntas (listing and filtering)."""

    def test_list_questions_for_user(self, client):
        """Listing questions for a user returns only their questions."""
        user1_id = _create_user(client, "list_user1@example.com", "List One")
        user2_id = _create_user(client, "list_user2@example.com", "List Two")
        doc1_id = _upload_document(client, "list_doc1.pdf")
        doc2_id = _upload_document(client, "list_doc2.pdf")

        _create_question(client, user1_id, doc1_id, "Pregunta A")
        _create_question(client, user1_id, doc2_id, "Pregunta B")
        _create_question(client, user2_id, doc1_id, "Otra pregunta")

        resp = client.get(QUESTIONS_ENDPOINT, headers={"X-User-ID": str(user1_id)})

        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert isinstance(data, list)
        assert any(q.get("pregunta") == "Pregunta A" for q in data)
        assert any(q.get("pregunta") == "Pregunta B" for q in data)
        assert all(q.get("user_id") == user1_id for q in data)

    def test_filter_questions_by_document_id(self, client):
        """Filtering questions by document_id returns only questions for that document."""
        user_id = _create_user(client, "filter_user@example.com", "Filter User")
        doc1_id = _upload_document(client, "filter_doc1.pdf")
        doc2_id = _upload_document(client, "filter_doc2.pdf")

        _create_question(client, user_id, doc1_id, "Doc1 pregunta")
        _create_question(client, user_id, doc2_id, "Doc2 pregunta")

        resp = client.get(f"{QUESTIONS_ENDPOINT}?document_id={doc1_id}", headers={"X-User-ID": str(user_id)})

        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert all(q.get("document_id") == doc1_id for q in data)


@pytest.mark.contract
class TestPatchQuestion:
    """Contract tests for PATCH /api/v1/pregunta/<id> (update question)."""

    def test_update_question_pregunta_success(self, client):
        """Updating a question's pregunta field returns 200 and updated data."""
        user_id = _create_user(client, "patch_user@example.com", "Patch User")
        doc_id = _upload_document(client, "patch_doc.pdf")
        created = _create_question(client, user_id, doc_id, "Original pregunta")
        question_id = created["id"]

        update_payload = {"pregunta": "Updated pregunta text"}
        resp = client.patch(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}", json=update_payload)

        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert data["id"] == question_id
        assert data["pregunta"] == "Updated pregunta text"

    def test_update_question_respuesta_success(self, client):
        """Updating a question's respuesta field returns 200 and updated data."""
        user_id = _create_user(client, "patch_resp@example.com", "Patch Resp User")
        doc_id = _upload_document(client, "patch_resp_doc.pdf")
        created = _create_question(client, user_id, doc_id, "Una pregunta")
        question_id = created["id"]

        update_payload = {"respuesta": "Esta es la respuesta"}
        resp = client.patch(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}", json=update_payload)

        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert data["respuesta"] == "Esta es la respuesta"

    def test_update_question_not_found_returns_404(self, client):
        """Updating a non-existent question returns 404 RFC9457 problem detail."""
        invalid_id = 99999
        resp = client.patch(f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}", json={"pregunta": "New text"})

        data = _assert_problem_details(resp, 404, "Not Found", f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}")
        assert "not found" in data["detail"].lower()


@pytest.mark.contract
class TestGetQuestionDetail:
    """Contract tests for GET /api/v1/pregunta/<id> (retrieve single question)."""

    def test_get_question_success(self, client):
        """Retrieving an existing question returns 200 and question data."""
        user_id = _create_user(client, "get_user@example.com", "Get User")
        doc_id = _upload_document(client, "get_doc.pdf")
        created = _create_question(client, user_id, doc_id, "Get pregunta")
        question_id = created["id"]

        resp = client.get(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")

        assert resp.status_code == 200
        assert resp.content_type == "application/json"
        data = resp.get_json()
        assert data is not None
        assert data["id"] == question_id
        assert data["pregunta"] == "Get pregunta"
        assert data["user_id"] == user_id
        assert data["document_id"] == doc_id

    def test_get_question_not_found_returns_404(self, client):
        """Retrieving a non-existent question returns 404 RFC9457 problem detail."""
        invalid_id = 99999
        resp = client.get(f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}")

        data = _assert_problem_details(resp, 404, "Not Found", f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}")
        assert "not found" in data["detail"].lower()


@pytest.mark.contract
class TestDeleteQuestion:
    """Contract tests for DELETE /api/v1/pregunta/<id> (delete question)."""

    def test_delete_question_success(self, client):
        """Deleting an existing question returns 204 (No Content)."""
        user_id = _create_user(client, "delete_user@example.com", "Delete User")
        doc_id = _upload_document(client, "delete_doc.pdf")
        created = _create_question(client, user_id, doc_id, "Question to delete")
        question_id = created["id"]

        # Verify the question exists
        resp = client.get(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")
        assert resp.status_code == 200

        # Delete the question
        delete_resp = client.delete(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")
        assert delete_resp.status_code == 204

        # Verify it's gone
        check_resp = client.get(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")
        assert check_resp.status_code == 404

    def test_delete_question_not_found_returns_404(self, client):
        """Deleting a non-existent question returns 404 RFC9457 problem detail."""
        invalid_id = 99999
        resp = client.delete(f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}")

        data = _assert_problem_details(resp, 404, "Not Found", f"{QUESTION_DETAIL_ENDPOINT}/{invalid_id}")
        assert "not found" in data["detail"].lower()
    """Contract tests for PATCH /api/v1/pregunta/{id} (update pregunta/respuesta)."""

    def test_update_question_and_answer_success(self, client):
        """PATCH updates pregunta and respuesta and returns 200 with updated resource."""
        user_id = _create_user(client, "patch_user@example.com", "Patch User")
        document_id = _upload_document(client, "patch_doc.pdf")
        question = _create_question(client, user_id, document_id, "Pregunta inicial")
        question_id = question["id"]

        patch_payload = {"pregunta": "Pregunta actualizada", "respuesta": "Respuesta generada"}
        resp = client.patch(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}", json=patch_payload)

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
        resp = client.patch(f"{QUESTION_DETAIL_ENDPOINT}/999999", json={"pregunta": "x"})

        _assert_problem_details(resp, 404, "Not Found", f"{QUESTION_DETAIL_ENDPOINT}/999999")


@pytest.mark.contract
class TestDeleteQuestion:
    """Contract tests for DELETE /api/v1/pregunta/{id} (deletion)."""

    def test_delete_question_success(self, client):
        """DELETE removes the question and returns 204 No Content."""
        user_id = _create_user(client, "del_user@example.com", "Del User")
        document_id = _upload_document(client, "del_doc.pdf")
        question = _create_question(client, user_id, document_id, "Pregunta a eliminar")
        question_id = question["id"]

        resp = client.delete(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")

        assert resp.status_code in (200, 204)

        get_resp = client.get(f"{QUESTION_DETAIL_ENDPOINT}/{question_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_question_returns_404(self, client):
        """DELETE to a non-existent question returns 404 RFC 9457 problem detail."""
        resp = client.delete(f"{QUESTION_DETAIL_ENDPOINT}/999999")

        _assert_problem_details(resp, 404, "Not Found", f"{QUESTION_DETAIL_ENDPOINT}/999999")
