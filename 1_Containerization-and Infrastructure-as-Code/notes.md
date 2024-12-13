# Introduction to Docker

## Creating a simple "data pipeline" in Docker

Let's create an example pipeline. We will create a dummy pipeline.py Python script that receives an 
argument and prints it.

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

You can run a containerized version of Postgres that doesn't require any installation steps. You only
 need to provide a few environment variables to it as well as a volume for storing data.

Create a folder anywhere you'd like for Postgres to store data in. We will use the example folder
 ny_taxi_postgres_data. Here's how to run the container:

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

The -p is for port mapping. Maps port 5432 on the container (default PostgreSQL port) to port 5433 on the host machine.

The last argument is the image name and tag. We run the official postgres image on its version 13.

Once the container is running, we can log into our database with the following command:

    pgcli -h localhost -p 5433 -u root2 -d ny_taxi

Lets test the db for example with "SELECT 1;", and it should print:

    ny_taxi=# select 1;
    ?column?
    ----------
            1
    (1 row)

Of course we haven't loaded data into the DB yet.

## Note on Docker Networking and Port Mapping

Since I already have postgresql installed on the host machine, I already have port 5432 occupied. 
That's why we use port 5433.

If you want to connect to PostgreSQL inside the container from the host machine, you will need to 
use port 5433. You must use the port you have exposed on the host using the -p option: 5433:5432, 
which means:

Port on the host machine: 5433
Port inside the container: 5432

If you want to connect to PostgreSQL inside the container from another container, you will need to 
use port 5432, which is the internal port of the PostgreSQL container. In this case, you don't need 
to worry about port 5433, as this is only relevant for external connections to the container (from 
the host or outside the Docker network).

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

Lets create a new python file importdata.py:

``` python

import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('yellow_tripdata_2021-01.csv', nrows=10000)
df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

engine = create_engine('postgresql://root2:root2@localhost:5433/ny_taxi')

print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))
```

In a new terminal, run python importdata.py

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


## Connecting pgAdmin and Postgres with Docker networking

pgAdmin is a web-based tool that makes it more convenient to access and manage our databases. It's possible
 to run pgAdmin as as container along with the Postgres container, but both containers will have to be
in the same virtual network so that they can find each other.

Let's create a virtual Docker network called pg-network:

    docker network create pg-network

We will now re-run our Postgres container with the added network name and the container network name, 
so that the pgAdmin container can find it (we'll use pg-database for the container name):


```
 winpty docker run -it \
  -e POSTGRES_USER="root2" \
  -e POSTGRES_PASSWORD="root2" \
  -e POSTGRES_DB="ny_taxi" \
  -v "C:\Users\nacho\Desktop\data-engineering-zoomcamp\1_Containerization-and Infrastructure-as-Code\ny_taxi_postgres_data:/var/lib/postgresql/data" \
  -p 5433:5432 \
  --network=pg-network \
  --name pg-database \
  postgres:13
```

We will now run the pgAdmin container on another terminal:

```
docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="root" \
    -p 8080:80 \
    --network=pg-network \
    --name pgadmin \
    dpage/pgadmin4
```    

You should now be able to load pgAdmin on a web browser by browsing to localhost:8080. Use the same 
email and password you used for running the container to log in.

Right-click on Servers on the left sidebar --> Register--> Server

Under General give the Server a name: Docker localhost

Under Connection add the same host name: pg-database, port:5432 user:root2 and password:root2

We use port 5432 because we are accessing from a docker container. If it were the case of accessing 
from the host machine, it would be port 5433.


## Using the ingestion script with Docker

We will also rename it to ingest_data.py and will use argparse to handle command line arguments.
The engine we created for connecting to Postgres will be tweaked so that we pass the parameters and build the URL from them, like this:

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

You can check the completed code in ingest_data.py    

In order to test the script we will have to drop the table we previously created. In pgAdmin, in the sidebar navigate to Servers > Docker localhost > Databases > ny_taxi > Schemas > public > Tables > yellow_taxi_data, right click on yellow_taxi_data and select Query tool. Introduce the following command:

    DROP TABLE yellow_taxi_data;

We are now ready to test the script with the following command:


    python ingest_data.py \
        --user=root2 \
        --password=root2 \
        --host=localhost \
        --port=5433 \
        --db=ny_taxi \
        --table_name=yellow_taxi_trips \
        --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"


We use port 5433 because we are accessing from the host machine.

## Dockerizing the script

Let's modify the Dockerfile we created before to include our ingest_data.py script and create a new image:

``` dockerfile
FROM python:3.9.1


RUN pip install pandas sqlalchemy psycopg2 requests

WORKDIR /app
COPY ingest_data.py ingest_data.py 

ENTRYPOINT [ "python", "ingest_data.py" ]
```

Build the image:

    docker build -t taxi_ingest:v001 .

And run it:

    docker run -it \
        --network=pg-network \
        taxi_ingest:v001 \
        --user=root2 \
        --password=root2 \
        --host=pg-database \
        --port=5432 \
        --db=ny_taxi \
        --table_name=yellow_taxi_trips \
        --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"


Now we use port 5432 because we are accessing from a docker container

## Running Postgres and pgAdmin with Docker-compose

Docker-compose allows us to launch multiple containers using a single configuration file, so that we don't have to run multiple complex docker run commands separately.

Docker compose makes use of YAML files. Here's the docker-compose.yaml file for running the Postgres and pgAdmin containers:

```dockerfile
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root2
      - POSTGRES_PASSWORD=root2
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "5433:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    volumes:
      - "./data_pgadmin:/var/lib/pgadmin"
    ports:
      - "8080:80"
    depends_on:
      - pgdatabase  
```       

We don't have to specify a network because docker-compose takes care of it: every single container (or "service", as the file states) will run withing the same network and will be able to find each other according to their names (pgdatabase and pgadmin in this example).

We've added a volume for pgAdmin to save its settings, so that you don't have to keep re-creating the connection to Postgres every time ypu rerun the container. 

We can now run Docker compose by running the following command from the same directory where docker-compose.yaml is found. Make sure that all previous containers aren't running anymore:

    docker-compose up

Since the settings for pgAdmin were stored within the container and we have killed the previous onem you will have to re-create the connection by following the steps    

Under General give the Server a name: Docker localhost

Under Connection add the same host name: pgdatabase, port:5432 user:root2 and password:root2 

The proper way of shutting down the containers is with this command:

    docker-compose down

If you just want to stop the containers without deleting resources like volumes or images, you can use the command:

    docker-compose stop

This command will stop all containers defined in your docker-compose.yml file, but will not remove containers, volumes, networks, or images. You can restart containers later with the command:

    docker-compose start


If you want to re-run the dockerized ingest script when you run Postgres and pgAdmin with docker-compose, you will have to find the name of the virtual network that Docker compose created for the containers. You can use the command docker network ls to find it and then change the docker run command for the dockerized script to include the network name.    