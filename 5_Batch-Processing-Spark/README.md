# Batch Processing

### Table of contents

- [Introduction to Batch Processing](#introduction-to-batch-processing)
- [Introduction to Spark](#introduction-to-spark)
- [Installation](#installation)
- [Spark SQL and DataFrames](#spark-sql-and-dataframes)
    - [First Look at PySpark](#first-look-at-pyspark)
    - [Spark DataFrames](#spark-dataframes)    
    - [Preparing Taxi Data](#preparing-taxi-data)  





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

### Spark DataFrames

 _[Video source](https://www.youtube.com/watch?v=ti3aC1m3rE8)_

In this section, we will talk more about Spark DataFrames. We already saw DataFrames, these are what we
call df, where df is short for DataFrame.Now, I want to use the Parquet files that we created in the 
previous section. I will read them using:

```python
df = spark.read.parquet('fhvhv/2021/01/')
```

Since Parquet files contain schema information, they remember the types for each column. We don’t need to specify the schema 
explicitly because it is already stored in the file. We can print the schema using:

```python

df.printSchema()
```

You should look something like this:

```
root
 |-- hvfhs_license_num: string (nullable = true)
 |-- dispatching_base_num: string (nullable = true)
 |-- pickup_datetime: timestamp (nullable = true)
 |-- dropoff_datetime: timestamp (nullable = true)
 |-- PULocationID: integer (nullable = true)
 |-- DOLocationID: integer (nullable = true)
 |-- SR_Flag: string (nullable = true)
``` 

One advantage of Parquet files is that they are smaller. They store the schema and use more efficient 
ways of compressing the data. For example, instead of using multiple bytes like a CSV file with plain
text, Parquet can store an integer in just four bytes per value.

**Select and filter**

So we have this DataFrame. What can we do with it? We can perform the usual operations we do with Pandas.
If we only want to select a few columns, we use dataframe.select(), providing a list of the columns we 
want. For example, if we want to select pickup_datetime, off_datetime, pickup_location_id, and 
dropoff_location_id, we do it like this:

```python
df.select("pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID")

```

We can also filter data. For example, we can use a filter statement to get only the records where a 
specific license number matches a given value:

```python
df.select("pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID")\
    .filter(df.hvfhs_license_num == 'HV003')

```

At first, when executing this, nothing appears to happen. However, this is because Spark operates 
lazily. The computation isn’t executed immediately.

But now if we add show(), then spark will do something. Lets execute this:

```python
df.select("pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID") \
    .filter(df.hvfhs_license_num == 'HV0003') \
    .show()

```

And you should see something like this:

<br>

![b13](images/b13.jpg)

<br><br>

In Spark, there is a distinction between operations that are executed right away and those that are 
deferred. These are called actions and transformations.

**Actions and Transformations**

Transformations are operations that do not execute right away. These operations create a sequence of transformations that Spark tracks internally. Spark does not execute anything immediately. Instead, it builds a logical plan of transformations. For example:

- Selecting columns
- Filtering data
- Applying functions to each column

However, when we call an action like .show(), Spark evaluates the entire transformation sequence and executes the computation. At this point, Spark processes all previous transformations and returns the result. Actions are eager and trigger execution. Examples of actions include:

- show(): Displays the DataFrame.
- take(5): Retrieves the first five records. Similar to head()
- write.csv() or write.parquet() – Triggers execution to write results to storage.

**Built-in functions available in Spark**

You might be wondering if this is the same as using SQL

```python
df.select("pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID") \
    .filter(df.hvfhs_license_num == 'HV0003') 

```

In SQL, we can simply write:

```sql

SELECT pickup_datetime, dropoff_datetime, PULocationID, DOLocationID
FROM df
WHERE hvfhs_license_num == HV0003;
```

So why use Spark instead? Spark is more flexible and provides additional functionality, such as User-Defined Functions (UDFs).

Before diving into UDFs, let's first look at the built-in functions available in Spark.

In Spark, we have pyspark.sql.functions, a collection of functions that Spark provides. To use them, we typically import them as follows:

```python
from pyspark.sql import functions as F
```

Using F, we can explore available functions by typing F. and pressing Tab. There are many built-in functions.

One useful function is to_date(), which extracts only the date from a datetime column, discarding hours, minutes, and seconds.

We can also use withColumn() to create new columns. For example:

```python

df \
    .withColumn("pickup_date", F.to_date(df.pickup_datetime)) \
    .withColumn("dropoff_date", F.to_date(df.dropoff_datetime)) \
    .show()    
```

This code performs the following operations:

- Creates a new column named "pickup_date". Converts the "pickup_datetime" column into a date format using F.to_date(). 

- Creates another new column named "dropoff_date". Converts the "dropoff_datetime" column to a date format, similar to the previous step.

And you should see something like this:

<br>

![b14](images/b14.jpg)

<br><br>

If we use a column name that already exists, Spark overwrites it. 

Finally, we can add a select():

```python

df \
    .withColumn("pickup_date", F.to_date(df.pickup_datetime)) \
    .withColumn("dropoff_date", F.to_date(df.dropoff_datetime)) \
    .select("pickup_date","dropoff_date","PULocationID","DOLocationID") \
    .show()    
```

And you should see something like this:

<br>

![b15](images/b15.jpg)

<br><br>

**User-Defined Functions**

Let's say we have a function that performs complex logic, something not easy to express with SQL. I'll call this function crazy_stuff.

For example, suppose it processes a column called dispatching_base_number. The logic could be:

- Extracts the numeric part of the string by removing the first character (base_num[1:]) and converts it to an integer (num).

- If the number is divisible by 7, return an ID starting with "S" followed by the number in hexadecimal format.
- If the number is divisible by 3, return an ID starting with "A" followed by the number in hexadecimal format.
- Otherwise, return an ID starting with "E" followed by the number in hexadecimal format.

```python

def crazy_stuff(base_num):

    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'
```        

Expressing this in SQL would be cumbersome, especially as the logic grows more complex with multiple conditions. The advantage of implementing this logic in Python is that it can live in a separate module and it can be unit-tested.

Now, to turn this Python function into a User-Defined Function (UDF) in PySpark:

```python

crazy_stuff_udf = F.udf(crazy_stuff, returnType=types.StringType())
```

Now we can use this udf:

```python

df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .withColumn('base_id', crazy_stuff_udf(df.dispatching_base_num)) \
    .select('base_id', 'pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()
```    

And you should see something like this:

<br>

![b16](images/b16.jpg)

<br><br>

Although this example is artificial, some business rules can be quite complex. SQL queries with multiple
CASE statements can become unreadable. While SQL-based tools like dbt allow testing, Python makes it 
much easier.

This is how you perform transformations in PySpark using DataFrames. While many operations resemble SQL,
the ability to define custom UDFs gives Spark an edge.

In the next section, we'll explore how to use SQL in Spark, but the key takeaway is that Spark allows
you to combine SQL with complex Python logic, offering the best of both worlds. This flexibility is 
especially useful in machine learning workflows, where logic often resembles this crazy_stuff function.


### Preparing Taxi Data

 _[Video source](https://www.youtube.com/watch?v=CI3P4tAtru4)_

We are going to use this bash script to download Yellow and Green Taxi Data. We save the code in a file 
called script.sh

```bash
set -e

TAXI_TYPE=$1 # "yellow"
YEAR=$2 # 2020

URL_PREFIX="https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

for MONTH in {1..12}; do
  FMONTH=`printf "%02d" ${MONTH}`

  URL="${URL_PREFIX}/${TAXI_TYPE}/${TAXI_TYPE}_tripdata_${YEAR}-${FMONTH}.csv.gz"

  LOCAL_PREFIX="data/raw/${TAXI_TYPE}/${YEAR}/${FMONTH}"
  LOCAL_FILE="${TAXI_TYPE}_tripdata_${YEAR}_${FMONTH}.csv.gz"
  LOCAL_PATH="${LOCAL_PREFIX}/${LOCAL_FILE}"

  echo "downloading ${URL} to ${LOCAL_PATH}"
  mkdir -p ${LOCAL_PREFIX}
  wget ${URL} -O ${LOCAL_PATH}

done
```

The script automates the process of downloading NYC taxi trip data for a given taxi type and year, 
saving each month’s data in an organized folder structure.

Then we run the script in the terminal, for example :

```
bash script.sh yellow 2020
```

To read the csv and convert them to parquet, we will use this script, for example for green taxi data:

```python

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types

spark = SparkSession.builder.master("local[*]").appName('test').getOrCreate()

green_schema = types.StructType([
    types.StructField("VendorID", types.IntegerType(), True),
    types.StructField("lpep_pickup_datetime", types.TimestampType(), True),
    types.StructField("lpep_dropoff_datetime", types.TimestampType(), True),
    types.StructField("store_and_fwd_flag", types.StringType(), True),
    types.StructField("RatecodeID", types.IntegerType(), True),
    types.StructField("PULocationID", types.IntegerType(), True),
    types.StructField("DOLocationID", types.IntegerType(), True),
    types.StructField("passenger_count", types.IntegerType(), True),
    types.StructField("trip_distance", types.DoubleType(), True),
    types.StructField("fare_amount", types.DoubleType(), True),
    types.StructField("extra", types.DoubleType(), True),
    types.StructField("mta_tax", types.DoubleType(), True),
    types.StructField("tip_amount", types.DoubleType(), True),
    types.StructField("tolls_amount", types.DoubleType(), True),
    types.StructField("ehail_fee", types.DoubleType(), True),
    types.StructField("improvement_surcharge", types.DoubleType(), True),
    types.StructField("total_amount", types.DoubleType(), True),
    types.StructField("payment_type", types.IntegerType(), True),
    types.StructField("trip_type", types.IntegerType(), True),
    types.StructField("congestion_surcharge", types.DoubleType(), True)
])


years = [2020,2021]

for year in years:
    for month in range(1, 13):
        print(f'processing data for {year}/{month}')

        input_path = f'data/raw/green/{year}/{month:02d}/'
        output_path = f'data/pq/green/{year}/{month:02d}/'

        df_green = spark.read.option("header", "true").schema(green_schema).csv(input_path)

        df_green.repartition(4).write.parquet(output_path)
```

This script uses PySpark to process and transform raw CSV files containing green taxi trip data into Parquet format. It creates a StructType schema (green_schema) that defines the expected structure of the dataset, including column names and data types. Loop through Years and Months. Constructs input (input_path) and output (output_path) file paths.

Reads the CSV file from the input_path, applying the green_schema and writes the transformed data to Parquet format in output_path

We can run the script in the /opt/spark directory, for example :

```
spark-submit green_taxi_data.py
```

After a couple of minutes, you should see something like this:

<br>

![b17](images/b17.jpg)

<br>

Finally, we can run the script for yellow taxi data:

```
spark-submit yellow_taxi_data.py
```