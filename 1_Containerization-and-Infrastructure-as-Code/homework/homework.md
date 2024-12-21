# Prepare Postgres

Run Postgres and load data as shown in the videos We'll use the green taxi trips from September 2019:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz

You will also need the dataset with zones:

https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

Download this data and put it into Postgres

Open the terminal and run:

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

# Question 3. Count records

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

# Question 4. Longest trip

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


# Question 6. Largest tip

For the passengers picked up in September 2019 in the zone name Astoria which was the drop off zone that had the largest tip? We want the name of the zone, not the id.

```
SELECT 
    zone.Zone,
    MAX(green_tripdata.tip_amount)
FROM 
    green_tripdata
JOIN 
    zone 
ON 
    green_tripdata.DOLocationID = zone.LocationID
WHERE 
    green_tripdata.PULocationID = (
        SELECT LocationID
        FROM zone
        WHERE Zone = 'Astoria'
    )
    AND green_tripdata.lpep_pickup_datetime BETWEEN '2019-09-01' AND '2019-09-30'
GROUP BY 
    zone.Zone
ORDER BY 
    green_tripdata.tip_amount DESC
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

