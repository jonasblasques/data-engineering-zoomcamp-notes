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