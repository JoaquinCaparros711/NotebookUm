"""Contract tests for POST /api/v1/users endpoint"""

import pytest
from app import create_app
from app.database import db


@pytest.fixture
def app():
    """Create and configure a test application instance"""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.mark.contract
class TestPostUsers:
    """Contract tests for POST /api/v1/users"""

    def test_create_user_success(self, client):
        """Test successful user creation with valid data"""
        # Given: Valid user data
        user_data = {
            "email": "test@example.com",
            "nombre": "Test User"
        }

        # When: POST request to /api/v1/users
        response = client.post("/api/v1/users", json=user_data)

        # Then: Returns 201 Created
        assert response.status_code == 201
        
        # Then: Response contains user data
        data = response.get_json()
        assert data is not None
        assert "id" in data
        assert data["email"] == "test@example.com"
        assert data["nombre"] == "Test User"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_missing_email(self, client):
        """Test user creation fails when email is missing"""
        # Given: User data without email
        user_data = {"nombre": "Test User"}

        # When: POST request to /api/v1/users
        response = client.post("/api/v1/users", json=user_data)

        # Then: Returns 400 Bad Request
        assert response.status_code == 400
        
        # Then: Response follows RFC 9457 format
        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "email" in data["detail"].lower()
        assert data["instance"] == "/api/v1/users"
        
    def test_create_user_missing_nombre(self, client):
        """Test user creation fails when nombre is missing"""
        # Given: User data without nombre
        user_data = {"email": "test@example.com"}

        # When: POST request to /api/v1/users
        response = client.post("/api/v1/users", json=user_data)

        # Then: Returns 400 Bad Request
        assert response.status_code == 400
        
        # Then: Response follows RFC 9457 format
        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert "nombre" in data["detail"].lower()
        assert data["instance"] == "/api/v1/users"

    def test_create_user_empty_body(self, client):
        """Test user creation fails when request body is empty JSON object"""
        # When: POST request with empty JSON object
        response = client.post("/api/v1/users", json={})

        # Then: Returns 400 Bad Request (missing required fields)
        assert response.status_code == 400
        
        # Then: Response follows RFC 9457 format
        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Bad Request"
        assert data["status"] == 400
        assert data["instance"] == "/api/v1/users"

    def test_create_user_duplicate_email(self, client):
        """Test user creation fails when email already exists"""
        # Given: An existing user
        existing_user = {
            "email": "duplicate@example.com",
            "nombre": "Existing User"
        }
        response1 = client.post("/api/v1/users", json=existing_user)
        assert response1.status_code == 201

        # When: Attempting to create another user with same email
        duplicate_user = {
            "email": "duplicate@example.com",
            "nombre": "Duplicate User"
        }
        response2 = client.post("/api/v1/users", json=duplicate_user)

        # Then: Returns 409 Conflict
        assert response2.status_code == 409
        
        # Then: Response follows RFC 9457 format
        data = response2.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Conflict"
        assert data["status"] == 409
        assert "duplicate@example.com" in data["detail"]
        assert data["instance"] == "/api/v1/users"


@pytest.mark.contract
class TestGetUsers:
    """Contract tests for GET /api/v1/users/{id}"""

    def test_get_user_success(self, client):
        """Test successful user retrieval with valid ID"""
        # Given: An existing user
        user_data = {
            "email": "get_test@example.com",
            "nombre": "Get Test User"
        }
        create_response = client.post("/api/v1/users", json=user_data)
        assert create_response.status_code == 201
        created_user = create_response.get_json()
        user_id = created_user["id"]

        # When: GET request to /api/v1/users/{id}
        response = client.get(f"/api/v1/users/{user_id}")

        # Then: Returns 200 OK
        assert response.status_code == 200
        
        # Then: Response contains user data
        data = response.get_json()
        assert data is not None
        assert data["id"] == user_id
        assert data["email"] == "get_test@example.com"
        assert data["nombre"] == "Get Test User"
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_user_not_found(self, client):
        """Test user retrieval fails when user does not exist"""
        # Given: A non-existent user ID
        non_existent_id = 99999

        # When: GET request to /api/v1/users/{id}
        response = client.get(f"/api/v1/users/{non_existent_id}")

        # Then: Returns 404 Not Found
        assert response.status_code == 404
        
        # Then: Response follows RFC 9457 format
        data = response.get_json()
        assert data is not None
        assert data["type"] == "about:blank"
        assert data["title"] == "Not Found"
        assert data["status"] == 404
        assert data["instance"] == f"/api/v1/users/{non_existent_id}"


@pytest.mark.contract
class TestRFC9457Compliance:
    """Tests to verify RFC 9457 Problem Details compliance"""

    def test_error_response_content_type_bad_request(self, client):
        """Test that error responses have application/problem+json content-type"""
        # Given: Invalid user data (missing email)
        user_data = {"nombre": "Test User"}

        # When: POST request to /api/v1/users
        response = client.post("/api/v1/users", json=user_data)

        # Then: Content-Type is application/problem+json
        assert response.content_type == "application/problem+json"
        assert response.status_code == 400

    def test_error_response_content_type_conflict(self, client):
        """Test that conflict errors have application/problem+json content-type"""
        # Given: An existing user
        existing_user = {
            "email": "rfc9457_test@example.com",
            "nombre": "Test User"
        }
        response1 = client.post("/api/v1/users", json=existing_user)
        assert response1.status_code == 201

        # When: Attempting to create duplicate user
        duplicate_user = {
            "email": "rfc9457_test@example.com",
            "nombre": "Duplicate User"
        }
        response2 = client.post("/api/v1/users", json=duplicate_user)

        # Then: Content-Type is application/problem+json
        assert response2.content_type == "application/problem+json"
        assert response2.status_code == 409

    def test_error_response_content_type_not_found(self, client):
        """Test that not found errors have application/problem+json content-type"""
        # When: GET request to non-existent user
        response = client.get("/api/v1/users/99999")

        # Then: Content-Type is application/problem+json
        assert response.content_type == "application/problem+json"
        assert response.status_code == 404

