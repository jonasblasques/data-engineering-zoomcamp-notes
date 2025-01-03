FROM apache/airflow:2.10.4-python3.8

ENV AIRFLOW_HOME=/opt/airflow


# Switch to airflow user to install Python packages
USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]


USER root

# Prepare the environment
WORKDIR $AIRFLOW_HOME
COPY ./google /opt/airflow/google

USER 50000
