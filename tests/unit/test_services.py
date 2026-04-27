"""Unit tests for UserService and SummaryService"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.user_service import UserService, ValidationError
from app.models.user import User
from app.models.document import HistorialDocumento
from app.models.summary import Summary
from app.services.summary_service import SummaryService


class TestUserServiceValidation:
    """Tests for UserService.validate_user_data"""

    def test_validate_user_data_with_valid_input(self):
        """Test validate_user_data returns clean dict for valid input"""
        # Given: Valid user data
        data = {"email": "test@example.com", "nombre": "Test User"}

        # When: Calling validate_user_data
        result = UserService.validate_user_data(data)

        # Then: Returns cleaned data
        assert result["email"] == "test@example.com"
        assert result["nombre"] == "Test User"

    def test_validate_user_data_with_whitespace(self):
        """Test validate_user_data strips whitespace"""
        # Given: User data with whitespace
        data = {"email": "  test@example.com  ", "nombre": "  Test User  "}

        # When: Calling validate_user_data
        result = UserService.validate_user_data(data)

        # Then: Returns data with whitespace stripped
        assert result["email"] == "test@example.com"
        assert result["nombre"] == "Test User"

    def test_validate_user_data_missing_email(self):
        """Test validate_user_data raises error when email is missing"""
        # Given: Data without email
        data = {"nombre": "Test User"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Email is required" in str(exc_info.value)

    def test_validate_user_data_missing_nombre(self):
        """Test validate_user_data raises error when nombre is missing"""
        # Given: Data without nombre
        data = {"email": "test@example.com"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Name (nombre) is required" in str(exc_info.value)

    def test_validate_user_data_empty_email(self):
        """Test validate_user_data raises error when email is empty"""
        # Given: Empty email
        data = {"email": "", "nombre": "Test User"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Email is required" in str(exc_info.value)

    def test_validate_user_data_empty_nombre(self):
        """Test validate_user_data raises error when nombre is empty"""
        # Given: Empty nombre
        data = {"email": "test@example.com", "nombre": ""}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Name (nombre) is required" in str(exc_info.value)

    def test_validate_user_data_invalid_email_format(self):
        """Test validate_user_data raises error for invalid email format"""
        # Given: Invalid email (missing @)
        data = {"email": "testexample.com", "nombre": "Test User"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Email format is invalid" in str(exc_info.value)

    def test_validate_user_data_invalid_email_missing_domain_dot(self):
        """Test validate_user_data raises error for email without domain dot"""
        # Given: Invalid email (@ but no dot after @)
        data = {"email": "test@example", "nombre": "Test User"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "Email format is invalid" in str(exc_info.value)

    def test_validate_user_data_with_none(self):
        """Test validate_user_data raises error when data is None"""
        # Given: None as data
        data = None

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "valid JSON" in str(exc_info.value)

    def test_validate_user_data_with_non_dict(self):
        """Test validate_user_data raises error when data is not a dict"""
        # Given: String instead of dict
        data = "not a dict"

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "valid JSON" in str(exc_info.value)

    def test_validate_user_data_nombre_too_short(self):
        """Test validate_user_data raises error when nombre is too short"""
        # Given: Nombre with only 1 character
        data = {"email": "test@example.com", "nombre": "X"}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "at least 2 characters" in str(exc_info.value)

    def test_validate_user_data_nombre_too_long(self):
        """Test validate_user_data raises error when nombre exceeds max length"""
        # Given: Nombre with more than 255 characters
        data = {"email": "test@example.com", "nombre": "X" * 256}

        # When: Calling validate_user_data
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.validate_user_data(data)

        assert "must not exceed 255 characters" in str(exc_info.value)


class TestUserServiceCreateUser:
    """Tests for UserService.create_user"""

    @patch("app.services.user_service.User")
    @patch("app.services.user_service.db.session")
    def test_create_user_success(self, mock_session, mock_user_class):
        """Test create_user successfully creates and saves user"""
        # Given: Valid email and nombre, no existing user
        email = "new@example.com"
        nombre = "New User"
        mock_user_class.query.filter_by.return_value.first.return_value = None

        # Create a mock user instance
        mock_user_instance = Mock()
        mock_user_instance.email = email
        mock_user_instance.nombre = nombre
        mock_user_class.return_value = mock_user_instance

        # When: Calling create_user
        result = UserService.create_user(email, nombre)

        # Then: User is created with correct data
        mock_user_class.assert_called_once_with(email=email, nombre=nombre)

        # Then: User is added to session
        mock_session.add.assert_called_once_with(mock_user_instance)

        # Then: Session is committed
        mock_session.commit.assert_called_once()

        # Then: Returns the created user
        assert result == mock_user_instance

    @patch("app.services.user_service.User")
    def test_create_user_duplicate_email(self, mock_user_class):
        """Test create_user raises error when email already exists"""
        # Given: Email that already exists
        email = "existing@example.com"
        nombre = "New User"
        mock_existing_user = Mock()
        mock_user_class.query.filter_by.return_value.first.return_value = mock_existing_user

        # When: Calling create_user
        # Then: Raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserService.create_user(email, nombre)

        assert "already exists" in str(exc_info.value)
        assert email in str(exc_info.value)

    @patch("app.services.user_service.User")
    @patch("app.services.user_service.db.session")
    def test_create_user_returns_user_object(self, mock_session, mock_user_class):
        """Test create_user returns User object with correct attributes"""
        # Given: Valid user data
        email = "test@example.com"
        nombre = "Test User"
        mock_user_class.query.filter_by.return_value.first.return_value = None

        # Create realistic mock
        mock_user_instance = Mock(spec=User)
        mock_user_instance.email = email
        mock_user_instance.nombre = nombre
        mock_user_class.return_value = mock_user_instance

        # When: Creating user
        result = UserService.create_user(email, nombre)

        # Then: Returned object has correct attributes
        assert result.email == email
        assert result.nombre == nombre


class TestUserServiceGetUserById:
    """Tests for UserService.get_user_by_id"""

    @patch("app.services.user_service.db.session")
    def test_get_user_by_id_found(self, mock_session):
        """Test get_user_by_id returns user when found"""
        # Given: User exists in database
        user_id = 1
        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.email = "test@example.com"
        mock_user.nombre = "Test User"
        mock_session.get.return_value = mock_user

        # When: Calling get_user_by_id
        result = UserService.get_user_by_id(user_id)

        # Then: Returns the user
        assert result == mock_user
        assert result.id == user_id

        # Then: Called session.get with correct arguments
        mock_session.get.assert_called_once_with(User, user_id)

    @patch("app.services.user_service.db.session")
    def test_get_user_by_id_not_found(self, mock_session):
        """Test get_user_by_id returns None when user not found"""
        # Given: User does not exist
        user_id = 99999
        mock_session.get.return_value = None

        # When: Calling get_user_by_id
        result = UserService.get_user_by_id(user_id)

        # Then: Returns None
        assert result is None

        # Then: Called session.get with correct arguments
        mock_session.get.assert_called_once_with(User, user_id)

    @patch("app.services.user_service.db.session")
    def test_get_user_by_id_uses_session_get(self, mock_session):
        """Test get_user_by_id uses Session.get (not legacy Query.get)"""
        # Given: A user ID
        user_id = 42

        # When: Calling get_user_by_id
        UserService.get_user_by_id(user_id)

        # Then: Uses modern Session.get method
        mock_session.get.assert_called_once_with(User, user_id)


# ---------------------------------------------------------------------------
# SummaryService – Tests
# ---------------------------------------------------------------------------


class TestSummaryServiceOwnership:
    """Tests for SummaryService.check_user_ownership (pure logic, no DB needed)."""

    def test_ownership_returns_true_when_user_id_matches(self):
        """Test check_user_ownership returns True when user owns the summary."""
        # Given: A summary owned by user 42
        summary = Mock(spec=Summary)
        summary.user_id = 42
        service = SummaryService()

        # When: Checking ownership for the same user
        result = service.check_user_ownership(summary, 42)

        # Then: Returns True
        assert result is True

    def test_ownership_returns_false_when_user_id_differs(self):
        """Test check_user_ownership returns False when another user checks."""
        # Given: A summary owned by user 1
        summary = Mock(spec=Summary)
        summary.user_id = 1
        service = SummaryService()

        # When: Checking ownership for a different user
        result = service.check_user_ownership(summary, 99)

        # Then: Returns False
        assert result is False

    def test_ownership_returns_true_when_no_user_restriction(self):
        """Test check_user_ownership returns True when summary.user_id is None."""
        # Given: A public summary (no user restriction)
        summary = Mock(spec=Summary)
        summary.user_id = None
        service = SummaryService()

        # When: Any user checks ownership
        result = service.check_user_ownership(summary, 7)

        # Then: Returns True (no restriction enforced)
        assert result is True

    def test_ownership_returns_false_for_zero_vs_nonzero_id(self):
        """Test check_user_ownership correctly handles user_id=0 edge case."""
        # Given: Summary owned by user_id=0 (edge case)
        summary = Mock(spec=Summary)
        summary.user_id = 0
        service = SummaryService()

        # When: User 0 checks (matches) and user 1 checks (does not match)
        result_match = service.check_user_ownership(summary, 0)
        result_no_match = service.check_user_ownership(summary, 1)

        # Then: Only the exact match returns True
        assert result_match is True
        assert result_no_match is False

    def test_ownership_is_strict_equality_not_truthiness(self):
        """Test that user_id comparison uses strict equality (not just truthy)."""
        # Given: Summary owned by user_id=5
        summary = Mock(spec=Summary)
        summary.user_id = 5
        service = SummaryService()

        # When: Checking with user_id=1 (truthy but not equal)
        result = service.check_user_ownership(summary, 1)

        # Then: Returns False despite both being truthy
        assert result is False


class TestSummaryServiceGetByDocumentId:
    """Tests for SummaryService.get_summary_by_document_id with mocked DB."""

    @patch("app.services.summary_service.Summary")
    def test_returns_summary_when_document_exists(self, mock_summary_class):
        """Test returns Summary object when document_id is found in DB."""
        # Given: DB returns a summary for document 1
        mock_summary = Mock(spec=Summary)
        mock_summary.document_id = 1
        mock_summary.summary_text = "Relevant content."
        mock_summary_class.query.filter_by.return_value.first.return_value = mock_summary
        service = SummaryService()

        # When: Retrieving summary for document 1
        result = service.get_summary_by_document_id(1)

        # Then: Returns the mock summary
        assert result is mock_summary
        assert result.document_id == 1
        mock_summary_class.query.filter_by.assert_called_once_with(document_id=1)
        mock_summary_class.query.filter_by.return_value.first.assert_called_once()

    @patch("app.services.summary_service.Summary")
    def test_returns_none_when_document_not_found(self, mock_summary_class):
        """Test returns None when document_id has no summary in DB."""
        # Given: DB returns None (no summary for document 99)
        mock_summary_class.query.filter_by.return_value.first.return_value = None
        service = SummaryService()

        # When: Retrieving summary for non-existent document
        result = service.get_summary_by_document_id(99)

        # Then: Returns None
        assert result is None
        mock_summary_class.query.filter_by.assert_called_once_with(document_id=99)

    @patch("app.services.summary_service.Summary")
    def test_passes_correct_document_id_to_query(self, mock_summary_class):
        """Test that the exact document_id is forwarded to the DB filter."""
        # Given: Any DB response
        mock_summary_class.query.filter_by.return_value.first.return_value = None
        service = SummaryService()
        target_id = 1234

        # When: Querying with a specific ID
        service.get_summary_by_document_id(target_id)

        # Then: Query is made with that exact ID
        mock_summary_class.query.filter_by.assert_called_once_with(document_id=target_id)

    @patch("app.services.summary_service.Summary")
    def test_returns_first_summary_when_multiple_exist(self, mock_summary_class):
        """Test that .first() is used, returning the first DB result."""
        # Given: DB has multiple summaries; .first() returns the earliest one
        mock_first = Mock(spec=Summary)
        mock_first.document_id = 5
        mock_summary_class.query.filter_by.return_value.first.return_value = mock_first
        service = SummaryService()

        # When: Querying document 5
        result = service.get_summary_by_document_id(5)

        # Then: Returns the first result from the DB query
        assert result is mock_first

    @patch("app.services.summary_service.Summary")
    def test_does_not_create_db_connection_directly(self, mock_summary_class):
        """Test that service delegates DB access to Summary.query, not raw SQL."""
        # Given: Mock summary returned by query
        mock_summary_class.query.filter_by.return_value.first.return_value = Mock(
            spec=Summary
        )
        service = SummaryService()

        # When: Calling get_summary_by_document_id
        service.get_summary_by_document_id(10)

        # Then: DB access is routed through Summary.query.filter_by (ORM layer)
        mock_summary_class.query.filter_by.assert_called_once()


class TestSummaryServiceDocumentOwnership:
    """Tests for SummaryService.check_document_ownership with mocked DB.

    Verifies that ownership is resolved from HistorialDocumento.usuario_id,
    not from Summary.user_id, fulfilling RF-018 (spec.md).
    """

    @patch("app.services.summary_service.db")
    def test_returns_true_when_user_owns_document(self, mock_db):
        """Test returns True when the requesting user owns the parent document."""
        # Given: Document owned by user 7
        mock_doc = Mock(spec=HistorialDocumento)
        mock_doc.usuario_id = 7
        mock_db.session.get.return_value = mock_doc
        service = SummaryService()

        # When: User 7 checks access for document 1
        result = service.check_document_ownership(document_id=1, user_id=7)

        # Then: Access granted
        assert result is True

    @patch("app.services.summary_service.db")
    def test_returns_false_when_user_does_not_own_document(self, mock_db):
        """Test returns False when the requesting user is not the document owner."""
        # Given: Document owned by user 1
        mock_doc = Mock(spec=HistorialDocumento)
        mock_doc.usuario_id = 1
        mock_db.session.get.return_value = mock_doc
        service = SummaryService()

        # When: User 99 (different user) checks access
        result = service.check_document_ownership(document_id=1, user_id=99)

        # Then: Access denied
        assert result is False

    @patch("app.services.summary_service.db")
    def test_returns_true_when_document_not_found(self, mock_db):
        """Test returns True when the document record doesn't exist (no restriction)."""
        # Given: Document not in DB
        mock_db.session.get.return_value = None
        service = SummaryService()

        # When: Any user checks access for a missing document
        result = service.check_document_ownership(document_id=999, user_id=5)

        # Then: No document → no restriction → allow access
        assert result is True

    @patch("app.services.summary_service.db")
    def test_queries_with_correct_document_id(self, mock_db):
        """Test that the exact document_id is passed to the DB query."""
        # Given: Any mock document
        mock_db.session.get.return_value = None
        service = SummaryService()
        target_doc_id = 42

        # When: Checking ownership for document 42
        service.check_document_ownership(document_id=target_doc_id, user_id=1)

        # Then: DB queried with the exact ID via modern session.get API
        mock_db.session.get.assert_called_once_with(HistorialDocumento, target_doc_id)

    @patch("app.services.summary_service.db")
    def test_delegates_db_access_to_orm(self, mock_db):
        """Test that DB access goes through db.session.get (SQLAlchemy 2.x ORM layer)."""
        # Given: Mock document
        mock_doc = Mock(spec=HistorialDocumento)
        mock_doc.usuario_id = 3
        mock_db.session.get.return_value = mock_doc
        service = SummaryService()

        # When: Calling check_document_ownership
        service.check_document_ownership(document_id=10, user_id=3)

        # Then: Access goes through db.session.get, not legacy Query.get
        mock_db.session.get.assert_called_once()
