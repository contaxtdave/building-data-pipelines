import urllib3 
from urllib3 import request
import certifi
import json
import sqlite3

import pandas as pd
import logging

# define top level module logger
logger = logging.getLogger(__name__)

def source_data_from_parquet(parquet_file_name):
    try:
        df_parquet = pd.read_parquet(parquet_file_name)
        logger.info(f'{parquet_file_name} : extracted {df_parquet.shape[0]} records from parquet file')
    except Exception as e:
        logger.exception( f'{parquet_file_name} : exception {e} encountered while extracting the parquet file')
        df_parquet = pd.DataFrame()
    return df_parquet

def source_data_from_csv(csv_file_name):
    try:
        df_csv = pd.read_csv(csv_file_name)
        logger.info(f'{csv_file_name} : extracted {df_csv.shape[0]} records from the csv file')
    except Exception as e:
        logger.exception( f'{csv_file_name} : exception {e} encountered while extracting the {csv_file_name} file')
        df_csv = pd.DataFrame()
    return df_csv

def source_data_from_api(api_endpoint):
    try:
        # Check if API is available to retrieve the data
        # Sometimes we get certificate error.  We should never silence this error as this may cause a security threat.
        # Create a Pool Manager that can be used to read the API response
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        api_response = http.request('GET', api_endpoint)
        api_status = api_response.status
        if api_status == 200:
            logger.info(f'{api_status} - ok : while invoking the api {api_endpoint}')
            data = json.loads(api_response.data.decode('utf-8'))
            df_api = pd.json_normalize(data)
            logger.info(f'{api_status} - extracted {df_api.shape[0]} records the api {api_endpoint}')
        else:
            logger.error(f'{api_status} - error : while invoking the api {api_endpoint}')
            df_api = pd.DataFrame()
    except Exception as e:
        logger.exception(f'exception {e} : - exception {e} encountered while reading data from the api {api_endpoint}')
        df_api = pd.DataFrame()
    return df_api

def source_data_from_table(db_name, table_name):
    try:
        # Read sqlite query results into a pandas DataFrame
        with sqlite3.connect(db_name) as conn:
            df_table = pd.read_sql(f"SELECT * from {table_name}", conn)
            logger.info(f'{table_name}- read {df_table.shape[0]} records from the table: {table_name} in the database: {db_name}')
    except Exception as e:
        logger.exception(f'{db_name} : - exception {e} : encountered while reading data from the table {table_name} in the database: {db_name}')
        df_table = pd.DataFrame()
    return df_table

def source_data_from_webpage(web_page_url, matching_keyword):
    try:
        # Read webpage table into a pandas DataFrame
        df_html = pd.read_html(web_page_url, match = matching_keyword)
        df_html = df_html[0]
        logger.info(f'{web_page_url}- read {df_html.shape[0]} records from the page: {web_page_url}')
    except Exception as e:
        logger.exception(f'{db_name} : - exception {e} encountered while reading data from the page {web_page_url}')
        df_html = pd.DataFrame()
    return df_html

def extracted_data():
    parquet_file_name = "chapter_4/data/yellow_tripdata_2025-01.parquet"
    csv_file_name = "chapter_4/data/yellow_tripdata_sample.csv"
    api_endpoint = "https://data.cityofnewyork.us/resource/hgi-nx95.json?$"limit"
    db_name = "chapter_4/data/movies.sqlite"
    table_name = "movies"
    web_page_url = "https://en.wikipedia.org/wiki/List_of_countries_by_GOP_(nominal)"
    matching_keyword = "by country"

    # Extract data from all source systems
    # Now these dataframes are available for loading data into either VSA table, PSA table or to be consumed in 
    # transformation pipeline
    df_parquet,df_csv,df_api,df_table,df_html = (source_data_from_parquet(parquet_file_name),
                                                 source_data_from_csv(csv_file_name),
                                                 source_data_from_api(api_endpoint),
                                                 source_data_from_table(db_name, table_name),
                                                 source_data_from_webpage(web_page_url, matching_keyword))
    return df_parquet, df_csv, df_api, df_table, df_html
    
        
    
    

