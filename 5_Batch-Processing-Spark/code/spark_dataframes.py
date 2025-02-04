import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql import functions as F

# First Look at PySpark

spark = SparkSession.builder.master("local[*]").appName('test').getOrCreate()


schema = types.StructType([
    types.StructField('hvfhs_license_num', types.StringType(), True),
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)
])

df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv('fhvhv_tripdata_2021-01.csv')

df.head(10)

df = df.repartition(24)

df.write.parquet('fhvhv/2021/01/')

# Spark DataFrames

df = spark.read.parquet('fhvhv/2021/01/')

df.printSchema()

df.select("pickup_datetime", "dropoff_datetime", "PULocationID", "DOLocationID") \
    .filter(df.hvfhs_license_num == 'HV0003') \
    .show()


df \
    .withColumn("pickup_date", F.to_date(df.pickup_datetime)) \
    .withColumn("dropoff_date", F.to_date(df.dropoff_datetime)) \
    .select("pickup_date","dropoff_date","PULocationID","DOLocationID") \
    .show()   


def crazy_stuff(base_num):

    num = int(base_num[1:])
    if num % 7 == 0:
        return f's/{num:03x}'
    elif num % 3 == 0:
        return f'a/{num:03x}'
    else:
        return f'e/{num:03x}'
    

crazy_stuff_udf = F.udf(crazy_stuff, returnType=types.StringType())


df \
    .withColumn('pickup_date', F.to_date(df.pickup_datetime)) \
    .withColumn('dropoff_date', F.to_date(df.dropoff_datetime)) \
    .withColumn('base_id', crazy_stuff_udf(df.dispatching_base_num)) \
    .select('base_id', 'pickup_date', 'dropoff_date', 'PULocationID', 'DOLocationID') \
    .show()