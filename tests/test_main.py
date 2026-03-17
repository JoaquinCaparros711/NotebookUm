import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
