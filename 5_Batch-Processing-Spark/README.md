# Batch Processing

### Table of contents

- [Introduction to Batch Processing](#introduction-to-batch-processing)
- [Introduction to Spark](#introduction-to-spark)
- [Installation](#installation)
- [Spark SQL and DataFrames](#spark-sql-and-dataframes)
    - [First Look at PySpark](#first-look-at-pyspark)




## Introduction

In this week we will first talk about what batch processing is. One of the tools that we can use for batch processing is Spark, and we will spend most of the time this week talking about Spark.

We'll use PySpark for that, meaning we will use Python, not Scala. Then, we will look at different features of Spark like DataFrames, SQL, how we do joins in Spark, and then we will talk about a relatively old concept from Spark called RDDs (Resilient Distributed Datasets).

We will discuss what they are and the difference between DataFrames and RDDs. We will spend some time talking about internals and how we can use Docker to run Spark jobs. All that we will do locally, but then at the end, in the last two lessons, we will talk about deploying, actually going to the cloud, and running Spark jobs there, then connecting this to a data warehouse.

## Introduction to Batch Processing

_[Video source](https://www.youtube.com/watch?v=dcHe5Fl3MF8)_

**Batch vs Streaming**

There are multiple ways of processing data. One is called batch, and the other one is called streaming.

**Batch:**

Let's say you have a database, and this is our taxi trip dataset. We have some data for January 15, for example. Then we take all the data we have for January 15 and there is one single job that takes all this data for January 15 and then produces something else, some other dataset.

This particular job reads the data for the entire day from 00:00 January 15th to 23:59 January 15th, takes all the data, processes it, and does something.

<br>

![b1](images/b1.jpg)

<br><br>


**Streaming:**

Imagine a taxi service where every time a user requests a ride, trip information (location, estimated
 time of arrival, fare, etc.) is sent and processed in real time. Each event that is generated (ride 
 start, stops, arrival at the destination) is part of the data stream.

A data stream is a continuous sequence of data that is generated and processed in real time or near 
real time. Instead of waiting for large amounts of data to accumulate before processing them (as in 
batch processing), data streams allow information to be handled as it arrives. This week, we will not 
talk about this. This week, we will focus on things that process huge chunks of data in one go.

**Batch jobs**

Batch jobs typically run on a scheduled basis, processing accumulated data over a set period. The most 
common intervals are daily and hourly.

- Daily batch jobs collect data throughout the day and process it once the day is over.

- Hourly batch jobs process everything that happened in the previous hour.
- Less common intervals include running batch jobs multiple times per hour, such as every five minutes,
 but these are not as typical.

 **Technologies for Batch Jobs**

Batch jobs often use Python scripts to handle data ingestion and transformation. For example, a script 
might retrieve a CSV file and load it into a database. These scripts can run at various intervals, 
including monthly.

SQL is another common choice for defining transformations. In week four, we saw how SQL can process 
large chunks of data at once, making it well-suited for batch processing.

Apache Spark is a widely used technology for batch jobs, along with alternatives like Apache Flink.

**Execution and Orchestration**

Python scripts can run on various platforms, including Kubernetes and AWS Batch. To manage and 
orchestrate batch workflows, Airflow is commonly used.

A typical workflow might look like this:

- Data ingestion: CSV files are stored in a data lake.

- Python processing:  A script processes the CSVs and moves the data to a warehouse.

- SQL transformations: Using tools like dbt, the data is transformed.

- Further processing: Spark or additional Python jobs refine the data.

Each of these steps represents a batch job, and Airflow helps coordinate them within a data pipeline.

**Advantages and Disadvantages of Batch Jobs**

Batch jobs offer several advantages:

- Ease of management: Workflow tools allow us to define steps, parameterize scripts, and easily retry 
failed executions. 

- Retry: Since batch jobs are not real-time, retries are safer and more controlled.

- Scalability: If a Python script encounters a larger file, we can scale up by using a more powerful 
machine. Similarly, if a Spark job requires more resources, we can add machines to the cluster. This 
flexibility makes batch processing highly adaptable.

However, batch processing has a key disadvantage:

- Delay: Since batch jobs run at scheduled intervals, data is not available in real time. 

While streaming can solve this issue, real-time processing is not always necessary. In many cases, it's
acceptable to wait an hour, a day, or even a week before using the data in reports or dashboards. Many
 metrics are not time-sensitive, making batch processing a practical choice.

Due to these advantages, batch jobs remain the dominant approach in most data processing workflows


## Introduction to Spark

_[Video source](https://www.youtube.com/watch?v=FhaqbEOuQ8U)_

Apache Spark is an open-source, distributed computing system designed for big data processing and 
analytics. It provides a fast and general-purpose engine for large-scale data processing by leveraging 
in-memory computing and efficient data processing techniques.

For example, if we have data stored in a database or a data lake, Spark pulls this data into 
its machines (executors), processes it, and then writes the output back to a data lake or a data
warehouse. This distributed processing is what makes Spark powerful. It can run on clusters with 
tens or even thousands of machines, all working together to transform and store data efficiently.

<br>

![b2](images/b2.jpg)

<br><br>

While Spark is written in Scala, it supports multiple languages. Scala is the native way to interact 
with Spark, but there are also wrappers for other languages. The Python wrapper, known as PySpark, is 
especially popular.

Spark is primarily used for executing batch jobs but also supports streaming. In a streaming context, 
incoming data is processed as a sequence of small batches, applying similar techniques as in batch 
processing. However, here we will focus only on batch jobs.

**When to use Spark?**

Typically Spark is used when your data is in a data lake. Usually, this is just some location in S3 or 
Google Cloud Storage, and then we have a bunch of Parquet files there. Spark would pull this data from
a data lake, do some processing, and then put this data back into the data lake.

You would typically use it for the same things where you would use SQL. Since we have a data lake here 
and not a data warehouse, in a data warehouse, we would just go with BigQuery and use SQL. But when you
just have a bunch of files lying in your S3 or Google Cloud Storage, using SQL is not always easy. In 
that case, you would go with Spark.

These days, you can actually run SQL on your data lake using things like Hive, Presto, or even Spark. 
In AWS, there is a managed version of Presto called Athena. You can also use these tools to execute SQL
on your data in a data lake and then write the results back to the lake.

If you can express your job as an SQL query, you should go with Presto, Athena, or even BigQuery with 
external tables. However, sometimes you cannot express your jobs with SQL. You may need more flexibility,
your code might become too difficult to manage, or you may want to split it into different modules with
unit tests. Some functionality might not be possible to implement in SQL. This is exactly when you want
 to use Spark.


 **Example workflow for machine learning**

A typical workflow at work involves handling raw data, which is first stored in a data lake. We then
perform a series of transformations on this data, such as aggregations and joins, using SQL tools like 
Athena or Presto. Once the data is prepared, there may be cases where SQL is not sufficient for more 
complex transformations. In such instances, we introduce another step using Spark, which allows us to 
run Python jobs or train machine learning models.

Another common workflow involves utilizing a trained machine learning model. For example, we can take
 the model generated by our Python script and apply it using Spark. The output can then be stored back 
 in the data lake and subsequently moved to a data warehouse or another destination.

This is a typical scenario where multiple components are involved, with most preprocessing occurring in
 the data lake. Therefore, my recommendation is to use SQL whenever possible, but for tasks that go 
 beyond SQL's capabilities, Spark is the better choice.


 ## Installation

 _[Video source](https://www.youtube.com/watch?v=hqUbB9c8sKg)_

 Install instructions for:
 
- [`Linux`](install/linux.md)
- [`MacOs`](install/macos.md)
- [`Windows`](install/windows.md)

If it was installed correctly and after configuring JAVA_HOME and SPARK_HOME, in the terminal (ubuntu WSL2 in this case) run this command:

```
spark-shell
```

And you should see something like this:

<br>

![b3](images/b3.jpg)

<br><br>

And follow this to run PySpark

- [`PySpark`](install/pyspark.md)


To test that pyspark works correctly, let's create a file called test.py, in this case in opt/spark:

```
touch test.py
```

And then open vscode:

```
code test.py
```

copy the file "taxi_zone_lookup.csv" inside the opt/spark folder and copy this code in test.py:

```python

import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

df = spark.read \
    .option("header", "true") \
    .csv('taxi_zone_lookup.csv')

df.show()

```

and run test.py in the ubuntu terminal:

```
python3 test.py
```

you should look something like this:

```

+----------+-------------+--------------------+------------+                    
|LocationID|      Borough|                Zone|service_zone|
+----------+-------------+--------------------+------------+
|         1|          EWR|      Newark Airport|         EWR|
|         2|       Queens|         Jamaica Bay|   Boro Zone|
|         3|        Bronx|Allerton/Pelham G...|   Boro Zone|
|         4|    Manhattan|       Alphabet City| Yellow Zone|
|         5|Staten Island|       Arden Heights|   Boro Zone|
|         6|Staten Island|Arrochar/Fort Wad...|   Boro Zone|
|         7|       Queens|             Astoria|   Boro Zone|
|         8|       Queens|        Astoria Park|   Boro Zone|
|         9|       Queens|          Auburndale|   Boro Zone|
|        10|       Queens|        Baisley Park|   Boro Zone|
|        11|     Brooklyn|          Bath Beach|   Boro Zone|
|        12|    Manhattan|        Battery Park| Yellow Zone|
|        13|    Manhattan|   Battery Park City| Yellow Zone|
|        14|     Brooklyn|           Bay Ridge|   Boro Zone|
|        15|       Queens|Bay Terrace/Fort ...|   Boro Zone|
|        16|       Queens|             Bayside|   Boro Zone|
|        17|     Brooklyn|             Bedford|   Boro Zone|
|        18|        Bronx|        Bedford Park|   Boro Zone|
|        19|       Queens|           Bellerose|   Boro Zone|
|        20|        Bronx|             Belmont|   Boro Zone|
+----------+-------------+--------------------+------------+
only showing top 20 rows
```


## Spark SQL and DataFrames

### First Look at PySpark

 _[Video source](https://www.youtube.com/watch?v=r_Sf6fCB40c)_

In this section, we will take a first look at PySpark, load some data, and save it using PySpark:

- We will see how to read a CSV file. 
- We will talk about partitions. What they are and why they matter.
- We will save this data to Parquet.
- We will explore the Spark Master UI.

SparkSession is the main entry point for interacting with Spark. We use it to read data and perform 
operations:

```python

import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()
```    

Rather than using yellow or green taxi records, we will work with high-volume for-hire vehicle trip 
records. Download the file:

```
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhvhv/fhvhv_tripdata_2021-01.csv.gz

```

Unzip it:

```
gunzip fhvhv_tripdata_2021-01.csv.gz
```

Next, I want to use the same approach as last time to read the CSV file into Spark. We specify the 
header, then run show(). It correctly detects the column names.

```python
df = spark.read \
    .option("header", "true") \
    .csv('fhvhv_tripdata_2021-01.csv')

df.show()
```

**Run pyspark in the terminal**

When you type pyspark in the Ubuntu terminal, it launches an interactive PySpark shell. This shell 
allows you to interact with Apache Spark using Python. 

- It initializes a Spark session (SparkSession)  with default configurations.
- You can run PySpark commands interactively, which is useful for testing and debugging Spark code.

Paste this code in the interactive PySpark shell:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").appName('test').getOrCreate()

df = spark.read.option("header", "true").csv('fhvhv_tripdata_2021-01.csv')

df.show()
```

You should look something like this:

<br>

![b4](images/b4.jpg)

<br><br>


If we check the Spark cluster UI and refresh it, we see new entries appear. Each time we execute an 
operation, a new job is logged. If I run the command again, another job will appear in the UI.

<br>

![b5](images/b5.jpg)

<br><br>

Now, instead of using show(), I will use df.head(5), which returns the first five records.

<br>

![b6](images/b6.jpg)

<br><br>

We can see that Spark is reading the data as strings instead of timestamps or numbers. Unlike Pandas, 
Spark does not infer data types automatically, so everything is treated as a string by default.

We can confirm this by checking the schema. It’s not well formatted, but we can see that all fields are
classified as string type. I will use df.schema:

<br>

![b7](images/b7.jpg)

<br><br>

**Defining the schema**

To properly define a schema for our DataFrame, I will format the inferred schema in Visual Studio Code. Spark schemas use StructType, which is a Scala construct, so I need to convert it into Python code.

```python

schema = types.StructType([
    types.StructField('hvfhs_license_num', types.StringType(), True),
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)
])
```

After defining the schema, I need to specify it when reading the CSV file. Adding the schema parameter ensures that Spark correctly interprets the data types. 

```python

df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv('fhvhv_tripdata_2021-01.csv')
```    

Running df.head(10) on the loaded data confirms that timestamps are parsed correctly, location IDs are treated as numbers without quotes, and SR_Flag remains a nullable string:

<br>

![b8](images/b8.jpg)

<br><br>

This is how we define and apply a schema in Spark.

**Partitions**

So here we have one huge CSV file, and actually, having just one file is not good. I want to tell you a bit about the internals of Spark. We will cover that in more detail later.

Imagine that this is our Spark cluster, and inside the Spark cluster, we have a bunch of executors. These are computers that are actually doing computational work. They pull the files from our data lake and perform computations.

If we have only one large file, only one executor can process it, while the others remain idle. This is inefficient, so we want multiple smaller files instead of one large file.

<br>

![b9](images/b9.jpg)

<br><br>

Now, let's say we have fewer executors than files. Each file will be assigned to an executor. One executor will get one file, another will get another file, and so on. When an executor finishes processing its file, it will pick the next available one. This way, all files will eventually be processed.

<br>

![b10](images/b10.jpg)

<br><br>

In Spark, these subdivisions are called partitions. Instead of having one large partition, which only one executor can handle, we want multiple partitions. If we take one large file and split it into, say, 24 partitions, each executor can process a smaller part of the file in parallel.

To achieve this, Spark has a special command called df.repartition(), which takes the number of partitions as a parameter. When we read a file into a DataFrame, Spark creates as many partitions as there are files in the folder.

Executing df.repartition(24) does not immediately change the DataFrame because repartitioning is lazy. The change is applied only when we perform an action, such as saving the DataFrame.

**Saves as Parquet file**

Now, let's write the DataFrame to Parquet:

```python

df = df.repartition(24)
df.write.parquet("for_hire_vehicles/2021.01")
```

When we execute this, Spark starts processing. We can see the job in the Spark UI under "Parquet." Clicking on it reveals the partitioning process. The operation is quite expensive, so it takes some time to complete.

<br>

![b11](images/b11.jpg)

<br><br>

Now, if I look at this folder, I can see that there's a bunch of files. Each file follows a naming pattern: the part number of the partition, a long name, snappy (which is the compression algorithm used in Parquet), and then .parquet.

We see multiple files—there should be 24, as we requested, or 26, because we also have a SUCCESS file. This SUCCESS file is empty (size zero) and simply indicates that the job finished successfully. If this file is missing, we can't be sure that the files are complete or not corrupted. Once the flag is there, we know the job has finished. This acts like a commit message at the end of a Spark job.

<br>

![b12](images/b12.jpg)

<br><br>