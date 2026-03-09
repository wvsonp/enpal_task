from datetime import datetime

from airflow import DAG  # type: ignore
from airflow.providers.docker.operators.docker import DockerOperator  # type: ignore


with DAG(
    dag_id="run_train_container",
    description=(
        "Run a pre-built training container image that "
        "executes src.train_entry and logs to MLflow."
    ),
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:
    run_train_container = DockerOperator(
        task_id="run_train_container",
        image="churn-train:latest",
        docker_url="unix://var/run/docker.sock",
        network_mode="mlflow-net",
        auto_remove=True,
        command=None,
    )

