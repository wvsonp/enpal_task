"""Airflow DAG. A real impl. would define tasks with an Airflow DAG object."""

# What Happens in Full:

# Trigger
#   - detect new data (for example new partition on feature store table)
#   - (other triggers are also possible like alert)

# Train and Model Registry
#   - load dataset and computes its hash or version
#   - Calls train.py
#   - Logs parameters, metrics, artifacts to MLflow
#   - Registers a new model version

# Evaluate Task
#   - Compares new model against current @champion
#   - Applies metric thresholds

# Promotion Gate
#   - If evaluation passes > promote to @champion
#   - If not → stop (no deployment impact)
