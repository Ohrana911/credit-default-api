from pathlib import Path

import joblib


def load_model(model_name: str = "model_v1.joblib"):
    project_root = Path(__file__).resolve().parent.parent
    model_path = project_root / "models" / model_name

    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    return joblib.load(model_path)
