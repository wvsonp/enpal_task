# Local dev runbook (Kind + Airflow)

Same operator everywhere: training runs in Kubernetes locally (Kind) and in prod.

## Prerequisites

- Docker
- [kind](https://kind.sigs.k8s.io/) installed (`go install sigs.k8s.io/kind@latest` or see kind docs)

## One-time: create Kind cluster and kubeconfig

From the **repo root**:

```bash
./infra/kind-setup.sh
```

This will:

1. Create a Kind cluster `dev-cluster` using `infra/kind-config.yaml`
2. Build `churn-train:latest` from `train.Dockerfile` and load it into Kind
3. Write `infra/kubeconfig-docker.yaml` so the Airflow container can talk to Kind (127.0.0.1 → host.docker.internal)

## Start the stack

```bash
cd infra
docker compose up -d
```

- Airflow: http://localhost:8080 (no Docker socket; no DOCKER_GID)
- MLflow: http://localhost:5000

## Trigger training

1. In Airflow UI, open the DAG **run_train_container**
2. Trigger it manually (no schedule)
3. The **run_train** task runs `churn-train:latest` as a pod in Kind; the pod logs to MLflow at `http://host.docker.internal:5000`

## Prod

Use the same DAG and `KubernetesPodOperator`. In prod:

- Omit `config_file` (or set it from a secret) and use Airflow’s Kubernetes connection / in-cluster config
- Point `TRAIN_IMAGE` to your registry (e.g. `myreg/churn-train:<tag>`)
- Set `TRAIN_ENV["MLFLOW_TRACKING_URI"]` to your prod MLflow URL
