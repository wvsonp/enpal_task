FROM apache/airflow:2.9.1-python3.11

# Install Docker provider so we can use DockerOperator
USER root
RUN pip install --no-cache-dir apache-airflow-providers-docker docker

USER airflow

