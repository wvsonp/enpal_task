"""Stub feature store."""


class FeatureStore:
    def get_features(self, entity_keys, feature_names):
        """Would return a DataFrame of features for the given entity keys (e.g. customer IDs)."""
        pass

    def push_features(self, feature_view_name):
        """Would materilize the feature view."""
        pass


# Full-setup approach:
#   Storage: offline (e.g. DuckDB/Parquet or SQL table) for training; optional online (Redis/DB) for low-latency serving.
#   push_features: e.g. DBT: computes feature view from raw data, writes snapshot keyed by entity (+ optional timestamp for point-in-time).
#   get_features: training uses offline store (full or filtered by entity keys); inference uses online lookup by entity_keys.
#   named feature views; schema/version, git commit hash logged in MLflow with the run for reproducibility.
