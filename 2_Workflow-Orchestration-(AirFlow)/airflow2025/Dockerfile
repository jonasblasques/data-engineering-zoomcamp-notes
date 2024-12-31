FROM apache/airflow:2.10.4-python3.8

ENV AIRFLOW_HOME=/opt/airflow

# Install system dependencies
USER root
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    vim \
    curl \
    tar \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to airflow user to install Python packages
USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary requests

# Install Google Cloud SDK
USER root
ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/opt/google-cloud-sdk
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

RUN curl -fL "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    | tar -xz -C /opt && \
    /opt/google-cloud-sdk/install.sh --quiet

# Prepare the environment
WORKDIR $AIRFLOW_HOME

COPY scripts scripts
COPY ./google /opt/airflow/google
RUN chmod +x scripts

USER $AIRFLOW_UID
