# Enpal (MLOps take-home), Masoud Azizi

Small model pipeline that demonstrates moving from "notebook" to "production-like" by considering Mlflow and mlops best practice.

## Setup

- **Python**: requires **3.13+** (see `pyproject.toml`)
- **Install deps (uv)**:

```bash
uv venv --seed
uv sync --dev
```

- **Configure MLflow**:

```bash
cp .env.example .env
(in windows 'copy' instead of 'cp')
```

`.env` defaults:

- `MLFLOW_TRACKING_URI=sqlite:///mlruns.db`
- `MLFLOW_EXPERIMENT_NAME=churn-prediction`

### Why I implemented the Model Registry component

I've chosen the **Model Registry** 
Given the time-box and a static CSV dataset, I implemented the Model Registry as the highest-leverage component: it provides experiment tracking, model versioning, and a clear production contract via the @champion alias. Other components are represented as stubs to show integration points.

I added aliasing to show how it would be connected to Deployment and Orchesteration. It's **not** part of Model Registry Component. Just for demo purpose!

### How to run it (Just to test the registry, it's NOT the complete and real flow)

#### run the full flow (recommended)

Open and run `demo.ipynb`. ! Please make sure the correct version of python path in .venv is selected as notebook kernel ! 
It covers:

- train on `WA_Fn-UseC_-Telco-Customer-C.csv`
- log params/metrics + model to MLflow
- register the model
- promote to `@champion`
- load `@champion` and run inference

#### MLflow UI

To see the logged models and metrics

```bash
uv run mlflow ui --backend-store-uri sqlite:///mlruns.db
```

Then open the MLflow UI to inspect runs, metrics, and the registered model versions.

### What’s in the code

- **Model Registry Component**

```text
Register model versions
Manage production alias

Training / feature engineering (`src/train.py`):
  loads + cleans CSV *
  builds a small feature set (`MonthlyCharges`, `tenure`, ...) 
  trains a sklearn pipeline and returns metrics + artifacts needed for logging

* (in real-setup, it should be part of FS, not training, train should only retrieve features from FS)

MLflow (`src/mlflow_wrapper.py`):
  `log_run(result, model_name)` logs params/metrics and registers the model
  `set_model_alias (model_name, version)` sets registry alias `champion` **
  `load_champion(model_name)` loads `models:/{name}@champion` ***


  **, ***: in prod, not part of Model Registry, rather handled by DAG and Deployment respectively.
  ```

### Other components (stubs / pseudocode)

- **Deployment (CI/CD, conceptual)** (`.github/workflows/deploy.yml`):

```text
Deployment is decoupled from retraining.
It always get model from the registry alias, never from a specific version.

on deploy start:
  pull models:/{MODEL_NAME}@champion from the registry
  package it (e.g., Docker image or model artifact)
  deploy to a serving target
```

- **Feature Store** (`mocked_components/feature_store.py`):

```text
get_features(entity_keys, feature_names):
  # online/offline lookup keyed by entity with Point-In-Time (e.g., customer_id)
  return features_dataframe

push_features(feature_view_name):
  materilize(feature_view_name)
```

- **Monitoring** (`mocked_components/monitoring.py`):

```text
check_drift(reference_data, current_data):
  # distribution tests.
  if drift > threshold: alert()

check_performance(y_true, y_pred):
  # compute metrics; compare to baseline / SLA
  if metric < threshold: alert() 

  alert can trigger DAG for retraining or change alias
```

- **Airflow DAG (conceptual)** (`mocked_components/airflow_dag_mock.py`):

```text
Airflow manages the ML lifecycle, not infrastructure.
It orchestrates: train > evaluate > (gate) > promote
DAG / Pipeline
├─ Train step
│  └─ Log + register model (optionally set alias "challenger")
├─ Evaluation step
│  └─ Compare with current "champion"
└─ Promote step (if passed)
   └─ Set alias "champion"
```

- **Extra Notes**:

```text
I'd include at least unit tests if I'd more time.

For production, I'd use Postgres + S3 store (scalable), FS with online/offline split

skops is prefered over pickle in production for security.

input example is different from signature.

Monitoring closes the loop, by detecting drift or performance degrade and start DAG.
```
