# Data Engineering Zoomcamp 2025

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

### [Module 2: Workflow Orchestration with Kestra](2_Workflow-Orchestration-(Kestra)/)

* Introduction to Workflow Orchestration
* Introduction to Kestra
* Launch Kestra using Docker Compose
* ETL Pipelines: Load Data to Local Postgres
* ETL Pipelines: Load Data to Google Cloud Platform (GCP)

### [Module 3: Data Warehouse with BigQuery](3_Data-Warehouse/)

* OLAP vs OLTP
* Data Warehouse
* BigQuery
* Creating an external table
* Partitioning and clustering
* BigQuery best practices

### [Module 4: Analytics Engineering with dbt](4_Analytics-Engineering/)

* Introduction to analytics engineering
* Introduction to dbt
* Setting up dbt with bigquery
* Development of dbt Models
* Building the model
* Testing and documenting
* Deployment 
* Visualizing the data 

### [Module 5: Batch Processing with spark](5_Batch-Processing-Spark/)

* Introduction to Batch Processing
* Introduction to Spark
* Spark SQL and DataFrames
* Spark Internals
* Running Spark in the Cloud


## Extra:

### [Module 2: Workflow Orchestration with Airflow](2_Workflow-Orchestration-AirFlow/)

* Data Lake vs Data Warehouse
* ETL vs ELT
* Introduction to Workflow Orchestration
* Airflow architecture
* Setting up Airflow with Docker
* Ingesting data to local Postgres with Airflow
* Ingesting data to GCP with Airflow
* Airflow with kubernetes
