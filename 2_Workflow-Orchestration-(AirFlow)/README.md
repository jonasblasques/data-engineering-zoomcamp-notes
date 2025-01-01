# Workflow Orchestration

- [Airflow 2022](#airflow-2022)
    - [Data Lake vs Data Warehouse](#data-lake-vs-data-warehouse)
    - [ETL vs ELT](#etl-vs-elt)
    - [Introduction to Workflow Orchestration](#introduction-to-workflow-orchestration)
    - [Airflow architecture](#airflow-architecture)
    - [Setting up Airflow with Docker (lite version)](#setting-up-airflow-with-docker-lite-version)
    - [Ingesting data to local Postgres with Airflow](#ingesting-data-to-local-postgres-with-airflow)
    - [Ingesting data to GCP with Airflow](#ingesting-data-to-gcp-with-airflow)
- [Airflow 2025](#airflow-2025)
    - [Setting up Airflow 2.10.4 with Docker](#setting-up-airflow-2104-with-docker)
    - [Ingesting data to local Postgres new version](#ingesting-data-to-local-postgres-new-version)
    - [Ingesting data to GCP new version](#ingesting-data-to-gcp-new-version)

    


## Data Lake vs Data Warehouse

**Data Lake:**

- Purpose: Stores raw, unprocessed data from various sources, often for exploratory or advanced analytics.
- Data Format: Stores data in its original format (structured, semi-structured, or unstructured).
- Schema: Schema-on-read approach, meaning the schema is applied when the data is read, not when it is stored.
- Scalability: Highly scalable, designed for big data and low-cost storage.
- Users: Used by data scientists and engineers for machine learning, advanced analytics, and experimentation.
- Tools: Commonly associated with platforms like Google Cloud Storage, Amazon S3, or Azure Data Lake.

**Data Warehouse:**

- Purpose: Stores structured and cleaned data optimized for querying and reporting.
- Data Format: Stores structured and pre-processed data.
- Schema: Schema-on-write approach, meaning the schema is defined when the data is loaded into the warehouse.
- Performance: Optimized for complex SQL queries and business intelligence (BI) tools.
- Users: Used by analysts and business users for reporting and decision-making.
- Tools: Examples include Snowflake, Amazon Redshift, Google BigQuery, or Microsoft Azure Synapse.


## ETL vs ELT

**ETL (Extract, Transform, Load):**

Process Order:

- Extract: Data is extracted from source systems.
- Transform: Data is processed and transformed into a desired format or schema.
- Load: The transformed data is loaded into the destination (e.g., a data warehouse).

When to Use:

Ideal for traditional data warehouses where structured data is required upfront.

Performance:

Transformation happens before loading, so processing can take longer.

**ELT (Extract, Load, Transform):**

Process Order:

- Extract: Data is extracted from source systems.
- Load: The raw data is loaded into the destination (e.g., a data lake).
- Transform: Transformation happens after loading, within the storage system using its compute resources.

When to Use:

Suitable for modern architectures (e.g., data lakes or cloud-native data warehouses) where raw data can be transformed as needed.

Performance:

Leverages the power of the destination system to perform transformations, which can scale better for large datasets.

Tools:

Cloud-native tools like Apache Spark, dbt, or Google Dataflow are common for ELT pipelines.



## Module 1 recap

In the previous lesson we saw the definition of data pipeline and we created a pipeline script that downloaded a CSV and processed it so that we could ingest it to Postgres. This is what our pipeline looked like:

![pipeline1](images/pipeline1.jpg)


The script we created is an example of how NOT to create a pipeline, because it contains 2 steps which could otherwise be separated (downloading and processing). The reason is that if we're simply testing the script, it will have to download the CSV file every single time that we run the script, which is less than ideal. Another reason, for example if the internet is not available, the entire script will fail.

This week we will work on a slightly more complex pipeline. This will involve extracting data from the web. Convert this CSV to a more effective format - parquet. We'll take this file and upload to Google Cloud Storage (data lake). Finally we'll create an external table in Google BigQuery:


![pipeline2](images/pipeline2.jpg)


## Introduction to Workflow Orchestration

Workflow Orchestration refers to the process of organizing, managing, and automating complex workflows, where multiple tasks or processes are coordinated to achieve a specific outcome. It involves ensuring that tasks are executed in the correct order, handling dependencies between them, and managing resources or systems involved in the workflow.

Key characteristics of workflow orchestration include:

- Task Coordination: Ensuring tasks are executed in the right sequence or simultaneously, based on predefined rules or dependencies.

- Automation: Automating repetitive or complex processes to reduce manual intervention and improve efficiency.

- Error Handling: Managing errors or failures in tasks, often with retry mechanisms or alternative execution paths.

- Resource Management: Allocating resources (e.g., computing power, APIs, or data) to tasks as needed.

- Monitoring and Reporting: Tracking the progress of workflows, identifying bottlenecks, and providing logs or reports for analysis.

Workflow orchestration is commonly used in areas like cloud computing, data processing, DevOps, and business process automation. 

Popular tools for workflow orchestration include Apache Airflow, Kubernetes, AWS Step Functions, Prefect and Kestra. These tools help streamline and standardize complex workflows across multiple systems or environments.

## Airflow architecture

Apache Airflow® is an open-source platform for developing, scheduling, and monitoring batch-oriented workflows

Airflow is a platform that lets you build and run workflows. A workflow is represented as a DAG (a Directed Acyclic Graph), and contains individual pieces of work called Tasks, arranged with dependencies and data flows taken into account.

A DAG specifies the dependencies between tasks, which defines the order in which to execute the tasks. Tasks describe what to do, be it fetching data, running analysis, triggering other systems, or more

#### Airflow components

A minimal Airflow installation consists of the following components:

- A scheduler, which handles both triggering scheduled workflows, and submitting Tasks to the executor to run. The executor, is a configuration property of the scheduler, not a separate component and runs within the scheduler process. There are several executors available out of the box, and you can also write your own.

- A webserver, which presents a handy user interface to inspect, trigger and debug the behaviour of DAGs and tasks.

- A folder of DAG files, which is read by the scheduler to figure out what tasks to run and when to run them.

- A metadata database, which airflow components use to store state of workflows and tasks. Setting up a metadata database is described in Set up a Database Backend and is required for Airflow to work

Optional components:

- Optional worker, which executes the tasks given to it by the scheduler. In the basic installation worker might be part of the scheduler not a separate component. It can be run as a long running process in the CeleryExecutor, or as a POD in the KubernetesExecutor.
- Optional folder of plugins. Plugins are a way to extend Airflow’s functionality (similar to installed packages). Plugins are read by the scheduler, dag processor, triggerer and webserver

#### DAGS

A DAG (Directed Acyclic Graph) is the core concept of Airflow, collecting Tasks together, organized with dependencies and relationships to say how they should run.

Here’s a basic example DAG:

![airflow5](images/airflow5.jpg)

It defines four Tasks - A, B, C, and D - and dictates the order in which they have to run, and which tasks depend on what others. It will also say how often to run the DAG - maybe “every 5 minutes starting tomorrow”, or “every day since January 1st, 2020”.

The DAG itself doesn’t care about what is happening inside the tasks; it is merely concerned with how to execute them - the order to run them in, how many times to retry them, if they have timeouts, and so on

#### Declaring a DAG

There are three ways to declare a DAG.

**1: with statement** 

```python
 import datetime

 from airflow import DAG
 from airflow.operators.empty import EmptyOperator

 with DAG(
     dag_id="my_dag_name",
     start_date=datetime.datetime(2021, 1, 1),
     schedule="@daily",
 ):
     EmptyOperator(task_id="task")
```    

**2: standard constructor, passing the DAG into any operators you use**

```python
 import datetime

 from airflow import DAG
 from airflow.operators.empty import EmptyOperator

 my_dag = DAG(
     dag_id="my_dag_name",
     start_date=datetime.datetime(2021, 1, 1),
     schedule="@daily",
 )
 EmptyOperator(task_id="task", dag=my_dag)
 ```

 **3: @dag decorator to turn a function into a DAG generator**

 ```python
 import datetime

from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator


@dag(start_date=datetime.datetime(2021, 1, 1), schedule="@daily")
def generate_dag():
    EmptyOperator(task_id="task")


generate_dag()
```

DAGs are nothing without Tasks to run, and those will usually come in the form of either Operators, Sensors or TaskFlow

#### Loading DAGs

Airflow loads DAGs from Python source files, which it looks for inside its configured DAG_FOLDER. It will take each file, execute it, and then load any DAG objects from that file.

This means you can define multiple DAGs per Python file, or even spread one very complex DAG across multiple Python files using imports.

#### Running DAGs

There are 2 main ways to run DAGs:

- **Triggering them manually via the web UI or programatically via API:** The Airflow web interface allows users to manually trigger the execution of a DAG. This is often used when you want to run a specific DAG outside of its scheduled time, for example, to run an ad-hoc task or for testing purposes. In the web UI, you can simply click the "Trigger Dag" button next to the DAG you want to execute, which will start its execution immediately.

- **Scheduling them:** Airflow allows you to schedule DAGs to run automatically at specific intervals. This is the most common way of running DAGs, as it enables them to execute regularly without manual intervention. You define the schedule using a cron expression or a predefined schedule like @daily, @hourly, etc., in the DAG definition. Once scheduled, Airflow's scheduler will monitor the DAG and trigger the tasks based on the defined schedule, ensuring that they run at the right times.

### DAG Runs

A DAG Run is an object representing an instantiation of the DAG in time. Any time the DAG is executed, a DAG Run is created and all tasks inside it are executed. The status of the DAG Run depends on the tasks states. Each DAG Run is run separately from one another, meaning that you can have many runs of a DAG at the same time.

A DAG Run status is determined when the execution of the DAG is finished. 

There are two possible terminal states for the DAG Run:

- success if all of the leaf nodes states are either success or skipped,

- failed if any of the leaf nodes state is either failed or upstream_failed.

#### Tasks

A Task is the basic unit of execution in Airflow. Tasks are arranged into DAGs, and then have upstream and downstream dependencies set between them in order to express the order they should run in.

There are three basic kinds of Task:

- Operators, predefined task templates that you can string together quickly to build most parts of your DAGs.

- Sensors, a special subclass of Operators which are entirely about waiting for an external event to happen.

- A TaskFlow-decorated @task, which is a custom Python function packaged up as a Task.

#### Operators

An Operator is conceptually a template for a predefined Task, that you can just define declaratively inside your DAG:

```python
with DAG("my-dag") as dag:
    ping = HttpOperator(endpoint="http://example.com/update/")
    email = EmailOperator(to="admin@example.com", subject="Update complete")

    ping >> email
```

Airflow has a very extensive set of operators available, with some built-in to the core or pre-installed providers. Some popular operators from core include:

- BashOperator - executes a bash command

- PythonOperator - calls an arbitrary Python function

- EmailOperator - sends an email

#### Executor

Executors are the mechanism by which task instances get run. Executors are set by the executor option in the [core] section of the configuration file.

There are two types of executors - those that run tasks locally (inside the scheduler process), and those that run their tasks remotely (usually via a pool of workers). 

**Local Executors**

Airflow tasks are run locally within the scheduler process.

Pros: Very easy to use, fast, very low latency, and few requirements for setup.

Cons: Limited in capabilities and shares resources with the Airflow scheduler.

Examples: Local Executor, Sequential Executor

**Remote Executors**

Remote executors can further be divided into two categories:

1. Queued/Batch Executors

Airflow tasks are sent to a central queue where remote workers pull tasks to execute. Often workers are persistent and run multiple tasks at once.

Pros: More robust since you’re decoupling workers from the scheduler process. Workers can be large hosts that can churn through many tasks (often in parallel) which is cost effective. Latency can be relatively low since workers can be provisioned to be running at all times to take tasks immediately from the queue.

Cons: Shared workers have the noisy neighbor problem with tasks competing for resources on the shared hosts or competing for how the environment/system is configured. They can also be expensive if your workload is not constant, you may have workers idle, overly scaled in resources, or you have to manage scaling them up and down.

Examples: CeleryExecutor, BatchExecutor

2. Containerized Executors

Airflow tasks are executed ad hoc inside containers/pods. Each task is isolated in its own containerized environment that is deployed when the Airflow task is queued.

Pros: Each Airflow task is isolated to one container so no noisy neighbor problem. The execution environment can be customized for specific tasks (system libs, binaries, dependencies, amount of resources, etc). Cost effective as the workers are only alive for the duration of the task.

Cons: There is latency on startup since the container or pod needs to deploy before the task can begin. Can be expensive if you’re running many short/small tasks. No workers to manage however you must manage something like a Kubernetes cluster.

Examples: KubernetesExecutor, EcsExecutor


#### References

For more info, check out official docs:

https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html





## Setting up Airflow with Docker (lite version)

This is a quick, simple & less memory-intensive setup of Airflow that works on a LocalExecutor.

Only runs the webserver and the scheduler and runs the DAGs in the scheduler rather than running them in external workers:

**1:** Create a new sub-directory called airflow in your project dir. Inside airflow create dags, google, logs and scripts folders.

The directory structure should look like this:

```

├── airflow
│   ├── dags
│       ├── data_ingestion_local.py
│       ├── data_ingestion_gcp.py
│       └── ingest_script.py
│   ├── google
│       └── credentials.json
│   ├── logs
│   └── scripts
│       └── entrypoint.sh
├── .env
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
```


**2:** Create a Dockerfile. Should look like:

```dockerfile

# First-time build can take upto 10 mins.

FROM apache/airflow:2.2.3

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim -qqq
# git gcc g++ -qqq

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary requests

# Ref: https://airflow.apache.org/docs/docker-stack/recipes.html

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk

ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
       --bash-completion=false \
       --path-update=false \
       --usage-reporting=false \
       --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version

WORKDIR $AIRFLOW_HOME

COPY scripts scripts
COPY ./google /opt/airflow/google
RUN chmod +x scripts

USER $AIRFLOW_UID
```

**3:** Create a Docker-compose.yaml. Should look like:

```yaml

version: '3'
services:
    postgres:
        image: postgres:13
        env_file:
            - .env
        volumes:
            - postgres-db-volume:/var/lib/postgresql/data
        healthcheck:
            test: ["CMD", "pg_isready", "-U", "airflow"]
            interval: 5s
            retries: 5

    scheduler:
        build: .
        command: scheduler
        depends_on:
            - postgres
        env_file:
            - .env
        environment:
        - GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/google/zoomcamp-airflow-444903-33738e1bcf7e.json  
        - AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud://zoomcamp-airflow-444903//opt/airflow/google/zoomcamp-airflow-444903-33738e1bcf7e.json           
        volumes:
            - ./dags:/opt/airflow/dags
            - ./logs:/opt/airflow/logs
            - ./plugins:/opt/airflow/plugins
            - ./scripts:/opt/airflow/scripts
            - ./google:/opt/airflow/google:ro


    webserver:
        build: .
        entrypoint: ./scripts/entrypoint.sh
        depends_on:
            - postgres
            - scheduler
        env_file:
            - .env
        environment:
        - GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/google/zoomcamp-airflow-444903-33738e1bcf7e.json   
        - AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud://zoomcamp-airflow-444903//opt/airflow/google/zoomcamp-airflow-444903-33738e1bcf7e.json          
        volumes:
            - ./dags:/opt/airflow/dags
            - ./logs:/opt/airflow/logs
            - ./plugins:/opt/airflow/plugins
            - ./google:/opt/airflow/google:ro
            - ./scripts:/opt/airflow/scripts

        user: "${AIRFLOW_UID:-50000}:0"
        ports:
            - "8080:8080"
        healthcheck:
            test: [ "CMD-SHELL", "[ -f /home/airflow/airflow-webserver.pid ]" ]
            interval: 30s
            timeout: 30s
            retries: 3

volumes:
  postgres-db-volume:
```  

In this part, make sure to modify with your project id and your json file:

```yaml
        environment:
        - GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/google/your_credentials.json  
        - AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=google-cloud://YOUR_PROJECT_ID//opt/airflow/google/your_credentials.json 
```        


**4:** Create a  .env file, should look like:

```dockerfile
# Custom
COMPOSE_PROJECT_NAME=dtc-de
GOOGLE_APPLICATION_CREDENTIALS=.google/zoomcamp-airflow-444903-33738e1bcf7e.json
AIRFLOW_UID=50000
GCP_PROJECT_ID=zoomcamp-airflow-444903
GCP_GCS_BUCKET=zoomcamp_datalake
BIGQUERY_DATASET=zoomcamp_bigquery

# Postgres
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__SCHEDULER__SCHEDULER_HEARTBEAT_SEC=10

AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
AIRFLOW_CONN_METADATA_DB=postgres+psycopg2://airflow:airflow@postgres:5432/airflow
AIRFLOW_VAR__METADATA_DB_SCHEMA=airflow

_AIRFLOW_WWW_USER_CREATE=True
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=True
AIRFLOW__CORE__LOAD_EXAMPLES=False
```


**IMPORTANT:**
Make sure to modify GCP_PROJECT_ID, GCP_GCS_BUCKET and BIGQUERY_DATASET with your project id, bucket name and big query dataset_id defined in the terraform file

For example my terraform file looks like:

```
resource "google_storage_bucket" "data-lake-bucket" {
  name          = "zoomcamp_datalake"
  location      = "US"

...}  

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "zoomcamp_bigquery"
  project    = "zoomcamp-airflow-444903"
  location   = "US"
}
```  

**5:** Create a entrypoint.sh inside scripts folder, should look like:

```dockerfile
#!/usr/bin/env bash
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
export AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT=${AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT}

airflow db upgrade

airflow users create -r Admin -u admin -p admin -e admin@example.com -f admin -l airflow
# "$_AIRFLOW_WWW_USER_USERNAME" -p "$_AIRFLOW_WWW_USER_PASSWORD"

airflow webserver
```

The script serves as the entry point for initializing and running an Airflow application inside a container. It ensures the proper setup of environment variables, upgrades the Airflow database, creates a default admin user, and starts the Airflow webserver.


**6:** Copy your google-credentials.json inside the google folder. Remember to add this json to the .gitignore file !


**7:** Create a requirements.txt, should look like:

```
apache-airflow-providers-google
pyarrow
```


**8:** Build the image. It may take several minutes You only need to do this the first time you run Airflow or if you modified the Dockerfile or the requirements.txt file:

```
    docker-compose build
```

**9:** Run Airflow:    

```
    docker-compose up -d
```

**10:** You may now access the Airflow GUI by browsing to localhost:8080. 

It may take a few minutes to load the webApp

```
Username: airflow
Password: airflow 
```


## Database error. Make database migrations:

Airflow database migrations may not have run successfully. You need to make sure that your Airflow tables are properly created and updated. Run the following command to initialize or update the database:

    docker-compose run --rm webserver airflow db upgrade

When you set up Airflow for the first time or when you upgrade to a new version, the database may require migrations to update its schema and ensure that all tables, indexes, and configurations are in line with the latest version of Airflow. If you do not run this command, Airflow may not function properly as it will not be able to access data correctly.

The airflow db upgrade command ensures that the database is configured and ready for use, allowing Airflow to operate stably.    


## Ingesting data to local Postgres with Airflow

We want to run our Postgres setup from last section as well as Airflow to ingest the NYC taxi trip data to our local Postgres.

In this example, we will download and insert data from yellow_tripdata_2021-01, yellow_tripdata_2021-02 and yellow_tripdata_2021-03.

You can find all datasets in https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow

**1:** Prepare an ingest_script.py:

```python
import pandas as pd
from sqlalchemy import create_engine
import requests
import gzip
import shutil


def download_and_unzip(csv_name_gz, csv_name, url):

    # Download the CSV.GZ file
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_name_gz, 'wb') as f_out:
            f_out.write(response.content)
    else:
        print(f"Error downloading file: {response.status_code}")
        return False

    # Unzip the CSV file
    with gzip.open(csv_name_gz, 'rb') as f_in:
        with open(csv_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return True


def process_and_insert_to_db(csv_name, user, password, host, port, db, table_name):
    # Connect to PostgreSQL database
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Process the first chunk
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Insert the data into the database
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    # Process the rest of the data
    while True:
        try:
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            print('inserted another chunk')

        except StopIteration:
            print('completed')
            break

```        

**2:** Create data_ingestion_local.py. The DAG will have the following tasks:

- A PythonOperator task that will download the NYC taxi data.
- A PythonOperator task that will call our ingest script in order to fill our database

Observe how the names of the tables in the database and the URL are generated dynamically according to the execution date using JINJA template

```python

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from ingest_script2 import download_and_unzip, process_and_insert_to_db

# This info is from docker-compose-lesson1.yaml
user = "root2"
password = "root2"
host = "pgdatabase"
port = "5432"
db = "ny_taxi"


# Defining the DAG
dag = DAG(
    "yellow_taxi_ingestion_v3",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 3, 28),
    catchup=True, # True means run past missed jobs
    max_active_runs=1,
)

table_name_template = 'yellow_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'
csv_name_gz_template = 'output_{{ execution_date.strftime(\'%Y_%m\') }}.csv.gz'
csv_name_template = 'output_{{ execution_date.strftime(\'%Y_%m\') }}.csv'

url_template = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz"

# Task 1
download_task = PythonOperator(
    task_id="download_and_unzip",
    python_callable=download_and_unzip,
    op_kwargs={
        'csv_name_gz': csv_name_gz_template,
        'csv_name': csv_name_template,
        'url': url_template
    },
    dag=dag
)

# Task 2:
process_task = PythonOperator(
    task_id="process_and_insert_to_db",
    python_callable=process_and_insert_to_db,
    op_kwargs={
        'csv_name': csv_name_template,
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'db': db,
        'table_name': table_name_template
     
    },
    dag=dag
)

# Establish the sequence of tasks
download_task >> process_task
```

- **catchup=True:** This parameter ensures that if the DAG was paused or missed runs during the period between the start_date and end_date, Airflow will try to "catch up" and run all the missed executions, one for each scheduled date.

- **max_active_runs=1:** This limits the DAG to only have one active run at any time, preventing overlapping executions of the DAG.


**3:** Modify the Airflow Dockerfile so that we can run our script (this is only for the purposes of this exercise) by installing the additional Python libraries that the ingest_script.py file needs. Add this right after installing the requirements.txt file: 

```dockerfile
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary requests
```

**4:** Rebuild the Airflow image with: 
```
    docker-compose build
```

**5:** Start Airflow by using:
```
 docker-compose up 
 ```
 and on a separate terminal, find out which virtual network it's running on with:
 
 ```
docker network ls:
```

It should print something like this:

```
    NETWORK ID     NAME             DRIVER    SCOPE
    e843f42a6fe1   bridge           bridge    local
    690b4b59769b   dtc-de_default   bridge    local
    1b4769ea7218   host             host      local
    348b319579e3   none             null      local
```    

**6:** Modify the docker-compose.yaml file from lesson 1 by adding the network (dtc-de_default) info and removing away the pgAdmin service in order to reduce the amount of resources we will consume (we can use pgcli to check the database). We will use this docker-compose-lesson1.yaml file:

```dockerfile

services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root2
      - POSTGRES_PASSWORD=root2
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5433:5432"
    networks:
      - airflow

    
networks:
  airflow:
    external: true
    name: dtc-de_default
```    

**7:** Run: 

```
    docker-compose -f docker-compose-lesson1.yaml up
```

**8:** Once the container is running, we can log into our database with the following command:
```
    pgcli -h localhost -p 5433 -u root2 -d ny_taxi
```

**9:** Open the Airflow dashboard and unpause the yellow_taxi_ingestion_v3 DAG:

![airflow4](images/airflow4.jpg)

Processing the first table should look like this:

![airflow2](images/airflow2.jpg)

Once the 3 tables are created, it should look like this:

![airflow3](images/airflow3.jpg)

Green squares with the status "success" should appear. One for each table.

**10:** Check tables on your local Postgres database:

```
    \dt
```

It should print:

```
root2@localhost:ny_taxi> \dt
+--------+---------------------+-------+-------+
| Schema | Name                | Type  | Owner |
|--------+---------------------+-------+-------|
| public | yellow_taxi_2021_01 | table | root2 |
| public | yellow_taxi_2021_02 | table | root2 |
| public | yellow_taxi_2021_03 | table | root2 |
+--------+---------------------+-------+-------+
```

For example lets check table from 2021-03:

```
select count(1) from yellow_taxi_2021_03;
```

It should print:

```
+---------+
| count   |
|---------|
| 1925152 |
+---------+
```


## Ingesting data to GCP with Airflow

We will now run a slightly more complex DAG that will download the NYC taxi trip data, convert it to parquet, upload it to a GCP bucket and ingest it to GCP's BigQuery.

![airflowgcp2](images/airflowgcp2.jpg)


### 1: Prepare a DAG 

We will use this DAG file. Copy it to the /dags subdirectory in your work folder:

```python

import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv
import pyarrow.parquet 
import requests
import gzip
import shutil

# Make sure the values ​​match your terraform main.tf file
PROJECT_ID="zoomcamp-airflow-444903"
BUCKET="zoomcamp_datalake"
BIGQUERY_DATASET = "zoomcamp_bigquery"

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


# Utility functions
def download_and_unzip(csv_name_gz, csv_name, url):

    # Download the CSV.GZ file
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_name_gz, 'wb') as f_out:
            f_out.write(response.content)
    else:
        print(f"Error downloading file: {response.status_code}")
        return False

    # Unzip the CSV file
    with gzip.open(csv_name_gz, 'rb') as f_in:
        with open(csv_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return True


def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pyarrow.csv.read_csv(src_file)
    pyarrow.parquet.write_table(table, src_file.replace('.csv', '.parquet'))


def upload_to_gcs(bucket, object_name, local_file):

    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


# Defining the DAG
dag = DAG(
    "GCP_ingestion",
    schedule_interval="0 6 2 * *",
    start_date=datetime(2021, 3, 1),
    end_date=datetime(2021, 3, 5),
    catchup=True, 
    max_active_runs=1,
)

table_name_template = 'yellow_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'
csv_name_gz_template = 'output_{{ execution_date.strftime(\'%Y_%m\') }}.csv.gz'
csv_name_template = 'output_{{ execution_date.strftime(\'%Y_%m\') }}.csv'

parquet_file = csv_name_template.replace('.csv', '.parquet')

url_template = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv.gz"

# Task 1
download_task = PythonOperator(
    task_id="download_and_unzip",
    python_callable=download_and_unzip,
    op_kwargs={
        'csv_name_gz': csv_name_gz_template,
        'csv_name': csv_name_template,
        'url': url_template
    },
    dag=dag
)

# Task 2
process_task = PythonOperator(
    task_id="format_to_parquet_task",
    python_callable=format_to_parquet,
    op_kwargs={
        "src_file": f"{path_to_local_home}/{csv_name_template}"
    },
    dag=dag
)

# Task 3
local_to_gcs_task = PythonOperator(
    task_id="local_to_gcs_task",
    python_callable=upload_to_gcs,
    op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    dag=dag
)

# Task 4
bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
        dag=dag
    )


download_task >> process_task >> local_to_gcs_task >> bigquery_external_table_task
```

The script defines a DAG (Directed Acyclic Graph), a workflow that orchestrates tasks such as downloading data, processing it, uploading it to Google Cloud Storage (GCS), and creating an external table in BigQuery


Let's explain step by step what this code does:

**Importing Libraries**

- os, logging, datetime: For environment handling, logging, and managing dates
- Airflow components: To define workflows and tasks.
- Google Cloud libraries: For interacting with GCS and BigQuery.
- pyarrow: For converting CSV files to Parquet.
- requests, gzip, shutil: To handle file downloads, decompression, and file manipulation.

**Constants**

- PROJECT_ID, BUCKET, BIGQUERY_DATASET: Define the GCP project, storage bucket, and BigQuery dataset. Make sure the values ​​match your terraform main.tf file!
- path_to_local_home: Determines the local directory for temporary file storage.

**Utility Functions**

- download_and_unzip: Downloads a compressed .csv.gz making an HTTP GET request file from a URL, decompresses it using gzip, and saves it as a .csv file locally

- format_to_parquet: Converts a CSV file into a Parquet format file for optimized storage and querying using pyarrow

- upload_to_gcs: Uses the Google Cloud storage.Client to upload the file to the specified bucket

**Task 1: download_task**

- Operator: PythonOperator.
- Purpose: Downloads and decompresses the .csv.gz file.
- Parameters:
    1. csv_name_gz: Template for the compressed file name.
    2. csv_name: Template for the decompressed file name.
    3. url: Template for the file's URL.

**Task 2: process_task**

- process_task
- Operator: PythonOperator.
- Purpose: Converts the downloaded CSV file to Parquet format.
- Parameter: src_file: Full path to the downloaded CSV file.

**Task 3: local_to_gcs_task**

- Purpose: This task uploads the Parquet file created in the previous step from the local file system to a Google Cloud Storage (GCS) bucket using a Python function (upload_to_gcs). A connection is established to GCS using the Google Cloud Storage library. The local Parquet file is uploaded to the specified bucket and folder (raw/).

- Operator: PythonOperator.


Arguments:

- bucket: Name of the target GCS bucket. Defined earlier as BUCKET = "zoomcamp_datalake".

- object_name: The path inside the GCS bucket where the file will be stored. The format is raw/{parquet_file}, indicating the file is stored in the raw/ folder of the bucket with the same name as the Parquet file.

- local_file: The full path to the Parquet file in the local file system. Constructed as f"{path_to_local_home}/{parquet_file}", where:

    1. path_to_local_home is the local working directory (e.g., /opt/airflow/).
    2. parquet_file is the Parquet version of the downloaded and processed CSV file.

Execution Flow

When the task runs, it calls the upload_to_gcs function with the specified arguments.
Inside the upload_to_gcs function:
A connection is established to GCS using the Google Cloud Storage library.
The local Parquet file is uploaded to the specified bucket and folder (raw/).


**Task 4: bigquery_external_table_task**

- Purpose: This task creates an external table in Google BigQuery, pointing to the Parquet file stored in GCS. External tables allow querying data directly in GCS without importing it into BigQuery's managed storage.

- Operator: BigQueryCreateExternalTableOperator. A predefined operator from Airflow's Google Cloud BigQuery provider. It simplifies the process of creating external tables.

Arguments:

- task_id: Unique identifier for the task in the DAG, "bigquery_external_table_task".

- table_resource: Defines the structure and configuration of the external table in BigQuery:

    1. projectId: The GCP project ID (zoomcamp-airflow-444903).
    2. datasetId: The dataset in BigQuery where the table will be created (zoomcamp_bigquery).
    3. tableId: Name of the external table (external_table).
    4. sourceFormat: Specifies the data format of the external source, here PARQUET.
    5. sourceUris: A list of GCS URIs pointing to the Parquet files to be queried: The URI is gs://{BUCKET}/raw/{parquet_file}, where BUCKET is the name of the GCS bucket and parquet_file is the file name generated in previous steps


The operator connects to BigQuery and creates an external table in the specified project and dataset. The table references the Parquet file stored in GCS. Once created, the table allows querying the Parquet file data directly using SQL in BigQuery    



### 2: Start Airflow

```
 docker-compose up 
 ```

 Open the Airflow dashboard and unpause the GCP_ingestion DAG

 If everything its ok, Green squares with the status "success" should appear:

![airflowgcp1](images/airflowgcp1.jpg)



### 3: Google Cloud Platform


Once the DAG finishes, you can go to your GCP project's dashboard and search for BigQuery. You should see your project ID; expand it and you should see a new zoomcamp_bigquery database with an external_table table.


![airflowgcp3](images/airflowgcp3.jpg)


Click on the 3 dots next to external_table and click on Open to display the table's schema.


![airflowgcp4](images/airflowgcp4.jpg)


Click on the 3 dots next to external_table and click on Query. Run the following SQL query to show the top 5 rows in the database:


![airflowgcp5](images/airflowgcp5.jpg)


You can also see the uploaded parquet file by searching the Cloud Storage service, selecting your bucket and then clickin on the raw/ folder. You may click on the filename to access an info panel:


![airflowgcp6](images/airflowgcp6.jpg)


You may now shutdown Airflow by running docker-compose down on the terminal where you run it.


# Airflow 2025

Since the 2022 cohort, airflow has been updated from version 2.2.3 to 2.10.4

Apache Airflow has undergone significant enhancements between versions 2.2.3 and 2.10.4. Below is an overview of the key changes introduced in each major release during this period:

- Apache Airflow 2.3.0: Introduced the concept of Datasets, enabling data-aware scheduling of DAGs.
- Apache Airflow 2.4.0: Improved scheduler performance and scalability. Introduced a new scheduler UI for better monitoring
- Apache Airflow 2.5.0: Enhanced the TaskFlow API for better PythonOperator support. Improved logging capabilities for better traceability.
- Apache Airflow 2.6.0: Enhanced the Kubernetes Executor for better resource management. Introduced new features in the web UI for better user experience.
- Apache Airflow 2.7.0: Introduced a new task instance details page in the web UI. Further improvements to scheduler performance.
- Apache Airflow 2.8.0: Continued improvements to scheduler performance. Additional features in the web UI for better monitoring.
- Apache Airflow 2.9.0: Enabled MySQL KEDA support for the triggerer. Added support for AWS Executors.


## Setting up Airflow 2.10.4 with Docker


**1:** Create a new version of the Dockerfile. Should look like:

```dockerfile

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
```

**2:** Use the same Docker-compose.yaml, same .env file, same entrypoint.sh and same requirements.txt

**3:** 

Make sure to execute the docker-compose command in the airflow2025 directory:

```
docker-compose build
```

**4:** Run Airflow:    

```
    docker-compose up -d
```

**5:** You may now access the Airflow GUI by browsing to localhost:8080. 

It may take a few minutes to load the webApp

```
Username: airflow
Password: airflow 
```

**6:** Database error. Make database migrations

Airflow database migrations may not have run successfully. You need to make sure that your Airflow tables are properly created and updated. Run the following command to initialize or update the database:

    docker-compose run --rm webserver airflow db upgrade

When you set up Airflow for the first time or when you upgrade to a new version, the database may require migrations to update its schema and ensure that all tables, indexes, and configurations are in line with the latest version of Airflow. If you do not run this command, Airflow may not function properly as it will not be able to access data correctly.

The airflow db upgrade command ensures that the database is configured and ready for use, allowing Airflow to operate stably.    


**7:** Prepare postgres

 On a separate terminal, find out which virtual network it's running on with:
 
 ```
docker network ls
```

**8:**  We will use this docker-compose-lesson1.yaml file:

```dockerfile


services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root2
      - POSTGRES_PASSWORD=root2
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5433:5432"
    networks:
      - airflow

    
networks:
  airflow:
    external: true
    name: airflow2025_default
```    

**9:** Run Postgres: 

Make sure to execute the docker-compose command in the database_ny_taxi2025 directory:

```
    docker-compose -f docker-compose-lesson1.yaml up
```

**10:** Once the container is running, we can log into our database with the following command:
```
    pgcli -h localhost -p 5433 -u root2 -d ny_taxi
```

**11:** Open the Airflow dashboard and unpause the "yellow_taxi_ingestion_slow" DAG:

After executing, should look like this:

![airflownew1](images/airflownew1.jpg)

**12:** Check tables on your local Postgres database:

It should print:

```
+--------+---------------------+-------+-------+
| Schema | Name                | Type  | Owner |
|--------+---------------------+-------+-------|
| public | yellow_taxi_2021_02 | table | root2 |
| public | yellow_taxi_2021_03 | table | root2 |
+--------+---------------------+-------+-------+
```

## Ingesting data to local Postgres new version

PostgreSQL’s COPY command is specifically designed for efficient bulk loading of data from a file (or memory buffer, in this case) into a table. It is highly optimized for performance, allowing it to insert large volumes of data in one go.

Lets modify the DAG with this COPY command inside process_and_insert_to_db function:

```python

def process_and_insert_to_db_with_copy(csv_name, user, password, host, port, db, table_name):

    # Connection to the PostgreSQL
    conn = psycopg2.connect(
        dbname=db, user=user, password=password, host=host, port=port
    )

    # Creates a cursor object for executing SQL queries
    cursor = conn.cursor()

    # Create the specified table if it does not already exist.
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        "VendorID" TEXT,
        "tpep_pickup_datetime" TIMESTAMP,
        "tpep_dropoff_datetime" TIMESTAMP,
        "passenger_count" REAL,
        "trip_distance" REAL,
        "RatecodeID" TEXT,
        "store_and_fwd_flag" TEXT,
        "PULocationID" TEXT,
        "DOLocationID" TEXT,
        "payment_type" REAL,
        "fare_amount" REAL,
        "extra" REAL,
        "mta_tax" REAL,
        "tip_amount" REAL,
        "tolls_amount" REAL,
        "improvement_surcharge" REAL,
        "total_amount" REAL,
        "congestion_surcharge" REAL
    );
    """
    # Runs the query
    cursor.execute(create_table_query)
    # Commits the changes to the database, ensuring the table is created.
    conn.commit()
  
    # Read the CSV file in chunks
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=300000)
    for i, chunk in enumerate(df_iter):
        
        chunk['tpep_pickup_datetime'] = pd.to_datetime(chunk['tpep_pickup_datetime'])
        chunk['tpep_dropoff_datetime'] = pd.to_datetime(chunk['tpep_dropoff_datetime'])

        # Memory buffer is created using io.StringIO() to hold the chunk as a CSV
        buffer = io.StringIO()
        chunk.to_csv(buffer, index=False, header=False)
        # Moves the pointer to the beginning of the buffer to prepare it for reading
        buffer.seek(0)  

        # Insert the data from the buffer into the PostgreSQL table.
        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV NULL ''", buffer)

        print(f"Inserted chunk {i + 1}")

        # Commits the changes to the database after each chunk is inserted.
        conn.commit()

    # After all chunks are processed, cursor and connection are closed
    cursor.close()
    conn.close()

```


The COPY command directly streams data into the database with minimal overhead, making it faster and more memory-efficient. SQLAlchemy, while flexible and powerful for general database management, isn’t designed to match the performance of PostgreSQL's COPY command for bulk inserts.


### Ingesting data to GCP new version

**1:** Lets modify upload_to_gcs function like this:

```python

def upload_to_gcs(bucket, object_name, local_file, gcp_conn_id="google_cloud_default"):
    hook = GCSHook(gcp_conn_id)
    hook.upload(
        bucket_name=bucket,
        object_name=object_name,
        filename=local_file
    )
```    

and task 3 like this:

```python

local_to_gcs_task = PythonOperator(
    task_id="local_to_gcs_task",
    python_callable=upload_to_gcs,
    op_kwargs={
        "bucket": BUCKET,
        "object_name": f"raw/{parquet_file}",
        "local_file": f"{path_to_local_home}/{parquet_file}",
        "gcp_conn_id": "google_cloud_default"
    },
    dag=dag
)
```

Full code in airflow2025/dags/data_ingestion_gcp.py


**2:** Unpause the GCP_ingestion DAG, should look like this:


![airflownew2](images/airflownew2.jpg)


**3:** Once the DAG finishes, you can go to your GCP project's dashboard and search for BigQuery. You should see your project ID; expand it and you should see a new external_table table

![airflownew3](images/airflownew3.jpg)

