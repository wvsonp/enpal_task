#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

KIND_NAME="${KIND_CLUSTER_NAME:-dev-cluster}"
KUBECONFIG_DOCKER="$REPO_ROOT/infra/kubeconfig-docker.yaml"

# 1. Create cluster if not exists
if kind get clusters | grep -q "^${KIND_NAME}$"; then
  echo "==> Cluster '$KIND_NAME' already exists, skipping create."
else
  echo "==> Creating Kind cluster '$KIND_NAME'..."
  kind create cluster --name "$KIND_NAME" --config infra/kind-config.yaml
fi

# 2. Prevent the "IsADirectory" bug
if [ -d "$KUBECONFIG_DOCKER" ]; then
  echo "==> Removing stale directory at $KUBECONFIG_DOCKER"
  rm -rf "$KUBECONFIG_DOCKER"
fi

# 3. Get kubeconfig, change IP, and disable TLS verification (Python hack)
echo "==> Writing kubeconfig for Airflow..."
kind get kubeconfig --name "$KIND_NAME" | \
  sed 's/127\.0\.0\.1/host.docker.internal/g' | \
  python3 -c "
import sys, yaml
cfg = yaml.safe_load(sys.stdin)
for cluster in cfg.get('clusters', []):
    if 'certificate-authority-data' in cluster['cluster']:
        del cluster['cluster']['certificate-authority-data']
    cluster['cluster']['insecure-skip-tls-verify'] = True
yaml.dump(cfg, sys.stdout, default_flow_style=False)
" > "$KUBECONFIG_DOCKER"

echo "✅ Kubeconfig written successfully to $KUBECONFIG_DOCKER"

# 4. Connect Kind to the Docker Compose network (mlflow-net)
NETWORK_NAME="mlflow-net"
KIND_NODE="${KIND_NAME}-control-plane"

echo "==> Ensuring Docker network '$NETWORK_NAME' exists..."
docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 || docker network create "$NETWORK_NAME"

echo "==> Connecting Kind node '$KIND_NODE' to network '$NETWORK_NAME'..."
if docker network inspect "$NETWORK_NAME" | grep -q "$KIND_NODE"; then
    echo "✅ Kind is already connected to $NETWORK_NAME."
else
    docker network connect "$NETWORK_NAME" "$KIND_NODE" || true
    echo "✅ Successfully connected Kind to $NETWORK_NAME."
fi