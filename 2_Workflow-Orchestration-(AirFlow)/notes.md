# Workflow Orchestration

- [Orchestration with Airflow] (## Orchestration with Airflow)
- [Setting up Airflow with Docker (lite version)] (## Setting up Airflow with Docker (lite version))
- [Ingesting data to local Postgres with Airflow] (## Ingesting data to local Postgres with Airflow)


## Orchestration with Airflow

In the previous lesson we saw the definition of data pipeline and we created a pipeline script that downloaded a CSV and processed it so that we could ingest it to Postgres.

The script we created is an example of how NOT to create a pipeline, because it contains 2 steps which could otherwise be separated (downloading and processing). The reason is that if we're simply testing the script, it will have to download the CSV file every single time that we run the script, which is less than ideal.

A Workflow Orchestration Tool allows us to define data workflows and parametrize them; it also provides additional tools such as history and logging.


A typical Airflow installation consists of the following components:

- The scheduler handles both triggering scheduled workflows as well as submitting tasks to the executor to run
- The executor handles running tasks
- A worker simply executes tasks given by the scheduler
- A webserver which seves as the GUI.
- A DAG directory; a folder with DAG files which is read by the scheduler and the executor
- A metadata database (Postgres) used by the scheduler, the executor and the web server to store state
- DAG: Directed acyclic graph, specifies the dependencies between a set of tasks with explicit execution order
- Task: a defined unit of work. The Tasks themselves describe what to do, be it fetching data, running analysis, triggering other systems, or more
- DAG Run: individual execution/run of a DAG. A run may be scheduled or triggered

## Setting up Airflow with Docker (lite version)

If you want a less overwhelming YAML that only runs the webserver and the scheduler and runs the DAGs in the scheduler rather than running them in external workers, please use the docker-compose.yaml from this repo

1. Create a new sub-directory called airflow in your project dir. Inside airflow create dags, google, logs,
plugins and scripts folders.


2. Create a Dockerfile. Should look like:

```dockerfile

# First-time build can take upto 10 mins.
FROM apache/airflow:2.2.3

ENV AIRFLOW_HOME=/opt/airflow

USER root
RUN apt-get update -qq && apt-get install vim -qqq

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
RUN chmod +x scripts

USER $AIRFLOW_UID
```

3. Create a Docker-compose.yaml. Should look like:

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
        restart: always

    scheduler:
        build: .
        command: scheduler
        restart: on-failure
        depends_on:
            - postgres
        env_file:
            - .env
        volumes:
            - ./dags:/opt/airflow/dags
            - ./logs:/opt/airflow/logs
            - ./plugins:/opt/airflow/plugins
            - ./scripts:/opt/airflow/scripts
            - ~/.google/credentials/:/.google/credentials


    webserver:
        build: .
        entrypoint: ./scripts/entrypoint.sh
        restart: on-failure
        depends_on:
            - postgres
            - scheduler
        env_file:
            - .env
        volumes:
            - ./dags:/opt/airflow/dags
            - ./logs:/opt/airflow/logs
            - ./plugins:/opt/airflow/plugins
            - ~/.google/credentials/:/.google/credentials:ro
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

4. Create a requirements.txt, a .env file, a entrypoint.sh inside scripts folder, and your google-credentials.json inside google folder

For this files, you can take the files in this repository as a reference.

5. Build the image. It may take several minutes You only need to do this the first time you run Airflow or if you modified the Dockerfile or the requirements.txt file:

```
    docker-compose build
```

6. Run Airflow:    

```
    docker-compose up -d
```

7. You may now access the Airflow GUI by browsing to localhost:8080. 

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

1. Prepare an ingest_script.py:

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

2. Create data_ingestion_local.py. The DAG will have the following tasks:

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
    "yellow_taxi_ingestion",
    schedule_interval="0 6 2 * *", # The task will be executed at 6:00 a.m. on the 2nd of each month.
    start_date=datetime(2021, 1, 1),
    end_date=datetime(2021, 3, 28),
    catchup=True, # Only run scheduled executions
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

3. Modify the Airflow Dockerfile so that we can run our script (this is only for the purposes of this exercise) by installing the additional Python libraries that the ingest_script.py file needs. Add this right after installing the requirements.txt file: 

```dockerfile
RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary requests
```

4. Rebuild the Airflow image with: 
```
    docker-compose build
```

5. Start Airflow by using:
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

6. Modify the docker-compose.yaml file from lesson 1 by adding the network (dtc-de_default) info and removing away the pgAdmin service in order to reduce the amount of resources we will consume (we can use pgcli to check the database). We will use this docker-compose-lesson1.yaml file:

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

7. Run: 

```
    docker-compose -f docker-compose-lesson1.yaml up
```

8. Once the container is running, we can log into our database with the following command:
```
    pgcli -h localhost -p 5433 -u root2 -d ny_taxi
```

9. Open the Airflow dashboard and trigger the LocalIngestionDag DAG by clicking on the Play icon. Inside the detailed DAG view you will find the status of the tasks as they download the files and ingest them to the database

Green squares with the status "success" should appear. One for each table.

10. Check tables on your local Postgres database:

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