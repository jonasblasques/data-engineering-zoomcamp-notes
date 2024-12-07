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