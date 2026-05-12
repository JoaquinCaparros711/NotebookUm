"""Unit tests for UserService, SummaryService, DocumentService, and QuestionService."""

import pytest
from types import SimpleNamespace
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy.exc import SQLAlchemyError

from app.models.user import User
from app.models.document import HistorialDocumento
from app.models.summary import Summary
from app.models.question import HistorialPregunta as Question
from app.services.document_service import (
    DocumentForbiddenError,
    DocumentNotFoundError,
    DocumentService,
    DocumentServiceError,
    DocumentValidationError,
)
from app.services.summary_service import SummaryService
from app.services.user_service import UserService, ValidationError
from app.services.question_service import (
    QuestionService,
    QuestionServiceError,
    QuestionNotFoundError,
    QuestionValidationError,
    QuestionForbiddenError,
)


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


class TestSummaryServiceStatusMessage:
    """Tests for SummaryService.get_status_message (pure logic, no DB).

    Verifies that state-aware messages are returned correctly for each
    possible Summary.status value, fulfilling spec escenario 3 of HU-3.
    """

    def test_completed_status_returns_none(self):
        """Test completed summaries have no processing message."""
        # Given: A completed summary
        summary = Mock(spec=Summary)
        summary.status = "completed"
        service = SummaryService()

        # When: Getting the status message
        result = service.get_status_message(summary)

        # Then: No message for completed summaries
        assert result is None

    def test_pending_status_returns_processing_message(self):
        """Test pending status returns a 'processing' message in Spanish."""
        # Given: A pending summary
        summary = Mock(spec=Summary)
        summary.status = "pending"
        service = SummaryService()

        # When: Getting the status message
        result = service.get_status_message(summary)

        # Then: Returns a descriptive processing message
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_processing_status_returns_processing_message(self):
        """Test 'processing' status returns a message indicating work in progress."""
        # Given: A summary being actively processed
        summary = Mock(spec=Summary)
        summary.status = "processing"
        service = SummaryService()

        # When: Getting the status message
        result = service.get_status_message(summary)

        # Then: Returns a non-empty message
        assert result is not None
        assert isinstance(result, str)

    def test_failed_status_returns_failure_message(self):
        """Test failed status returns an error message distinct from pending."""
        # Given: A failed summary
        summary = Mock(spec=Summary)
        summary.status = "failed"
        service = SummaryService()

        # When: Getting the status message
        result = service.get_status_message(summary)

        # Then: Returns a non-empty failure message
        assert result is not None
        assert isinstance(result, str)

    def test_pending_and_failed_messages_are_different(self):
        """Test that 'pending' and 'failed' statuses produce distinct messages."""
        # Given: Summaries with different non-completed statuses
        pending_summary = Mock(spec=Summary)
        pending_summary.status = "pending"
        failed_summary = Mock(spec=Summary)
        failed_summary.status = "failed"

        service = SummaryService()

        # When: Getting messages for both statuses
        pending_msg = service.get_status_message(pending_summary)
        failed_msg = service.get_status_message(failed_summary)

        # Then: Messages are different
        assert pending_msg != failed_msg


# ---------------------------------------------------------------------------
# QuestionService – Tests
# ---------------------------------------------------------------------------


