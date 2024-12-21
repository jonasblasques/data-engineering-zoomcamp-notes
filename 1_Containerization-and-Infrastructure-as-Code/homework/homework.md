# Docker

## Question 1. Knowing docker tags

Run the command to get information on Docker

docker --help

Now run the command to get help on the "docker build" command:

docker build --help

Do the same for "docker run".

Which tag has the following text? - Automatically remove the container when it exits

```
   --rm                               Automatically remove the
                                         container and its associated
                                         anonymous volumes when it exits
```

## Question 2. Understanding docker first run

Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash. Now check the python modules that are installed ( use pip list ).

What is version of the package wheel ?

Open  new terminal and run:

```
docker run -it --entrypoint bash python:3.9
```

Output:

```
root@8b944e90c591:/# pip list
Package    Version
---------- -------
pip        23.0.1
setuptools 58.1.0
wheel      0.45.1
```


# Prepare Postgres & SQL

Run Postgres and load data as shown in the videos We'll use the green taxi trips from September 2019:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz

You will also need the dataset with zones:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

Download this data and put it into Postgres

Open the terminal in the homework directory and run:

```
docker-compose up
```

```python

python ingest_data.py \
    --user=root2 \
    --password=root2 \
    --host=localhost \
    --port=5433 \
    --db=homework_taxi \
    --table_name=green_tripdata \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz"
``` 

and:

```python

python ingest_zone.py \
    --user=root2 \
    --password=root2 \
    --host=localhost \
    --port=5433 \
    --db=homework_taxi \
    --table_name=zone \
```  

Now in a new terminal run:

```
pgcli -h localhost -p 5433 -u root2 -d homework_taxi
```

## Question 3. Count records

How many taxi trips were totally made on September 18th 2019?

```
SELECT
  COUNT(1)
FROM
  green_tripdata
WHERE
  (lpep_pickup_datetime>='2019-09-18 00:00:00' AND
  lpep_pickup_datetime<'2019-09-19 00:00:00');
```

Output:

```
+-------+
| count |
|-------|
| 15767 |
+-------+
```

## Question 4. Longest trip

Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

```
SELECT
  lpep_pickup_datetime,trip_distance
FROM
  green_tripdata
ORDER BY
  trip_distance DESC
  LIMIT 1;
```

Output:

```
+----------------------+---------------+
| lpep_pickup_datetime | trip_distance |
|----------------------+---------------|
| 2019-09-26 19:32:52  | 341.64        |
+----------------------+---------------+
```
## Question 5. Three biggest pick up Boroughs

Consider lpep_pickup_datetime in '2019-09-18' and ignoring Borough has Unknown

Which were the 3 pick up Boroughs that had a sum of total_amount superior to 50000?

```
SELECT z."Borough", SUM(green_tripdata.total_amount) AS total_sum
FROM green_tripdata
INNER JOIN zone z
ON green_tripdata."PULocationID" = z."LocationID"
WHERE DATE(green_tripdata.lpep_pickup_datetime) = '2019-09-18'
  AND z."Borough" != 'Unknown'
GROUP BY z."Borough"
HAVING SUM(green_tripdata.total_amount) > 50000
ORDER BY total_sum DESC
LIMIT 3;
```

Output:

```
+-----------+-------------------+
| Borough   | total_sum         |
|-----------+-------------------|
| Brooklyn  | 96333.23999999912 |
| Manhattan | 92271.29999999829 |
| Queens    | 78671.70999999889 |
+-----------+-------------------+
```

## Question 6. Largest tip

For the passengers picked up in September 2019 in the zone name Astoria which was the drop off zone that had the largest tip? We want the name of the zone, not the id.

```
SELECT z2."Zone", max(tip_amount) as Max_tip
FROM green_tripdata
INNER JOIN zone z
on green_tripdata."PULocationID" = z."LocationID"
INNER JOIN zone z2
on green_tripdata."DOLocationID" = z2."LocationID"
WHERE z."Zone" = 'Astoria'
GROUP BY z2."Zone"
ORDER BY Max_tip DESC
LIMIT 1;

```

Output:

```
+-------------+---------+
| Zone        | max_tip |
|-------------+---------|
| JFK Airport | 62.31   |
+-------------+---------+
```

# Terraform

## Question 7. Creating Resources

After updating the main.tf and variable.tf files run: terraform apply

Paste the output of this command into the homework submission form.

```
/terraform# terraform plan

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # google_bigquery_dataset.dataset will be created
  + resource "google_bigquery_dataset" "dataset" {
      + creation_time              = (known after apply)
      + dataset_id                 = "zoomcamp_bigquery"
      + delete_contents_on_destroy = false
      + etag                       = (known after apply)
      + id                         = (known after apply)
      + labels                     = (known after apply)
      + last_modified_time         = (known after apply)
      + location                   = "US"
      + project                    = "zoomcamp-airflow-444903"
      + self_link                  = (known after apply)

      + access (known after apply)
    }

  # google_storage_bucket.data-lake-bucket will be created
  + resource "google_storage_bucket" "data-lake-bucket" {
      + force_destroy               = true
      + id                          = (known after apply)
      + location                    = "US"
      + name                        = "zoomcamp_datalake"
      + project                     = (known after apply)
      + public_access_prevention    = (known after apply)
      + self_link                   = (known after apply)
      + storage_class               = "STANDARD"
      + uniform_bucket_level_access = true
      + url                         = (known after apply)

      + lifecycle_rule {
          + action {
              + type          = "Delete"
                # (1 unchanged attribute hidden)
            }
          + condition {
              + age                    = 30
              + matches_prefix         = []
              + matches_storage_class  = []
              + matches_suffix         = []
              + with_state             = (known after apply)
                # (3 unchanged attributes hidden)
            }
        }

      + versioning {
          + enabled = true
        }

      + website (known after apply)
    }
```

```
google_bigquery_dataset.dataset: Creating...
google_storage_bucket.data-lake-bucket: Creating...
google_bigquery_dataset.dataset: Creation complete after 1s [id=projects/zoomcamp-airflow-444903/datasets/zoomcamp_bigquery]
google_storage_bucket.data-lake-bucket: Creation complete after 2s [id=zoomcamp_datalake]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```