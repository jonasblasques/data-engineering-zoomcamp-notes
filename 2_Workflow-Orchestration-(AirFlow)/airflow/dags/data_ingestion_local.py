from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from ingest_script import download_and_unzip, process_and_insert_to_db

# This info is from docker-compose-lesson1.yaml
user = "root2"
password = "root2"
host = "pgdatabase"
port = "5432"
db = "ny_taxi"

table_name = "yellow_taxi_trips"
csv_name_gz = 'output.csv.gz'
csv_name = 'output.csv'

# Defining the DAG
dag = DAG(
    "yellow_taxi_ingestion",
    schedule_interval=None,  # It will be executed only once, manually
    start_date=datetime(2021, 1, 1),
    catchup=False
)

# Task 1
download_task = PythonOperator(
    task_id="download_and_unzip",
    python_callable=download_and_unzip,
    op_kwargs={
        'csv_name_gz': csv_name_gz,
        'csv_name': csv_name
    },
    dag=dag
)

# Task 2:
process_task = PythonOperator(
    task_id="process_and_insert_to_db",
    python_callable=process_and_insert_to_db,
    op_kwargs={
        'csv_name': csv_name,
        'user': user,
        'password': password,
        'host': host,
        'port': port,
        'db': db,
        'table_name': table_name
    },
    dag=dag
)

# Establish the sequence of tasks
download_task >> process_task



