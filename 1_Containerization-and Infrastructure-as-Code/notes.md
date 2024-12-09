# Introduction to Docker

## Creating a simple "data pipeline" in Docker

Let's create an example pipeline. We will create a dummy pipeline.py Python script that receives an argument and prints it.

```python
import sys
import pandas 

day = sys.argv[1]

print(f'job finished successfully for day {day}')
```

We can run this script with 'python pipeline.py <some_number>' and it should print:

    job finished successfully for day = <some_number>

Let's containerize it by creating a Docker image. Create the folllowing Dockerfile file:

```dockerfile
# base Docker image that we will build on
FROM python:3.9.1

# set up our image by installing prerequisites; pandas in this case
RUN pip install pandas

# set up the working directory inside the container
WORKDIR /app

# copy the script to the container. 1st name is source file, 2nd is destination
COPY pipeline.py pipeline.py

# define what to do first when the container runs in this example, we will just run the script
ENTRYPOINT ["python", "pipeline.py"]
```

Let's build the image:

    docker build -t zoomcampw1 .

We can now run the container and pass an argument to it, so that our pipeline will receive it:

    docker run -it zoomcampw1 some_number

You should get the same output you did when you ran the pipeline script by itself:

    job finished successfully for day = <some_number>

## Running Postgres in a container

You can run a containerized version of Postgres that doesn't require any installation steps. You only need to provide a few environment variables to it as well as a volume for storing data.

Create a folder anywhere you'd like for Postgres to store data in. We will use the example folder ny_taxi_postgres_data. Here's how to run the container:

```
 winpty docker run -it \
  -e POSTGRES_USER="root2" \
  -e POSTGRES_PASSWORD="root2" \
  -e POSTGRES_DB="ny_taxi" \
  -v "C:\Users\nacho\Desktop\data-engineering-zoomcamp\1_Containerization-and Infrastructure-as-Code\ny_taxi_postgres_data:/var/lib/postgresql/data" \
  -p 5433:5432 \
  postgres:13
```

The container needs 3 environment variables:

POSTGRES_USER is the username for logging into the database
POSTGRES_PASSWORD is the password for the database
POSTGRES_DB is the name that we will give the database.

-v points to the volume directory. The colon : separates the first part (path to the folder in the host computer)
 from the second part (path to the folder inside the container).

Path names must be absolute. If you're in a UNIX-like system, you can use pwd to print you local folder as a shortcut;
this example should work with bash shell.

This command will only work if you run it from a directory which contains the ny_taxi_postgres_data subdirectory you created above.

The -p is for port mapping. We map the default Postgres port to the same port in the host.
The last argument is the image name and tag. We run the official postgres image on its version 13.

Once the container is running, we can log into our database with the following command:

    docker exec -it <container_name_or_id> psql -U root2 -d ny_taxi 

Lets test the db for example with "SELECT 1;", and it should print:

    ny_taxi=# select 1;
    ?column?
    ----------
            1
    (1 row)

Of course we haven't loaded data into the DB yet.

## Ingesting data to Postgres with Python

We will use data from the NYC TLC Trip Record Data website. Specifically, we will use https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow

Let's create an importdata.py file that reads the csv file and generates the schema for the database

``` python

import pandas as pd

df = pd.read_csv("yellow_tripdata_2019-01.csv", nrows=10)

df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

print(pd.io.sql.get_schema(df, name="yellow_taxi_data"))
```

It should print:

    CREATE TABLE "yellow_taxi_data" (
    "VendorID" INTEGER,
    "tpep_pickup_datetime" TIMESTAMP,
    "tpep_dropoff_datetime" TIMESTAMP,
    "passenger_count" INTEGER,
    "trip_distance" REAL,
    "RatecodeID" INTEGER,
    "store_and_fwd_flag" TEXT,
    "PULocationID" INTEGER,
    "DOLocationID" INTEGER,
    "payment_type" INTEGER,
    "fare_amount" REAL,
    "extra" REAL,
    "mta_tax" REAL,
    "tip_amount" REAL,
    "tolls_amount" REAL,
    "improvement_surcharge" REAL,
    "total_amount" REAL,
    "congestion_surcharge" REAL
    )

Even though we have the DDL instructions, we still need specific instructions for Postgres to connect to it and create the table. We will use sqlalchemy for this. 

``` python

import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=10000)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

engine = create_engine('postgresql://root2:root2@localhost:5433/ny_taxi')

print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

It should print:

    CREATE TABLE yellow_taxi_data (
            "VendorID" BIGINT, 
            tpep_pickup_datetime TIMESTAMP WITHOUT TIME ZONE,  
            tpep_dropoff_datetime TIMESTAMP WITHOUT TIME ZONE, 
            passenger_count BIGINT,
            trip_distance FLOAT(53),
            "RatecodeID" BIGINT,
            store_and_fwd_flag TEXT,
            "PULocationID" BIGINT,
            "DOLocationID" BIGINT,
            payment_type BIGINT,
            fare_amount FLOAT(53),
            store_and_fwd_flag TEXT,
            "PULocationID" BIGINT,
            "DOLocationID" BIGINT,
            payment_type BIGINT,
            fare_amount FLOAT(53),
            "PULocationID" BIGINT,
            "DOLocationID" BIGINT,
            payment_type BIGINT,
            fare_amount FLOAT(53),
            "DOLocationID" BIGINT,
            payment_type BIGINT,
            fare_amount FLOAT(53),
            payment_type BIGINT,
            fare_amount FLOAT(53),
            fare_amount FLOAT(53),
            extra FLOAT(53),
            mta_tax FLOAT(53),
            extra FLOAT(53),
            mta_tax FLOAT(53),
            tip_amount FLOAT(53),
            mta_tax FLOAT(53),
            tip_amount FLOAT(53),
            tip_amount FLOAT(53),
            tolls_amount FLOAT(53),
            tolls_amount FLOAT(53),
            improvement_surcharge FLOAT(53),
            total_amount FLOAT(53),
            congestion_surcharge FLOAT(53)
    )

Lets create the table:

``` python
# we need to provide the table name, the connection and what to do if the table already exists
df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
```

Insert first chunk:

``` python
df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)

df = next(df_iter)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
```

Back on the database terminal, we can check:

SELECT count(1) FROM yellow_taxi_data;

It should print:

    ny_taxi=# select count(1) FROM yellow_taxi_data;
    count  
    --------
    100000 
    (1 row) 


Let's write a loop to write all chunks to the database

``` python

while True: 
    try:
       
        df = next(df_iter)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)    
        df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

        print('inserted another chunk')
    except StopIteration:
        print('completed')
        break
```    

Back on the database terminal, we can check:

SELECT count(1) FROM yellow_taxi_data;

It should print:

    ny_taxi=# select count(1) FROM yellow_taxi_data;
    count  
    ---------
    1369765
    (1 row)