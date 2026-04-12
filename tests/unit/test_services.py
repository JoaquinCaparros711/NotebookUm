"""Unit tests for UserService"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.user_service import UserService, ValidationError
from app.models.user import User


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
