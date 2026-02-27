"""ML logic only"""

import hashlib
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DEFAULT_RANDOM_STATE: int = 42


def load_and_clean(csv_path: str) -> tuple[pd.DataFrame, str]:
    """Read CSV, drop NAs, coerce TotalCharges, drop customerID. Return (DataFrame, dataset_sha256)."""
    path = Path(csv_path)
    raw_bytes = path.read_bytes()
    dataset_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    df = pd.read_csv(csv_path)
    df = df.dropna()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])
    df = df.drop(columns=["customerID"])
    return df, dataset_sha256


def engineer_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Create HighValueFiber, encode Churn, return (X, y, feature_cols)."""
    df = df.copy()
    df["HighValueFiber"] = (
        (df["InternetService"] == "Fiber optic")
        & (df["MonthlyCharges"] > df["MonthlyCharges"].median())
    ).astype(int)
    feature_cols = ["MonthlyCharges", "tenure", "TotalCharges", "HighValueFiber"]
    X = df[feature_cols]
    y = (df["Churn"] == "Yes").astype(int)
    return X, y, feature_cols


def build_pipeline(random_state: int = DEFAULT_RANDOM_STATE) -> Pipeline:
    """Return a scaler + RandomForest pipeline."""
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                RandomForestClassifier(n_estimators=100, random_state=random_state),
            ),
        ]
    )


def train_and_evaluate(
    csv_path: str,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> dict:
    """Orchestrate load, feature engineering, train/test split, fit, evaluate. Return result dict."""
    df, dataset_sha256 = load_and_clean(csv_path)
    X, y, feature_cols = engineer_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    pipeline = build_pipeline(random_state=random_state)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
    }

    return {
        "pipeline": pipeline,
        "X_train": X_train,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "metrics": metrics,
        "feature_cols": feature_cols,
        "csv_path": csv_path,
        "dataset_sha256": dataset_sha256,
        "random_state": random_state,
        "n_estimators": pipeline.get_params()["clf__n_estimators"],
    }