class TestQuestionServiceCreateQuestion:
    """Tests for QuestionService.create_question"""

    @patch("app.services.question_service.db.session")
    @patch("app.services.question_service.Question")
    def test_create_question_success(self, mock_question_class, mock_session):
        """Test create_question successfully creates and saves a question"""
        # Given: Valid question data
        data = {
            "user_id": 1,
            "document_id": 5,
            "pregunta": "What is this about?"
        }
        mock_question_instance = Mock(spec=Question)
        mock_question_class.return_value = mock_question_instance

        # When: Calling create_question
        result = QuestionService.create_question(data)

        # Then: Question is created with correct data
        mock_question_class.assert_called_once_with(
            usuario_id=1,
            documento_id=5,
            pregunta="What is this about?"
        )

        # Then: Question is added to session and committed
        mock_session.add.assert_called_once_with(mock_question_instance)
        mock_session.commit.assert_called_once()

        # Then: Returns the created question
        assert result == mock_question_instance

    def test_create_question_data_not_dict(self):
        """Test create_question raises ValidationError when data is not a dict"""
        # Given: Non-dict data
        data = "not a dict"

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "JSON object" in str(exc_info.value)

    def test_create_question_missing_user_id(self):
        """Test create_question raises ValidationError when user_id is missing"""
        # Given: Data without user_id
        data = {
            "document_id": 5,
            "pregunta": "What is this about?"
        }

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "user_id" in str(exc_info.value)

    def test_create_question_missing_document_id(self):
        """Test create_question raises ValidationError when document_id is missing"""
        # Given: Data without document_id
        data = {
            "user_id": 1,
            "pregunta": "What is this about?"
        }

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "document_id" in str(exc_info.value)

    def test_create_question_missing_pregunta(self):
        """Test create_question raises ValidationError when pregunta is missing"""
        # Given: Data without pregunta
        data = {
            "user_id": 1,
            "document_id": 5
        }

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "pregunta" in str(exc_info.value)

    def test_create_question_pregunta_empty_string(self):
        """Test create_question raises ValidationError when pregunta is empty"""
        # Given: Empty pregunta
        data = {
            "user_id": 1,
            "document_id": 5,
            "pregunta": ""
        }

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "non-empty string" in str(exc_info.value)

    def test_create_question_pregunta_not_string(self):
        """Test create_question raises ValidationError when pregunta is not a string"""
        # Given: pregunta is a number
        data = {
            "user_id": 1,
            "document_id": 5,
            "pregunta": 123
        }

        # When: Calling create_question
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.create_question(data)

        assert "non-empty string" in str(exc_info.value)

    def test_create_question_strips_whitespace(self):
        """Test create_question strips whitespace from pregunta"""
        # Given: pregunta with leading/trailing whitespace
        data = {
            "user_id": 1,
            "document_id": 5,
            "pregunta": "  What is this about?  "
        }

        with patch("app.services.question_service.db.session"):
            with patch("app.services.question_service.Question") as mock_question_class:
                mock_instance = Mock(spec=Question)
                mock_question_class.return_value = mock_instance

                # When: Creating the question
                QuestionService.create_question(data)

                # Then: pregunta is stripped
                assert mock_question_class.call_args[1]["pregunta"] == "What is this about?"

    @patch("app.services.question_service.db.session")
    def test_create_question_database_error(self, mock_session):
        """Test create_question raises QuestionServiceError on database error"""
        # Given: Database error during commit
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        data = {
            "user_id": 1,
            "document_id": 5,
            "pregunta": "What is this about?"
        }

        with patch("app.services.question_service.Question"):
            # When: Creating the question
            # Then: Raises QuestionServiceError and rolls back
            with pytest.raises(QuestionServiceError) as exc_info:
                QuestionService.create_question(data)

            assert "Unable to persist" in str(exc_info.value)
            mock_session.rollback.assert_called_once()


