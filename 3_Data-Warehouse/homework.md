# Module 3 Homework

## Inserting data with airflow:

To see how to insert data to GCS every month and build the 2022 table in Big Query using airflow, see here:

https://github.com/ManuelGuerra1987/data-engineering-zoomcamp-notes/tree/main/2_Workflow-Orchestration-(AirFlow)#ingesting-data-to-gcp-multiple-months

## Inserting data manually:

1: Create a green_2022 bucket in Google Cloud Storage

2: Upload parquet files to the bucket:

![hw1](images/hw1.jpg)

3: Create external table for whole 2022

Run this query in Big Query:

```sql

CREATE OR REPLACE EXTERNAL TABLE zoomcamp-airflow-444903.airflow2025.external_green_2022
OPTIONS(
  FORMAT='PARQUET',
  URIS=['gs://green_2022/*']
)

```

4: Create native table for whole 2022

```sql

CREATE OR REPLACE TABLE zoomcamp-airflow-444903.airflow2025.native_green_2022
AS(
  SELECT * FROM `zoomcamp-airflow-444903.airflow2025.external_green_2022`
)

```


## Question 1:

What is count of records for the 2022 Green Taxi Data??

```sql

SELECT count(1) FROM `zoomcamp-airflow-444903.airflow2025.green_2022` ;

```

Answer: 840402


## Question 2:

Write a query to count the distinct number of PULocationIDs for the entire dataset on both the tables.
What is the estimated amount of data that will be read when this query is executed on the External Table and the Table?

Type this query:

```sql

 SELECT COUNT(DISTINCT PULocationID)

 FROM `zoomcamp-airflow-444903.airflow2025.external_green_2022`
 ```

You should see for the external table:

 ![hw2](images/hw2.jpg)

You should see for the native table:

 ![hw3](images/hw3.jpg)

 0 MB for the External Table and 6.41MB for the native Table

 ## Question 3:

How many records have a fare_amount of 0?

 ```sql

  SELECT COUNT(1)

 FROM `zoomcamp-airflow-444903.airflow2025.native_green_2022`

 WHERE fare_amount = 0;
 ```

 Answer: 1622