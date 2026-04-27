"""Contract tests for /api/v1/summaries endpoints"""

import pytest
from datetime import datetime
from app import create_app
from app.database import db
from app.models.summary import Summary


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app("testing")

    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        from app.models.summary import Summary  # noqa: F401

        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


def create_summary(app, **kwargs):
    """Helper to create a summary in the database"""
    with app.app_context():
        summary = Summary(**kwargs)
        db.session.add(summary)
        db.session.commit()
        return summary.id


class TestGetDocumentSummary:
    """Contract tests for GET /api/v1/summaries/document/{document_id}"""

    @pytest.mark.contract
    def test_successful_retrieval(self, client, app):
        """Test successful retrieval of document summary returns 200 with complete JSON"""
        # Arrange: Create a completed summary in the database
        summary_id = create_summary(
            app,
            id=1,
            document_id=100,
            summary_text="This is a test summary of the document content.",
            status="completed",
            created_at=datetime(2026, 4, 7, 10, 0, 0),
            updated_at=datetime(2026, 4, 7, 10, 30, 0),
        )

        # Act: Request the summary via GET endpoint
        response = client.get("/api/v1/summaries/document/100")

        # Assert: Response is 200 with complete summary data
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert data["id"] == summary_id
        assert data["document_id"] == 100
        assert data["summary_text"] == "This is a test summary of the document content."
        assert data["status"] == "completed"
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.contract
    def test_not_found_for_nonexistent_document(self, client):
        """Test GET request with non-existent document_id returns 404 Not Found"""
        # Act: Request summary for document that doesn't exist
        response = client.get("/api/v1/summaries/document/99999")

        # Assert: Response is 404 with RFC 9457 error format
        assert response.status_code == 404
        assert response.content_type == "application/problem+json"

        data = response.get_json()
        assert data["type"] == "about:blank"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert "document 99999 not found" in data["detail"].lower()
        assert data["instance"] == "/api/v1/summaries/document/99999"

    @pytest.mark.contract
    def test_forbidden_for_unauthorized_access(self, client, app):
        """Test GET request from user without access returns 403 Forbidden"""
        # Arrange: Create user 1, their document, and the linked summary
        with app.app_context():
            from app.models.user import User
            from app.models.document import HistorialDocumento

            user = User(id=1, email="owner@example.com", nombre="Owner")
            db.session.add(user)
            db.session.flush()

            doc = HistorialDocumento(
                id=200,
                usuario_id=user.id,
                nombre_archivo="private.pdf",
                tamanio_bytes=1024,
                estado="completed",
            )
            db.session.add(doc)
            db.session.flush()

            from app.models.summary import Summary
            from datetime import datetime

            summary = Summary(
                id=2,
                document_id=200,
                summary_text="Private document summary.",
                status="completed",
                user_id=user.id,
                created_at=datetime(2026, 4, 7, 12, 0, 0),
                updated_at=datetime(2026, 4, 7, 12, 30, 0),
            )
            db.session.add(summary)
            db.session.commit()

        # Act: Request summary as different user (user 2) via mocked auth
        response = client.get(
            "/api/v1/summaries/document/200",
            headers={"X-User-ID": "2"},  # Mock authentication as user 2
        )

        # Assert: Response is 403 Forbidden
        assert response.status_code == 403
        assert response.content_type == "application/problem+json"

        data = response.get_json()
        assert data["type"] == "about:blank"
        assert data["title"] == "Forbidden"
        assert data["status"] == 403
        assert (
            "access denied" in data["detail"].lower() or "not authorized" in data["detail"].lower()
        )

    @pytest.mark.contract
    def test_pending_status_for_processing_document(self, client, app):
        """Test GET request for document still processing returns 200 with status=pending"""
        # Arrange: Create a summary with pending status
        create_summary(
            app,
            id=3,
            document_id=300,
            summary_text="",  # Empty while processing
            status="pending",  # Still being processed
            created_at=datetime(2026, 4, 7, 14, 0, 0),
            updated_at=datetime(2026, 4, 7, 14, 0, 0),
        )

        # Act: Request the pending summary
        response = client.get("/api/v1/summaries/document/300")

        # Assert: Response is 200 with status='pending'
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert data["document_id"] == 300
        assert data["status"] == "pending"
        assert data["summary_text"] == ""  # Empty while processing
        assert "created_at" in data
        assert "updated_at" in data
