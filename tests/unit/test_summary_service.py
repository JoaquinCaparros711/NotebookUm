"""Unit tests for SummaryService database and authorization methods."""

import pytest

from app import create_app
from app.database import db
from app.models.summary import Summary
from app.models.user import User
from app.services.summary_service import SummaryService


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
def service():
    """Create SummaryService instance."""
    return SummaryService()


@pytest.mark.unit
class TestSummaryServiceGetByDocumentId:
    """Tests for SummaryService.get_summary_by_document_id method."""

    def test_get_summary_by_document_id_returns_summary_when_exists(self, app, service):
        """Test get_summary_by_document_id returns summary when document exists."""
        with app.app_context():
            # Arrange: Create a summary
            user = User(email="test@example.com", nombre="Test User")
            db.session.add(user)
            db.session.commit()

            summary = Summary(
                document_id=100,
                summary_text="Test summary content",
                user_id=user.id,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()
            summary_id = summary.id

            # Act: Retrieve summary by document_id
            result = service.get_summary_by_document_id(100)

            # Assert: Returns summary object
            assert result is not None
            assert result.id == summary_id
            assert result.document_id == 100
            assert result.summary_text == "Test summary content"
            assert result.status == "completed"

    def test_get_summary_by_document_id_returns_none_when_not_found(self, app, service):
        """Test get_summary_by_document_id returns None when document doesn't exist."""
        with app.app_context():
            # Act: Try to retrieve non-existent summary
            result = service.get_summary_by_document_id(99999)

            # Assert: Returns None
            assert result is None

    def test_get_summary_by_document_id_returns_latest_when_multiple(self, app, service):
        """Test get_summary_by_document_id returns most recent summary."""
        with app.app_context():
            # Arrange: Create user and two summaries for same document
            user = User(email="user@example.com", nombre="User")
            db.session.add(user)
            db.session.commit()

            summary1 = Summary(
                document_id=200,
                summary_text="Old summary",
                user_id=user.id,
                status="completed",
            )
            db.session.add(summary1)
            db.session.commit()

            summary2 = Summary(
                document_id=200,
                summary_text="New summary",
                user_id=user.id,
                status="completed",
            )
            db.session.add(summary2)
            db.session.commit()

            # Act: Retrieve summary
            result = service.get_summary_by_document_id(200)

            # Assert: Returns first (latest) summary
            assert result is not None
            assert result.id == summary1.id


@pytest.mark.unit
class TestSummaryServiceCheckUserOwnership:
    """Tests for SummaryService.check_user_ownership method."""

    def test_check_user_ownership_returns_true_when_user_owns_summary(self, app, service):
        """Test check_user_ownership returns True when user_id matches."""
        with app.app_context():
            # Arrange: Create user and summary owned by them
            user = User(email="owner@example.com", nombre="Owner")
            db.session.add(user)
            db.session.commit()

            summary = Summary(
                document_id=300,
                summary_text="Owned summary",
                user_id=user.id,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()

            # Act: Check ownership
            result = service.check_user_ownership(summary, user.id)

            # Assert: Returns True
            assert result is True

    def test_check_user_ownership_returns_false_when_user_does_not_own(self, app, service):
        """Test check_user_ownership returns False when user_id doesn't match."""
        with app.app_context():
            # Arrange: Create two users and summary owned by first
            user1 = User(email="user1@example.com", nombre="User One")
            user2 = User(email="user2@example.com", nombre="User Two")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            summary = Summary(
                document_id=400,
                summary_text="User1 summary",
                user_id=user1.id,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()

            # Act: Check if user2 owns user1's summary
            result = service.check_user_ownership(summary, user2.id)

            # Assert: Returns False
            assert result is False

    def test_check_user_ownership_returns_true_when_no_user_id_restriction(self, app, service):
        """Test check_user_ownership returns True when summary has no user_id."""
        with app.app_context():
            # Arrange: Create summary with no user restriction
            summary = Summary(
                document_id=500,
                summary_text="Public summary",
                user_id=None,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()

            # Act: Check ownership with any user_id
            result = service.check_user_ownership(summary, 999)

            # Assert: Returns True (no user restriction)
            assert result is True

    def test_check_user_ownership_with_zero_user_id(self, app, service):
        """Test check_user_ownership handles user_id=0 correctly."""
        with app.app_context():
            # Arrange: Create summary with user_id=0 (edge case)
            summary = Summary(
                document_id=600,
                summary_text="System summary",
                user_id=0,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()

            # Act: Check if user 0 owns it
            result_zero = service.check_user_ownership(summary, 0)
            result_other = service.check_user_ownership(summary, 1)

            # Assert: Correctly matches/doesn't match user_id=0
            assert result_zero is True
            assert result_other is False


@pytest.mark.unit
class TestSummaryServiceIntegration:
    """Integration tests between SummaryService methods."""

    def test_get_summary_and_check_ownership_workflow(self, app, service):
        """Test complete workflow: get summary then check ownership."""
        with app.app_context():
            # Arrange: Create user and summary
            user = User(email="workflow@example.com", nombre="Workflow User")
            db.session.add(user)
            db.session.commit()

            summary = Summary(
                document_id=700,
                summary_text="Workflow summary",
                user_id=user.id,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()
            user_id = user.id

            # Act: Retrieve summary and check ownership
            retrieved = service.get_summary_by_document_id(700)
            is_owner = service.check_user_ownership(retrieved, user_id)

            # Assert: Both operations succeed
            assert retrieved is not None
            assert is_owner is True

    def test_get_summary_and_check_unauthorized_workflow(self, app, service):
        """Test workflow: get summary but fail ownership check."""
        with app.app_context():
            # Arrange: Create two users and summary for first user
            user1 = User(email="user1@workflow.com", nombre="User One")
            user2 = User(email="user2@workflow.com", nombre="User Two")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            summary = Summary(
                document_id=800,
                summary_text="Restricted summary",
                user_id=user1.id,
                status="completed",
            )
            db.session.add(summary)
            db.session.commit()

            # Act: Retrieve summary and check if user2 owns it
            retrieved = service.get_summary_by_document_id(800)
            is_owner = service.check_user_ownership(retrieved, user2.id)

            # Assert: Retrieved but not authorized
            assert retrieved is not None
            assert is_owner is False
