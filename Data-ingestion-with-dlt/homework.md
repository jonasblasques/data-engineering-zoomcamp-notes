
[data ingestion workshop](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2025/workshops/dlt/data_ingestion_workshop.md)

[Video source](https://www.youtube.com/live/pgJWP_xqO1g)

## Question 1: dlt Version

1. Install dlt:

```
pip install dlt[duckdb]
```

2. Check version:

```
dlt --version
```

Answer: dlt 1.6.1


## Question 2: Define & Run the Pipeline (NYC Taxi API)

Use dlt to extract all pages of data from the API.

Steps:

1️. Use the @dlt.resource decorator to define the API source.

2️. Implement automatic pagination using dlt's built-in REST client.

3️. Load the extracted data into DuckDB for querying.

```python

import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
import duckdb


# Use the @dlt.resource decorator to define the API source. Implement automatic pagination
@dlt.resource(name="rides") 
def ny_taxi():
    client = RESTClient(
        base_url="https://us-central1-dlthub-analytics.cloudfunctions.net",
        paginator=PageNumberPaginator(
            base_page=1,
            total_path=None
        )
    )

    for page in client.paginate("data_engineering_zoomcamp_api"):    # <--- API endpoint for retrieving taxi ride data
        yield page   # <--- yield data to manage memory


# define new dlt pipeline
pipeline = dlt.pipeline(
    pipeline_name="ny_taxi_pipeline",
    destination="duckdb",
    dataset_name="ny_taxi_data"
)

# Load the extracted data into DuckDB for querying.
load_info = pipeline.run(ny_taxi, write_disposition="replace")

# Connect to the DuckDB database
conn = duckdb.connect(f"{pipeline.pipeline_name}.duckdb")

# Set search path to the dataset
conn.sql(f"SET search_path = '{pipeline.dataset_name}'")

# Describe the dataset and load it into a Pandas DataFrame
df = conn.sql("DESCRIBE").df()

# Display the DataFrame
print(df)
```

Output:

```
           database        schema  ...                                       column_types temporary
0  ny_taxi_pipeline  ny_taxi_data  ...  [VARCHAR, VARCHAR, BIGINT, TIMESTAMP WITH TIME...     False
1  ny_taxi_pipeline  ny_taxi_data  ...  [BIGINT, BIGINT, VARCHAR, VARCHAR, TIMESTAMP W...     False
2  ny_taxi_pipeline  ny_taxi_data  ...  [BIGINT, BIGINT, TIMESTAMP WITH TIME ZONE, VAR...     False
3  ny_taxi_pipeline  ny_taxi_data  ...  [DOUBLE, DOUBLE, DOUBLE, BIGINT, VARCHAR, DOUB...     False
```


## Question 3: Explore the loaded data

```python

df = pipeline.dataset(dataset_type="default").rides.df()
df.info()

```

Output:

```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 10000 entries, 0 to 9999
```

## Question 4: Trip Duration Analysis

Run the SQL query below to calculate the average trip duration in minutes.

```python

with pipeline.sql_client() as client:
    res = client.execute_sql(
            """
            SELECT
            AVG(date_diff('minute', trip_pickup_date_time, trip_dropoff_date_time))
            FROM rides;
            """
        )
    # Prints column values of the first row
    print(res)
```    

```
[(12.3049,)]
```