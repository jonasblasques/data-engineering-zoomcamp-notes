# Workflow Orchestration
## Orchestration with Airflow

In the previous lesson we saw the definition of data pipeline and we created a pipeline script that downloaded a CSV and processed it so that we could ingest it to Postgres.

The script we created is an example of how NOT to create a pipeline, because it contains 2 steps which could otherwise be separated (downloading and processing). The reason is that if we're simply testing the script, it will have to download the CSV file every single time that we run the script, which is less than ideal.

A Workflow Orchestration Tool allows us to define data workflows and parametrize them; it also provides additional tools such as history and logging.

## Airflow architecture

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

Create a new sub-directory called airflow in your project dir. Inside airflow create dags, google, logs,
plugins and scripts folders

Copy from this repo: Dockerfile, a requirements.txt, a dockercompose.yaml, a .env file, a entrypoint.sh inside scripts folder, and your google-credentials.json inside google folder

Build the image. It may take several minutes You only need to do this the first time you run Airflow or if you modified the Dockerfile or the requirements.txt file:

    docker-compose build

Run Airflow:    

    docker-compose up -d

You may now access the Airflow GUI by browsing to localhost:8080. Username and password are both airflow .

## Database error. Make database migrations:

Airflow database migrations may not have run successfully. You need to make sure that your Airflow tables are properly created and updated. Run the following command to initialize or update the database:

    docker-compose run --rm webserver airflow db upgrade

When you set up Airflow for the first time or when you upgrade to a new version, the database may require migrations to update its schema and ensure that all tables, indexes, and configurations are in line with the latest version of Airflow. If you do not run this command, Airflow may not function properly as it will not be able to access data correctly.

The airflow db upgrade command ensures that the database is configured and ready for use, allowing Airflow to operate stably.    

## Simple airflow example

To test that airflow works correctly, we are going to create a simple dag that prints text to the terminal. Inside the dags folder, create a file data_ingestion_local.py and test it with the following code:

```python

from airflow import DAG

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datetime import datetime

local_workflow = DAG(

    "LocalIngestionDagv2",
    schedule_interval = "0 6 2 * *",
    start_date=datetime(2021, 1, 1)
)

with local_workflow:

    wget_task = BashOperator(
        task_id = 'wget',
        bash_command = 'echo "Hello world"'
    )

    ingest_task = BashOperator(
        task_id = 'ingest',
        bash_command = 'echo "Hello world"'
    )    

    wget_task >> ingest_task
```

If everything works correctly, the dag should appear in the airflow webserver. Click on the dag and run the "trigger dag" option. Green squares with the status "success" should appear.


## Ingesting data to local Postgres with Airflow

We want to run our Postgres setup from last section locally as well as Airflow, and we will use the ingest_data.py script from a DAG to ingest the NYC taxi trip data to our local Postgres.

1. Prepare an ingest_script.py
2. Prepare a DAG: data_ingestion_local.py. The DAG will have the following tasks:
A download PythonOperator task that will download the NYC taxi data.
A PythonOperator task that will call our ingest script in order to fill our database
3. Modify the custom Airflow Dockerfile so that we can run our script (this is only for the purposes of this exercise) by installing the additional Python libraries that the ingest_script.py file needs. We will use this Dockerfile. Add this right after installing the requirements.txt file: RUN pip install --no-cache-dir pandas sqlalchemy psycopg2-binary requests
4. Rebuild the Airflow image with docker-compose build
5. Start Airflow by using docker-compose up and on a separate terminal, find out which virtual network it's running on with docker network ls
6. Modify the docker-compose.yaml file from lesson 1 by adding the network info and removing away the pgAdmin service in order to reduce the amount of resources we will consume (we can use pgcli to check the database). We will use this docker-compose-lesson1.yaml file.
7. Run docker-compose -f docker-compose-lesson2.yaml up
8. Open the Airflow dashboard and trigger the LocalIngestionDag DAG by clicking on the Play icon. Inside the detailed DAG view you will find the status of the tasks as they download the files and ingest them to the database
