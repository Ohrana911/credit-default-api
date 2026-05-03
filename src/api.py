import json
import logging
import sys
import time
from datetime import datetime, timezone

from flask import Flask, jsonify, request
import pandas as pd

try:
    from src.model import load_model
except ModuleNotFoundError:
    from model import load_model

app = Flask(__name__)
MODELS = {
    "v1": load_model("model_v1.joblib"),
    "v2": load_model("model_v2.joblib"),
}

logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stream_handler)
logger.propagate = False

FEATURE_COLUMNS = [
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
]


def log_event(event_type: str, status_code: int, response_body: dict) -> None:
    payload = request.get_json(silent=True)
    log_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "path": request.path,
        "method": request.method,
        "status_code": status_code,
        "request_payload": payload,
        "response_body": response_body,
        "duration_ms": round((time.perf_counter() - request.start_time) * 1000, 2),
    }
    logger.info(json.dumps(log_record, ensure_ascii=False))


@app.before_request
def before_request():
    request.start_time = time.perf_counter()


@app.get("/health")
def health():
    response_body = {"status": "ok"}
    log_event(event_type="health_check", status_code=200, response_body=response_body)
    return jsonify(response_body), 200


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    if payload is None:
        response_body = {"error": "Request body must be valid JSON"}
        log_event(event_type="prediction", status_code=400, response_body=response_body)
        return jsonify(response_body), 400

    model_version = payload.get("model_version", "v1")
    if model_version not in MODELS:
        response_body = {
            "error": "Unknown model_version",
            "allowed_versions": list(MODELS.keys()),
        }
        log_event(event_type="prediction", status_code=400, response_body=response_body)
        return jsonify(response_body), 400

    missing = [col for col in FEATURE_COLUMNS if col not in payload]
    if missing:
        response_body = {"error": "Missing required fields", "missing_fields": missing}
        log_event(event_type="prediction", status_code=400, response_body=response_body)
        return (
            jsonify(response_body),
            400,
        )

    input_df = pd.DataFrame([{col: payload[col] for col in FEATURE_COLUMNS}])
    model = MODELS[model_version]
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0][1])

    response_body = {
        "model_version": model_version,
        "prediction": prediction,
        "default_probability": round(probability, 6),
    }
    log_event(event_type="prediction", status_code=200, response_body=response_body)
    return jsonify(response_body), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
