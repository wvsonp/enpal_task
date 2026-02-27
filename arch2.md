# Architecture

## System Overview

```mermaid
flowchart TB
    subgraph Orchestration["Orchestration (Airflow DAG)"]
        direction LR
        Trigger["Trigger<br/>(new data, alert)"]
        TrainTask["Train Task"]
        EvalTask["Evaluate Task"]
        PromoGate["Promotion Gate"]
        Trigger --> TrainTask --> EvalTask --> PromoGate
        TrainTask --> TrainPy["train.py"]
        EvalTask --> Compare["compare new vs<br/>current champion"]
        PromoGate --> Alias["set @champion<br/>alias if passed"]
    end

    subgraph FeatureStore["Feature Store"]
        FS["mocked_components/feature_store.py"]
        Get["get_features(entity, feature_names)"]
        Push["push_features(view)"]
        FS --> Get
        FS --> Push
        note["(online / offline lookup by entity key)"]
    end

    subgraph ModelRegistry["Model Registry (MLflow)"]
        MR["src/mlflow_wrapper.py"]
        LogRun["log_run()<br/>├ params & metrics<br/>├ model artifact<br/>└ register version"]
        SetAlias["set_model_alias()<br/>└ @champion promotion"]
        LoadChamp["load_champion()<br/>└ models:/{name}@champion"]
        MR --> LogRun
        MR --> SetAlias
        MR --> LoadChamp
    end

    subgraph Deployment["Deployment (CI/CD)"]
        Deploy[" .github/workflows/deploy.yml"]
        DeploySteps["pull @champion from registry<br/>package (e.g. Docker image)<br/>deploy to serving target"]
        Deploy --> DeploySteps
    end

    subgraph Monitoring["Monitoring"]
        Mon["mocked_components/monitoring.py"]
        Drift["check_drift(ref, current)"]
        Perf["check_performance(y_true, y_pred)"]
        Alert["drift / perf drop → alert<br/>└ triggers retraining"]
        Mon --> Drift
        Mon --> Perf
        Mon --> Alert
    end

    Orchestration --> FeatureStore
    Orchestration --> ModelRegistry
    ModelRegistry -->|"pulls @champion"| Deployment
    Deployment -->|"serves predictions"| Monitoring
```

## Data & Training Flow

```mermaid
flowchart LR
    subgraph CSV["CSV dataset"]
        Data["Telco-Customer-Churn.csv<br/>data/"]
    end

    subgraph FeatureEng["Feature Engineering"]
        Load["load_and_clean()"]
        Engineer["engineer_features()"]
        Feats["Features:<br/>MonthlyCharges, tenure,<br/>TotalCharges, HighValueFiber"]
        Load --> Engineer --> Feats
    end

    subgraph ModelTrain["Model Training"]
        Pipeline["build_pipeline()<br/>StandardScaler<br/>RandomForest (n=100)"]
        Split["train_test_split (80/20)"]
        Pipeline --> Split
    end

    subgraph Eval["Evaluate"]
        Metrics["accuracy, precision<br/>recall, f1"]
    end

    subgraph MLflow["MLflow log_run()"]
        Log["log params<br/>log metrics<br/>log model<br/>register version"]
    end

    CSV --> FeatureEng --> ModelTrain --> Eval --> MLflow
```

## Component Status

| Component | Status | Location |
|---|---|---|
| Training / Feature Eng. | **Implemented** | `src/train.py` |
| Model Registry (MLflow) | **Implemented** | `src/mlflow_wrapper.py` |
| Feature Store | Stub | `mocked_components/feature_store.py` |
| Monitoring | Stub | `mocked_components/monitoring.py` |
| Orchestration (Airflow) | Stub | `mocked_components/airflow_dag_mock.py` |
| Deployment (CI/CD) | Stub | `.github/workflows/deploy.yml` |

## Mapping to Task Requirements

| Task | Delivered by | Role of Training |
|------|--------------|------------------|
| **1. Model Registry** | Model Registry (MLflow) | Training produces the model that gets logged (version, metrics, params, timestamp) and registered. |
| **2. Feature Store** | Feature Store | Supplies features for both training and inference; Training (and Orchestration) consume them. |
| **3. Monitoring** | Monitoring | Tracks inference volume, latency, performance/drift; alerts can trigger retraining. |
| **4. Orchestration** | Orchestration (Airflow) | Runs the **retraining pipeline**: trigger → **Train Task** (training step) → evaluate → register new version. Training is the ML step inside this pipeline. |
| **5. Deployment** | Deployment (CI/CD) | Containerized inference; pulls `@champion` from registry. No direct link to Training. |

So the **Training** component is logical: it is the retraining step (task 4) and the producer of models for the Registry (task 1).

## Key Design Decisions

- **Deployment is decoupled from retraining** -- the deploy step always pulls from the `@champion` registry alias, never a specific version.
- **Orchestration owns the lifecycle** -- Airflow manages train > evaluate > promote; infrastructure concerns stay separate.
- **Monitoring closes the loop** -- drift or performance degradation triggers alerts that can kick off a new DAG run.
