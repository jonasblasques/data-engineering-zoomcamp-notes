# Module 1 Homework: Docker & SQL

## Question 1. Understanding docker first run 

Run docker with the `python:3.12.8` image in an interactive mode, use the entrypoint `bash`.

What's the version of `pip` in the image?


Open new terminal and run:

```
docker run -it --entrypoint bash python:3.12.8
```

It may take a few minutes the first time. After that you should see something like this:

```
Status: Downloaded newer image for python:3.12.8
root@16c439542eff:/# 
```

Now run:

```
pip --version
```
you should see something like this:

```
root@16c439542eff:/# pip --version
pip 24.3.1 from /usr/local/lib/python3.12/site-packages/pip (python 3.12)
```


## Question 2. Understanding Docker networking and docker-compose

Given the following `docker-compose.yaml`, what is the `hostname` and `port` that **pgadmin** should use to connect to the postgres database?

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'ny_taxi'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data

  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4:latest
    environment:
      PGADMIN_DEFAULT_EMAIL: "pgadmin@pgadmin.com"
      PGADMIN_DEFAULT_PASSWORD: "pgadmin"
    ports:
      - "8080:80"
    volumes:
      - vol-pgadmin_data:/var/lib/pgadmin  

volumes:
  vol-pgdata:
    name: vol-pgdata
  vol-pgadmin_data:
    name: vol-pgadmin_data
```


Internal Hostname: pgadmin and postgres are part of the same Docker Compose network, which means they can communicate with each other using the service names defined in the services section. Each service in the docker-compose.yaml can access others using the service name (e.g., db for the postgres service) as the hostname.

Ports Mapping: The ports configuration ('5433:5432') maps the container's internal port 5432 to the host machine's port 5433. However, this mapping is only relevant when accessing the service from outside the Docker network (e.g., from the host machine).

Answer:

Hostname: db (service name).
Port: 5432 (internal port of the postgres container).


## Prepare Postgres & SQL

Run Postgres and load data as shown in the videos We'll use the green taxi trips from October 2019:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz

You will also need the dataset with zones:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv


Open the terminal in the homework directory and run:

```
docker-compose up
```

In another terminal run:

```bash

python ingest_data.py \
    --user=root2 \
    --password=root2 \
    --host=localhost \
    --port=5433 \
    --db=homework_taxi \
    --table_name=green_tripdata_2019-10 \
    --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-10.csv.gz"
``` 

> [!NOTE]  
> The script ingest_data.py is the same except that the green taxi files have the column "lpep_pickup_datetime" > instead of "tpep_pickup_datetime"

---

and also run:

```python

python ingest_zone.py \
    --user=root2 \
    --password=root2 \
    --host=localhost \
    --port=5433 \
    --db=homework_taxi \
    --table_name=zone 
```  

## Question 3. Trip Segmentation Count

 During the period of October 1st 2019 (inclusive) and November 1st 2019 (exclusive), how many trips, **respectively**, happened:
 
1. Up to 1 mile
2. In between 1 (exclusive) and 3 miles (inclusive),
3. In between 3 (exclusive) and 7 miles (inclusive),
4. In between 7 (exclusive) and 10 miles (inclusive),
5. Over 10 miles 



```sql
SELECT COUNT(1) 
FROM public."green_tripdata_2019-10"
WHERE trip_distance <= 1;
```

Output:

```
+--------+
| count  |
|--------|
| 104838 |
+--------+
```

```sql
SELECT COUNT(1) 
FROM public."green_tripdata_2019-10"
WHERE trip_distance > 1 AND trip_distance <= 3;
```

Output:

```
+--------+
| count  |
|--------|
| 199013 |
+--------+
```

Answer with outliers:

104,838; 199,013; 109,645; 27,688; 35,202

The October table contains some outliers, i.e. some values ​​that are not from October. To filter those values ​​use this query:

```sql
SELECT 
    CASE
		WHEN trip_distance <= 1 THEN 'Range 1'
        WHEN trip_distance >1 AND trip_distance <=3 THEN 'Range 3'
        WHEN trip_distance >3 AND trip_distance <=7 THEN 'Range 7'
		WHEN trip_distance >7 AND trip_distance <=10 THEN 'Range 10'
        ELSE 'Bigger distance'
    END AS ranges,
    COUNT(*) AS trip_count
FROM public.green_taxi_data
WHERE DATE(lpep_pickup_datetime) >= '2019-10-1' AND DATE(lpep_pickup_datetime) < '2019-11-1' 
GROUP BY ranges;
```

Answer without outliers:

104,830; 198,995; 109,642; 27,686; 35,201


## Question 4. Longest trip for each day

Which was the pick up day with the longest trip distance? Use the pick up time for your calculations.

```sql

SELECT lpep_pickup_datetime,trip_distance
FROM public."green_tripdata_2019-10"
ORDER BY trip_distance DESC
LIMIT 1;
```

Output:

```
+----------------------+---------------+
| lpep_pickup_datetime | trip_distance |
|----------------------+---------------|
| 2019-10-31 23:23:41  | 515.89        |
+----------------------+---------------+
```

Answer: 2019-10-31


## Question 5. Three biggest pickup zones

Which were the top pickup locations with over 13,000 in total_amount (across all trips) for 2019-10-18?

Consider only lpep_pickup_datetime when filtering by date.

```sql

SELECT z."Zone", SUM(public."green_tripdata_2019-10".total_amount) AS total_sum
FROM public."green_tripdata_2019-10"
INNER JOIN zone z
ON public."green_tripdata_2019-10"."PULocationID" = z."LocationID"
WHERE DATE(public."green_tripdata_2019-10".lpep_pickup_datetime) = '2019-10-18'
AND z."Borough" != 'Unknown'
GROUP BY z."Zone"
HAVING SUM(public."green_tripdata_2019-10".total_amount) > 13000
ORDER BY total_sum DESC
LIMIT 3;
```

Output:

```
+---------------------+-------------------+
| Zone                | total_sum         |
|---------------------+-------------------|
| East Harlem North   | 18686.68000000009 |
| East Harlem South   | 16797.26000000006 |
| Morningside Heights | 13029.78999999993 |
+---------------------+-------------------+
```


## Question 6. Largest tip

For the passengers picked up in October 2019 in the zone name "East Harlem North" which was the drop off zone that had the largest tip?

We need the name of the zone, not the ID.

```sql

SELECT z2."Zone", max(tip_amount) as Max_tip
FROM public."green_tripdata_2019-10"
INNER JOIN zone z2
ON public."green_tripdata_2019-10"."DOLocationID" = z2."LocationID"
INNER JOIN zone z1
ON public."green_tripdata_2019-10"."PULocationID" = z1."LocationID"
WHERE z1."Zone" = 'East Harlem North'
GROUP BY z2."Zone"
ORDER BY Max_tip DESC
LIMIT 1;

```

Output:

```
+-------------+---------+
| Zone        | max_tip |
|-------------+---------|
| JFK Airport | 87.3   |
+-------------+---------+
```

## Question 7. Terraform Workflow

Which of the following sequences, respectively, describes the workflow for:

Downloading the provider plugins and setting up backend,
Generating proposed changes and auto-executing the plan
Remove all resources managed by terraform`


Answer: terraform init, terraform apply -auto-approve, terraform destroy