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
        """Test GET for pending document returns 200 with 'message' field."""
        # Arrange: Create a summary with pending status
        create_summary(
            app,
            id=3,
            document_id=300,
            summary_text="",
            status="pending",
            created_at=datetime(2026, 4, 7, 14, 0, 0),
            updated_at=datetime(2026, 4, 7, 14, 0, 0),
        )

        # Act: Request the pending summary
        response = client.get("/api/v1/summaries/document/300")

        # Assert: 200 with status-aware message
        assert response.status_code == 200
        assert response.content_type == "application/json"

        data = response.get_json()
        assert data["document_id"] == 300
        assert data["status"] == "pending"
        assert data["summary_text"] == ""
        assert "created_at" in data
        assert "updated_at" in data
        # State-aware: message must be present and non-empty for non-completed
        assert "message" in data
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0

    @pytest.mark.contract
    def test_processing_status_includes_message(self, client, app):
        """Test GET for 'processing' document returns 200 with a message field."""
        # Arrange: Create a summary actively being processed
        create_summary(
            app,
            id=4,
            document_id=400,
            summary_text="",
            status="processing",
            created_at=datetime(2026, 4, 7, 15, 0, 0),
            updated_at=datetime(2026, 4, 7, 15, 0, 0),
        )

        # Act
        response = client.get("/api/v1/summaries/document/400")

        # Assert: 200 with a non-empty message
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "processing"
        assert "message" in data
        assert len(data["message"]) > 0

    @pytest.mark.contract
    def test_failed_status_includes_distinct_message(self, client, app):
        """Test GET for a failed summary returns 200 with a failure-specific message."""
        # Arrange: Create a failed summary
        create_summary(
            app,
            id=5,
            document_id=500,
            summary_text="",
            status="failed",
            created_at=datetime(2026, 4, 7, 16, 0, 0),
            updated_at=datetime(2026, 4, 7, 16, 0, 0),
        )

        # Act
        response = client.get("/api/v1/summaries/document/500")

        # Assert: 200 with failure message (not the same as pending message)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "failed"
        assert "message" in data
        assert len(data["message"]) > 0

    @pytest.mark.contract
    def test_completed_status_has_no_message(self, client, app):
        """Test completed summaries do NOT include a 'message' field in the response."""
        # Arrange: Create a completed summary (already covered by test_successful_retrieval,
        # but this makes the absence of 'message' explicit)
        create_summary(
            app,
            id=6,
            document_id=600,
            summary_text="Full summary text here.",
            status="completed",
            created_at=datetime(2026, 4, 7, 17, 0, 0),
            updated_at=datetime(2026, 4, 7, 17, 0, 0),
        )

        # Act
        response = client.get("/api/v1/summaries/document/600")

        # Assert: 200 WITHOUT a 'message' field
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "completed"
        assert "message" not in data


