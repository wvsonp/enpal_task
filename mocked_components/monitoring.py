"""Stub model monitoring"""


class ModelMonitor:
    """Real impl would compare reference vs current data and alert on drift/regression."""

    def check_drift(self, reference_data, current_data, feature_names=None):
        """Would run statistical drift tests and return drift scores or alerts."""
        pass

    def check_performance(self, y_true, y_pred, metrics=None):
        """Would compute metrics and compare to baseline, triggering alerts if below threshold."""
        pass
