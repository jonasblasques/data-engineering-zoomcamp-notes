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


