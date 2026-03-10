"""Run training in a Kubernetes pod (same image as prod). No Docker socket."""

from datetime import datetime

from airflow import DAG  # type: ignore
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator  # type: ignore

# Shared task spec: same image and args in dev (Kind) and prod (real K8s).
TRAIN_IMAGE = "churn-train:latest"
TRAIN_ARGS = [
    "--csv-path", "data/WA_Fn-UseC_-Telco-Customer-C.csv",
    "--model-name", "churn-predictor",
    "--random-state", "42",
]
# Pod must reach MLflow. In dev, MLflow is on host:5000; use host.docker.internal.
TRAIN_ENV = {
    "MLFLOW_TRACKING_URI": "http://mlflow-server:5000",
    "MLFLOW_EXPERIMENT_NAME": "churn-prediction",
    "MLFLOW_S3_ENDPOINT_URL": "http://host.docker.internal:9000",
    "AWS_ACCESS_KEY_ID": "mlflow_minio_user",
    "AWS_SECRET_ACCESS_KEY": "minio123"
}

with DAG(
    dag_id="run_train_container_v3",
    description=(
        "Run the training container in Kubernetes (Kind locally, same operator in prod). "
        "Image: train.Dockerfile → src.train_entry; logs to MLflow."
    ),
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    run_train = KubernetesPodOperator(
        task_id="run_train",
        image=TRAIN_IMAGE,
        arguments=TRAIN_ARGS,
        env_vars=TRAIN_ENV,
        namespace="default",
        name="train-churn",
        get_logs=True,
        config_file="/opt/airflow/kubeconfig-docker.yaml",
        image_pull_policy="Never",
        # In-cluster (prod) would omit config_file and use Airflow's K8s connection.
    )
