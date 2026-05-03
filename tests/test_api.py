import pytest

from src.api import app


@pytest.fixture()
def client():
    app.config.update({"TESTING": True})
    return app.test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_predict_v1_success(client):
    payload = {
        "LIMIT_BAL": 20000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 24,
        "PAY_0": 2,
        "PAY_2": 2,
        "PAY_3": -1,
        "PAY_4": -1,
        "PAY_5": -2,
        "PAY_6": -2,
        "BILL_AMT1": 3913,
        "BILL_AMT2": 3102,
        "BILL_AMT3": 689,
        "BILL_AMT4": 0,
        "BILL_AMT5": 0,
        "BILL_AMT6": 0,
        "PAY_AMT1": 0,
        "PAY_AMT2": 689,
        "PAY_AMT3": 0,
        "PAY_AMT4": 0,
        "PAY_AMT5": 0,
        "PAY_AMT6": 0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json
    assert data["model_version"] == "v1"
    assert data["prediction"] in (0, 1)
    assert 0.0 <= data["default_probability"] <= 1.0


def test_predict_v2_success(client):
    payload = {
        "model_version": "v2",
        "LIMIT_BAL": 20000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 24,
        "PAY_0": 2,
        "PAY_2": 2,
        "PAY_3": -1,
        "PAY_4": -1,
        "PAY_5": -2,
        "PAY_6": -2,
        "BILL_AMT1": 3913,
        "BILL_AMT2": 3102,
        "BILL_AMT3": 689,
        "BILL_AMT4": 0,
        "BILL_AMT5": 0,
        "BILL_AMT6": 0,
        "PAY_AMT1": 0,
        "PAY_AMT2": 689,
        "PAY_AMT3": 0,
        "PAY_AMT4": 0,
        "PAY_AMT5": 0,
        "PAY_AMT6": 0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json
    assert data["model_version"] == "v2"
    assert data["prediction"] in (0, 1)
    assert 0.0 <= data["default_probability"] <= 1.0


def test_predict_missing_fields(client):
    response = client.post("/predict", json={"LIMIT_BAL": 20000})
    assert response.status_code == 400
    assert "missing_fields" in response.json


def test_predict_invalid_json(client):
    response = client.post(
        "/predict",
        data="not-json",
        content_type="application/json",
    )
    assert response.status_code == 400


def test_predict_unknown_model_version(client):
    payload = {
        "model_version": "v3",
        "LIMIT_BAL": 20000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 24,
        "PAY_0": 2,
        "PAY_2": 2,
        "PAY_3": -1,
        "PAY_4": -1,
        "PAY_5": -2,
        "PAY_6": -2,
        "BILL_AMT1": 3913,
        "BILL_AMT2": 3102,
        "BILL_AMT3": 689,
        "BILL_AMT4": 0,
        "BILL_AMT5": 0,
        "BILL_AMT6": 0,
        "PAY_AMT1": 0,
        "PAY_AMT2": 689,
        "PAY_AMT3": 0,
        "PAY_AMT4": 0,
        "PAY_AMT5": 0,
        "PAY_AMT6": 0,
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert response.json["error"] == "Unknown model_version"
