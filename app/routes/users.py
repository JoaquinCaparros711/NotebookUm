"""Users API routes"""

from flask import Blueprint, request, jsonify
from app.database import db
from app.models.user import User
from app.utils.errors import bad_request, conflict, not_found

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users_bp.post("")
def create_user():
    """Create a new user"""
    data = request.get_json()

    if not data:
        return bad_request("Request body must be JSON", instance="/api/v1/users")

    # Validate required fields
    email = data.get("email")
    nombre = data.get("nombre")

    if not email:
        return bad_request("Email is required", instance="/api/v1/users")

    if not nombre:
        return bad_request("Name (nombre) is required", instance="/api/v1/users")

    # Check for duplicate email
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return conflict(f"User with email '{email}' already exists", instance="/api/v1/users")

    # Create new user
    user = User(email=email, nombre=nombre)
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    return response


@users_bp.get("/<int:user_id>")
def get_user(user_id: int):
    """Retrieve a user by ID"""
    user = db.session.get(User, user_id)
    
    if not user:
        return not_found(f"User with ID {user_id} not found", instance=f"/api/v1/users/{user_id}")
    
    response = jsonify(user.to_dict())
    response.status_code = 200
    return response

