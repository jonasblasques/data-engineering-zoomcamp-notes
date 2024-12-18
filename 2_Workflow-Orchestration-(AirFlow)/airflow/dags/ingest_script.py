import pandas as pd
from sqlalchemy import create_engine
import requests
import gzip
import shutil


def download_and_unzip(csv_name_gz, csv_name):

    url = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
    
    # Download the CSV.GZ file
    response = requests.get(url)
    if response.status_code == 200:
        with open(csv_name_gz, 'wb') as f_out:
            f_out.write(response.content)
    else:
        print(f"Error al descargar el archivo: {response.status_code}")
        return False

    # Unzip the CSV file
    with gzip.open(csv_name_gz, 'rb') as f_in:
        with open(csv_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return True


def process_and_insert_to_db(csv_name, user, password, host, port, db, table_name):
    # Connect to PostgreSQL database
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)

    # Process the first chunk
    df = next(df_iter)
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # Insert the data into the database
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    # Process the rest of the data
    while True:
        try:
            df = next(df_iter)
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            df.to_sql(name=table_name, con=engine, if_exists='append')
            print('inserted another chunk')

        except StopIteration:
            print('completed')
            break



 