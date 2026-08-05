from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to AppLen API"
    }
def test_create_app():
    response = client.post(
        "/apps",
        json={
            "name": "Spotify98765",
            "price": 299
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Spotify98765"
    assert data["price"] == 299
    assert "id" in data