class TestQuestionServiceListQuestions:
    """Tests for QuestionService.list_questions"""

    @patch("app.services.question_service.Question")
    def test_list_all_questions(self, mock_question_class):
        """Test list_questions returns all questions when no filters applied"""
        # Given: Mock questions in database
        mock_q1 = Mock(spec=Question)
        mock_q1.id = 2
        mock_q2 = Mock(spec=Question)
        mock_q2.id = 1
        mock_question_class.query.order_by.return_value.all.return_value = [mock_q1, mock_q2]

        # When: Listing all questions
        result = QuestionService.list_questions()

        # Then: Returns all questions
        assert len(result) == 2
        assert result == [mock_q1, mock_q2]

    @patch("app.services.question_service.Question")
    def test_list_questions_filtered_by_user_id(self, mock_question_class):
        """Test list_questions filters by user_id when provided"""
        # Given: Mock questions for a specific user
        mock_q1 = Mock(spec=Question)
        mock_q1.usuario_id = 1
        mock_q1.id = 2
        mock_question_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_q1]

        # When: Listing questions for user 1
        result = QuestionService.list_questions(user_id=1)

        # Then: Returns filtered questions
        assert len(result) == 1
        assert result[0].usuario_id == 1
        mock_question_class.query.filter_by.assert_called_once_with(usuario_id=1)

    @patch("app.services.question_service.Question")
    def test_list_questions_filtered_by_document_id(self, mock_question_class):
        """Test list_questions filters by document_id when provided"""
        # Given: Mock questions for a specific document
        mock_q1 = Mock(spec=Question)
        mock_q1.documento_id = 5
        mock_q1.id = 1
        mock_question_class.query.filter_by.return_value.order_by.return_value.all.return_value = [mock_q1]

        # When: Listing questions for document 5
        result = QuestionService.list_questions(document_id=5)

        # Then: Returns filtered questions
        assert len(result) == 1
        assert result[0].documento_id == 5
        mock_question_class.query.filter_by.assert_called_once_with(documento_id=5)

    @patch("app.services.question_service.Question")
    def test_list_questions_filtered_by_both_filters(self, mock_question_class):
        """Test list_questions filters by both user_id and document_id"""
        # Given: Mock questions
        mock_q1 = Mock(spec=Question)
        mock_q1.usuario_id = 1
        mock_q1.documento_id = 5
        mock_q1.id = 1

        # Set up the chain of filter_by calls
        # First filter_by returns a mock, second filter_by (on that mock) also returns the same mock
        mock_chain = MagicMock()
        mock_chain.filter_by.return_value = mock_chain
        mock_chain.order_by.return_value.all.return_value = [mock_q1]
        mock_question_class.query = mock_chain

        # When: Listing questions with both filters
        result = QuestionService.list_questions(user_id=1, document_id=5)

        # Then: Returns filtered questions
        assert len(result) == 1
        assert result[0].usuario_id == 1
        assert result[0].documento_id == 5

    @patch("app.services.question_service.Question")
    def test_list_questions_orders_by_id_descending(self, mock_question_class):
        """Test list_questions orders results by id descending"""
        # Given: Questions in database
        mock_q1 = Mock(spec=Question)
        mock_q1.id = 1
        mock_q2 = Mock(spec=Question)
        mock_q2.id = 2

        mock_question_class.query.order_by.return_value.all.return_value = [mock_q2, mock_q1]

        # When: Listing questions
        QuestionService.list_questions()

        # Then: order_by is called on the query
        mock_question_class.query.order_by.assert_called_once()

    @patch("app.services.question_service.Question")
    def test_list_questions_returns_empty_list(self, mock_question_class):
        """Test list_questions returns empty list when no questions found"""
        # Given: No questions in database
        mock_question_class.query.order_by.return_value.all.return_value = []

        # When: Listing questions
        result = QuestionService.list_questions()

        # Then: Returns empty list
        assert result == []


class TestQuestionServiceGetQuestion:
    """Tests for QuestionService.get_question"""

    @patch("app.services.question_service.db.session")
    def test_get_question_found(self, mock_session):
        """Test get_question returns question when found"""
        # Given: Question exists
        mock_q = Mock(spec=Question)
        mock_q.id = 1
        mock_q.pregunta = "What is this?"
        mock_session.get.return_value = mock_q

        # When: Getting question by ID
        result = QuestionService.get_question(1)

        # Then: Returns the question
        assert result == mock_q
        assert result.id == 1
        mock_session.get.assert_called_once_with(Question, 1)

    @patch("app.services.question_service.db.session")
    def test_get_question_not_found(self, mock_session):
        """Test get_question returns None when not found"""
        # Given: Question does not exist
        mock_session.get.return_value = None

        # When: Getting non-existent question
        result = QuestionService.get_question(999)

        # Then: Returns None
        assert result is None
        mock_session.get.assert_called_once_with(Question, 999)

    @patch("app.services.question_service.db.session")
    def test_get_question_uses_session_get(self, mock_session):
        """Test get_question uses Session.get (SQLAlchemy 2.x API)"""
        # Given: A question ID
        question_id = 42

        # When: Calling get_question
        QuestionService.get_question(question_id)

        # Then: Uses modern Session.get method
        mock_session.get.assert_called_once_with(Question, question_id)


