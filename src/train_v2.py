from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "UCI_Credit_Card.csv"
    model_path = project_root / "models" / "model_v2.joblib"

    df = pd.read_csv(data_path)

    if "ID" in df.columns:
        df = df.drop(columns=["ID"])

    target_col = "default.payment.next.month"
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=80,
        max_depth=12,
        min_samples_leaf=5,
        max_features="sqrt",
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"Model saved to: {model_path}")
    print(f"F1-score: {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")


if __name__ == "__main__":
    main()
