"""CLI entrypoint for training + MLflow logging.

Designed so the same container can be triggered manually or by Airflow.
"""

import argparse

from src.train import train_and_evaluate
from src.mlflow_wrapper import log_run, set_model_alias


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train churn model and log to MLflow.")
    parser.add_argument(
        "--csv-path",
        default="data/WA_Fn-UseC_-Telco-Customer-C.csv",
        help="Path to training CSV inside the container.",
    )
    parser.add_argument(
        "--model-name",
        default="churn-predictor",
        help="Registered model name in MLflow.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for training.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    result = train_and_evaluate(
        csv_path=args.csv_path,
        random_state=args.random_state,
    )
    model_version = log_run(result, args.model_name)
    set_model_alias(args.model_name, int(model_version.version))

    print("Run ID:", model_version.run_id)
    print("Model version:", model_version.version)


if __name__ == "__main__":
    main()