class TestQuestionServiceUpdateQuestion:
    """Tests for QuestionService.update_question"""

    @patch("app.services.question_service.db.session")
    def test_update_question_pregunta_success(self, mock_session):
        """Test update_question successfully updates pregunta"""
        # Given: Question exists and valid update data
        mock_q = Mock(spec=Question)
        mock_q.pregunta = "Old question"
        mock_session.get.return_value = mock_q
        data = {"pregunta": "New question"}

        # When: Updating the question
        result = QuestionService.update_question(1, data)

        # Then: pregunta is updated
        assert mock_q.pregunta == "New question"
        mock_session.commit.assert_called_once()
        assert result == mock_q

    @patch("app.services.question_service.db.session")
    def test_update_question_respuesta_success(self, mock_session):
        """Test update_question successfully updates respuesta"""
        # Given: Question exists
        mock_q = Mock(spec=Question)
        mock_q.respuesta = None
        mock_session.get.return_value = mock_q
        data = {"respuesta": "This is the answer"}

        # When: Updating respuesta
        result = QuestionService.update_question(1, data)

        # Then: respuesta is updated
        assert mock_q.respuesta == "This is the answer"
        mock_session.commit.assert_called_once()
        assert result == mock_q

    @patch("app.services.question_service.db.session")
    def test_update_question_both_fields(self, mock_session):
        """Test update_question updates both pregunta and respuesta"""
        # Given: Question exists
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q
        data = {"pregunta": "Updated question", "respuesta": "Updated answer"}

        # When: Updating both fields
        QuestionService.update_question(1, data)

        # Then: Both fields are updated
        assert mock_q.pregunta == "Updated question"
        assert mock_q.respuesta == "Updated answer"
        mock_session.commit.assert_called_once()

    def test_update_question_not_found(self):
        """Test update_question raises QuestionNotFoundError when not found"""
        # Given: Question does not exist
        with patch("app.services.question_service.db.session") as mock_session:
            mock_session.get.return_value = None
            data = {"pregunta": "New question"}

            # When: Trying to update non-existent question
            # Then: Raises QuestionNotFoundError
            with pytest.raises(QuestionNotFoundError) as exc_info:
                QuestionService.update_question(999, data)

            assert "not found" in str(exc_info.value)

    def test_update_question_invalid_data_type(self):
        """Test update_question raises ValidationError when data is not a dict"""
        # Given: Invalid data
        with patch("app.services.question_service.db.session") as mock_session:
            mock_q = Mock(spec=Question)
            mock_session.get.return_value = mock_q

            # When: Passing non-dict data
            # Then: Raises QuestionValidationError
            with pytest.raises(QuestionValidationError) as exc_info:
                QuestionService.update_question(1, "not a dict")

            assert "JSON object" in str(exc_info.value)

    def test_update_question_pregunta_empty(self):
        """Test update_question raises ValidationError for empty pregunta"""
        # Given: Empty pregunta in update data
        with patch("app.services.question_service.db.session") as mock_session:
            mock_q = Mock(spec=Question)
            mock_session.get.return_value = mock_q
            data = {"pregunta": ""}

            # When: Trying to update with empty pregunta
            # Then: Raises QuestionValidationError
            with pytest.raises(QuestionValidationError) as exc_info:
                QuestionService.update_question(1, data)

            assert "non-empty string" in str(exc_info.value)

    def test_update_question_pregunta_not_string(self):
        """Test update_question raises ValidationError when pregunta is not a string"""
        # Given: Non-string pregunta
        with patch("app.services.question_service.db.session") as mock_session:
            mock_q = Mock(spec=Question)
            mock_session.get.return_value = mock_q
            data = {"pregunta": 123}

            # When: Trying to update with non-string pregunta
            # Then: Raises QuestionValidationError
            with pytest.raises(QuestionValidationError) as exc_info:
                QuestionService.update_question(1, data)

            assert "non-empty string" in str(exc_info.value)

    @patch("app.services.question_service.db.session")
    def test_update_question_no_fields(self, mock_session):
        """Test update_question raises ValidationError when no supported fields"""
        # Given: Update data with no supported fields
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q
        data = {"unsupported_field": "value"}

        # When: Trying to update with no supported fields
        # Then: Raises QuestionValidationError
        with pytest.raises(QuestionValidationError) as exc_info:
            QuestionService.update_question(1, data)

        assert "No supported fields" in str(exc_info.value)

    @patch("app.services.question_service.db.session")
    def test_update_question_database_error(self, mock_session):
        """Test update_question raises QuestionServiceError on database error"""
        # Given: Database error during commit
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")
        data = {"pregunta": "New question"}

        # When: Updating question with database error
        # Then: Raises QuestionServiceError and rolls back
        with pytest.raises(QuestionServiceError) as exc_info:
            QuestionService.update_question(1, data)

        assert "Unable to update" in str(exc_info.value)
        mock_session.rollback.assert_called_once()

    @patch("app.services.question_service.db.session")
    def test_update_question_strips_pregunta_whitespace(self, mock_session):
        """Test update_question strips whitespace from pregunta"""
        # Given: pregunta with whitespace
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q
        data = {"pregunta": "  Updated question  "}

        # When: Updating pregunta
        QuestionService.update_question(1, data)

        # Then: Whitespace is stripped
        assert mock_q.pregunta == "Updated question"


