from fastapi import status
from fastapi.testclient import TestClient


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["message"] == "Hello World"
    assert "current_time" in response_json
    assert "current_uptime" in response_json
