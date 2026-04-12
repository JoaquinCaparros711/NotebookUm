"""Users API routes"""

from flask import Blueprint, request, jsonify
from app.services.user_service import UserService, ValidationError
from app.utils.errors import bad_request, conflict, not_found

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.post("")
def create_user():
    """Create a new user"""
    data = request.get_json()

    try:
        # Validate user data using UserService
        validated_data = UserService.validate_user_data(data)
        email = validated_data["email"]
        nombre = validated_data["nombre"]

        # Create user using UserService
        user = UserService.create_user(email, nombre)

        response = jsonify(user.to_dict())
        response.status_code = 201
        return response

    except ValidationError as e:
        # Handle validation errors
        if "already exists" in str(e):
            return conflict(str(e), instance="/api/v1/users")
        return bad_request(str(e), instance="/api/v1/users")


@users_bp.get("/<int:user_id>")
def get_user(user_id: int):
    """Retrieve a user by ID"""
    user = UserService.get_user_by_id(user_id)

    if not user:
        return not_found(
            f"User with ID {user_id} not found",
            instance=f"/api/v1/users/{user_id}"
        )

    response = jsonify(user.to_dict())
    response.status_code = 200
    return response

