# Variables
image_name := "churn-train:latest"
cluster_name := "dev-cluster"

# Default command: List all available recipes
default:
    @just --list

# ---------------------------------------------------------
# Infrastructure (Kind Cluster)
# ---------------------------------------------------------

# Create the Kind cluster and configure networking/kubeconfig
setup-kind:
    @echo "==> Setting up Kind cluster..."
    ./infra/kind-setup.sh

# ---------------------------------------------------------
# Docker Build & Kind Load
# ---------------------------------------------------------

# Build the Python training Docker image locally
build:
    @echo "==> Building Docker image: {{image_name}}"
    docker build -f train.Dockerfile -t {{image_name}} .

# Build the image and load it into the Kind cluster
load: build
    @echo "==> Loading image {{image_name}} into cluster: {{cluster_name}}"
    kind load docker-image {{image_name}} --name {{cluster_name}}
    @echo "✅ Image successfully loaded into Kind!"

# ---------------------------------------------------------
# Airflow & MLflow Stack (Docker Compose)
# ---------------------------------------------------------

# Start the Docker Compose stack (Airflow, MLflow, Postgres, Minio)
up:
    @echo "==> Starting Docker Compose stack..."
    cd infra && docker compose up -d
    @echo "🚀 Airflow is available at: http://localhost:8080"
    @echo "🚀 MLflow is available at: http://localhost:5000"

# Stop and remove the Docker Compose stack
down:
    @echo "==> Stopping Docker Compose stack..."
    cd infra && docker compose down

# ---------------------------------------------------------
# The Magic Workflow Command
# ---------------------------------------------------------

# Sync local code changes to Kubernetes (Builds & Loads image)
sync: load
    @echo "🔄 Code synced! You can now trigger the DAG 'run_train_container' in Airflow UI."