class TestSummaryErrorHandling:
    """Contract tests verifying comprehensive RFC 9457 error handling.

    Covers: 400 (bad header), 403 (unauthorized), 404 (not found),
    500 (service failure) — all with correct content-type and shape.
    """

    @pytest.mark.contract
    def test_404_has_rfc9457_shape_with_instance(self, client):
        """Test 404 response includes type, title, status, detail, instance."""
        # Act
        response = client.get("/api/v1/summaries/document/99999")

        # Assert: Full RFC 9457 shape present
        assert response.status_code == 404
        assert response.content_type == "application/problem+json"
        data = response.get_json()
        assert data["type"] == "about:blank"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert "detail" in data and len(data["detail"]) > 0
        assert data["instance"] == "/api/v1/summaries/document/99999"

    @pytest.mark.contract
    def test_400_for_invalid_user_id_header(self, client, app):
        """Test non-integer X-User-ID returns 400 Bad Request (RFC 9457)."""
        # Arrange: Valid summary exists
        create_summary(
            app,
            id=10,
            document_id=1000,
            summary_text="Some text",
            status="completed",
            created_at=datetime(2026, 4, 7, 10, 0, 0),
            updated_at=datetime(2026, 4, 7, 10, 0, 0),
        )

        # Act: Send non-integer user ID
        response = client.get(
            "/api/v1/summaries/document/1000",
            headers={"X-User-ID": "not-a-number"},
        )

        # Assert: RFC 9457 400 with clear detail and correct instance
        assert response.status_code == 400
        assert response.content_type == "application/problem+json"
        data = response.get_json()
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "integer" in data["detail"].lower()
        assert data["instance"] == "/api/v1/summaries/document/1000"

    @pytest.mark.contract
    def test_403_has_rfc9457_shape_with_instance(self, client, app):
        """Test 403 response contains 'instance' pointing to the endpoint."""
        # Arrange: Document owned by user 1
        with app.app_context():
            from app.models.user import User
            from app.models.document import HistorialDocumento

            user = User(id=11, email="owner2@example.com", nombre="Owner2")
            db.session.add(user)
            db.session.flush()
            doc = HistorialDocumento(
                id=1100, usuario_id=user.id,
                nombre_archivo="doc.pdf", tamanio_bytes=512, estado="completed",
            )
            db.session.add(doc)
            db.session.flush()
            summary = Summary(
                id=11, document_id=1100,
                summary_text="Private", status="completed",
                user_id=user.id,
                created_at=datetime(2026, 4, 7, 10, 0, 0),
                updated_at=datetime(2026, 4, 7, 10, 0, 0),
            )
            db.session.add(summary)
            db.session.commit()

        # Act: Different user requests
        response = client.get(
            "/api/v1/summaries/document/1100",
            headers={"X-User-ID": "99"},
        )

        # Assert: 403 with full RFC 9457 shape
        assert response.status_code == 403
        assert response.content_type == "application/problem+json"
        data = response.get_json()
        assert data["type"] == "about:blank"
        assert data["title"] == "Forbidden"
        assert data["status"] == 403
        assert "detail" in data and len(data["detail"]) > 0
        assert data["instance"] == "/api/v1/summaries/document/1100"

    @pytest.mark.contract
    def test_500_on_db_failure_returns_rfc9457(self, client, monkeypatch):
        """Test that an unhandled DB exception returns 500 RFC 9457 (not HTML)."""
        # Arrange: Simulate DB failure by patching SummaryService method
        from app.services.summary_service import SummaryService

        def raise_db_error(document_id):
            raise RuntimeError("Simulated DB connection failure")

        monkeypatch.setattr(
            SummaryService,
            "get_summary_by_document_id",
            raise_db_error,
        )

        # Act
        response = client.get("/api/v1/summaries/document/1")

        # Assert: RFC 9457 500, not an HTML error page
        assert response.status_code == 500
        assert response.content_type == "application/problem+json"
        data = response.get_json()
        assert data["status"] == 500
        assert "title" in data
        assert "instance" in data
        assert data["instance"] == "/api/v1/summaries/document/1"

    @pytest.mark.contract
    def test_500_on_ownership_check_failure_returns_rfc9457(self, client, app, monkeypatch):
        """Test ownership check DB failure returns 500 RFC 9457 with instance."""
        # Arrange: Valid summary but ownership check raises
        create_summary(
            app,
            id=12,
            document_id=1200,
            summary_text="Some content",
            status="completed",
            created_at=datetime(2026, 4, 7, 10, 0, 0),
            updated_at=datetime(2026, 4, 7, 10, 0, 0),
        )
        from app.services.summary_service import SummaryService

        def raise_ownership_error(document_id, user_id):
            raise RuntimeError("Simulated ownership check failure")

        monkeypatch.setattr(
            SummaryService,
            "check_document_ownership",
            raise_ownership_error,
        )

        # Act: Request with X-User-ID to trigger ownership check
        response = client.get(
            "/api/v1/summaries/document/1200",
            headers={"X-User-ID": "1"},
        )

        # Assert: RFC 9457 500 with endpoint-specific instance
        assert response.status_code == 500
        assert response.content_type == "application/problem+json"
        data = response.get_json()
        assert data["status"] == 500
        assert data["instance"] == "/api/v1/summaries/document/1200"
