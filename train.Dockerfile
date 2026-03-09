FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages (kept minimal) to support scientific Python stack
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency lock file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project metadata and source
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data

# Default command: run training entrypoint.
# Parameters (csv path, model name, random state) are overridable via CLI args.
ENTRYPOINT ["python", "-m", "src.train_entry"]


