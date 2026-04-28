import pytest
from noshow_iq.api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_predict_returns_risk(client):
    payload = {
        "age": 30, "scholarship": 0, "hipertension": 0,
        "diabetes": 0, "alcoholism": 0, "handcap": 0,
        "sms_received": 1, "days_in_advance": 5,
        "appointment_weekday": 2
    }
    res = client.post("/predict", json=payload)
    data = res.get_json()
    assert "risk_level" in data
    assert data["risk_level"] in ["high", "low"]


def test_predict_has_probability(client):
    payload = {
        "age": 45, "scholarship": 1, "hipertension": 1,
        "diabetes": 0, "alcoholism": 0, "handcap": 0,
        "sms_received": 0, "days_in_advance": 10,
        "appointment_weekday": 3
    }
    res = client.post("/predict", json=payload)
    data = res.get_json()
    assert "probability" in data
    assert 0.0 <= data["probability"] <= 1.0


def test_predict_has_recommendation(client):
    payload = {
        "age": 25, "scholarship": 0, "hipertension": 0,
        "diabetes": 0, "alcoholism": 0, "handcap": 0,
        "sms_received": 1, "days_in_advance": 2,
        "appointment_weekday": 1
    }
    res = client.post("/predict", json=payload)
    data = res.get_json()
    assert "recommendation" in data


def test_history_returns_list(client):
    res = client.get("/history")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_stats_returns_counts(client):
    res = client.get("/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_predictions" in data
