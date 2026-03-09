FROM apache/airflow:2.9.1-python3.11

# Install Docker provider and Postgres driver (must run as airflow user)
USER airflow
RUN pip install --no-cache-dir apache-airflow-providers-docker docker psycopg2-binary