class TestQuestionServiceDeleteQuestion:
    """Tests for QuestionService.delete_question"""

    @patch("app.services.question_service.db.session")
    def test_delete_question_success(self, mock_session):
        """Test delete_question successfully deletes a question"""
        # Given: Question exists
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q

        # When: Deleting the question
        QuestionService.delete_question(1)

        # Then: Question is deleted and committed
        mock_session.delete.assert_called_once_with(mock_q)
        mock_session.commit.assert_called_once()

    def test_delete_question_not_found(self):
        """Test delete_question raises QuestionNotFoundError when not found"""
        # Given: Question does not exist
        with patch("app.services.question_service.db.session") as mock_session:
            mock_session.get.return_value = None

            # When: Trying to delete non-existent question
            # Then: Raises QuestionNotFoundError
            with pytest.raises(QuestionNotFoundError) as exc_info:
                QuestionService.delete_question(999)

            assert "not found" in str(exc_info.value)
            mock_session.delete.assert_not_called()

    @patch("app.services.question_service.db.session")
    def test_delete_question_database_error(self, mock_session):
        """Test delete_question raises QuestionServiceError on database error"""
        # Given: Database error during delete
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q
        mock_session.commit.side_effect = SQLAlchemyError("DB Error")

        # When: Deleting question with database error
        # Then: Raises QuestionServiceError and rolls back
        with pytest.raises(QuestionServiceError) as exc_info:
            QuestionService.delete_question(1)

        assert "Unable to delete" in str(exc_info.value)
        mock_session.rollback.assert_called_once()

    @patch("app.services.question_service.db.session")
    def test_delete_question_uses_session_get(self, mock_session):
        """Test delete_question uses Session.get to retrieve the question"""
        # Given: A question ID
        question_id = 42
        mock_q = Mock(spec=Question)
        mock_session.get.return_value = mock_q

        # When: Deleting the question
        QuestionService.delete_question(question_id)

        # Then: Uses modern Session.get method
        mock_session.get.assert_called_once_with(Question, question_id)


class TestDocumentServiceListUserDocuments:
    """Unit tests for DocumentService.list_user_documents."""

    @patch("app.services.document_service.HistorialDocumento")
    def test_list_returns_all_documents_for_user(self, mock_hist):
        """Without pagination, returns all items newest-first and pagination None."""
        doc = Mock()
        mock_hist.query.filter_by.return_value.order_by.return_value.all.return_value = [doc]
        result = DocumentService.list_user_documents(usuario_id=7)
        mock_hist.query.filter_by.assert_called_once_with(usuario_id=7)
        assert result["pagination"] is None
        assert result["items"] == [doc]

    @patch("app.services.document_service.HistorialDocumento")
    def test_list_paginated_includes_metadata(self, mock_hist):
        """With page and per_page, returns items plus pagination fields."""
        doc = Mock()
        pag = Mock()
        pag.items = [doc]
        pag.page = 1
        pag.per_page = 10
        pag.total = 40
        pag.pages = 4
        pag.has_next = True
        mock_hist.query.filter_by.return_value.order_by.return_value.paginate.return_value = pag

        result = DocumentService.list_user_documents(2, page=1, per_page=10)

        assert result["items"] == [doc]
        assert result["pagination"] == {
            "page": 1,
            "per_page": 10,
            "total": 40,
            "pages": 4,
            "has_next": True,
        }

    @patch("app.services.document_service.HistorialDocumento")
    def test_list_invalid_page_raises_validation_error(self, mock_hist):
        """Non-positive page or per_page raises DocumentValidationError."""
        with pytest.raises(DocumentValidationError):
            DocumentService.list_user_documents(1, page=0, per_page=5)
        mock_hist.query.filter_by.assert_not_called()


