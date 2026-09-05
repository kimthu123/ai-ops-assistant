import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

def test_create_ticket():
    response = client.post("/tickets", json={
        "title": "Test ticket",
        "description": "This is a test"
    })
    assert response.status_code == 200

def test_get_ticket():
    response = client.get("/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_ticket_not_found():
    response = client.get("/tickets/999999")
    assert response.status_code == 404

def test_update_ticket():
    response = client.put("/tickets/1", json={
        "title": "Test update ticket",
        "description": "Testing update"
    })
    assert response.json()["title"] == "Test update ticket"
    assert response.status_code == 200

@pytest.mark.skip(reason="Voyage AI free tier rate limit (3 RPM) - chạy local, không chạy trên CI")
def test_create_ticket_with_similar():
    client.post("/tickets", json={
        "title": "Network outage",
        "description": "Office network is completely down"
    })

    response = client.post("/tickets", json={
        "title": "Network down",
        "description": "Internet connection lost in the office"
    })
    assert response.status_code == 200
    assert len(response.json()["similar_tickets"]) > 0