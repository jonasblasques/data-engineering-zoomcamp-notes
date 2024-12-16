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