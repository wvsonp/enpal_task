"""MLflow tracking and registry only — no sklearn/pandas ML logic."""

import json
import os

import mlflow
from dotenv import load_dotenv
from mlflow import MlflowClient
from mlflow.models.signature import infer_signature
from mlflow.sklearn import log_model as sklearn_log_model
from mlflow.tracking.fluent import log_metrics, log_param, start_run


def load_config() -> None:
    """Load .env and set MLflow tracking URI and experiment."""
    load_dotenv()
    uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlruns.db")
    experiment = os.environ.get("MLFLOW_EXPERIMENT_NAME", "churn-prediction")
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(experiment)


def log_run(result: dict, model_name: str):
    """Log run (params, metrics, model), register model. Return ModelVersion."""
    load_config()
    with start_run():
        log_param("random_state", result["random_state"])
        log_param("n_estimators", result["n_estimators"])
        log_param("feature_cols", json.dumps(result["feature_cols"]))
        log_param("csv_path", result["csv_path"])
        log_param("dataset_sha256", result["dataset_sha256"])
        log_metrics(result["metrics"])
        input_example = result["X_train"].head(5)
        signature = infer_signature(
            input_example, result["pipeline"].predict(input_example)
        )
        model_info = sklearn_log_model(
            result["pipeline"],
            name="model",
            input_example=input_example,
            signature=signature,
            registered_model_name=model_name,
        )

    if model_info.registered_model_version is not None:
        return MlflowClient().get_model_version(
            name=model_name, version=str(model_info.registered_model_version)
        )


def set_model_alias(model_name: str, version: int) -> None:  # part of orchestration
    """Set the 'champion' alias to the given model version. Idempotent."""
    MlflowClient().set_registered_model_alias(
        name=model_name, alias="champion", version=str(version)
    )


def load_champion(model_name: str):  # part of deployment
    """Load the model with alias 'champion' from the registry."""
    return mlflow.sklearn.load_model(f"models:/{model_name}@champion")
