import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    return app.test_client()


def test_chat_endpoint_returns_response_from_gemma(client):
    """User sends a message and receives a response from Gemma model"""
    # Arrange
    user_message = {"message": "Hello, what is 2+2?"}
    
    # Act
    response = client.post("/api/chat", json=user_message)
    
    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0
    assert "Hello, what is 2+2?" in data["response"]
