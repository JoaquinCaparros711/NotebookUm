"""Integration tests for complete summary retrieval workflow."""

from io import BytesIO

import pytest

from app import create_app
from app.database import db
from app.models.document import HistorialDocumento
from app.models.summary import Summary
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    flask_app = create_app("testing")
    flask_app.config["CELERY_TASK_ALWAYS_EAGER"] = True
    flask_app.config["CELERY_TASK_EAGER_PROPAGATES"] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def valid_pdf_bytes():
    """Create valid minimal PDF bytes for testing."""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(email="test@example.com", nombre="Test User")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.mark.integration
class TestSummaryRetrievalWorkflow:
    """Integration tests for complete document upload → process → retrieve flow."""

    def test_complete_flow_upload_process_retrieve(self, client, app, test_user, valid_pdf_bytes):
        """Test complete workflow: upload PDF → async process → retrieve summary."""
        # Arrange: Prepare PDF file data
        pdf_file = (BytesIO(valid_pdf_bytes), "sample.pdf", "application/pdf")
        file_data = {"file": pdf_file}

        # Act 1: Upload document
        upload_response = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
            headers={"X-User-ID": str(test_user)},
        )

        # Assert 1: Upload returns 202 Accepted with document_id
        assert upload_response.status_code == 202
        assert upload_response.content_type == "application/json"

        upload_data = upload_response.get_json()
        assert "document_id" in upload_data
        assert upload_data["status"] == "pending"
        assert "job_id" in upload_data
        assert "status_url" in upload_data

        document_id = upload_data["document_id"]

        # Act 2: Check document status after processing
        with app.app_context():
            db.session.expire_all()
            document = db.session.get(HistorialDocumento, document_id)
            summary = Summary.query.filter_by(document_id=document_id).first()

        # Assert 2: Document processing completed and summary created
        assert document is not None
        assert document.estado == "completed"
        assert summary is not None
        assert summary.document_id == document_id
        assert summary.status == "completed"
        assert len(summary.summary_text) > 0

        # Act 3: Retrieve summary via GET endpoint
        retrieve_response = client.get(
            f"/api/v1/summaries/document/{document_id}",
            headers={"X-User-ID": str(test_user)},
        )

        # Assert 3: Summary retrieval returns 200 with complete data
        assert retrieve_response.status_code == 200
        assert retrieve_response.content_type == "application/json"

        summary_data = retrieve_response.get_json()
        assert summary_data["document_id"] == document_id
        assert summary_data["status"] == "completed"
        assert len(summary_data["summary_text"]) > 0
        assert "created_at" in summary_data
        assert "updated_at" in summary_data

    def test_flow_with_status_polling(self, client, app, test_user, valid_pdf_bytes):
        """Test upload → poll status endpoint → retrieve summary."""
        # Arrange: Prepare PDF file data
        pdf_file = (BytesIO(valid_pdf_bytes), "document.pdf", "application/pdf")
        file_data = {"file": pdf_file}

        # Act 1: Upload document
        upload_response = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
            headers={"X-User-ID": str(test_user)},
        )

        assert upload_response.status_code == 202
        upload_data = upload_response.get_json()
        document_id = upload_data["document_id"]
        status_url = upload_data["status_url"]

        # Act 2: Poll document status endpoint
        status_response = client.get(
            status_url,
            headers={"X-User-ID": str(test_user)},
        )

        # Assert 2: Status endpoint returns document state
        assert status_response.status_code == 200
        status_data = status_response.get_json()
        assert status_data["document_id"] == document_id
        assert status_data["status"] == "completed"

        # Act 3: Retrieve summary after confirming completion
        retrieve_response = client.get(
            f"/api/v1/summaries/document/{document_id}",
            headers={"X-User-ID": str(test_user)},
        )

        # Assert 3: Summary available with proper fields
        assert retrieve_response.status_code == 200
        summary_data = retrieve_response.get_json()
        assert summary_data["id"] is not None
        assert summary_data["summary_text"] is not None

    def test_flow_with_multiple_documents_same_user(self, client, app, test_user, valid_pdf_bytes):
        """Test multiple document uploads and separate summary retrieval."""
        document_ids = []

        # Act: Upload 3 documents
        for i in range(3):
            pdf_file = (
                BytesIO(valid_pdf_bytes),
                f"document_{i}.pdf",
                "application/pdf",
            )
            file_data = {"file": pdf_file}

            response = client.post(
                "/api/v1/documento/upload",
                data=file_data,
                content_type="multipart/form-data",
                headers={"X-User-ID": str(test_user)},
            )

            assert response.status_code == 202
            document_ids.append(response.get_json()["document_id"])

        # Assert: All summaries retrieved correctly
        for document_id in document_ids:
            retrieve_response = client.get(
                f"/api/v1/summaries/document/{document_id}",
                headers={"X-User-ID": str(test_user)},
            )

            assert retrieve_response.status_code == 200
            summary_data = retrieve_response.get_json()
            assert summary_data["document_id"] == document_id
            assert summary_data["status"] == "completed"

    def test_flow_respects_user_isolation(self, client, app, valid_pdf_bytes):
        """Test that document upload and summary retrieval respect user boundaries."""
        # Arrange: Create 2 users
        with app.app_context():
            user1 = User(email="user1@example.com", nombre="User One")
            user2 = User(email="user2@example.com", nombre="User Two")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            user1_id = user1.id
            user2_id = user2.id

        # Act 1: User1 uploads document
        pdf_file = (BytesIO(valid_pdf_bytes), "private.pdf", "application/pdf")
        file_data = {"file": pdf_file}

        upload_response = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
            headers={"X-User-ID": str(user1_id)},
        )

        assert upload_response.status_code == 202
        document_id = upload_response.get_json()["document_id"]

        # Act 2: User1 retrieves their own summary (should succeed)
        user1_retrieve = client.get(
            f"/api/v1/summaries/document/{document_id}",
            headers={"X-User-ID": str(user1_id)},
        )

        # Assert 2: User1 can access their document
        assert user1_retrieve.status_code == 200
        assert user1_retrieve.get_json()["document_id"] == document_id

        # Act 3: User2 tries to retrieve User1's summary
        user2_retrieve = client.get(
            f"/api/v1/summaries/document/{document_id}",
            headers={"X-User-ID": str(user2_id)},
        )

        # Assert 3: User2 is forbidden
        assert user2_retrieve.status_code == 403

    def test_flow_document_retrieval_with_extracted_text(
        self, client, app, test_user, valid_pdf_bytes
    ):
        """Test that document extracted text is available after processing."""
        # Arrange: Prepare PDF file
        pdf_file = (BytesIO(valid_pdf_bytes), "extract_test.pdf", "application/pdf")
        file_data = {"file": pdf_file}

        # Act 1: Upload document
        upload_response = client.post(
            "/api/v1/documento/upload",
            data=file_data,
            content_type="multipart/form-data",
            headers={"X-User-ID": str(test_user)},
        )

        document_id = upload_response.get_json()["document_id"]

        # Act 2: Verify extracted text in database
        with app.app_context():
            db.session.expire_all()
            document = db.session.get(HistorialDocumento, document_id)

        # Assert 2: Document has extracted text (from PDF service)
        assert document is not None
        assert document.extracto_texto is not None
        assert len(document.extracto_texto) >= 0

        # Act 3: Retrieve summary and verify linked to extracted document
        retrieve_response = client.get(
            f"/api/v1/summaries/document/{document_id}",
            headers={"X-User-ID": str(test_user)},
        )

        # Assert 3: Summary successfully created from extracted text
        assert retrieve_response.status_code == 200
        summary_data = retrieve_response.get_json()
        assert summary_data["status"] == "completed"
