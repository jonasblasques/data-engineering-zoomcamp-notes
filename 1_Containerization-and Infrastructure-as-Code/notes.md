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
docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
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

    docker exec -it <container_name_or_id> psql -U root -d ny_taxi 

Lets test the db for example with "SELECT 1;", and it should print:

    ny_taxi=# select 1;
    ?column?
    ----------
            1
    (1 row)

Of course we haven't loaded data into the DB yet.