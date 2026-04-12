"""User service for business logic"""

import re
from typing import Optional, Dict, Any
from app.database import db
from app.models.user import User
from app.utils.errors import bad_request, conflict


class ValidationError(Exception):
    """Raised when user data validation fails"""

    pass


class UserService:
    """Service layer for user operations"""

    @staticmethod
    def validate_user_data(data: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Validate user input data.

        Args:
            data: Dictionary containing user data from request

        Returns:
            Dictionary containing validated email and nombre

        Raises:
            ValidationError: If data is invalid or incomplete
        """
        if not data or not isinstance(data, dict):
            raise ValidationError("Request body must be valid JSON")

        email = data.get("email", "").strip()
        nombre = data.get("nombre", "").strip()

        if not email:
            raise ValidationError("Email is required")

        if not nombre:
            raise ValidationError("Name (nombre) is required")

        # RFC 5322 simplified email validation pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Email format is invalid")

        # Validate nombre length (reasonable bounds)
        if len(nombre) > 255:
            raise ValidationError("Name (nombre) must not exceed 255 characters")

        if len(nombre) < 2:
            raise ValidationError("Name (nombre) must be at least 2 characters")

        return {"email": email, "nombre": nombre}

    @staticmethod
    def create_user(email: str, nombre: str) -> User:
        """
        Create a new user in the database.

        Args:
            email: User email address
            nombre: User full name

        Returns:
            Created User object

        Raises:
            ValidationError: If email already exists
        """
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValidationError(f"User with email '{email}' already exists")

        user = User(email=email, nombre=nombre)
        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: The user's ID

        Returns:
            User object if found, None otherwise
        """
        return db.session.get(User, user_id)