class TestDocumentServiceUpdateDocument:
    """Unit tests for DocumentService.update_document."""

    @patch("app.services.document_service.db.session")
    def test_update_raises_not_found_when_missing(self, mock_session):
        mock_session.get.return_value = None
        with pytest.raises(DocumentNotFoundError):
            DocumentService.update_document(99, 1, {"nombre_archivo": "a.pdf"})

    @patch("app.services.document_service.db.session")
    def test_update_raises_forbidden_when_wrong_owner(self, mock_session):
        doc = SimpleNamespace(usuario_id=2, id=1)
        mock_session.get.return_value = doc
        with pytest.raises(DocumentForbiddenError):
            DocumentService.update_document(1, 1, {"nombre_archivo": "a.pdf"})

    @patch("app.services.document_service.db.session")
    def test_update_raises_validation_when_body_not_object(self, mock_session):
        doc = SimpleNamespace(usuario_id=1, id=1, nombre_archivo="old.pdf")
        mock_session.get.return_value = doc
        with pytest.raises(DocumentValidationError):
            DocumentService.update_document(1, 1, None)

    @patch("app.services.document_service.db.session")
    def test_update_raises_validation_when_no_supported_fields(self, mock_session):
        doc = SimpleNamespace(usuario_id=1, id=1, nombre_archivo="old.pdf")
        mock_session.get.return_value = doc
        with pytest.raises(DocumentValidationError):
            DocumentService.update_document(1, 1, {"other": True})

    @patch("app.services.document_service.db.session")
    def test_update_raises_validation_when_nombre_empty(self, mock_session):
        doc = SimpleNamespace(usuario_id=1, id=1, nombre_archivo="old.pdf")
        mock_session.get.return_value = doc
        with pytest.raises(DocumentValidationError):
            DocumentService.update_document(1, 1, {"nombre_archivo": "  "})

    @patch("app.services.document_service.db.session")
    def test_update_success_commits_and_returns_document(self, mock_session):
        doc = SimpleNamespace(usuario_id=1, id=5, nombre_archivo="before.pdf")
        mock_session.get.return_value = doc
        out = DocumentService.update_document(5, 1, {"nombre_archivo": "after.pdf"})
        assert doc.nombre_archivo == "after.pdf"
        assert out is doc
        mock_session.commit.assert_called_once()

    @patch("app.services.document_service.db.session")
    def test_update_commit_failure_wraps_in_service_error(self, mock_session):
        doc = SimpleNamespace(usuario_id=1, id=1, nombre_archivo="x.pdf")
        mock_session.get.return_value = doc
        mock_session.commit.side_effect = SQLAlchemyError("db down")
        with pytest.raises(DocumentServiceError):
            DocumentService.update_document(1, 1, {"nombre_archivo": "y.pdf"})
        mock_session.rollback.assert_called_once()


class TestDocumentServiceDeleteDocument:
    """Unit tests for DocumentService.delete_document."""

    @patch("app.services.document_service.Summary")
    @patch("app.services.document_service.db.session")
    def test_delete_raises_not_found(self, mock_session, mock_summary):
        mock_session.get.return_value = None
        with pytest.raises(DocumentNotFoundError):
            DocumentService.delete_document(42, 1)
        mock_summary.query.filter.assert_not_called()

    @patch("app.services.document_service.Summary")
    @patch("app.services.document_service.db.session")
    def test_delete_raises_forbidden(self, mock_session, mock_summary):
        doc = SimpleNamespace(usuario_id=9)
        mock_session.get.return_value = doc
        with pytest.raises(DocumentForbiddenError):
            DocumentService.delete_document(1, 1)

    @patch("app.services.document_service.Summary")
    @patch("app.services.document_service.db.session")
    def test_delete_removes_summaries_then_document(self, mock_session, mock_summary):
        doc = SimpleNamespace(usuario_id=1)
        mock_session.get.return_value = doc
        delete_q = Mock()
        mock_summary.query.filter.return_value = delete_q
        delete_q.delete.return_value = 2

        DocumentService.delete_document(3, 1)

        delete_q.delete.assert_called_once_with(synchronize_session=False)
        mock_session.delete.assert_called_once_with(doc)
        mock_session.commit.assert_called_once()

    @patch("app.services.document_service.Summary")
    @patch("app.services.document_service.db.session")
    def test_delete_commit_failure_wraps_in_service_error(self, mock_session, mock_summary):
        doc = SimpleNamespace(usuario_id=1)
        mock_session.get.return_value = doc
        mock_summary.query.filter.return_value.delete.return_value = 1
        mock_session.commit.side_effect = SQLAlchemyError("fail")
        with pytest.raises(DocumentServiceError):
            DocumentService.delete_document(3, 1)
        mock_session.rollback.assert_called_once()
