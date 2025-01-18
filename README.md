# Data Engineering Zoomcamp

This repo contains files and notes for the [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by [Datatalks.Club](https://datatalks.club/)

### Environment setup 

You can set it up on your laptop or PC if you prefer to work locally or you can set up a virtual machine in Google Cloud Platform.

In this repo we will use windows + WSL2 locally

For the course you'll need:

* Python 3 
* Google Cloud SDK (explained in module 1)
* Docker with docker-compose
* Terraform (explained in module 1)
* Git account
* Google Cloud Platform account


## Syllabus

### [Module 1: Containerization and Infrastructure as Code](1_Containerization-and-Infrastructure-as-Code/)

* Docker and docker-compose
* Running Postgres in a container
* Ingesting data to Postgres with Python
* Running Postgres and pgAdmin with Docker-compose
* Google Cloud Platform (GCP)
* Terraform
* Setting up infrastructure on GCP with Terraform

### [Module 2: Workflow Orchestration (Kestra)](2_Workflow-Orchestration-(Kestra)/)

* Introduction to Workflow Orchestration
* Introduction to Kestra
* Launch Kestra using Docker Compose
* ETL Pipelines: Load Data to Local Postgres
* ETL Pipelines: Load Data to Google Cloud Platform (GCP)

### [Module 3: Data Warehouse](3_Data-Warehouse/)

* Data Warehouse
* BigQuery
* Partitioning and clustering
* BigQuery best practices
* Internals of BigQuery

### [Module 4: Analytics Engineering](4_Analytics-Engineering/)

* Basics of analytics engineering
* dbt (data build tool)
* BigQuery and dbt
* Postgres and dbt
* dbt models
* Testing and documenting
* Deployment to the cloud and locally
* Visualizing the data with google data studio and metabase

## Extra:

### [Module 2: Workflow Orchestration (Airflow)](2_Workflow-Orchestration-(AirFlow)/)

* Data Lake vs Data Warehouse
* ETL vs ELT
* Introduction to Workflow Orchestration
* Airflow architecture
* Setting up Airflow with Docker
* Ingesting data to local Postgres with Airflow
* Ingesting data to GCP with Airflow
* Airflow 2025
* Airflow with kubernetes
